"""
streamlit_app.py — Browser app for the UX Research Synthesis Agent.

Two tabs:
  • Demo            — pre-computed results, no key needed (safe to share publicly).
  • Analyze         — upload your own transcripts (.txt) or a survey (.csv), paste
                      your own Anthropic API key, and run the agent live. Each user
                      brings their own key, so it costs you nothing to share.

Run locally:   python3 -m streamlit run streamlit_app.py
Deploy free:   push to GitHub, then share.streamlit.io -> point at this file.
"""

import os
import re
import io
import csv
import glob
import json
import tempfile
import streamlit as st

from core import synthesize_transcripts, synthesize_survey, survey_sources
from research_agent import build_workbook

REPO_URL = "https://github.com/bharaliree-ui/uxr-agent"

st.set_page_config(page_title="UX Research Synthesis Agent",
                   page_icon="🔎", layout="wide")

CONF = {"High": ("#C6EFCE", "#1b5e20"), "Medium": ("#FFEB9C", "#7a5b00"),
        "Low": ("#E6E6E6", "#555555")}


@st.cache_data
def load_demo():
    with open("demo_findings.json", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_demo_sources(folder):
    out = {}
    for p in glob.glob(os.path.join(folder, "*.txt")):
        out[os.path.splitext(os.path.basename(p))[0]] = open(p, encoding="utf-8").read()
    return out


def _unify(s):
    return (s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
             .replace("—", "-").replace("–", "-"))


def source_snippet(participant, quote, sources):
    text = sources.get(participant)
    if not text:
        return None
    utext, uquote = _unify(text), _unify(quote)
    m = re.search(re.sub(r"\\ ", r"\\s+", re.escape(uquote)), utext, re.I)
    if not m:
        return None
    a, b = m.span()
    pre = ("… " if a > 240 else "") + utext[max(0, a - 240):a]
    post = utext[b:b + 240] + (" …" if b + 240 < len(utext) else "")
    body = (pre + "<mark>" + utext[a:b] + "</mark>" + post).replace("\n", " ")
    return f"<div style='font-size:0.9rem;line-height:1.6'>{body}</div>"


def conf_badge(level):
    bg, fg = CONF.get(level, CONF["Low"])
    return (f"<span style='background:{bg};color:{fg};padding:2px 10px;border-radius:999px;"
            f"font-size:0.8rem;font-weight:600'>{level} confidence</span>")


def render_findings(data, sources):
    total_quotes = sum(len(t["quotes"]) for t in data["themes"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Participants", len(data.get("participants", [])))
    c2.metric("Themes", len(data["themes"]))
    c3.metric("Supporting quotes", total_quotes)
    st.info("Draft for researcher review — not a final report. Every claim links to "
            "a participant's exact words.", icon="ℹ️")
    st.divider()
    for i, t in enumerate(data["themes"], start=1):
        with st.container(border=True):
            top = st.columns([0.75, 0.25])
            top[0].markdown(f"### {i}. {t['name']}")
            top[1].markdown(conf_badge(t["confidence"]), unsafe_allow_html=True)
            st.write(t["summary"])
            st.markdown(f"**Recommendation:** {t['recommendation']}")
            with st.expander(f"Evidence — {len(t['quotes'])} supporting quote(s)"):
                for q in t["quotes"]:
                    st.markdown(f"**{q['participant']}** · _{q.get('topic', '')}_")
                    st.markdown(f"> {q['quote']}")
                    with st.expander(f"🔎 View in source ({q['participant']})"):
                        snip = source_snippet(q["participant"], q["quote"], sources)
                        st.markdown(snip, unsafe_allow_html=True) if snip else \
                            st.caption(f"Source: {q['participant']}")
                    st.write("")
    st.divider()
    st.subheader("⚠️ Needs human verification")
    for v in data.get("verification_notes", []):
        st.markdown(f"- {v}")


def read_docx(file):
    from docx import Document
    doc = Document(io.BytesIO(file.getvalue()))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def workbook_bytes(data):
    path = os.path.join(tempfile.gettempdir(), "Research_Report_Tracker.xlsx")
    build_workbook(data, path)
    with open(path, "rb") as f:
        return f.read()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("About")
    st.write("An AI agent that reads interview transcripts or open-ended survey answers "
             "and drafts themed insights — with verbatim quotes, confidence ratings, and "
             "a required human-verification step.")
    st.link_button("View the code on GitHub", REPO_URL, use_container_width=True)

st.title("UX Research Synthesis Agent")

demo_tab, analyze_tab = st.tabs(["🔎 Demo (no key needed)", "⚡ Analyze your own files"])

# ── Demo tab ─────────────────────────────────────────────────────────────────
with demo_tab:
    data = load_demo()
    sources = load_demo_sources(data.get("transcripts_dir", "transcripts"))
    st.caption(f"{data['product']} · {data.get('study', '')}")
    render_findings(data, sources)
    with st.expander("Browse the raw transcripts"):
        if sources:
            for tab, name in zip(st.tabs(sorted(sources)), sorted(sources)):
                tab.text(sources[name])

# ── Analyze tab ──────────────────────────────────────────────────────────────
with analyze_tab:
    st.write("Upload interview transcripts (`.txt` or `.docx`, one interview per file) **or** a "
             "survey (`.csv`, one row per respondent with open-text columns). Then paste your own "
             "Anthropic API key and run.")
    key = st.text_input("Your Anthropic API key", type="password",
                        help="Get one at console.anthropic.com. It's used only for this run and never stored.")
    files = st.file_uploader("Upload .txt / .docx transcripts or a .csv survey",
                             type=["txt", "docx", "csv"], accept_multiple_files=True)

    if st.button("Run analysis", type="primary"):
        if not key:
            st.error("Please paste your Anthropic API key first.")
        elif not files:
            st.error("Please upload at least one file.")
        else:
            csvs = [f for f in files if f.name.lower().endswith(".csv")]
            docs = [f for f in files if f.name.lower().endswith(".docx")]
            txts = [f for f in files if f.name.lower().endswith(".txt")]
            try:
                with st.spinner("The agent is reading and synthesizing… this can take a minute."):
                    if csvs:
                        rows = list(csv.DictReader(io.StringIO(csvs[0].getvalue().decode("utf-8-sig"))))
                        result = synthesize_survey(rows, key)
                        src = survey_sources(rows)
                    else:
                        texts = {f.name: f.getvalue().decode("utf-8", errors="replace") for f in txts}
                        texts.update({f.name: read_docx(f) for f in docs})
                        result = synthesize_transcripts(texts, key)
                        src = texts
                st.session_state["result"] = result
                st.session_state["sources"] = src
                st.success("Done.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    if "result" in st.session_state:
        st.divider()
        render_findings(st.session_state["result"], st.session_state.get("sources", {}))
        st.download_button("⬇️ Download the Excel tracker",
                           data=workbook_bytes(st.session_state["result"]),
                           file_name="Research_Report_Tracker.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
