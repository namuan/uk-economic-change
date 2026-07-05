# Project History

This document preserves the useful implementation history from the original planning, proof-of-concept, and phase-summary documents. The current canonical report is `docs/index.md`; this file is only historical context.

## Original implementation plan

The project was originally designed as a five-phase build:

1. **Data source discovery** — identify working official sources for the priority indicators.
2. **Fetch layer** — build repeatable, caching-aware downloads.
3. **Processing and normalisation** — convert raw files into comparable 2007-vs-latest tables.
4. **Output generation** — create comparison CSVs, charts, and the claims-evidence matrix.
5. **Validation and documentation** — cross-check values, document caveats, and publish a readable evidence pack.

The original ONS API plan had to change because the ONS v0 API (`api.ons.gov.uk`) was retired on 25 November 2024. The project now uses ONS generator CSV endpoints and direct file downloads instead.

## Phase 1 and 2: source discovery and fetch layer

Completed on 4 July 2026.

Key outcomes:

- Confirmed working ONS generator endpoints for GDP per head (`IHXW`) and NDP per head (`MWB6`).
- Confirmed ONS direct file downloads for labour productivity (`PRDY`) and regional productivity (`PRODBYREG`).
- Built `src/fetch_ons.py` with cached downloads and a `fetch_all(force=False)` orchestration function.
- Established `data/raw/` as the raw-source cache.

The original priority set had four populated indicators: GDP per head, NDP per head, output per hour, and regional output per hour. Later work expanded the core set to include real earnings, housing affordability, and NHS waiting lists.

## Phase 3: data processing and normalisation

Completed on 4 July 2026.

Key outcomes:

- Built `src/process_indicators.py`.
- Parsed ONS generator CSVs, direct CSVs, and XLSX workbooks.
- Normalised national and regional indicators into processed comparison tables.
- Added a long-format analytical dataset: `data/processed/long_format.csv`.
- Standardised annual period handling and geography labels.

Important implementation details:

- Generator CSVs include metadata rows and require skipped headers.
- PRDY contains many labour productivity series; the project uses output per hour (`LZVB`).
- Regional productivity uses the output-per-hour table from the PRODBYREG workbook.
- England is excluded from the regional productivity comparison because the framework compares UK nations and English regions.

## Phase 4: charts, claims matrix, and validation

Completed on 4 July 2026, then expanded later.

Initial outcomes:

- Added national indicators comparison chart.
- Added regional productivity change chart.
- Added GDP/NDP timeline chart.
- Populated the claims-evidence matrix using real data.
- Cross-checked growth rates and regional dispersion.

Later additions:

- Added regional ranking chart.
- Expanded the national indicator set to six core indicators.
- Rated all eight claims in the claims-evidence matrix.
- Added QA coverage for all four chart outputs.

## Expanded evidence pack

After the initial proof-of-concept criteria were met, the project was expanded into the current core evidence pack.

Added indicators:

- **Real average weekly earnings** — nominal AWE (`KAB9`) deflated by CPI (`D7BT`) to 2025 prices.
- **Housing affordability** — median house price to median workplace-based earnings, England and Wales.
- **NHS waiting list pressure** — NHS England RTT incomplete pathways, compiled from official NHS England releases.

Added outputs:

- `docs/index.md` as the canonical public report and GitHub Pages landing page.
- `docs/assets/charts/` for Pages-ready chart images.
- `.github/workflows/static.yml` to build and deploy the `docs/` site through GitHub Actions.
- `docs/index-update-prompt.md` as a reusable AI prompt for refreshing the public report from generated outputs.

## Publication and chart improvements

The publication-ready report was then expanded with additional analytical outputs that did not add new indicators but made existing evidence easier to interpret.

Added outputs:

- `outputs/tables/growth_rate_comparison.csv` for pre-2007 versus post-2007 CAGR comparisons.
- Standalone productivity timeline chart.
- Regional productivity small-multiple chart.
- Housing affordability timeline chart.
- NHS waiting-list timeline chart.
- Growth-rate comparison chart.

## Current project state

The project now has:

- 6 core national/current indicators,
- 12 regional productivity measures,
- 8 evidence-rated claims,
- 9 chart outputs,
- a reproducible pipeline (`make fetch`, `make process`, `make build`, `make pages`),
- and a passing QA suite.

For current methodology, source details, caveats, and limitations, use `docs/methodology-note.md`. For future work, use `docs/future-plan.md`.
