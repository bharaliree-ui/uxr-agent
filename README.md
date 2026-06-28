# UX Research Synthesis Agent

An AI agent that turns interview transcripts into a themed insights **draft** — backed by verbatim quotes, rated for confidence, and output as an Excel tracker where every finding links back to the exact words that prove it.

Built as a self-directed experiment in applying AI to UX research, with a focus on the part that matters most: making the output trustworthy and traceable enough to act on.

---

## See it in 2 minutes (no setup required)

If you'd rather not run anything:

- **[`Research_Report_Tracker.xlsx`](Research_Report_Tracker.xlsx)** — the agent's output: a 3-tab workbook (Raw Data → Synthesis → Report). Download it and click any quote in the Synthesis tab to jump straight to its source on the Raw Data tab. This is the main thing to look at.
- **[`CASE_STUDY.md`](CASE_STUDY.md)** — the thinking: the design decisions, the failure modes I tested for, and how I'd evaluate it properly.

That's the fastest way to judge the work. Everything below is for running it yourself.

---

## What it does

Point it at a folder of interview transcripts and it will, on its own:

1. discover and read each transcript,
2. cluster findings into 3–6 themes,
3. support every theme with **verbatim, attributed** participant quotes,
4. rate each theme High / Medium / Low confidence,
5. flag what a human must verify, and
6. build an Excel workbook (`Research_Report_Tracker.xlsx`) with three linked tabs:
   - **Raw Data** — every evidence quote, one per row
   - **Synthesis** — themes + quotes; each quote links back to its Raw Data row
   - **Report** — a stakeholder summary; each theme links to its evidence

So every finding is one click from the words that prove it. It never presents output as final — it's a first-pass accelerator for a researcher, not a replacement.

## How it's built

A from-scratch agent — a language model in a loop with tools — in ~150 lines of Python, no heavyweight framework, so every decision is visible and auditable:

```
read transcripts  →  cluster into themes  →  attach verbatim quotes  →  save draft
        ↑_______________ the model decides each step in a loop _______________↓
```

Most of the behavior lives in the system prompt (the rules that force verbatim quotes, confidence ratings, and the human-verification section) — not in clever code. Designing those constraints is the actual work.

## Run it yourself

You'll need Python 3.9+ and an [Anthropic API key](https://console.anthropic.com) (a full run costs a few cents).

```bash
# 1. install dependencies (anthropic + openpyxl)
pip3 install -r requirements.txt

# 2. set your API key
export ANTHROPIC_API_KEY="sk-ant-...your-key..."

# 3. run it
python3 research_agent.py
```

It reads every `.txt` file in `transcripts/` and writes `Research_Report_Tracker.xlsx`. To try it on your own study, drop your transcripts into `transcripts/` (one interview per `.txt` file) and run it again — the included samples are just demo data.

**No API key?** Rebuild the sample spreadsheet offline with one command:

```bash
pip3 install openpyxl
python3 generate_sample_report.py
```

## A note on the data

The transcripts in `transcripts/` are **synthetic** — made-up usability interviews for a fictional meal-planning app, written to demonstrate the agent. No real participant data is included.

## What I'd build next

- A **web_search tool** so the agent can pull in competitor reviews alongside the interviews.
- An **evaluation harness** — run the agent on a study I've hand-synthesized and measure quote accuracy and theme recall. That turns "I built an agent" into "I evaluated an agent."

---

**Reecha Bharali** · UX Researcher · [reechabharali.com](https://reechabharali.com)
