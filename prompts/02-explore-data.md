# Step 2 – Data exploration and relationships

**Goal:** understand the data model before analysing it.

## Prompt

```text
Analyse every table in QUICKBITE_DB.RAW. For each one explain what it represents,
what one row is, its key columns and likely primary/foreign keys.

Verify these relationships with SQL (count orphans and duplicates):
- ORDERS -> REFUNDS, ORDER_ITEMS, SUPPORT_CHATS on ORDER_ID
- ORDERS -> CUSTOMERS, RESTAURANTS, RIDERS, CITIES_ZONES
- WEATHER_HOURLY -> ORDERS on CITY + DATE_TRUNC('hour', PLACED_AT)
- APP_RELEASES as a release timeline (compare with ORDERS.ASSIGNMENT_ALGO_VERSION)

List data quality issues you find (nulls, odd values, date ranges, duplicate keys)
and draw a simple text diagram of the relationships.
```

## Checkpoint

- No orphan refunds, order items or chats.
- No order has more than one refund.
- Orders run from 2026-01-01 to 2026-10-31.
- `ASSIGNMENT_ALGO_VERSION` has two values: v2.2 and v2.3.
