# Synthesis Draft: PlateUp (meal-planning + grocery app)
_Auto-generated draft — requires researcher review. 4 participants (P1–P4)._

> This is example output produced by the agent from the 4 synthetic transcripts in `transcripts/`. It's included so you can see what the agent produces without running it. Quotes are pulled verbatim from those transcripts.

## Themes

### 1. The recipe-swap control is undiscoverable — Confidence: High
Every participant who tried to change a meal struggled to find how. The swap action is hidden behind a long-press with no visible affordance, so users either give up or find it by accident.
- "I spent a while looking for a swap button. I eventually long-pressed the recipe and a menu popped up, but I found that by accident. I'd never have guessed." — P1
- "I could not find where to do it. I looked in the recipe screen, in settings, everywhere. A friend told me you have to long-press. Who would know that?" — P2
- "There was no visible edit or swap control. I finally found it through a long-press, which is not discoverable at all. On a first run I'd assume the feature just didn't exist." — P3

**Recommendation:** Add a visible "Swap recipe" control on each recipe card and test whether first-time users can find it unaided.

### 2. Users don't trust the auto-generated quantities — Confidence: High
Participants trust the recipes but not the math behind grocery amounts, so they manually override quantities — which erodes the time-saving the product is built on.
- "I don't trust the quantities on the grocery list. It told me to buy 800 grams of chicken for two people and that felt like way too much." — P2
- "The portion amounts. For a family of four it sometimes suggests amounts that seem random — too much one week, too little the next. I've learned to sanity-check the meat and produce before I order." — P4

**Recommendation:** Show how each quantity is calculated (per-person × servings) so the number is explainable, and test whether transparency reduces manual overrides.

### 3. Onboarding asks too much before showing value — Confidence: Medium
The upfront questionnaire (diet, allergies, household size, budget, goals) arrives before users see any payoff, prompting drop-off risk and low-quality answers that undermine personalization.
- "It asked me a ton of questions — diet, allergies, how many people, my budget, my goals. I almost quit. It felt like homework before I'd even seen anything." — P1
- "The signup-slash-onboarding was long. So many questions before any payoff. I'd rather see the product first and earn my trust before I hand over all that." — P3

**Recommendation:** Let users skip questions and fill them in later; defer the budget question past first value. Measure completion and drop-off before/after.

### 4. The core time-saving is the reason people stay — Confidence: Medium
The strongest positive: planning effort saved. Several participants framed this as the main reason they'd keep using the app, often in contrast to the rough edges elsewhere.
- "The time-saving is the main reason I'd keep using it honestly. Not the fancy stuff, just — it gave me back an evening." — P1
- "Time, honestly. Before this I'd stand in the kitchen at 6pm with no plan. Now the week is decided and the shopping is mostly done for me. That's worth a lot." — P4

**Recommendation:** Protect and surface time-saved as a core value metric; the trust issues above directly threaten it.

### 5. The subscription tiers are confusing — Confidence: Medium
Paying users can't articulate what they're paying for; the free-vs-Plus comparison doesn't map to what they actually unlocked.
- "I genuinely don't understand what I'm paying for. There's a free tier and a 'Plus' tier and the screen comparing them is confusing." — P2
- "I upgraded but I couldn't tell you exactly what changed. The billing screen and the feature list don't line up in my head." — P4

**Recommendation:** Rewrite the tier-comparison screen around outcomes, and surface "what you unlocked" after upgrade. Test comprehension.

## Single-source signals
- Onboarding length may be degrading data quality, not just causing drop-off: P1 admitted "I rushed through it and probably gave it junk answers just to get past it." If common, personalization is being trained on noise — worth quantifying.

## Needs Human Verification
- **Sample size and recruiting.** Only 4 participants. Patterns are directional, not statistically reliable. Confirm how participants were recruited and whether they represent target segments.
- **Severity vs. frequency.** The agent ranks themes partly by how many people raised them. A serious issue mentioned once (e.g., the data-quality signal above) could be under-weighted. A researcher should re-rank by severity, not just frequency.
- **Quote fidelity.** Spot-check every quote against the source transcript before sharing — verbatim accuracy is the trust foundation of this draft.
- **Theme boundaries.** "Onboarding length" and "trust in personalization" may be distinct problems the agent has grouped together; verify they belong as one theme.
- **No usage data.** These are self-reported attitudes from interviews. Triangulate against analytics (actual drop-off, override rates) before acting.
