# UX Research Synthesis Agent

An AI agent that turns interview transcripts into a themed insights **draft** — backed by verbatim quotes, rated for confidence, and output as an Excel tracker where every finding links back to the exact words that prove it.

Built as a self-directed experiment in applying AI to UX research, with a focus on the part that matters most: making the output trustworthy and traceable enough to act on.

---

## See it in 2 minutes (no setup required)

If you'd rather not run anything:

- **Live web app** — open the demo in your browser, no setup: explore themes and click any quote to see it highlighted in the source transcript. (Add your deployed link here, e.g. `https://uxr-agent.streamlit.app`.)
- **[`Research_Report_Tracker.xlsx`](Research_Report_Tracker.xlsx)** — the agent's output: a 3-tab workbook (Raw Data → Synthesis → Report). Download it and click any quote in the Synthesis tab to jump straight to its source on the Raw Data tab.
- **[`CASE_STUDY.md`](CASE_STUDY.md)** — the thinking: the design decisions, the failure modes I tested for, and how I'd evaluate it properly.

That's the fastest way to judge the work. Everything below is for running it yourself.

## Web app (upload and analyze)

`streamlit_app.py` is a browser app with two tabs:

- **Demo** — pre-computed results, no API key needed (safe to share publicly).
- **Analyze your own files** — upload interview transcripts (`.txt` or `.docx`) or a survey (`.csv`), paste your own Anthropic API key, and the agent runs live: it synthesizes the material, shows themes with click-to-source quotes, and offers the Excel tracker as a download. Each user brings their own key, so sharing the link costs the owner nothing.

```bash
python3 -m streamlit run streamlit_app.py     # run locally
```

**Deploy free (so a hiring manager just clicks a link):**

1. Push the repo to GitHub (include `streamlit_app.py`, `core.py`, `demo_findings.json`, `transcripts/`, and `requirements.txt`).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and click **New app**.
3. Pick this repo, branch `main`, main file `streamlit_app.py`, and **Deploy**.
4. You'll get a public URL like `https://uxr-agent.streamlit.app` — paste it at the top of this README.

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

It reads every `.txt` file in the transcripts folder and writes `Research_Report_Tracker.xlsx`.

**Two datasets are included to try:**

```bash
python3 research_agent.py                        # 1. synthetic meal-app usability interviews (transcripts/)
python3 research_agent.py transcripts_experience  # 2. real interviews with first-time managers (CC BY 4.0)
```

The first is made-up demo data; the second is a real, openly licensed dataset from Figshare (see `transcripts_experience/ATTRIBUTION.md`), so you can see the agent work on genuine third-party material. Both write to the same `Research_Report_Tracker.xlsx`, so run one, open the result, then run the other. To try your own study, drop transcripts into a folder (one interview per `.txt` file) and pass the folder name.

### Survey mode (open-ended survey responses)

The same approach works on small surveys (< ~500 responses) with free-text answers. `survey_agent.py` reads a CSV — one row per respondent, one or more open-text columns — and produces the same linked tracker (`Survey_Report_Tracker.xlsx`).

```bash
python3 survey_agent.py sample_survey.csv
```

It analyzes only the open-text columns and deliberately **ignores rating/multiple-choice columns** — those are quantitative and belong in a spreadsheet, not a language model (asking an LLM to count invites made-up numbers). Knowing which tool fits which data is the point.

**No API key?** Rebuild the sample spreadsheet offline with one command:

```bash
pip3 install openpyxl
python3 generate_sample_report.py
```

## A note on the data

The transcripts in `transcripts/` are **synthetic** — made-up usability interviews for a fictional meal-planning app, written to demonstrate the agent. No real participant data is included.

The transcripts in `transcripts_experience/` are **third-party open data**, reused here as realistic sample material: Raulgaonkar, Haresh (2021), *Experience Survey Transcripts*, figshare, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [doi.org/10.6084/m9.figshare.14616966.v1](https://doi.org/10.6084/m9.figshare.14616966.v1). See [`transcripts_experience/ATTRIBUTION.md`](transcripts_experience/ATTRIBUTION.md) for details. No confidential or personal research data of my own is in this repository.

## What I'd build next

- A **web_search tool** so the agent can pull in competitor reviews alongside the interviews.
- An **evaluation harness** — run the agent on a study I've hand-synthesized and measure quote accuracy and theme recall. That turns "I built an agent" into "I evaluated an agent."

---

**Reecha Bharali** · UX Researcher · [reechabharali.com](https://reechabharali.com)
