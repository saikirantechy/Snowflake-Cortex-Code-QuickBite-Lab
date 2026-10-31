# QuickBite – Complete end-to-end master prompt

Paste everything below the line into Snowflake Cortex Code (CoCo) Desktop. It runs the whole lab, Step 0 to Step 8. CoCo will stop and ask for approval before it creates or changes resources.

> Before running: connect CoCo to your Snowflake account, extract `quickbite_data.zip`, and replace `<PATH_TO>/quickbite_data` with your folder.

---

Act as a senior Snowflake Data Engineer, Data Analyst, AI Engineer and Streamlit Developer.
Complete the QuickBite hands-on lab **"Why Is My Biryani Always Late?"**

## Business scenario

QuickBite is a fictional food-delivery company operating in six Indian cities. The COO says:
"Refunds are up 40% in two months and ratings are tanking. Board call at 5 PM. What's going on, and what do we fix?"
I have 10 CSV files of synthetic data in `<PATH_TO>/quickbite_data`.

Rules:
- Generate and execute all SQL through Cortex Code. Don't ask me to write SQL.
- Explain important operations in simple language.
- Ask for my approval before creating, modifying or deleting resources.
- Never fabricate results. Validate every analysis against actual Snowflake data.
- Work through Steps 0–8 in order. Verify each step before moving on.

### Step 0 – Environment and connection
Report the account, user, role, warehouse (with size and state), database and schema, and whether the role can create databases, schemas, tables and stages. Prefer SYSADMIN and an X-Small warehouse. Explain anything missing. Do not create a database until this is verified.

### Step 1 – Database and CSV loading
Create `QUICKBITE_DB` with schemas `RAW` and `ANALYTICS` (as SYSADMIN). Load all 10 CSVs into separate tables in `RAW`. Infer the schema from the headers, keep proper data types, handle nulls, use a stage and COPY INTO, avoid duplicate loads, and leave the original files untouched. Then show each table's columns, data types, row count and any load errors.
Checkpoints: ORDERS 247,741 · ORDER_ITEMS 521,607 · REFUNDS 15,057 · SUPPORT_CHATS 6,728 · WEATHER_HOURLY 43,776 · CUSTOMERS 30,000.

### Step 2 – Exploration and relationships
For each table, explain what it represents, what one row is, its keys, important columns and data quality issues. Verify these relationships: ORDERS→REFUNDS, ORDER_ITEMS and SUPPORT_CHATS (ORDER_ID); WEATHER_HOURLY→ORDERS (CITY + hour); APP_RELEASES as the release history. Add any other supported relationships, and draw a simple relationship diagram.

### Step 3 – Monthly refund analysis (2026)
Calculate monthly orders, GMV, refunds, refund % of GMV, MoM refund growth and order growth, and chart them.
Checkpoints: Aug refunds ≈ ₹5.08 L · Oct ≈ ₹7.13 L (+≈40%) · refund rate 3.71% → 4.76% · orders +≈9%.

### Step 4 – Affected city and zone
Break down the Aug→Oct refund increase by city, zone and reason, with each zone's share of the increase.
Checkpoints: Bengaluru / Whitefield-East · Late delivery and Cold food · ≈₹1.6 L of ₹2.05 L (≈78%).
Red herring: did Cloud Kitchens Hub (launched 1 Sep 2026) cause it? Compare refund counts, amounts, missing-item refunds and contribution. Expected: extra missing-item refunds, but only a small contribution of a few thousand ₹.

### Step 5 – Root cause and weather
Inspect APP_RELEASES. Expected: rider-assign v2.3 on 8 Sep 2026, "Expanded assignment radius to 10 km".
Compare Whitefield-East before and after the release, and against other zones, on: average assignment distance, pickup waiting time, and late % (late = more than 45 min from placed to delivered).
Checkpoints: distance ≈2.1 → 6.0 km · late ≈6% → 20–28% · other zones ≈6%.
Weather: join WEATHER_HOURLY on city and hour, and compare rainy and dry hours for Whitefield-East after 8 Sep. Checkpoints: ≈56% late in rain vs ≈14% in dry hours. Don't claim causation beyond what the data supports.

### Step 6 – Complaint analysis with Cortex AI
Take Whitefield-East support chats from 8 Sep 2026 onward. Classify them with AI_CLASSIFY into: Rider assigned too far away · Food arrived cold · General late delivery · Missing or wrong item · Food quality. Then summarise them with AI_SUMMARIZE_AGG. Show the total, the count and % per category, the top complaint, examples and recurring problems.
Checkpoints: ≈446 chats · top theme "Rider assigned too far away" ≈237. The summary should mention far-away riders, long waits, cold food and rain. Report any unsupported function or missing permission clearly.

### Step 7 – Board-ready Streamlit dashboard
Title: **QuickBite – Refund Crisis & Delivery Performance Intelligence**
Subtitle: Understanding the 40% Refund Increase | August–October 2026
Sections:
1. KPI cards: Oct refunds, refund % of GMV, Oct orders, Whitefield-East share of the increase
2. Monthly performance
3. Refunds by city, zone and reason
4. Delivery performance with a zone selector: weekly late % (selected zone vs others), assignment distance and pickup wait, with the 8 Sep release marked
5. Weather impact
6. Cloud Kitchens investigation
7. Cortex AI complaint intelligence
8. Recommendations, kept separate from verified findings

Use Python, Streamlit, Plotly and a direct Snowflake connection. Add filters, loading indicators and error handling, and never expose credentials. Save it in its own folder, run it locally and open it in my browser.

### Step 8 – Validation and final report
Validate every KPI, checkpoint, chart and section, and confirm the app runs without errors. Fix anything incorrect.
If late % looks ≈10× too high, check whether the value is already a percentage before multiplying by 100 again.
Finally, report on: the database overview, the 10 tables, exploration, refund analysis, root cause, weather, the Cortex AI results, the dashboard, recommendations and completion status.
