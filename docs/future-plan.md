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

## 3. Workstream 1: Data Source Validation

### Objective

Confirm which datasets are suitable, comparable, and defensible for each indicator.

### Required work

- Review every indicator in `data/indicator_register.csv`.
- Confirm the correct ONS dataset, series code, edition, geography, and unit.
- Identify whether each series has a valid 2007 observation.
- Identify the latest available comparable observation.
- Record release frequency and update schedule.
- Document methodology breaks, boundary changes, discontinuities, and caveats.
- Add supplementary official sources where ONS does not cover the required measure.

### Output

A validated indicator register with fields for:

- `indicator_id`,
- `indicator_name`,
- `domain`,
- `source_owner`,
- `source_url`,
- `dataset_id`,
- `series_code`,
- `geography_level`,
- `unit`,
- `baseline_year_available`,
- `latest_year_available`,
- `update_frequency`,
- `comparability_status`,
- `known_caveats`,
- `priority`.

## 4. Workstream 2: Data Ingestion

### Objective

Replace placeholder tables with real data pulls from ONS and other approved official sources.

### Required work

- Implement ONS time-series fetching for national indicators.
- Implement ONS dataset or CSV fetching for labour productivity datasets.
- Add caching for raw downloaded data in `data/raw/`.
- Preserve source filenames or response metadata for auditability.
- Add error handling for unavailable sources, changed endpoints, and missing periods.
- Add a manual import path for official sources that cannot be fetched reliably.
- Ensure all data ingestion runs through `uv run` commands.

### Output

A reproducible ingestion layer that can populate:

- `data/raw/`,
- `data/processed/`,
- `outputs/tables/`.

## 5. Workstream 3: Data Cleaning and Normalisation

### Objective

Convert all raw source data into a shared long-format analytical model.

### Required work

- Standardise date, year, quarter, and annual fields.
- Standardise geography names and geography codes.
- Standardise units and measurement types.
- Separate nominal, real, index, and percentage measures.
- Add inflation-adjustment flags where relevant.
- Add data-quality flags.
- Create a single canonical processed table for all indicators.

### Target table shape

| Column | Description |
|---|---|
| `indicator_id` | Stable project indicator ID |
| `indicator_name` | Human-readable indicator name |
| `domain` | Economy, productivity, wages, housing, public services, etc. |
| `geography_code` | Standard geography code where available |
| `geography_name` | UK, London, Scotland, North West, etc. |
| `geography_type` | National, nation, region, local authority, city region |
| `period_type` | Annual, quarterly, monthly |
| `period` | Source period label |
| `year` | Calendar year or reference year |
| `value` | Numeric value |
| `unit` | Unit of measurement |
| `source_url` | Source link |
| `source_release` | Release or edition information |
| `quality_flag` | OK, partial, estimated, missing, methodology break |
| `notes` | Caveats or interpretation notes |

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

## 8. Workstream 6: Claims-Evidence Matrix

### Objective

Turn broad article or policy claims into testable statements.

### Required work

- Create a structured claim list.
- Link each claim to one or more indicators.
- Define what would count as strong, partial, weak, or unsupported evidence.
- Record whether the evidence is national, regional, or both.
- Add caveats and recommended wording.

### Evidence categories

| Rating | Meaning |
|---|---|
| Strong | Clear baseline, clear latest figure, stable method, direct measure |
| Partial | Directionally useful but incomplete, indirect, or geographically limited |
| Weak | Noisy, indirect, short time series, or difficult to interpret |
| Not testable | No suitable comparable data found |

### Output

A completed `claims_evidence_matrix.csv` and a short written interpretation for each major claim.

## 9. Workstream 7: Charts and Dashboard Outputs

### Objective

Create visual outputs that make the evidence pack usable for reports and presentations.

### Required charts

- National GDP or income per head over time.
- Productivity over time.
- 2007 vs latest comparison by indicator.
- Regional productivity change.
- Regional ranking against UK average.
- Optional small-multiple charts by region.

### Output formats

- PNG or SVG charts in `outputs/charts/`.
- CSV tables in `outputs/tables/`.
- Optional HTML dashboard as a later extension.

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

## 11. Workstream 9: Quality Assurance

### Objective

Ensure the project is reproducible, auditable, and safe to use in external work.

### Required checks

- Validate all source URLs.
- Check all baseline and latest values against source datasets.
- Confirm units before calculating changes.
- Check that percentage changes are calculated correctly.
- Review charts against underlying tables.
- Add tests for core transformation functions.
- Add a QA checklist before publication.
- Record all known limitations.

### Suggested tests

- `indicator_id` values are unique in the register.
- Required fields are not missing.
- Baseline year rows exist where expected.
- Latest year rows exist where expected.
- Numeric values parse correctly.
- No percentage-change calculation divides by zero.
- Output files are generated successfully.

## 12. Workstream 10: Packaging and Reproducibility

### Objective

Make the project easy for another analyst or bidder to run.

### Required work

- Keep dependency management in `pyproject.toml` and `uv.lock`.
- Add clear `uv` commands to the README.
- Avoid committing `.venv/`, caches, or large raw downloads unless required.
- Add `.gitignore`.
- Add a reproducible build command.
- Add a data refresh command.
- Add a report generation command if the final report is automated.

### Suggested commands

```bash
uv sync
uv run python src/fetch_ons.py
uv run python src/build_outputs.py
uv run pytest
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
- QA check script added (`src/qa_checks.py`). All 68 checks pass.

### Milestone 4: Expanded Evidence Pack

- Wages or household income added.
- Housing indicator added.
- Public-service indicator added.
- Regional comparison expanded.
- Draft narrative summary created.

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
6. ✅ Add a simple QA check script (`src/qa_checks.py`, 68 checks, all pass).
7. Add real earnings / household disposable income indicator (Workstream 4).
8. Update indicator register with expanded fields per Workstream 1.
9. Build the long-format analytical dataset per Workstream 3.
10. Add housing affordability indicator.

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
