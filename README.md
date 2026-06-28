# UX Research Synthesis Agent

An AI agent that turns interview transcripts into a themed insights **draft** — backed by verbatim quotes, rated for confidence, and deliberately designed to hand work back to a human researcher rather than replace one.

Built as a self-directed experiment in applying AI to UX research, with a focus on the part that matters most: making the output trustworthy enough to act on.

---

## See it in 2 minutes (no setup required)

If you'd rather not run anything:

- **[`sample_synthesis_report.md`](sample_synthesis_report.md)** — example output the agent produced from the sample transcripts. This is what it makes.
- **[`CASE_STUDY.md`](CASE_STUDY.md)** — the thinking: the design decisions, the failure modes I tested for, and how I'd evaluate it properly.

That's the fastest way to judge the work. Everything below is for running it yourself.

---

## What it does

Point it at a folder of interview transcripts and it will, on its own:

1. discover and read each transcript,
2. cluster findings into 3–6 themes,
3. support every theme with **verbatim, attributed** participant quotes,
4. rate each theme High / Medium / Low confidence, and
5. write a required **"Needs Human Verification"** section before saving a draft.

It never presents output as final. It's a first-pass accelerator for a researcher, not a replacement.

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
# 1. install the one dependency
pip3 install anthropic

# 2. set your API key
export ANTHROPIC_API_KEY="sk-ant-...your-key..."

# 3. run it
python3 research_agent.py
```

It reads every `.txt` file in `transcripts/` and writes `synthesis_report.md`. Swap in your own transcripts (one interview per `.txt` file) to try it on real material.

## A note on the data

The transcripts in `transcripts/` are **synthetic** — made-up usability interviews for a fictional meal-planning app, written to demonstrate the agent. No real participant data is included.

## What I'd build next

- A **web_search tool** so the agent can pull in competitor reviews alongside the interviews.
- An **evaluation harness** — run the agent on a study I've hand-synthesized and measure quote accuracy and theme recall. That turns "I built an agent" into "I evaluated an agent."

---

**Reecha Bharali** · UX Researcher · [reechabharali.com](https://reechabharali.com)
