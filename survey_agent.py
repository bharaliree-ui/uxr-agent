"""
survey_agent.py — Survey mode: synthesize OPEN-ENDED survey responses.

Same idea as research_agent.py, but the input is a CSV (one row per respondent,
one or more free-text columns) instead of interview transcripts. It reuses the
exact same Excel tracker builder, so the output looks identical: a 3-tab workbook
where every theme links back to the respondent's words.

WHAT IT DOES vs. DOESN'T
    DOES:    cluster free-text answers ("what would you improve?") into themes,
             with verbatim attributed quotes and confidence ratings.
    DOESN'T: analyze rating/multiple-choice columns. Those are quantitative —
             count them in a spreadsheet. Feeding numbers to a language model
             invites made-up statistics. This agent ignores closed-ended columns.

    Designed for small studies (< ~500 responses). Past that, you'd batch the
    responses instead of reading them all at once.

RUN IT
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY="sk-ant-..."
    python survey_agent.py sample_survey.csv
"""

import os
import sys
import csv
import anthropic
from research_agent import build_workbook   # reuse the same linked-Excel builder

SURVEY_CSV = sys.argv[1] if len(sys.argv) > 1 else "sample_survey.csv"
OUTPUT_FILE = "Survey_Report_Tracker.xlsx"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers: load the CSV and assign a respondent ID to each row.
# ─────────────────────────────────────────────────────────────────────────────

def _load():
    with open(SURVEY_CSV, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    cols = rows[0].keys() if rows else []
    id_col = next((c for c in cols if "id" in c.lower() or "respondent" in c.lower()), None)
    for i, row in enumerate(rows, start=1):
        row["__id__"] = (row.get(id_col) or f"R{i}").strip() if id_col else f"R{i}"
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# 1. TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def inspect_survey() -> str:
    """Report the columns, row count, and sample values so the model can pick the open-text columns."""
    rows = _load()
    if not rows:
        return "The CSV is empty."
    out = [f"{len(rows)} responses. Columns and samples:"]
    for col in rows[0].keys():
        if col == "__id__":
            continue
        vals = [r[col].strip() for r in rows if r.get(col, "").strip()]
        avg = sum(len(v) for v in vals) / len(vals) if vals else 0
        kind = "OPEN-TEXT (likely)" if avg > 25 else "short/closed (likely numeric or category)"
        sample = " | ".join(vals[:2])[:160]
        out.append(f"- '{col}': {kind}; avg length {avg:.0f}; e.g. {sample}")
    return "\n".join(out)


def get_responses(columns: list) -> str:
    """Return every respondent's answers for the chosen open-text columns, attributed by ID."""
    rows = _load()
    valid = [c for c in columns if rows and c in rows[0]]
    if not valid:
        return f"None of {columns} are valid columns."
    out = []
    for r in rows:
        parts = [f"[{c}] {r[c].strip()[:600]}" for c in valid if r.get(c, "").strip()]
        if parts:
            out.append(f"{r['__id__']}: " + "  ||  ".join(parts))
    return "\n".join(out) if out else "No non-empty responses in those columns."


def submit_findings(product: str, participants: list, themes: list,
                    verification_notes: list) -> str:
    data = {"product": product, "participants": participants,
            "themes": themes, "verification_notes": verification_notes}
    build_workbook(data, OUTPUT_FILE)
    n = sum(len(t.get("quotes", [])) for t in themes)
    return f"Built {OUTPUT_FILE}: {len(themes)} themes, {n} linked quotes, {len(participants)} respondents."


TOOL_FUNCTIONS = {
    "inspect_survey": inspect_survey,
    "get_responses": get_responses,
    "submit_findings": submit_findings,
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. TOOL MENU
# ─────────────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "inspect_survey",
        "description": "Show the survey's columns, row count, and sample values. Call this first to find the open-text columns.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_responses",
        "description": "Get every respondent's verbatim answers for the chosen open-text columns. Ignore rating/closed columns.",
        "input_schema": {
            "type": "object",
            "properties": {
                "columns": {"type": "array", "items": {"type": "string"},
                            "description": "The open-text column names to synthesize"},
            },
            "required": ["columns"],
        },
    },
    {
        "name": "submit_findings",
        "description": "Submit the final synthesis as structured data. Call ONCE at the end. Every quote must be verbatim and attributed to a respondent ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "description": "What the survey is about"},
                "participants": {"type": "array", "items": {"type": "string"},
                                 "description": "Respondent IDs included, e.g. ['R1','R2',...]"},
                "themes": {
                    "type": "array",
                    "description": "3-6 themes, each supported by at least two quotes from different respondents",
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
                                        "participant": {"type": "string", "description": "Respondent ID"},
                                        "topic": {"type": "string", "description": "Which question/column"},
                                        "quote": {"type": "string", "description": "VERBATIM answer text"},
                                    },
                                    "required": ["participant", "quote"],
                                },
                            },
                        },
                        "required": ["name", "confidence", "summary", "recommendation", "quotes"],
                    },
                },
                "verification_notes": {"type": "array", "items": {"type": "string"},
                                       "description": "Sample caveats, thin evidence, inferences, open questions"},
            },
            "required": ["product", "participants", "themes", "verification_notes"],
        },
    },
]


SYSTEM_PROMPT = """You synthesize OPEN-ENDED survey responses into a structured, \
evidence-driven insights draft for a human researcher.

PROCESS
1. Call inspect_survey to see the columns. Identify the free-text columns; IGNORE \
rating/multiple-choice/numeric columns (those need quantitative analysis, not you).
2. Call get_responses on the open-text columns.
3. Cluster the answers into 3-6 themes.
4. Call submit_findings ONCE with the structured result.

RULES
- Quotes must be VERBATIM and attributed to the right respondent ID. Never invent or \
paraphrase a quote.
- Each theme needs at least TWO quotes from DIFFERENT respondents.
- Rate confidence High / Medium / Low by how many respondents raised it.
- verification_notes MUST list sample limitations and anything a researcher should check. \
This is a draft, never a final answer. Do NOT compute statistics from rating columns."""


# ─────────────────────────────────────────────────────────────────────────────
# 3. AGENT LOOP (same think → act → observe shape as research_agent.py)
# ─────────────────────────────────────────────────────────────────────────────

def run_agent(goal: str, client: anthropic.Anthropic, model: str = "claude-sonnet-4-6") -> str:
    messages = [{"role": "user", "content": goal}]
    while True:
        response = client.messages.create(
            model=model, max_tokens=4096, system=SYSTEM_PROMPT,
            tools=TOOLS, messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_FUNCTIONS[block.name](**block.input)
                print(f"  [tool] {block.name} -> {str(result)[:70]}")
                tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                     "content": str(result)})
        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY first (see the top of this file).")
    if not os.path.exists(SURVEY_CSV):
        raise SystemExit(f"CSV not found: {SURVEY_CSV}")
    client = anthropic.Anthropic()
    goal = f"Synthesize the open-ended responses in {SURVEY_CSV} and submit your findings."
    print(f"\nGOAL: {goal}\n")
    answer = run_agent(goal, client)
    print(f"\nAGENT:\n{answer}\n")
    print(f"Open {OUTPUT_FILE} to see the linked report.")
