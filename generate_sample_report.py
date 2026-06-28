"""
generate_sample_report.py — Rebuild the sample Excel tracker. No API key needed.

This regenerates Research_Report_Tracker.xlsx from baked-in sample findings, so the
spreadsheet is reproducible straight from the repo without running the full agent.

    python3 generate_sample_report.py

(The live agent, research_agent.py, produces the same workbook from real transcripts
using the Anthropic API. This script is just the offline, key-free way to recreate the
sample so anyone can see the output.)
"""

from research_agent import build_workbook, OUTPUT_FILE

SAMPLE = {
    "product": "PlateUp (meal-planning + grocery app)",
    "participants": ["P1", "P2", "P3", "P4"],
    "themes": [
        {"name": "1. Recipe-swap control is undiscoverable", "confidence": "High",
         "summary": "Every participant who tried to change a meal struggled to find how. The swap action is hidden behind a long-press with no visible affordance, so users give up or find it by accident.",
         "recommendation": "Add a visible 'Swap recipe' control on each recipe card; test first-time findability unaided.",
         "quotes": [
             {"participant": "P1", "topic": "Swap feature", "quote": "I spent a while looking for a swap button. I eventually long-pressed the recipe and a menu popped up, but I found that by accident. I'd never have guessed."},
             {"participant": "P2", "topic": "Swap feature", "quote": "I could not find where to do it. I looked in the recipe screen, in settings, everywhere. A friend told me you have to long-press. Who would know that?"},
             {"participant": "P3", "topic": "Swap feature", "quote": "There was no visible edit or swap control. I finally found it through a long-press, which is not discoverable at all. On a first run I'd assume the feature just didn't exist."}]},
        {"name": "2. Users don't trust auto-generated quantities", "confidence": "High",
         "summary": "Participants trust the recipes but not the grocery math, so they manually override quantities, eroding the time-saving the product is built on.",
         "recommendation": "Show how each quantity is calculated (per-person x servings); test whether transparency reduces overrides.",
         "quotes": [
             {"participant": "P2", "topic": "Quantities", "quote": "I don't trust the quantities on the grocery list. It told me to buy 800 grams of chicken for two people and that felt like way too much."},
             {"participant": "P4", "topic": "Quantities", "quote": "The portion amounts. For a family of four it sometimes suggests amounts that seem random — too much one week, too little the next. I've learned to sanity-check the meat and produce before I order."},
             {"participant": "P4", "topic": "Quantities", "quote": "I trust the recipes, but not the math."}]},
        {"name": "3. Onboarding asks too much before showing value", "confidence": "Medium",
         "summary": "The upfront questionnaire arrives before any payoff, prompting drop-off risk and low-quality answers that undermine personalization.",
         "recommendation": "Let users skip and fill in later; defer the budget question past first value. Measure drop-off.",
         "quotes": [
             {"participant": "P1", "topic": "Onboarding", "quote": "It asked me a ton of questions — diet, allergies, how many people, my budget, my goals. I almost quit. It felt like homework before I'd even seen anything."},
             {"participant": "P3", "topic": "Onboarding", "quote": "The signup-slash-onboarding was long. So many questions before any payoff. I'd rather see the product first and earn my trust before I hand over all that."}]},
        {"name": "4. Time-saving is the reason people stay", "confidence": "Medium",
         "summary": "The strongest positive: planning effort saved, framed by several participants as the main reason to keep using the app.",
         "recommendation": "Protect and surface time-saved as a core value metric; the trust issues above threaten it.",
         "quotes": [
             {"participant": "P1", "topic": "Value", "quote": "The time-saving is the main reason I'd keep using it honestly. Not the fancy stuff, just — it gave me back an evening."},
             {"participant": "P4", "topic": "Value", "quote": "Time, honestly. Before this I'd stand in the kitchen at 6pm with no plan. Now the week is decided and the shopping is mostly done for me. That's worth a lot."}]},
        {"name": "5. Subscription tiers are confusing", "confidence": "Medium",
         "summary": "Paying users can't articulate what they pay for; the free-vs-Plus comparison doesn't map to what they unlocked.",
         "recommendation": "Rewrite the tier-comparison screen around outcomes; surface 'what you unlocked' after upgrade.",
         "quotes": [
             {"participant": "P2", "topic": "Subscription", "quote": "I genuinely don't understand what I'm paying for. There's a free tier and a 'Plus' tier and the screen comparing them is confusing."},
             {"participant": "P4", "topic": "Subscription", "quote": "I upgraded but I couldn't tell you exactly what changed. The billing screen and the feature list don't line up in my head."}]},
    ],
    "verification_notes": [
        "Sample size: only 4 participants. Patterns are directional, not statistically reliable. Confirm recruiting and segment representation.",
        "Severity vs. frequency: themes are ranked partly by how many people raised them; a rare-but-severe issue could be under-weighted. Re-rank by severity.",
        "Quote fidelity: spot-check every quote against the source transcript before sharing.",
        "Theme boundaries: 'onboarding length' and 'trust in personalization' may be distinct problems grouped together; verify.",
        "No usage data: these are self-reported attitudes. Triangulate against analytics (drop-off, override rates) before acting.",
    ],
}

if __name__ == "__main__":
    build_workbook(SAMPLE, OUTPUT_FILE)
    print(f"Built {OUTPUT_FILE} from sample data — open it to see the linked tabs.")
