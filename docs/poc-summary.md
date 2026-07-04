# Britain Since 2007: Proof of Concept Evidence Framework

## Status: Complete ✅

All six POC success criteria are met. The pipeline fetches ONS data, computes 2007-vs-latest comparisons, and generates tables and charts reproducibly.

## What this POC contains

### Data pipeline (3-stage, fully automated)

| Stage | Command | Output |
|-------|---------|--------|
| Fetch | `uv run python src/fetch_ons.py` | 4 raw ONS files in `data/raw/` |
| Process | `uv run python src/process_indicators.py` | Populated comparison tables in `data/processed/` |
| Build | `uv run python src/build_outputs.py` | Final tables + 3 charts + claims matrix |

### Indicators (4 populated)

| # | Indicator | 2007 | Latest | Change |
|---|-----------|------|--------|--------|
| 1 | Real GDP per head | £37,625 | £40,537 (2025) | +7.7% |
| 2 | Real NDP per head | £33,070 | £34,300 (2025) | +3.7% |
| 3 | Output per hour worked | 93.0 | 99.4 (2025) | +6.9% |
| 4 | Regional output per hour | — | — | 12 regions |

### Key findings

- **Growth collapsed after 2007.** GDP per head grew at 2.3% pa before the crisis and just 0.4% pa afterwards. Productivity followed the same pattern (2.1% → 0.4% pa).
- **NDP tells a different story.** Net domestic product per head grew at less than half the rate of GDP (+3.7% vs +7.7%), suggesting capital consumption absorbed a growing share of output.
- **Regional convergence is happening.** Scotland (+7.3%) and Northern Ireland (+8.1%) saw the largest productivity gains relative to the UK average. London's advantage narrowed (−7.3%) but it remains a clear outlier at 28% above UK average.
- **Seven regions improved** their position relative to the UK average since 2007; five declined.

### Outputs

```
outputs/tables/
├── national_comparison.csv              — 3 indicators
├── regional_productivity_comparison.csv  — 12 regions
├── combined_comparison.csv              — 15 rows combined
└── claims_evidence_matrix.csv            — 5 rated, 2 TBD

outputs/charts/
├── national_indicators_change.png       — horizontal bar
├── regional_productivity_change.png     — colour-coded bar chart
└── gdp_per_head_timeline.png            — line chart 2007-2025

docs/
├── methodology-note.md                  — full methodology
├── findings-summary.md                  — one-page findings
├── poc-summary.md                       — this document
├── phase-1-2-summary.md                 — data source discovery & fetch layer
├── phase-3-summary.md                   — data processing
├── phase-4-summary.md                   — charts, claims, validation
└── implementation-plan.md               — original 5-phase plan
```

### Technology

- **Python 3.11+** with `uv` for dependency management
- **pandas** for data processing, **matplotlib** for charts, **openpyxl** for XLSX
- All data sourced from ONS official releases via generator CSV and direct file endpoints
- No manual data entry; fully reproducible

---

## Next steps (beyond POC)

See `docs/future-plan.md` for the 10-workstream roadmap to a finished evidence product. Immediate next actions:

1. Add real earnings / household disposable income indicator.
2. Add housing affordability indicator.
3. Expand to local authority or city-region geographies.
4. Produce a narrative report.
