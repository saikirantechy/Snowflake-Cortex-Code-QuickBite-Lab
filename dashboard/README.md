# QuickBite dashboard

A local Streamlit + Plotly app that reads from `QUICKBITE_DB`.

## Prerequisites

- Python 3.11 or 3.12. The Snowflake connector may not yet support newer versions.
- Steps 1 and 6 of the lab completed, so these objects exist:
  - `QUICKBITE_DB.RAW.*` (the 10 tables)
  - `QUICKBITE_DB.ANALYTICS.WFE_CHAT_CLASSIFIED`
  - `QUICKBITE_DB.ANALYTICS.WFE_CHAT_SUMMARY`
- A named connection in `~/.snowflake/config.toml` (or `connections.toml`). For example:

```toml
[connections.my_conn]
account = "<ORG>-<ACCOUNT>"
user = "<USER>"
authenticator = "externalbrowser"   # or snowflake_jwt / password, which you must keep out of git
```

## Run

```bash
cd dashboard
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export SNOWFLAKE_DEFAULT_CONNECTION_NAME=my_conn     # PowerShell: $env:SNOWFLAKE_DEFAULT_CONNECTION_NAME="my_conn"
streamlit run app.py
```

Optional environment variables:

| Variable | Default |
|---|---|
| `QUICKBITE_ROLE` | `SYSADMIN` |
| `QUICKBITE_WAREHOUSE` | `COMPUTE_WH` |

## Notes

- **Credentials:** they never live in the code. `snowflake.connector.connect(connection_name=...)` resolves them from your local config.
- **Percentages:** they are computed once, in SQL, on a 0–100 scale. Don't multiply them by 100 again in Python.
- **Late delivery:** defined as `DATEDIFF('minute', PLACED_AT, DELIVERED_AT) > 45`.
