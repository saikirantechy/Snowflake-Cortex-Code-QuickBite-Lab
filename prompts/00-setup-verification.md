# Step 0 – Environment and connection verification

**Goal:** confirm that CoCo can reach Snowflake with a role and warehouse able to create objects.

## Prompt

```text
Inspect my current Snowflake connection and report:
- account, user, current role, available roles
- current warehouse, its size and state (use an X-Small warehouse if available)
- current database and schema
- whether my role (prefer SYSADMIN) can create databases, schemas, tables and stages

If anything is missing (e.g. SYSADMIN has no USAGE on the warehouse), explain what
needs to be granted and ask for my approval before changing anything.
Do not create any objects yet.
```

## Checkpoint

- A warehouse is running (X-Small is enough).
- SYSADMIN has `CREATE DATABASE` and `USAGE` on the warehouse.
