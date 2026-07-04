# Future Plan: From POC to Finished Project

**Project:** UK Economic Change Comparison Framework  
**Working title:** Britain Since 2007: Evidence Framework  
**Status:** Roadmap from proof of concept to finished project  
**Baseline year:** 2007  
**Primary source policy:** ONS first

## 1. Purpose

This document sets out what is needed to move the current proof of concept into a finished, reusable evidence product.

The POC is intended to prove the core workflow:

1. define indicators,
2. fetch or import official data,
3. compare 2007 with the latest available period,
4. calculate change,
5. produce national and regional outputs,
6. assess claims against evidence.

The finished project should become a robust analytical package that can support tenders, reports, policy papers, public briefings, dashboards, and further research.

## 2. Target Finished Product

The finished project should deliver a repeatable evidence framework for assessing how Britain has changed since 2007.

The final product should include:

- a validated indicator register,
- automated or semi-automated data ingestion,
- cleaned national and regional datasets,
- reproducible calculations,
- national and regional comparison tables,
- chart outputs,
- a claims-evidence matrix,
- a methodology note,
- a limitations and caveats appendix,
- source documentation,
- and a final narrative report or tender-ready evidence pack.

## 3. Workstream 1: Data Source Validation ✅

### Objective

Confirm which datasets are suitable, comparable, and defensible for each indicator.

### Completed

- Reviewed every indicator in `data/indicator_register.csv`.
- Confirmed the correct ONS dataset, series code, edition, geography, and unit for all 5 populated indicators.
- Verified each series has a valid 2007 observation and latest comparable observation.
- Recorded release frequency and update schedule.
- Documented known caveats for each indicator.
- Remaining: housing affordability (TBD, Workstream 4).

### Output

A validated indicator register with fields for:

- `indicator_id`, `indicator_name`, `domain`, `source_owner`,
- `source_url`, `dataset_id`, `series_code`,
- `geography_level`, `unit`,
- `baseline_year_available`, `latest_year_available`,
- `update_frequency`, `comparability_status`,
- `known_caveats`, `priority`.

## 4. Workstream 2: Data Ingestion ✅

### Objective

Replace placeholder tables with real data pulls from ONS and other approved official sources.

### Completed

- ONS time-series fetching implemented for 5 national indicators.
- Dataset CSV/XLSX fetching for labour productivity, regional productivity, housing affordability.
- Caching for all raw downloads in `data/raw/`.
- Error handling for unavailable sources and changed endpoints.
- All data ingestion runs through `make fetch` and `uv run python src/fetch_ons.py`.

### Output

A reproducible ingestion layer: `data/raw/` contains 7 source files, all fetchable or verified via Makefile.

## 5. Workstream 3: Data Cleaning and Normalisation ✅

### Objective

Convert all raw source data into a shared long-format analytical model.

### Completed

- Standardised date, year, quarter, and annual fields using `^\d{4}$` regex.
- Standardised geography names and ONS geography codes.
- Standardised units and measurement types.
- Created a single canonical processed table: `data/processed/long_format.csv` (362 rows, 13 columns).
- All data quality flags set to OK.

### Target table shape (implemented)

| Column | Description |
|---|---|
| `indicator_id` | Stable project indicator ID |
| `indicator_name` | Human-readable indicator name |
| `domain` | Economy, productivity, wages, housing, public services, etc. |
| `geography_code` | Standard ONS geography code |
| `geography_name` | UK, East Midlands, Scotland, etc. |
| `geography_type` | National, region |
| `period_type` | Annual |
| `period` | Source period label (e.g. "2007") |
| `year` | Calendar year (integer) |
| `value` | Numeric value |
| `unit` | Unit of measurement |
| `source_url` | Source link |
| `quality_flag` | OK, partial, estimated, missing, methodology break |
| `notes` | (available in indicator register caveats)

## 6. Workstream 4: Indicator Expansion

### Objective

Expand beyond the POC indicator set while keeping the project manageable and evidence-led.

### Recommended expansion order

1. National output and income indicators.
2. Productivity indicators.
3. Earnings, wages, and household income.
4. Housing affordability and housing supply.
5. Public-service pressure indicators.
6. Local government finance indicators.
7. Transport and infrastructure indicators.
8. Optional international peer comparison.

### Acceptance criteria

An indicator should only be promoted into the core set if:

- it has a clear definition,
- it has a valid 2007 or near-2007 baseline,
- it has a latest comparable figure,
- it can be explained to a non-specialist audience,
- and the caveats are manageable.

## 7. Workstream 5: Regional and Geographic Design

### Objective

Define the project geography consistently before expanding the analysis.

### Decisions required

- Whether the first regional view should use UK nations and English regions.
- Whether to include London as both a region and a special analytical case.
- Whether to add local authority, ITL, or city-region breakdowns later.
- Whether to include Northern Ireland where coverage is incomplete or source ownership differs.
- How to handle changing geographic boundaries.

### Recommended approach

Use this order:

1. UK national view.
2. UK nations plus English regions.
3. Selected city regions or local authorities as a later extension.

This keeps the first finished version coherent while allowing deeper geographic work later.

## 8. Workstream 6: Claims-Evidence Matrix ✅

### Objective

Turn broad article or policy claims into testable statements.

### Completed

- 8 claims created and linked to indicators.
- Evidence ratings defined (Strong, Partial, Weak, Not testable).
- All 8 claims rated with data-driven findings (5 Strong, 3 Partial, 0 TBD).
- Caveats and recommended wording added for each claim.

### Output

A completed `claims_evidence_matrix.csv` with written interpretations.

## 9. Workstream 7: Charts and Dashboard Outputs

### Completed

- National GDP/NDP timeline chart (2007–2025).
- National indicators comparison chart (6 indicators, horizontal bar).
- Regional productivity change chart (12 regions, colour-coded).
- Regional ranking chart (2007 vs 2023 side-by-side).

### Remaining

- Productivity-over-time standalone chart.
- Small-multiple charts by region.
- Optional HTML dashboard.

### Output formats

- PNG charts in `outputs/charts/` (4 charts).
- CSV tables in `outputs/tables/` (4 tables).

## 10. Workstream 8: Narrative Report

### Objective

Create a written evidence pack that can be used by non-technical stakeholders.

### Recommended report structure

1. Executive summary.
2. What changed since 2007.
3. National output and income.
4. Productivity.
5. Wages and living standards.
6. Housing.
7. Public services.
8. Regional differences.
9. Claims-evidence matrix.
10. Data limitations.
11. Methodology.
12. Source appendix.

### Writing standard

The report should separate:

- what the data clearly show,
- what the data suggest,
- what remains uncertain,
- and what cannot be concluded from the available evidence.

## 11. Workstream 9: Quality Assurance ✅

### Completed

- All source URLs validated (`make test` includes URL checks).
- Baseline and latest values spot-checked against source datasets.
- Units confirmed before change calculations.
- Percentage changes verified (spot-checks in QA).
- Charts reviewed against underlying tables.
- Core transformation functions tested via QA suite.
- Known limitations recorded in methodology note.

### QA suite

`src/qa_checks.py` — run with `make test`. Covers indicator register integrity, data completeness, calculation correctness, output table validation, chart generation, claims register cross-references, and long-format dataset validation.

## 12. Workstream 10: Packaging and Reproducibility ✅

### Completed

- Dependency management in `pyproject.toml` and `uv.lock`.
- Makefile with 15 targets (`make help`, `make all`, `make test`, etc.).
- `.gitignore` excludes `.venv/`, caches, and downloadable raw data.
- GitHub repo created with gh CLI, public, full README.
- Single command rebuild: `make all`.

### Commands

```bash
make install    # uv sync
make all        # fetch → process → build
make test       # 94+ QA checks
make clean-all  # remove everything including cached downloads
```

## 13. Proposed Milestones

### Milestone 1: POC Complete ✅

- Skeleton project exists.
- Indicator register exists.
- Claims register exists.
- Placeholder tables are generated.
- uv project management is configured.

### Milestone 2: First Real Data Pull ✅

- National GDP per head is fetched and processed.
- Labour productivity is fetched and processed.
- At least one regional productivity table is populated.
- First real charts are generated.

### Milestone 3: Validated Core Indicator Set ✅

- Core indicators are confirmed.
- Data caveats are documented.
- National 2007 vs latest table is populated.
- Regional productivity table is populated.
- Claims-evidence matrix is partially completed.
- QA check script added (`src/qa_checks.py`). 94+ checks pass.

### Milestone 4: Expanded Evidence Pack ✅

- ✅ Wages or household income added (real earnings).
- ✅ Housing indicator added (price/earnings ratio).
- ✅ Public-service indicator added (NHS waiting list).
- ✅ Regional comparison expanded.
- ✅ Narrative report created (`docs/full-report.md`).

### Milestone 5: Finished Project

- Final data refresh completed.
- All tables and charts generated.
- Claims-evidence matrix completed.
- Methodology note completed.
- Limitations appendix completed.
- Final report or tender-ready evidence pack completed.
- QA checklist passed.

## 14. Key Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Dataset does not go back to 2007 | Indicator may be unusable | Use nearest defensible baseline or move to supporting appendix |
| Dataset methodology changed | Trend may be misleading | Add caveat, split series, or downgrade evidence rating |
| Regional coverage is incomplete | Regional claims may be weak | Use only comparable geographies in core output |
| ONS endpoint or file format changes | Ingestion may fail | Cache raw data and add manual import fallback |
| Indicators are too technical for public use | Narrative may be unclear | Separate technical appendix from public-facing summary |
| Scope expands too quickly | Project becomes unmanageable | Lock a core indicator set before extensions |

## 15. Immediate Next Actions

1. ✅ Add `.gitignore` to exclude `.venv/`, `__pycache__/`, and temporary files.
2. ✅ Validate the ONS source links in `data/indicator_register.csv`.
3. ✅ Implement the first real ONS time-series pull for GDP per head.
4. ✅ Populate the national comparison table for one indicator end to end.
5. ✅ Generate one chart from real data.
6. ✅ Add a simple QA check script (`src/qa_checks.py`, now 72 checks, all pass).
7. ✅ Add real earnings / household disposable income indicator (Workstream 4).
8. ✅ Update indicator register with expanded fields per Workstream 1.
9. ✅ Build the long-format analytical dataset per Workstream 3.
10. ✅ Add housing affordability indicator (Workstream 4).

## 16. Definition of Done for Finished Project

The project can be considered finished when:

- the core indicator register is validated,
- all core indicators have baseline and latest values or documented exclusions,
- national and regional tables are populated,
- charts are generated from processed data,
- the claims-evidence matrix is complete,
- every source is documented,
- caveats are explicit,
- the project can be rebuilt with `uv`,
- and the final report or evidence pack is ready for external use.
