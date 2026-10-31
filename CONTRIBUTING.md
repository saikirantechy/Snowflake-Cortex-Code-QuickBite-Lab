# Contributing

Contributions that make this lab easier to learn from are welcome.

## Ideas

- Improve a prompt in `prompts/` or add a variation, such as a Snowsight-only version
- Add dashboard features, such as a deploy-to-Streamlit-in-Snowflake option or new charts
- Report checkpoint differences you observed, with your region and date
- Fix docs, typos or broken links

## How to contribute

1. Fork the repo and create a branch: `git checkout -b feature/my-change`.
2. Keep changes focused. Update `docs/expected-results.md` if your change affects the numbers.
3. **Never commit credentials, account identifiers, `.env` files or the dataset.**
4. Run the dashboard locally to confirm that it still loads without errors.
5. Open a pull request that describes what you changed and why.

## Style

- Prompts: plain English, one step per file, ending with a **Checkpoint** section.
- Python: follow the existing style in `dashboard/app.py`, and compute percentages once in SQL.
