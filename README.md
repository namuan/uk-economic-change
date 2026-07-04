# UK Economic Change

**Working title:** Britain Since 2007: Proof of Concept Evidence Framework  
**Status:** POC complete ✅

An ONS-first evidence framework comparing Britain in 2007 with the latest available data. Pulls real ONS time-series data, computes national and regional comparisons, and generates publication-ready tables and charts.

## Quick start

```bash
make install   # create virtual environment and install dependencies
make all       # fetch ONS data → process → build tables & charts
```

That's it. Outputs appear in `outputs/tables/` and `outputs/charts/`.

## Common commands

```bash
make            # show all available commands
make install    # uv sync
make fetch      # download ONS source files (cached — skips if already present)
make fetch-force  # force re-download all ONS source files
make process    # normalise raw data into processed tables
make build      # generate output tables and charts
make all        # fetch → process → build (full pipeline)
make test       # run QA checks (68 checks)
make validate   # run data validation checks
```

### Partial rebuilds

```bash
make tables     # regenerate tables only (skips fetch)
make charts     # regenerate charts only (skips fetch)
```

### Cleaning

```bash
make clean      # remove outputs + processed data
make clean-all  # remove everything including cached raw downloads
```

## What's inside

### Pipeline (3 stages)

| Stage | Command | What it does |
|-------|---------|--------------|
| Fetch | `make fetch` | Downloads 4 ONS source files to `data/raw/` |
| Process | `make process` | Extracts 2007 & latest values, writes to `data/processed/` |
| Build | `make build` | Computes changes, generates 4 CSVs + 3 PNG charts |

### Indicators (4 populated)

| Indicator | 2007 | Latest | Change |
|-----------|------|--------|--------|
| Real GDP per head | £37,625 | £40,537 (2025) | +7.7% |
| Real NDP per head | £33,070 | £34,300 (2025) | +3.7% |
| Output per hour worked | 93.0 | 99.4 (2025) | +6.9% |
| Real earnings (AWE) | £711/wk | £727/wk (2025) | +2.3% |
| Regional output per hour | — | — | 12 regions |

### Outputs

```
outputs/
├── tables/
│   ├── national_comparison.csv
│   ├── regional_productivity_comparison.csv
│   ├── combined_comparison.csv
│   └── claims_evidence_matrix.csv
└── charts/
    ├── national_indicators_change.png
    ├── regional_productivity_change.png
    └── gdp_per_head_timeline.png
```

## Project management

This project uses [`uv`](https://docs.astral.sh/uv/) for Python dependency management. The `Makefile` wraps common tasks — you should never need to type long `uv run python src/...` commands.

### Adding dependencies

```bash
uv add package-name          # runtime dependency
uv add --dev package-name    # development dependency
uv lock                      # update lockfile after changes
```

`project.yaml` contains lightweight project metadata including the baseline year (2007), output paths, and definition of done.

## Key findings

- **Growth collapsed.** GDP per head grew at 2.3% pa (1997–2007) vs 0.4% pa (2007–2025).
- **NDP grew at half the rate of GDP** (+3.7% vs +7.7%), suggesting capital consumption absorbed a growing share of output.
- **Productivity stagnated.** Output per hour rose just 6.9% over 18 years (~0.4% pa).
- **Real earnings barely moved.** Real AWE rose only 2.3% (+£16/wk) while GDP per head rose 7.7%. The output-pay gap is the defining living-standards story.
- **Regional convergence is happening.** Scotland (+7.3%) and NI (+8.1%) gained most; London (−7.3%) saw the largest relative decline but remains the clear outlier.

See `docs/findings-summary.md` for the full one-page evidence summary.

## Documentation

| Document | Description |
|----------|-------------|
| `docs/full-report.md` | **Full narrative report** — evidence, charts, claims matrix |
| `docs/findings-summary.md` | One-page key findings |
| `docs/methodology-note.md` | Full methodology, data sources, limitations |
| `docs/poc-summary.md` | POC status and structure overview |
| `docs/future-plan.md` | Roadmap from POC to finished evidence product |
| `docs/phase-*-summary.md` | Phase-by-phase implementation records |

## POC definition of done

- ✅ Four national indicators comparing 2007 with latest
- ✅ One regional indicator comparing 2007 with latest (12 regions)
- ✅ Reproducible absolute and percentage change calculations
- ✅ At least one chart (3 generated)
- ✅ Claims-evidence matrix (6 rated, 1 TBD)
- ✅ Methodology note

## Data principle

ONS is the primary source of truth. Non-ONS sources may be added only when ONS does not cover the indicator or when an official source is more appropriate for the domain.

All data is fetched programmatically — no manual data entry. The ONS v0 API was retired in November 2024; this project uses the generator CSV and direct file endpoints instead.
