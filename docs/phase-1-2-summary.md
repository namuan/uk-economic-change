# Phase 1 & 2 Completion: Data Source Discovery & Fetch Layer

**Date:** 4 July 2026  
**Status:** Complete ✓

---

## Phase 1: Data Source Discovery

### Objective
Find working ONS endpoints for all 4 priority indicators and extract real 2007 vs latest values.

### Key finding: Old ONS API is retired
The `api.ons.gov.uk` v0 API (time-series endpoints like `/timeseries/IHXW/dataset/PN2/data`) was **fully retired on 25 November 2024**. All indicators required alternative access paths.

### Resolved endpoints

| # | Indicator | ONS Code | Working endpoint | Format |
|---|-----------|----------|------------------|--------|
| 1 | Real GDP per head | IHXW | `ons.gov.uk/generator?uri=.../ihxw/ukea&format=csv` | CSV |
| 2 | Real NDP per head | MWB6 | `ons.gov.uk/generator?uri=.../mwb6/ukea&format=csv` | CSV |
| 3 | Output per hour worked (UK) | LZVB (in PRDY) | `ons.gov.uk/file?uri=.../prdy.csv` | CSV |
| 4 | Regional output per hour | PRODBYREG | `ons.gov.uk/file?uri=.../prodbyregaccessiblefinal.xlsx` | XLSX |

### Extracted values

#### National indicators

| Indicator | 2007 | Latest (2025) | Absolute change | % change |
|-----------|------|---------------|-----------------|----------|
| GDP per head (CVM, 2023 £) | £37,625 | £40,563 | +£2,938 | **+7.8%** |
| NDP per head (CVM, 2023 £) | £33,070 | £34,300 | +£1,230 | **+3.7%** |
| Output per hour (Index 2023=100) | 93.0 | 99.4 | +6.4 pts | **+6.9%** |

NDP per head grew at **less than half the rate** of GDP per head (3.7% vs 7.8%), confirming these measures tell materially different stories about post-2007 economic change.

#### Regional productivity (Output per hour, Index UK=100)

| Region | 2007 | 2023 | Change |
|--------|------|------|--------|
| North East | 86.75 | 85.40 | −1.36 |
| North West | 93.25 | 94.79 | +1.54 |
| Yorkshire & The Humber | 90.42 | 87.88 | −2.54 |
| East Midlands | 84.51 | 85.26 | +0.75 |
| West Midlands | 84.94 | 85.21 | +0.26 |
| East of England | 97.43 | 94.72 | −2.71 |
| **London** | **138.66** | **128.52** | **−10.13** |
| South East | 107.55 | 107.67 | +0.12 |
| South West | 91.30 | 92.46 | +1.16 |
| Wales | 82.39 | 84.87 | +2.48 |
| **Scotland** | **92.16** | **98.89** | **+6.73** |
| **Northern Ireland** | **81.10** | **87.64** | **+6.54** |

**Key patterns:**
- London's relative productivity advantage shrank substantially (−10.1 pts), while still remaining the clear outlier.
- Scotland and Northern Ireland showed the strongest convergence gains (+6.7 and +6.5 pts respectively).
- Five regions saw their position relative to the UK average worsen since 2007.

### Data notes
- All national values are chained volume measures (CVM) at 2023 reference prices, seasonally adjusted.
- Regional data is latest available (2023, published June 2025). Regional productivity typically lags national data by 1–2 years.
- Labour productivity uses index 2023=100 (not GBP per hour), but year-over-year comparisons are valid.

---

## Phase 2: Data Fetching Layer

### Objective
Build a robust, caching-aware fetch layer that makes the pipeline repeatable with a single command.

### What was built

**`src/fetch_ons.py`** — rewritten from placeholder to production-ready:

| Component | Description |
|-----------|-------------|
| `fetch_gdp_per_head(force=False)` | Downloads IHXW CSV from ONS generator endpoint |
| `fetch_ndp_per_head(force=False)` | Downloads MWB6 CSV from ONS generator endpoint |
| `fetch_labour_productivity(force=False)` | Downloads PRDY CSV from ONS direct file endpoint |
| `fetch_regional_productivity(force=False)` | Downloads PRODBYREG XLSX from ONS direct file endpoint |
| `fetch_all(force=False)` | Orchestrates all 4 fetchers, returns `FetchReport` |
| Caching | Skips download if file exists in `data/raw/` |
| `FetchReport` | Aggregate summary: OK / Cached / Failed counts per indicator |
| CLI entry point | `uv run python src/fetch_ons.py` |

### Usage

```bash
# Normal run (uses cache if files exist)
uv run python src/fetch_ons.py

# Force re-download all
uv run python -c "from src.fetch_ons import fetch_all; fetch_all(force=True)"

# Fetch a single indicator
uv run python -c "from src.fetch_ons import fetch_gdp_per_head; print(fetch_gdp_per_head(force=True))"
```

### Validation

All 4 downloaded files confirmed valid and parseable:

| File | Rows | Columns | Format |
|------|------|---------|--------|
| `ihxw.csv` | 401 | 2 (year, value) | CSV with 7-line metadata header |
| `mwb6.csv` | 156 | 2 (year, value) | CSV with 7-line metadata header |
| `prdy.csv` | 339 | 136 (time series) | CSV with 6-line metadata header |
| `prodbyreg.xlsx` | 7 sheets | Table_2: 34×14 | Multi-sheet XLSX |

### Raw data location
All source files are saved to `data/raw/`:
```
data/raw/
├── ihxw.csv          (6.8 KB) — Real GDP per head
├── mwb6.csv          (2.8 KB) — Real NDP per head
├── prdy.csv           (234 KB) — Labour productivity
├── prodbyreg.xlsx     (198 KB) — Regional productivity
└── ukea.csv          (11.8 MB) — Full UK Economic Accounts (reference)
```

---

## Next: Phase 3 — Data Processing & Normalisation

The raw data needs to be parsed and mapped into the canonical skeleton format at `data/processed/`. This involves:
1. Extracting 2007 and latest values from each source.
2. Mapping to `indicator_id`, `geography`, `baseline_year`, `baseline_value`, `latest_year`, `latest_value`.
3. Writing to `national_comparison_skeleton.csv` and `regional_productivity_skeleton.csv`.
4. Handling quarterly/annual, missing values, and units consistently.
