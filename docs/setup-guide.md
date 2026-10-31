# Setup guide

## 1. Snowflake account

1. Create a Snowflake trial account. Choose a region where Cortex AI functions are available; this lab was tested in AWS ap-northeast-1.
2. Check that you can use `SYSADMIN` and that an X-Small warehouse (e.g. `COMPUTE_WH`) exists.
3. For Cortex AI, the role needs the `SNOWFLAKE.CORTEX_USER` database role. Trial accounts grant it to `PUBLIC` by default. To check:

```sql
SELECT EXPLAIN_PRIVILEGES(statement => $$SELECT AI_CLASSIFY('x',['a','b'])$$, missing_only => true);
```

## 2. Cortex Code Desktop

1. Install Snowflake Cortex Code (CoCo) Desktop.
2. Add a connection to your account. CoCo saves it in `~/.snowflake/config.toml`.
3. Ask CoCo: *"show me my connection details"* to confirm it works.

## 3. Dataset

1. Download `quickbite_data.zip` from the official lab materials. It isn't redistributed here.
2. Extract it. You should have 10 CSV files:
   `app_releases, cities_zones, customers, orders, order_items, refunds, restaurants, riders, support_chats, weather_hourly`
3. Ignore the `__MACOSX` folder if there is one.

## 4. Run the lab

Follow `prompts/00` → `07`, or paste `prompts/master-prompt.md`. Approve CoCo's requests to create objects as they come up.

## 5. Clean up (optional)

```sql
DROP DATABASE IF EXISTS QUICKBITE_DB;
```
