"""
core.py — reusable synthesis engine used by the Streamlit app.

Two entry points, both run the agent loop on IN-MEMORY data (not files) and
return the structured findings dict, so a UI can display and download them:

    synthesize_transcripts(texts, api_key)   texts = {name: transcript_text}
    synthesize_survey(rows, api_key)         rows  = list of dict (one per respondent)

Same think→act→observe loop as research_agent.py; the tools just read from the
data passed in, and submit_findings captures the result instead of writing a file.
"""

import anthropic

MODEL = "claude-sonnet-4-6"

# The structured shape the model must return (shared by both modes).
_FINDINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "product": {"type": "string", "description": "What was studied"},
        "participants": {"type": "array", "items": {"type": "string"}},
        "themes": {
            "type": "array",
            "description": "3-6 themes, each with >=2 quotes from different people",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["High", "Medium", "Low"]},
                    "summary": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "quotes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "participant": {"type": "string"},
                                "topic": {"type": "string"},
                                "quote": {"type": "string", "description": "VERBATIM, no paraphrase"},
                            },
                            "required": ["participant", "quote"],
                        },
                    },
                },
                "required": ["name", "confidence", "summary", "recommendation", "quotes"],
            },
        },
        "verification_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["product", "participants", "themes", "verification_notes"],
}

_RULES = (
    "Quotes must be VERBATIM and correctly attributed — never invent or paraphrase. "
    "Each theme needs at least TWO quotes from DIFFERENT people. Rate confidence "
    "High/Medium/Low by how many raised it and how consistent they were. "
    "verification_notes must list sample limits, inferences, and open questions. "
    "This is a draft for a human to check, never a final answer. "
    "Always finish by calling the submit_findings tool — never reply in prose and "
    "never ask the user questions; make reasonable assumptions if something is unclear."
)

MAX_TOKENS = 8192


def _loop(client, system, tools, funcs, goal, max_turns=40):
    """Run the agent loop; return whatever submit_findings captured."""
    captured = {}

    def submit_findings(**kwargs):
        captured.update(kwargs)
        return "Findings received."

    funcs = {**funcs, "submit_findings": submit_findings}
    messages = [{"role": "user", "content": goal}]
    last_text = ""
    for _ in range(max_turns):
        resp = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, system=system,
                                      tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        text = "".join(b.text for b in resp.content if b.type == "text")
        if text:
            last_text = text

        if resp.stop_reason == "tool_use":
            results = []
            for b in resp.content:
                if b.type == "tool_use":
                    out = funcs[b.name](**b.input)
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": str(out)})
            messages.append({"role": "user", "content": results})
            if captured:                      # findings submitted — done
                return captured
            continue

        if captured:
            return captured
        if resp.stop_reason == "max_tokens":
            messages.append({"role": "user", "content":
                             "Your message was cut off. Continue and call submit_findings with the complete result."})
            continue
        # ended in prose without finishing — nudge it once more
        messages.append({"role": "user", "content":
                         "Finish now by calling the submit_findings tool with your themes."})

    if captured:
        return captured
    raise RuntimeError("The agent didn't return structured findings. It said: "
                       + (last_text[:250] or "(nothing)"))


_SUBMIT_TOOL = {
    "name": "submit_findings",
    "description": "Submit the final synthesis as structured data. Call ONCE at the end.",
    "input_schema": _FINDINGS_SCHEMA,
}


# ─────────────────────────────────────────────────────────────────────────────
# Transcript mode
# ─────────────────────────────────────────────────────────────────────────────

def synthesize_transcripts(texts: dict, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    def list_transcripts():
        return "\n".join(texts.keys())

    def read_transcript(name):
        return texts.get(name, f"Error: {name} not found.")

    tools = [
        {"name": "list_transcripts", "description": "List transcript names. Call first.",
         "input_schema": {"type": "object", "properties": {}}},
        {"name": "read_transcript", "description": "Read one transcript by name. Read all before synthesizing.",
         "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
        _SUBMIT_TOOL,
    ]
    system = ("You are a UX research synthesis assistant. List the transcripts, read every "
              "one, cluster findings into 3-6 themes, then call submit_findings. " + _RULES)
    funcs = {"list_transcripts": list_transcripts, "read_transcript": read_transcript}
    return _loop(client, system, tools, funcs,
                 "Synthesize all the transcripts and submit your findings.")


# ─────────────────────────────────────────────────────────────────────────────
# Survey mode
# ─────────────────────────────────────────────────────────────────────────────

def _respondent_id(row, cols, i):
    id_col = next((c for c in cols if "id" in c.lower() or "respondent" in c.lower()), None)
    return (str(row.get(id_col)).strip() if id_col and row.get(id_col) else f"R{i}")


def survey_sources(rows: list) -> dict:
    """Map each respondent ID to all their free-text, for quote highlighting."""
    if not rows:
        return {}
    cols = list(rows[0].keys())
    src = {}
    for i, row in enumerate(rows, start=1):
        rid = _respondent_id(row, cols, i)
        parts = [str(v) for v in row.values() if isinstance(v, str) and len(v.strip()) > 20]
        src[rid] = "  ".join(parts)
    return src


def synthesize_survey(rows: list, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    cols = list(rows[0].keys()) if rows else []

    def inspect_survey():
        out = [f"{len(rows)} responses. Columns:"]
        for c in cols:
            vals = [str(r[c]).strip() for r in rows if str(r.get(c, "")).strip()]
            avg = sum(len(v) for v in vals) / len(vals) if vals else 0
            kind = "OPEN-TEXT (likely)" if avg > 25 else "short/closed"
            out.append(f"- '{c}': {kind}; e.g. {' | '.join(vals[:2])[:140]}")
        return "\n".join(out)

    def get_responses(columns):
        valid = [c for c in columns if c in cols]
        out = []
        for i, r in enumerate(rows, start=1):
            rid = _respondent_id(r, cols, i)
            parts = [f"[{c}] {str(r[c]).strip()[:600]}" for c in valid if str(r.get(c, "")).strip()]
            if parts:
                out.append(f"{rid}: " + "  ||  ".join(parts))
        return "\n".join(out) if out else "No responses."

    tools = [
        {"name": "inspect_survey", "description": "Show columns and samples. Call first to find open-text columns.",
         "input_schema": {"type": "object", "properties": {}}},
        {"name": "get_responses", "description": "Get verbatim answers for chosen open-text columns. Ignore rating/closed columns.",
         "input_schema": {"type": "object", "properties": {
             "columns": {"type": "array", "items": {"type": "string"}}}, "required": ["columns"]}},
        _SUBMIT_TOOL,
    ]
    system = ("You synthesize OPEN-ENDED survey answers. Inspect the survey, get the open-text "
              "columns (IGNORE rating/numeric columns), cluster into 3-6 themes, then call "
              "submit_findings. Do NOT compute statistics from rating columns. " + _RULES)
    funcs = {"inspect_survey": inspect_survey, "get_responses": get_responses}
    return _loop(client, system, tools, funcs,
                 "Synthesize the open-ended survey responses and submit your findings.")
