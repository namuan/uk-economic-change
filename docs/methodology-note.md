# Methodology Note: UK Economic Change POC

## Purpose

This proof of concept tests whether an ONS-first evidence framework can compare Britain in 2007 with the latest available data and repeat at least one measure regionally.

**Status:** POC complete. All six success criteria met.

## Baseline

The baseline year is **2007**. This provides a pre-financial-crisis comparison point and aligns with the wider RFC frame.

## Latest period

| Indicator | Latest available | Published |
|-----------|-----------------|-----------|
| GDP per head (IHXW) | 2025 (annual) | June 2026 |
| NDP per head (MWB6) | 2025 (annual) | June 2026 |
| Output per hour (LZVB) | 2025 (annual) | May 2026 |
| Regional output per hour | 2023 | June 2025 |

National GDP and productivity have more recent data than regional productivity, which typically lags by 1–2 years.

## Source hierarchy

1. Office for National Statistics datasets and time series.
2. Other official UK statistical sources where ONS coverage is insufficient.
3. Supplementary non-official sources only for context, not primary measurement.

**Important:** The ONS v0 API (`api.ons.gov.uk`) was retired on 25 November 2024. All data is fetched via:
- **Time series:** `ons.gov.uk/generator?uri=...&format=csv` (CSV generator endpoint)
- **Datasets:** `ons.gov.uk/file?uri=...` (direct file downloads)

## Data sources (confirmed)

| Indicator | ONS code | Dataset | Access method | File in data/raw/ |
|-----------|----------|---------|---------------|-------------------|
| Real GDP per head | IHXW | UK Economic Accounts (UKEA) | Generator CSV | ihxw.csv |
| Real NDP per head | MWB6 | UK Economic Accounts (UKEA) | Generator CSV | mwb6.csv |
| Output per hour worked | LZVB | Labour productivity (PRDY) | Direct file CSV | prdy.csv |
| Real average weekly earnings | KAB9 + D7BT | Labour Market Stats (LMS) + CPI (MM23) | Generator CSV | kab9_awe.csv, d7bt_cpi.csv |
| Regional output per hour | — | Regional labour productivity (PRODBYREG) | Direct file XLSX | prodbyreg.xlsx |

All values are Chained Volume Measures (CVM) at 2023 reference prices, seasonally adjusted, unless otherwise noted.

## Initial indicators

### Priority (populated)

1. **Real GDP per head** — GBP, CVM 2023 prices, seasonally adjusted.
2. **Real net domestic product per head** — GBP, CVM 2023 prices, seasonally adjusted.
3. **Output per hour worked** — Index 2023=100, whole economy, seasonally adjusted.
4. **Regional output per hour worked** — Index UK=100, 12 ITL1 regions.
5. **Real average weekly earnings** — GBP per week, CPI-deflated to 2025 prices, seasonally adjusted. Computed from nominal AWE (KAB9) and CPI (D7BT).

See `data/indicator_register.csv` for the full validated register with 15 metadata fields per indicator.

### Optional (not yet populated)

- Housing affordability / housing supply.
- NHS waiting times.
- Local authority finance.

## Calculation method

For each indicator:

```text
absolute_change = latest_value - baseline_value
percentage_change = absolute_change / baseline_value * 100
```

Each output row includes the baseline year, latest year, geography, unit, source, and caveat.

For time-series sources, the latest **annual** value is used (quarterly rows are filtered out) to ensure comparability with the 2007 baseline.

## Evidence grading

| Rating | Criteria |
|--------|----------|
| **Strong** | Clear 2007 baseline, current comparable figure, stable definition, transparent official source. |
| **Partial** | Data supports broad direction but has caveats (mixed regional picture, methodology notes, etc.). |
| **TBD** | Indicator not yet populated in this POC. |

## Known limitations

- Regional productivity data is only available to 2023 (published June 2025), while national data extends to 2025.
- Labour productivity uses an index (2023=100) rather than GBP per hour; year-over-year comparisons remain valid.
- Regional productivity is measured relative to UK=100, so region-to-region comparisons show relative position, not absolute output levels.
- The ONS v0 API retirement means fetching relies on website endpoints that may change without notice. Raw files are cached in `data/raw/` for reproducibility.
- NDP per head starts from 1998 in the source data (MWB6 series).
- The POC does not attempt policy attribution.
- Not all social or public-service indicators are best measured by ONS.

## Reproducibility

The full pipeline runs with three commands:

```bash
uv sync                                # install dependencies
uv run python src/fetch_ons.py         # download raw ONS data (cached)
uv run python src/process_indicators.py  # normalise into processed tables
uv run python src/build_outputs.py     # compute changes, generate outputs & charts
```

All output files are generated programmatically with no manual data entry.

## POC success criteria

| Criterion | Status |
|-----------|--------|
| Three national indicators comparing 2007 with latest | ✅ GDP per head, NDP per head, output per hour |
| One regional indicator comparing 2007 with latest | ✅ Output per hour, 12 regions |
| Reproducible absolute and percentage change calculations | ✅ `calculate_change()` in clean_indicators.py |
| At least one chart | ✅ 3 charts (national, regional, timeline) |
| Claims-evidence matrix | ✅ 5 claims rated, 2 TBD |
| Short methodology note | ✅ This document |
