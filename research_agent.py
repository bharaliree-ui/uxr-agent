"""
research_agent.py — A UX Research Synthesis Agent, built from scratch.

WHAT IT DOES
    Point it at a folder of interview transcripts. It reads each one, clusters
    findings into themes, backs every theme with VERBATIM participant quotes,
    rates how confident it is, and writes a section flagging what a human must
    verify. Output: synthesis_report.md.

WHY IT'S BUILT THIS WAY (the part you talk about in interviews)
    Naive "summarize these interviews" prompts hallucinate quotes, over-merge
    themes, and present guesses as findings. This agent is designed against
    those failure modes on purpose:
      - It must quote participants word-for-word and attribute by ID (P1, P2...).
      - It rates each theme High / Medium / Low confidence.
      - It is required to produce a "Needs Human Verification" section.
      - It never finalizes — it produces a DRAFT for a researcher to check.
    That's the UX-research judgment layered on top of the model.

    It's a true agent (a model in a loop with tools), not a single prompt: it
    decides which transcripts to read, reads them one by one, then writes the
    report — all on its own.

RUN IT
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python research_agent.py
"""

import os
import glob
import anthropic


# ─────────────────────────────────────────────────────────────────────────────
# 1. TOOLS — ordinary functions the agent is allowed to call.
# ─────────────────────────────────────────────────────────────────────────────

TRANSCRIPT_DIR = "transcripts"


def list_transcripts() -> str:
    """Return the filenames of all transcripts available to analyze."""
    files = sorted(os.path.basename(p) for p in glob.glob(f"{TRANSCRIPT_DIR}/*.txt"))
    return "\n".join(files) if files else "No transcripts found."


def read_transcript(filename: str) -> str:
    """Return the full text of one transcript by filename, e.g. 'P1.txt'."""
    path = os.path.join(TRANSCRIPT_DIR, os.path.basename(filename))  # basename = stay in-folder
    if not os.path.exists(path):
        return f"Error: {filename} not found."
    with open(path) as f:
        return f.read()


def save_report(filename: str, content: str) -> str:
    """Save the finished synthesis report to a markdown file."""
    with open(filename, "w") as f:
        f.write(content)
    return f"Saved report to {filename} ({len(content)} characters)."


TOOL_FUNCTIONS = {
    "list_transcripts": list_transcripts,
    "read_transcript": read_transcript,
    "save_report": save_report,
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. TOOL MENU — what the model sees. (Writing these well is UX work.)
# ─────────────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_transcripts",
        "description": "List every interview transcript filename available to analyze. Call this first.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_transcript",
        "description": "Read the full text of ONE transcript. Read every transcript before synthesizing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "A transcript filename, e.g. 'P1.txt'"}
            },
            "required": ["filename"],
        },
    },
    {
        "name": "save_report",
        "description": "Save the final synthesis report. Call this once, at the very end, with the complete markdown.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Output filename, e.g. 'synthesis_report.md'"},
                "content": {"type": "string", "description": "The complete synthesis report in markdown"},
            },
            "required": ["filename", "content"],
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. SYSTEM PROMPT — where the research rigor lives.
#    Most of an agent's behavior comes from instructions like these, not code.
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a UX research synthesis assistant. You help a human \
researcher turn interview transcripts into a themed insights draft. You are \
careful, evidence-driven, and honest about uncertainty.

PROCESS
1. Call list_transcripts to see what's available.
2. Read EVERY transcript, one at a time, before drawing any conclusions.
3. Cluster what you heard into 3-6 themes. A theme should reflect a pattern \
across participants, not a one-off comment (note one-offs separately if severe).
4. Save one markdown report with save_report.

RULES THAT KEEP YOU HONEST
- Quote participants VERBATIM and attribute every quote by ID (e.g., P2). \
Never invent, paraphrase inside quotation marks, or attribute a quote to the \
wrong participant. If you can't find a real supporting quote, you don't have \
the theme.
- Each theme needs at least TWO supporting quotes from DIFFERENT participants, \
or it goes under "Single-source signals" instead.
- Rate each theme's confidence High / Medium / Low based on how many \
participants raised it and how consistent they were.
- You MUST end with a "## Needs Human Verification" section listing anything \
you inferred, any thin evidence, sample limitations, and questions a \
researcher should check before sharing these findings. Never present this \
draft as final or decision-ready.

REPORT FORMAT (markdown)
# Synthesis Draft: <product>
_Auto-generated draft — requires researcher review. N participants._

## Themes
### 1. <Theme name>  — Confidence: <High/Med/Low>
<2-3 sentence summary>
- "<verbatim quote>" — P#
- "<verbatim quote>" — P#
**Recommendation:** <one concrete, testable suggestion>

## Single-source signals
- <severe or notable one-off issues, attributed>

## Needs Human Verification
- <inferences, thin spots, sample caveats, open questions>
"""


# ─────────────────────────────────────────────────────────────────────────────
# 4. THE AGENT LOOP — identical shape to your first agent. think→act→observe.
# ─────────────────────────────────────────────────────────────────────────────

def run_agent(goal: str, client: anthropic.Anthropic, model: str = "claude-sonnet-4-6") -> str:
    messages = [{"role": "user", "content": goal}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_FUNCTIONS[block.name](**block.input)
                preview = result if len(str(result)) < 80 else str(result)[:77] + "..."
                print(f"  [tool] {block.name}({block.input}) -> {preview}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        messages.append({"role": "user", "content": tool_results})


# ─────────────────────────────────────────────────────────────────────────────
# 5. RUN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY first (see the top of this file).")

    client = anthropic.Anthropic()
    goal = (
        "Synthesize all the interview transcripts into a themed insights draft "
        "and save it to synthesis_report.md."
    )
    print(f"\nGOAL: {goal}\n")
    answer = run_agent(goal, client)
    print(f"\nAGENT:\n{answer}\n")
    print("Open synthesis_report.md to see the draft.")
