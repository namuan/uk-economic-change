You are working in the `uk-economic-change` repository. Update the public GitHub Pages evidence report at `docs/index.md` from the latest project data and generated outputs.

Important context:
- `docs/index.md` is the canonical public report and GitHub Pages landing page.
- Do not recreate `docs/full-report.md`; that file was intentionally removed to avoid duplicate report copies.
- Preserve the current writing style in `docs/index.md`: plain, direct, public-facing prose; sentence case headings; minimal bolding; no unnecessary academic phrasing.
- Keep the Jekyll front matter at the top
- Chart links in `docs/index.md` must point to `assets/charts/...`, not `../outputs/charts/...`.

Process:

1. Refresh the generated evidence base.
   - Run `make fetch` unless the user explicitly asks for a forced refresh.
   - If the user asks for a full source refresh, run `make fetch-force` first.
   - Run `make process`.
   - Run `make build`.
   - Run `make pages` to copy chart assets into `docs/assets/charts/`.

2. Read the current generated data outputs.
   Use these as the source of truth for numbers:
   - `outputs/tables/national_comparison.csv`
   - `outputs/tables/regional_productivity_comparison.csv`
   - `outputs/tables/claims_evidence_matrix.csv`
   - `data/indicator_register.csv`
   - `data/claims_register.csv`
   - `data/processed/long_format.csv` when time-series context is needed

3. Confirm chart assets exist for Pages.
   Check that these files exist and are non-empty:
   - `docs/assets/charts/gdp_per_head_timeline.png`
   - `docs/assets/charts/national_indicators_change.png`
   - `docs/assets/charts/regional_productivity_change.png`
   - `docs/assets/charts/regional_ranking.png`

4. Update `docs/index.md` only where the data or generated outputs require changes.
   Keep the current structure unless there is a good reason to change it:
   - Executive summary
   - National output: GDP per head
   - National income: NDP per head
   - Productivity: output per hour worked
   - Real earnings
   - Housing affordability
   - NHS waiting times
   - Regional productivity
   - Claims-evidence matrix
   - What is still left
   - Methodology
   - Appendix

5. Update all figures and narrative claims from generated data.
   Check and update:
   - baseline values,
   - latest values,
   - latest years/months,
   - absolute changes,
   - percentage changes,
   - evidence ratings,
   - source/caveat wording,
   - count of indicators, claims, tables, charts, and QA checks if mentioned.

6. Preserve caveats.
   Keep these caveats explicit unless the underlying data changes:
   - Housing affordability covers England and Wales only.
   - NHS waiting-list data covers England only.
   - NHS RTT baseline is August 2007, the first month of RTT data collection.
   - Regional productivity latest year lags national indicators.
   - The framework measures what happened, not policy attribution.

7. Preserve chart links.
   In `docs/index.md`, images must use:
   - `assets/charts/gdp_per_head_timeline.png`
   - `assets/charts/national_indicators_change.png`
   - `assets/charts/regional_productivity_change.png`
   - `assets/charts/regional_ranking.png`

8. Validate the report.
   - Run `make test`.
   - Search for stale references to `docs/full-report.md` or `../outputs/charts/` in `docs/index.md`.
   - Search current-facing docs for stale phrases like “proof of concept” if you changed status wording.

9. Report back with a concise summary.
   Include:
   - files changed,
   - whether `make pages` passed,
   - whether `make test` passed,
   - any data values that changed materially,
   - any caveats or unresolved issues.

Rules:
- Do not invent data. Use only project outputs or official source files already fetched by the pipeline.
- Do not manually edit generated output tables unless explicitly asked; regenerate them through the pipeline.
- Do not remove caveats to make the story cleaner.
- Do not introduce a second canonical report file.
- Keep `docs/index.md` readable as a public report, not a technical changelog.

Quick command sequence

For a normal refresh:

```bash
make fetch
make process
make build
make pages
make test
```

For a full source refresh:

```bash
make fetch-force
make process
make build
make pages
make test
```
