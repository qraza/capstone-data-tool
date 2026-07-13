# CLAUDE.md

Guidance for Claude Code when working in this repo. See `README.md` for the full project
description, architecture, and quickstart — this file is process notes, not a duplicate of it.

## Conventions

- dbt SQL: CTE-per-source, `round(..., n)` on aggregates, singular tests named
  `assert_<model>_<check>.sql` in `dbt_project/tests/`, generic `not_null` / `accepted_values` /
  `relationships` tests declared in each layer's `schema.yml`.
- `reporting/` has no Streamlit imports — it's called by both `cli/main.py` and `app/dashboard.py`,
  keep it that way.
- Local dbt runs can use the committed `.ci/profiles.yml` (reads `DBT_DB_PATH` from the
  environment) instead of a personal `~/.dbt/profiles.yml` — see README Quickstart.
- Don't push to origin unless explicitly asked, even after commits are made and verified — work is
  reviewed locally first.

## Roadmap

- [x] Root `README.md`
- [ ] MotherDuck (or other hosted DuckDB) deployment for the dashboard, so it's not local-only
- [ ] Give `mart_hourly_patterns` a month grain (currently aggregates the full dataset regardless
      of the month a board pack is generated for)
- [ ] Cloud ingestion layer — `scripts/load_raw.py` is source-pluggable; pointing DuckDB's
      `read_parquet` at an `s3://` path is the natural next step
