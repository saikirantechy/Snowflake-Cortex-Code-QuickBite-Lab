# Step 1 – Database creation and CSV loading

**Goal:** load all 10 CSV files into `QUICKBITE_DB.RAW`.

## Prompt

```text
Using SYSADMIN, create database QUICKBITE_DB with schemas RAW and ANALYTICS.
Ask for my approval before creating anything.

My extracted CSV files are in: <PATH_TO>/quickbite_data
(Ignore any __MACOSX folder.)

Load each of the 10 CSV files into its own table in QUICKBITE_DB.RAW:
- create an internal stage and a named CSV file format (PARSE_HEADER = TRUE)
- PUT the files to the stage (do not modify the originals)
- create tables with INFER_SCHEMA so data types come from the data
- load with COPY INTO ... MATCH_BY_COLUMN_NAME, without FORCE, so files aren't loaded twice

Then show every table with its columns, data types, row count and any load errors
(use COPY_HISTORY).
```

## Checkpoint

| Table | Rows |
|---|---|
| ORDERS | 247,741 |
| ORDER_ITEMS | 521,607 |
| REFUNDS | 15,057 |
| SUPPORT_CHATS | 6,728 |
| WEATHER_HOURLY | 43,776 |
| CUSTOMERS | 30,000 |
| RIDERS | 2,828 |
| RESTAURANTS | 1,386 |
| CITIES_ZONES | 40 |
| APP_RELEASES | 15 |

Tip: check that decimal columns such as `RIDER_ASSIGN_DISTANCE_KM` and `RAIN_MM` kept their scale.
