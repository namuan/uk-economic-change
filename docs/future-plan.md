# Future Plan: Evidence Pack Extensions

**Project:** UK Economic Change Comparison Framework  
**Working title:** Britain Since 2007: Evidence Framework  
**Status:** Core evidence pack complete; publication readiness and documentation cleanup complete; remaining work is phased extension  
**Baseline year:** 2007  
**Primary source policy:** ONS first; other official sources where ONS does not cover the measure

## 1. Current Status

The core evidence pack is complete and published through `docs/index.md`, which is the canonical report and GitHub Pages landing page.

The project now has:

- a validated indicator register (`data/indicator_register.csv`),
- a claims register (`data/claims_register.csv`),
- automated data fetching and processing,
- a long-format analytical dataset,
- national and regional comparison tables,
- nine chart outputs,
- a completed claims-evidence matrix with 8 rated claims,
- a methodology note,
- QA checks (`make test`),
- a GitHub Pages workflow (`.github/workflows/static.yml`),
- and a public report at `docs/index.md`.

The remaining work is no longer about proving the concept. It is about improving publication quality, broadening evidence coverage, adding geographic depth, and preparing optional dashboard or tender-pack outputs.

## 2. Completed Core Scope

### Data sources and ingestion ✅

- ONS time-series fetching implemented for GDP per head, NDP per head, earnings, and CPI.
- ONS file downloads implemented for labour productivity, regional productivity, and housing affordability.
- NHS England RTT waiting-list data incorporated as an official non-ONS source.
- Raw downloads cached in `data/raw/`; curated NHS waiting-list CSV tracked in git.
- Pipeline runs through `make fetch`, `make process`, and `make build`.

### Core indicators ✅

| Domain | Indicator | Coverage | Latest |
|---|---|---|---|
| Output | Real GDP per head | UK | 2025 |
| Income | Real NDP per head | UK | 2025 |
| Productivity | Output per hour worked | UK | 2025 |
| Earnings | CPI-deflated average weekly earnings | UK | 2025 |
| Housing | House price to earnings ratio | England and Wales | 2025 |
| Public services | NHS RTT incomplete pathways | England | 2026 |
| Regional productivity | Output per hour, UK nations and English regions | 12 ITL1 regions | 2023 |

### Outputs ✅

- `outputs/tables/national_comparison.csv`
- `outputs/tables/regional_productivity_comparison.csv`
- `outputs/tables/combined_comparison.csv`
- `outputs/tables/claims_evidence_matrix.csv`
- `outputs/charts/national_indicators_change.png`
- `outputs/charts/gdp_per_head_timeline.png`
- `outputs/charts/regional_productivity_change.png`
- `outputs/charts/regional_ranking.png`
- `outputs/charts/productivity_timeline.png`
- `outputs/charts/regional_productivity_small_multiples.png`
- `outputs/charts/housing_affordability_timeline.png`
- `outputs/charts/nhs_waiting_list_timeline.png`
- `outputs/charts/growth_rate_comparison.png`
- `docs/index.md` public report
- `docs/assets/charts/` GitHub Pages chart assets

### Claims matrix ✅

All 8 claims are rated:

- 5 Strong
- 3 Partial
- 0 TBD

## 3. Outstanding Work by Phase

The phases below are ordered so that each one can be tackled independently. Later phases should not block publication of the current evidence pack.

---

## Phase 1: Publication Readiness ✅ Complete

**Goal:** Ensure the current evidence pack is externally publishable and easy to maintain.

**Completed:** 2026-07-05  
**Live report:** <https://namuan.github.io/uk-economic-change/>

### Tasks

1. ✅ Confirm GitHub Pages deployment succeeds from `.github/workflows/static.yml`.
2. ✅ Verify the live Pages URL loads `docs/index.md` by default.
3. ✅ Check that all four chart images render on the live page.
4. ✅ Do a final copy-edit of `docs/index.md` for public readability.
5. ✅ Add the live Pages URL to `README.md` once known.
6. ✅ Run `make pages` and `make test` before release.

### Acceptance criteria

- ✅ GitHub Pages is live.
- ✅ The report loads at the repo Pages root.
- ✅ Charts render correctly.
- ✅ `make test` passes.
- ✅ README links to the live report.

### Verification notes

- Latest checked Pages workflow run succeeded on `main`.
- The repo Pages root loads the report generated from `docs/index.md`.
- The 4 live chart assets returned HTTP 200 responses.
- `make pages` completed successfully.
- `make test` passed.

---

## Phase 2: Documentation and Maintenance Cleanup ✅ Complete

**Goal:** Remove stale project-history wording and make maintenance instructions explicit.

**Completed:** 2026-07-05

### Tasks

1. ✅ Keep `docs/project-history.md` as the single consolidated historical record.
2. ✅ Update `docs/methodology-note.md` so its status, indicator list, and QA count match the current project.
3. ✅ Add a short “how to refresh the report” note covering:
   - `make fetch-force` when source data changes,
   - `make all`,
   - `make pages`,
   - `make test`.
4. ✅ Ensure all documentation points to `docs/index.md` as the canonical report.

### Acceptance criteria

- ✅ No current-facing document describes the live evidence pack as unfinished POC work.
- ✅ Maintenance steps are clear enough for a new contributor.
- ✅ Historical context is consolidated in `docs/project-history.md` rather than spread across stale phase documents.

### Verification notes

- `docs/project-history.md` is the single historical record for the original implementation phases.
- `docs/methodology-note.md` reflects the current indicator set and QA status.
- `README.md` includes a concise report-refresh sequence using `make fetch-force`, `make all`, `make pages`, and `make test`.
- Current-facing documentation points to `docs/index.md` as the canonical report.
- Stale proof-of-concept wording is confined to historical context or maintenance prompts.

---

## Phase 3: Chart and Analytical Output Improvements ✅ Complete

**Goal:** Improve the evidence pack's visual and analytical clarity without adding new indicators.

**Completed:** 2026-07-05

### Tasks

1. ✅ Add a standalone productivity-over-time chart.
2. ✅ Add small-multiple regional productivity charts or sparklines.
3. ✅ Add a housing affordability timeline chart.
4. ✅ Add an NHS waiting-list timeline chart.
5. ✅ Consider adding a table or chart showing pre-2007 versus post-2007 CAGR for GDP per head and productivity.
6. ✅ Update `docs/index.md` to include any new charts where they strengthen the narrative.

### Acceptance criteria

- ✅ New charts are generated reproducibly from processed or raw source data.
- ✅ QA checks verify each new chart exists and has content.
- ✅ The report uses only charts that add interpretive value.

### Verification notes

- Added 5 new chart outputs: productivity timeline, regional productivity small multiples, housing affordability timeline, NHS waiting-list timeline, and growth-rate comparison.
- Added `outputs/tables/growth_rate_comparison.csv` for pre-2007 versus post-2007 CAGR comparisons.
- Updated `docs/index.md` to include the new charts in the relevant narrative sections.
- Updated QA checks to cover the new table and all 9 charts.
- `make pages` completed successfully.
- `make test` passed.

---

## Phase 4: Living Standards and Distributional Expansion

**Goal:** Move beyond average earnings and GDP per head to better represent household experience.

### Candidate indicators

1. Real household disposable income per head.
2. Equivalised household disposable income by decile or quintile.
3. Income inequality measures such as Gini coefficient or percentile ratios.
4. Poverty or material deprivation measures, if comparable to 2007.
5. Wealth indicators, if a defensible 2007 baseline and latest figure exist.

### Tasks

1. Identify official sources and confirm comparability.
2. Add validated indicators to `data/indicator_register.csv`.
3. Extend fetch/process/build scripts.
4. Add claims only where the indicator can test a clear statement.
5. Update methodology and report caveats.

### Acceptance criteria

- At least one distributional living-standards indicator is added or explicitly rejected with documented rationale.
- Any promoted indicator has a defensible baseline, latest value, source, and caveat.

---

## Phase 5: Housing and Public-Service Expansion

**Goal:** Broaden domains where the current report has partial geographic or service coverage.

### Housing tasks

1. Investigate Scotland and Northern Ireland housing affordability sources.
2. Assess whether a UK-wide or four-nation comparable housing affordability measure can be constructed.
3. Consider housing supply indicators: completions, starts, dwellings per household, or planning approvals.
4. Add local authority housing affordability only if geography and methodology are manageable.

### Public-service tasks

1. Evaluate A&E waiting-time indicators.
2. Evaluate social care indicators.
3. Evaluate local authority spending power.
4. Consider courts, schools, or other public-service pressure indicators where official time series exist.

### Acceptance criteria

- Housing coverage gaps are either filled or clearly documented as unresolved.
- At least one broader public-service indicator is added or rejected with documented rationale.

---

## Phase 6: Geographic Deepening

**Goal:** Add sub-regional insight while avoiding boundary and comparability traps.

### Tasks

1. Decide the next geography level: local authority, ITL2/ITL3, or selected city regions.
2. Document boundary-change handling rules.
3. Decide whether London should be split or treated as a special analytical case.
4. Add sub-regional outputs for one domain first, likely productivity or housing.
5. Add maps only if they improve interpretation and can be generated reproducibly.

### Acceptance criteria

- Geography design is documented before new data is added.
- The first sub-regional extension is limited, reproducible, and caveated.

---

## Phase 7: International Context

**Goal:** Put the UK's post-2007 productivity and GDP performance in peer-country context.

### Candidate sources

- OECD
- World Bank
- IMF
- Eurostat, where still appropriate for historical European comparisons

### Tasks

1. Choose a small peer group, e.g. US, Germany, France, Italy, Canada.
2. Select comparable measures: GDP per head, GDP per hour worked, productivity index, or real wages.
3. Confirm 2007 and latest comparability.
4. Add one concise international comparison section or appendix.

### Acceptance criteria

- International comparison is clearly caveated and does not dilute the ONS-first domestic evidence base.
- Data source and methodology are transparent.

---

## Phase 8: Optional Dashboard or Tender Pack

**Goal:** Package the evidence for different audiences.

### Options

1. Lightweight HTML dashboard.
2. Downloadable tender-ready evidence pack.
3. Static PDF export of the report.
4. Data appendix with source links and machine-readable output tables.

### Acceptance criteria

- Chosen output is generated reproducibly.
- It does not introduce a second unsynchronised copy of the report.
- README explains how to rebuild or publish it.

## 4. Definition of Done for Future Extensions

An extension should only be considered complete when:

- source and caveats are documented,
- 2007 or nearest defensible baseline is available,
- latest comparable value is available,
- calculations are reproducible,
- output tables and charts are generated where needed,
- claims are updated only where evidence supports them,
- `make test` passes,
- `docs/index.md` and `docs/methodology-note.md` are updated,
- and the live Pages report can be refreshed with `make pages` plus the GitHub Actions workflow.

## 5. Immediate Next Phase Recommendation

Start with **Phase 4: Living Standards and Distributional Expansion**.

Reason: Phases 1 to 3 are complete. The current report is published, documented, and visually strengthened. The highest-value next step is now to broaden the living-standards evidence beyond averages.
