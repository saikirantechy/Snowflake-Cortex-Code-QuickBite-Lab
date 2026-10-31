# Architecture

```text
 Local CSV files ──PUT──▶ @QUICKBITE_DB.RAW.QUICKBITE_STAGE (internal, gzip)
                                   │  INFER_SCHEMA + COPY INTO (MATCH_BY_COLUMN_NAME)
                                   ▼
                        QUICKBITE_DB.RAW  (10 tables)
                                   │  SQL analytics            Cortex AI
                                   │                           AI_CLASSIFY / AI_SUMMARIZE_AGG
                                   ▼                                   ▼
                        ad-hoc analysis in CoCo        QUICKBITE_DB.ANALYTICS
                                   │                    ├─ WFE_CHAT_CLASSIFIED
                                   │                    └─ WFE_CHAT_SUMMARY
                                   ▼
                 Streamlit + Plotly dashboard (local, snowflake-connector-python)
```

## Data model

```text
CITIES_ZONES (ZONE_ID) ─┬─< ORDERS.ZONE_ID
                        ├─< RESTAURANTS.ZONE_ID
                        ├─< RIDERS.HOME_ZONE_ID
                        └─< CUSTOMERS.ZONE_ID

ORDERS (ORDER_ID) ─┬─< ORDER_ITEMS     (1 : many)
                   ├─< REFUNDS         (1 : 0..1)
                   └─< SUPPORT_CHATS   (1 : 0..many)

ORDERS.CUSTOMER_ID → CUSTOMERS
ORDERS.RESTAURANT_ID → RESTAURANTS   (CLUSTER = 'Standard' | 'Cloud Kitchens Hub')
ORDERS.RIDER_ID → RIDERS
WEATHER_HOURLY (CITY, HOUR_TS) ↔ ORDERS (CITY, DATE_TRUNC('hour', PLACED_AT))
APP_RELEASES ↔ ORDERS.ASSIGNMENT_ALGO_VERSION (release timeline)
```

## Tables

| Table | One row is… |
|---|---|
| ORDERS | a delivered order, with timestamps, distances, value and algorithm version |
| ORDER_ITEMS | a line item in an order |
| REFUNDS | a refund on an order, with its reason and amount |
| SUPPORT_CHATS | a customer support message linked to an order |
| CUSTOMERS | a customer, with their city, zone and loyalty tier |
| RESTAURANTS | a restaurant, with its cuisine, zone, cluster and rating |
| RIDERS | a rider, with their home zone and vehicle |
| CITIES_ZONES | a delivery zone within a city |
| WEATHER_HOURLY | the rain and temperature for one city in one hour |
| APP_RELEASES | a product or business release, with its date and notes |

## Dashboard roles

- **`SYSADMIN`** owns all objects and needs `USAGE` on the warehouse.
- **Other roles:** to share the dashboard read-only, grant `USAGE` on the database and schemas plus `SELECT` on their tables.
