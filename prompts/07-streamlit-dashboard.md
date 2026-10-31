# Step 7 – Board-ready Streamlit dashboard (and Step 8 validation)

**Goal:** present the story to the COO and board.

## Prompt

```text
Build a local Streamlit + Plotly dashboard on QUICKBITE_DB, saved in its own project folder.
Title: "QuickBite – Refund Crisis & Delivery Performance Intelligence"
Subtitle: "Understanding the 40% Refund Increase | August–October 2026"

Sections:
1. KPI cards: Oct refunds, refund % of GMV, Oct orders, Whitefield-East share of increase
2. Monthly performance: refunds, GMV, orders, refund rate
3. Refund increase by city, zone and reason
4. Delivery performance: zone selector; weekly late % for the selected zone vs others;
   assignment distance; pickup wait; mark the 8 Sep 2026 rider-assign v2.3 release
5. Weather impact: rainy vs dry late %
6. Cloud Kitchens Hub red-herring check
7. Cortex AI: AI_CLASSIFY distribution and the AI_SUMMARIZE_AGG summary
8. Recommendations, clearly separated from verified findings

Read credentials from my local Snowflake connection config. Never hard-code them.
Add loading spinners and error handling. Run the app and open it in the browser.

Then validate: compare every KPI with the SQL checkpoints, confirm all sections load
without errors, and fix any problems. If late % looks ~10x too high, check whether
the value is already a percentage before multiplying by 100 again.
```

## Checkpoint

- Every section renders with no errors.
- The KPI cards match `docs/expected-results.md`.
- Percentages are computed once on a 0–100 scale.
