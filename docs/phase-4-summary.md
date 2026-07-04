# Phase 4 Completion: Charts, Claims Matrix & Validation

**Date:** 4 July 2026  
**Status:** Complete ✓  
**Build:** 3 publication-quality charts, populated claims matrix, data validated.

---

## Objective

Replace the placeholder chart with a suite of publication-quality visualisations, populate the claims-evidence matrix with real ratings, and cross-validate all extracted values.

---

## Charts generated

### 1. National Indicators Comparison (`national_indicators_change.png`)
Horizontal bar chart showing percentage change since 2007 for all three national indicators:
- GDP per head: **+7.7%**
- Output per hour: **+6.9%**
- NDP per head: **+3.7%**

Colour-coded with value labels. ONS-style styling (blue bars, clean axes).

### 2. Regional Productivity Change (`regional_productivity_change.png`)
Bar chart of all 12 regions, colour-coded green (above 2007) / red (below 2007):
- **Biggest gainers:** Northern Ireland (+8.1%), Scotland (+7.3%), Wales (+3.0%)
- **Biggest decliners:** London (−7.3%), East of England (−2.8%), Yorkshire & The Humber (−2.8%)
- Includes legend and per-bar value labels.

### 3. GDP & NDP Timeline (`gdp_per_head_timeline.png`)
Line chart plotting GDP per head and NDP per head from 2007 to 2025:
- Annotated with the 2008 financial crisis and COVID-19 markers.
- Shows the 2008-09 crash, slow recovery, COVID dip, and modest post-COVID growth.
- NDP consistently tracks below GDP, with the gap widening slightly over time.

---

## Claims-evidence matrix

The `build_claims_matrix()` function now populates evidence ratings and findings using actual data values:

| Claim | Rating | Key finding |
|-------|--------|-------------|
| C001: Output per person changed materially | **Strong** | GDP per head +7.7%; ~0.4% pa growth |
| C002: National income changed materially | **Strong** | NDP per head +3.7%; half the GDP rate |
| C003: Productivity growth has been weak | **Strong** | +6.9% over 18 years vs ~2% pa pre-2007 |
| C004: Regional inequality persists | **Partial** | Mixed: 7 regions gained, 5 declined |
| C005: London remains a productivity outlier | **Strong** | Still 28% above UK average, but gap narrowed |
| C006: Living standards vs GDP | **TBD** | Earnings indicator not yet populated |
| C007: Housing pressure worsened | **TBD** | Housing indicator not yet populated |

---

## Data validation

### Internal consistency checks

| Check | Result |
|-------|--------|
| Annual values vs quarterly data | ✓ Consistent (annual ~4× quarterly, as expected for per-head figures) |
| GDP per head CAGR 1997–2007 | 2.3% pa — matches pre-crisis trend |
| GDP per head CAGR 2007–2025 | 0.4% pa — confirms growth collapse |
| Productivity CAGR 1997–2007 | 2.1% pa |
| Productivity CAGR 2007–2025 | 0.4% pa — confirms stagnation narrative |
| Regional dispersion (std dev) | 15.1 (2007) → 12.2 (2023) — inequality narrowed |

### Source provenance
All data sourced directly from ONS official releases:
- **IHXW / MWB6**: UK Economic Accounts (UKEA), chained volume measures, 2023 reference year
- **PRDY (LZVB)**: Labour productivity quarterly dataset, May 2026 release
- **PRODBYREG**: Regional labour productivity, 2023 estimates, June 2025 release

No manual data entry; all values extracted programmatically from official source files.

---

## Updated build outputs

Running `uv run python src/build_outputs.py` now produces:

```
outputs/tables/
├── national_comparison.csv           — 3 indicators with real data
├── regional_productivity_comparison.csv — 12 regions with real data
├── combined_comparison.csv           — 15 rows combined
└── claims_evidence_matrix.csv         — 5 rated, 2 TBD

outputs/charts/
├── national_indicators_change.png    (38 KB)
├── regional_productivity_change.png  (104 KB)
└── gdp_per_head_timeline.png         (107 KB)
```

---

## Full pipeline status

```bash
uv sync                                # ✅
uv run python src/fetch_ons.py         # ✅ 4 raw files (cached)
uv run python src/process_indicators.py  # ✅ 3 national + 12 regional
uv run python src/build_outputs.py     # ✅ 4 tables + 3 charts
```

All POC success criteria from `project.yaml` are now met:
- ✅ Three national indicators comparing 2007 with latest
- ✅ One regional indicator comparing 2007 with latest (12 regions)
- ✅ Reproducible absolute and percentage change calculations
- ✅ At least one chart (3 charts)
- ✅ Claims-evidence matrix (5 rated)
- ✅ Short methodology note (already exists in docs/)

---

## Next: Phase 5 — Documentation & Final Polish

Remaining tasks to close out the POC:
1. Update `docs/methodology-note.md` with actual data sources.
2. Update `data/indicator_register.csv` with confirmed endpoints.
3. Add a one-page findings summary.
4. Clean up any remaining placeholder text.
