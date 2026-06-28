# Pet Project: A UX Research Synthesis Agent

*A self-directed experiment in building — and stress-testing — an AI agent for my own craft.*

This is the write-up I talk through in interviews when asked "what AI experiments or pet projects have you done?" The point isn't that I can call an API. It's that I treated the agent as a **design and research problem**, not just a coding one.

---

## The problem I chose, and why

Synthesizing interview transcripts is the most time-consuming, least-loved part of UX research — and the part people most want to throw AI at. It's also where naive AI use is most dangerous: a model will happily invent a quote, merge two distinct problems into one tidy theme, and present a guess as a finding. If a team ships decisions on a hallucinated insight, that's worse than no synthesis at all.

So I picked synthesis on purpose. It let me demonstrate the thing I actually care about: **not whether AI can do research, but how you design an agent so its output is trustworthy enough to act on.**

## What I built

A from-scratch agent (a language model in a loop with tools — no heavyweight framework, so I understand every line). Given a folder of interview transcripts, it:

1. discovers and reads each transcript on its own,
2. clusters findings into themes,
3. backs every theme with verbatim, attributed participant quotes,
4. rates its confidence per theme, and
5. writes a mandatory "Needs Human Verification" section before saving a **draft** — never a finished deliverable.

The tech is ~150 lines of Python. The interesting part is everything I made it *not* do.

## The design decisions (this is the real content)

Every one of these is a response to a specific, known AI failure mode:

- **Verbatim quotes, attributed by participant ID.** The model must quote word-for-word and tag each quote (P1, P2…). If it can't find a real supporting quote, it isn't allowed to claim the theme. This is my main defense against hallucinated evidence — and it makes every claim auditable against the source.
- **Two-participant rule.** A "theme" needs support from at least two different participants; anything else is filed under "single-source signals." This stops the agent from inflating one loud comment into a pattern.
- **Explicit confidence ratings.** Each theme is High/Med/Low confidence. I'd rather the agent say "Low confidence" than smooth over uncertainty — calibrated doubt is more useful to a team than false tidiness.
- **A required human-verification section.** The agent cannot finish without listing its own inferences, thin spots, and sample caveats. I designed it to hand work *back* to the researcher, not to replace them. Deciding where the human stays in the loop is the core call here.
- **It produces a draft, never a verdict.** Framing matters. Labeling the output a "draft requiring review" changes how a reader treats it. That's a UX decision encoded into the agent's instructions.

Most of the agent's behavior lives in the **system prompt**, not the code — which itself was a lesson: shaping an agent is mostly writing clear, constraint-rich instructions for a non-human reader. That's microcopy and policy design, which is squarely UX work.

## Where it fails (I tested for this, and I lead with it)

I deliberately tried to break it, because knowing the failure modes is the job:

- **It over-merges.** Distinct issues with related vibes (e.g., "onboarding is long" vs. "I don't trust the personalization it produced") sometimes collapse into one theme. A human catches the distinction; the agent smooths it.
- **It under-weights rare-but-severe issues.** A frequency-based clustering bias means a serious problem mentioned by one participant can get buried under a common-but-minor one. My two-participant rule helps, but it's also part of the problem — severity and frequency aren't the same thing, and the agent leans on frequency.
- **Quote fidelity needs guarding.** Without the explicit verbatim rule, it paraphrases inside quotation marks. The rule mostly fixes it, but I'd still spot-check every quote against the transcript before trusting it.
- **It's confident in its own structure.** It rates theme confidence, but not its decision to split or merge themes in the first place — a blind spot I'd address next.

The honest takeaway I share: this agent makes a researcher **faster**, not optional. It's a strong first-pass that turns hours of tagging into minutes of *reviewing* — but the reviewing is non-negotiable.

## How I'd evaluate it properly (my next step)

Talking points are cheap; here's the rigor. I'd run the agent on a study I'd already synthesized by hand and measure:

- **Quote accuracy** — what % of quotes are truly verbatim and correctly attributed (target: 100%; anything less is a trust failure).
- **Theme precision/recall** — did it find the themes I found (recall), and did it invent ones that aren't supported (precision)?
- **Severity catch rate** — did it surface the high-severity, low-frequency issues, or bury them?

That comparison turns "I built an agent" into "I evaluated an agent," which is the more senior signal — and it's exactly the research skill teams building AI products are short on.

## What I learned about agents (the transferable insight)

Agents fail less on raw model quality and more on **design**: how they handle uncertainty, how they recover from a bad input, where a human stays in the loop, and how you'd even know if they're working. Those are research and design questions. The Python got me in the door; my edge is knowing how to make an agent behave responsibly and how to measure whether it does.

---

## Interview talking points (your cheat sheet)

Use these as scaffolding — say them in your own words.

**The 30-second version:**
> "I built an AI agent that synthesizes interview transcripts into themed insights. But the interesting part was designing it *not* to be trusted blindly — it has to quote participants verbatim, rate its own confidence, and produce a 'needs human verification' section every time. I was more interested in where AI breaks in research than in what it can automate."

**If they ask what was hard:**
> "Getting it to be honest about uncertainty. The default behavior is confident, tidy output — which is exactly what's dangerous in research. Most of my work was constraint design: verbatim-quote rules, a two-participant threshold for themes, and forcing it to hand findings back to a human."

**If they ask about limitations:**
> "It over-merges distinct issues and under-weights rare-but-severe ones, because it leans on frequency. So it's a first-pass accelerator, not a replacement — it turns hours of tagging into minutes of reviewing. I'd validate it by running it against a study I'd hand-synthesized and measuring quote accuracy and theme recall."

**If they ask why it matters for the role:**
> "Teams building AI products keep hiring engineers and forgetting that the hard problems are about trust, uncertainty, and human-in-the-loop design. That's research. This project is me showing I can sit in the middle — build the thing *and* judge whether it's any good."

**The one-liner to land:**
> "Agents fail less on model quality and more on design. That's a UX problem, and it's why I'm a fit."
