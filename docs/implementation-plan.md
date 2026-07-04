# Implementation Plan: Real Data & Charts

**Status:** Ready  
**Goal:** Replace all placeholder values with real ONS data and produce charts.

---

## Phase 1: Data Source Discovery (1 session)

### Objective
Find the actual working endpoint for each of the 4 priority indicators. ONS provides multiple access paths (API, direct CSV, bulk downloads) and not all work for every dataset.

### Indicators to resolve

| # | Indicator | ONS Code | Approach |
|---|-----------|----------|----------|
| 1 | Real GDP per head | IHXW (PN2) | ONS API time-series |
| 2 | Real NDP per head | MWB6 (UKEA) | ONS API time-series |
| 3 | Output per hour worked (UK) | PRDY dataset | ONS API dataset → CSV |
| 4 | Regional output per hour worked | PRODBYREG dataset | ONS API dataset → CSV |

### Tasks

1. **Test ONS time-series API** for IHXW and MWB6:
   - `GET https://api.ons.gov.uk/timeseries/IHXW/dataset/PN2/data`
   - `GET https://api.ons.gov.uk/timeseries/MWB6/dataset/UKEA/data`
   - Parse JSON response, confirm 2007 row exists, find latest year.

2. **Test ONS dataset API** for PRDY and PRODBYREG:
   - Discover editions: `GET https://api.ons.gov.uk/datasets/{id}/editions`
   - Get latest edition → versions → CSV download URL.
   - Confirm the dataset contains output-per-hour (not output-per-job).

3. **Fallback plan** if API doesn't work:
   - Direct CSV download from ONS website (often at `/file?uri=...` links).
   - Manual download as last resort, saved to `data/raw/`.

4. **Document findings** in `data/indicator_register.csv` (update `source_url` with confirmed working endpoint).

### Deliverable
- All 4 indicators have a confirmed working data source.
- Raw data downloaded to `data/raw/`.

---

## Phase 2: Data Fetching Layer (1 session)

### Objective
Build robust, cached fetch functions so the pipeline is repeatable.

### Tasks

1. **Enhance `src/fetch_ons.py`**:
   - Add `fetch_ons_timeseries(series_id, dataset_id)` that calls the ONS API and returns a DataFrame with `year` and `value` columns.
   - Add `fetch_ons_dataset_csv(dataset_id)` that discovers the latest edition/version and downloads the CSV.
   - Both functions save raw responses to `data/raw/` for auditability.
   - Add caching: skip download if raw file already exists (force-refresh flag optional).

2. **Create `src/fetch_all.py`** (or extend `fetch_ons.py`):
   - Orchestrates fetching all indicators.
   - Run via `uv run python src/fetch_all.py`.

3. **Add error handling**:
   - Graceful failure with useful messages when endpoints change.
   - Timeout handling.
   - Logging.

### Deliverable
- `uv run python src/fetch_all.py` populates `data/raw/` with all source files.

---

## Phase 3: Data Processing & Normalisation (1 session)

### Objective
Convert raw source data into the canonical processed format with 2007 baseline and latest values.

### Tasks

1. **Create `src/process_indicators.py`**:
   - `process_gdp_per_head()`: Parse IHXW time-series, extract 2007 and latest annual values.
   - `process_ndp_per_head()`: Parse MWB6, extract 2007 and latest.
   - `process_national_productivity()`: Parse PRDY CSV, find output-per-hour series, extract years.
   - `process_regional_productivity()`: Parse PRODBYREG CSV, extract 2007 and latest by region.

2. **Normalise to skeleton format**:
   - Map each indicator to `indicator_id`, `geography`, `baseline_year`, `baseline_value`, `latest_year`, `latest_value`.
   - Overwrite `data/processed/national_comparison_skeleton.csv` and `data/processed/regional_productivity_skeleton.csv`.

3. **Handle edge cases**:
   - Quarterly vs annual data (take annual average or Q4 for annual).
   - Missing 2007 (use nearest year, document).
   - Methodology breaks (flag in caveats column).
   - Chained volume measures vs current prices.

4. **Add units to processed tables**:
   - GBP per head, chained volume measure.
   - Index numbers or GBP per hour.

### Deliverable
- Populated `data/processed/national_comparison_skeleton.csv` with real values.
- Populated `data/processed/regional_productivity_skeleton.csv` with real values.

---

## Phase 4: Output Generation (1 session)

### Objective
Run the existing build pipeline with real data and verify outputs.

### Tasks

1. **Run `build_outputs.py`**:
   - Confirm `calculate_change()` produces correct absolute and % changes.
   - Confirm `classify_evidence()` rates all rows as "Strong candidate" (since data is now populated).

2. **Verify output CSVs**:
   - `outputs/tables/national_comparison.csv` — 3 rows with real numbers.
   - `outputs/tables/regional_productivity_comparison.csv` — 12 rows with real numbers.
   - `outputs/tables/combined_comparison.csv` — 15 rows combined.
   - `outputs/tables/claims_evidence_matrix.csv` — claims register as-is (update evidence columns later).

3. **Generate the regional chart**:
   - The existing `build_placeholder_chart()` will now render because `percentage_change` will have values.
   - Verify: `outputs/charts/regional_productivity_change.png`.

4. **Add national indicator chart** (not currently in build script):
   - Horizontal bar chart of 3 national indicators, percentage change from 2007.
   - Save to `outputs/charts/national_indicators_change.png`.

5. **Add a time-series chart** (stretch goal):
   - GDP per head over time 2007–latest.
   - Save to `outputs/charts/gdp_per_head_timeline.png`.

### Deliverable
- All 4 output tables populated with real data.
- 2–3 charts with real data.

---

## Phase 5: Validation & Documentation (1 session)

### Objective
Ensure numbers are defensible and caveats are clear.

### Tasks

1. **Cross-check values**:
   - Compare extracted values against ONS published bulletins.
   - Verify percentage change calculations match published figures.
   - Check regional totals align with national.

2. **Update caveats**:
   - Populate the `caveat` column in all processed/output tables.
   - Document any methodology breaks, revisions, or limitations.

3. **Update claims matrix**:
   - Set `evidence_strength` for each claim based on actual data.
   - Add specific findings to each claim row.

4. **Update methodology note** if anything changed during implementation.

5. **Run final build** and confirm reproducibility:
   ```bash
   uv sync
   uv run python src/fetch_all.py
   uv run python src/process_indicators.py
   uv run python src/build_outputs.py
   ```

### Deliverable
- Fully populated, validated, documented evidence framework.
- Single `uv run` command chain produces everything.

---

## Quick Reference: ONS API Patterns

### Time-series endpoint
```
GET https://api.ons.gov.uk/timeseries/{SERIES_ID}/dataset/{DATASET_ID}/data
```
Returns JSON with `years` array containing `year`, `value`, `sourceDataset`.

### Dataset discovery
```
GET https://api.ons.gov.uk/datasets/{DATASET_ID}/editions
→ pick latest edition
GET https://api.ons.gov.uk/datasets/{DATASET_ID}/editions/{EDITION}/versions
→ pick latest version
GET .../versions/{VERSION}  → contains downloads.csv.href for CSV URL
```

### Notes
- ONS API does not require authentication.
- Some older time-series IDs may be deprecated — check response.
- Datasets like PRDY and PRODBYREG are large CSVs; filter in pandas after download.
- Chained volume measures (CVM) are the real-terms series; confirm we use the right one.

---

## Implementation Order

1. **Start here →** Phase 1: Test ONS endpoints, confirm data exists.
2. Phase 2: Build fetch layer with caching.
3. Phase 3: Process and normalise data.
4. Phase 4: Generate outputs and charts.
5. Phase 5: Validate and document.

Each phase can be done independently once the previous phase is complete.
