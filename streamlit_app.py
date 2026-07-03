"""
streamlit_app.py — A browser demo of the UX Research Synthesis Agent.

The hiring manager just opens a link: no download, no Python, no API key.
It displays a pre-computed synthesis (demo_findings.json) and lets you click any
theme to see its supporting quotes, then click a quote to jump to that line in the
original transcript — the same traceability as the Excel tracker, on the web.

Run locally:   streamlit run streamlit_app.py
Deploy free:   push to GitHub, then share.streamlit.io  ->  point it at this file.
"""

import os
import re
import glob
import json
import streamlit as st

REPO_URL = "https://github.com/bharaliree-ui/uxr-agent"

st.set_page_config(page_title="UX Research Synthesis Agent — Demo",
                   page_icon="🔎", layout="wide")

CONF = {
    "High":   ("#C6EFCE", "#1b5e20"),
    "Medium": ("#FFEB9C", "#7a5b00"),
    "Low":    ("#E6E6E6", "#555555"),
}


@st.cache_data
def load_findings():
    with open("demo_findings.json", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_transcripts(folder):
    out = {}
    for p in glob.glob(os.path.join(folder, "*.txt")):
        stem = os.path.splitext(os.path.basename(p))[0]
        with open(p, encoding="utf-8") as f:
            out[stem] = f.read()
    return out


def _unify(s):
    return (s.replace("’", "'").replace("‘", "'")
             .replace("“", '"').replace("”", '"')
             .replace("—", "-").replace("–", "-"))


def source_snippet(participant, quote, transcripts):
    """Return an HTML snippet of the transcript with the quote highlighted, or None."""
    text = transcripts.get(participant)
    if not text:
        return None
    utext, uquote = _unify(text), _unify(quote)
    pattern = re.sub(r"\\ ", r"\\s+", re.escape(uquote))
    m = re.search(pattern, utext, re.I)
    if not m:
        return None
    a, b = m.span()
    pre = ("… " if a > 240 else "") + utext[max(0, a - 240):a]
    post = utext[b:b + 240] + (" …" if b + 240 < len(utext) else "")
    body = (pre + "<mark>" + utext[a:b] + "</mark>" + post).replace("\n", " ")
    return f"<div style='font-size:0.9rem;line-height:1.6;color:inherit'>{body}</div>"


def conf_badge(level):
    bg, fg = CONF.get(level, CONF["Low"])
    return (f"<span style='background:{bg};color:{fg};padding:2px 10px;"
            f"border-radius:999px;font-size:0.8rem;font-weight:600'>{level} confidence</span>")


data = load_findings()
transcripts = load_transcripts(data.get("transcripts_dir", "transcripts"))

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("About this demo")
    st.write(
        "An AI agent reads interview transcripts and drafts themed insights — with "
        "verbatim quotes, confidence ratings, and a required human-verification step."
    )
    st.write("**How to use it:** expand a theme to see its evidence, then expand a "
             "quote to jump to that line in the original transcript.")
    st.divider()
    st.caption("This is a live demo on synthetic data — no download or setup needed.")
    st.link_button("View the code on GitHub", REPO_URL, use_container_width=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("UX Research Synthesis Agent")
st.caption(f"{data['product']} · {data.get('study', '')}")

total_quotes = sum(len(t["quotes"]) for t in data["themes"])
c1, c2, c3 = st.columns(3)
c1.metric("Participants", len(data["participants"]))
c2.metric("Themes", len(data["themes"]))
c3.metric("Supporting quotes", total_quotes)

st.info("Draft for researcher review — not a final, decision-ready report. "
        "Every claim links back to a participant's exact words.", icon="ℹ️")

st.divider()

# ── Themes ───────────────────────────────────────────────────────────────────
st.subheader("Themes")
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
                snippet = source_snippet(q["participant"], q["quote"], transcripts)
                with st.expander(f"🔎 View in source transcript ({q['participant']})"):
                    if snippet:
                        st.markdown(snippet, unsafe_allow_html=True)
                    else:
                        st.caption(f"Source: {q['participant']} (full transcript below).")
                st.write("")

# ── Verification ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("⚠️ Needs human verification")
st.caption("The agent flags its own limits — a researcher checks these before sharing.")
for v in data["verification_notes"]:
    st.markdown(f"- {v}")

# ── Raw transcripts ──────────────────────────────────────────────────────────
st.divider()
with st.expander("Browse the raw transcripts"):
    if transcripts:
        tabs = st.tabs(sorted(transcripts.keys()))
        for tab, name in zip(tabs, sorted(transcripts.keys())):
            tab.text(transcripts[name])
    else:
        st.caption("No transcript files found next to the app.")
