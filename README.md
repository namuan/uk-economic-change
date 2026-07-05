# UK Economic Change

**Working title:** Britain Since 2007: Evidence Framework  
**Status:** Core evidence pack complete ✅

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
make pages      # sync chart assets for GitHub Pages
make all        # fetch → process → build (full pipeline)
make test       # run QA checks
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
| Build | `make build` | Computes changes, generates CSV tables and PNG charts |

### Indicators (6 core indicators + regional productivity)

| Indicator | 2007 | Latest | Change |
|-----------|------|--------|--------|
| Real GDP per head | £37,625 | £40,537 (2025) | +7.7% |
| Real NDP per head | £33,070 | £34,300 (2025) | +3.7% |
| Output per hour worked | 93.0 | 99.4 (2025) | +6.9% |
| Real earnings (AWE) | £711/wk | £727/wk (2025) | +2.3% |
| House price / earnings ratio | 7.17× | 7.55× (2025) | +5.3% |
| NHS waiting list | 4.19M | 7.01M (2026) | +67.5% |
| A&E attendances within 4 hours | 96.8% (2011) | 74.7% (2025) | −22.1pp |
| Regional output per hour | — | — | 12 regions |

### Outputs

```
outputs/
├── tables/
│   ├── national_comparison.csv
│   ├── regional_productivity_comparison.csv
│   ├── combined_comparison.csv
│   ├── claims_evidence_matrix.csv
│   ├── growth_rate_comparison.csv
│   └── public_service_extension.csv
└── charts/
    ├── national_indicators_change.png
    ├── gdp_per_head_timeline.png
    ├── productivity_timeline.png
    ├── growth_rate_comparison.png
    ├── housing_affordability_timeline.png
    ├── nhs_waiting_list_timeline.png
    ├── ae_four_hour_performance_timeline.png
    ├── regional_productivity_change.png
    ├── regional_productivity_small_multiples.png
    └── regional_ranking.png
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
- **Housing affordability deteriorated then partially recovered.** The house price to earnings ratio rose from 7.2× (2007) to a peak of 8.95× (2021) before declining to 7.55× (2025). The 5-year average of 8.19 confirms sustained pressure above 2007 levels for most of the post-crisis period.

See `docs/index.md` for the full public evidence report.

## GitHub Pages

The canonical public report is `docs/index.md` and is live at <https://namuan.github.io/uk-economic-change/>. The workflow in `.github/workflows/static.yml` builds the `docs/` folder with Jekyll and deploys the generated site to GitHub Pages. In repository settings, configure Pages to use **GitHub Actions** as the source. Chart assets used by the page are copied to `docs/assets/charts/`. Run `make pages` after regenerating charts.

### Refreshing the report

Use this sequence when source data changes or before a publication refresh:

```bash
make fetch-force  # optional: re-download source files when upstream data changes
make all          # rebuild processed data, tables and charts
make pages        # copy chart assets into docs/assets/charts/
make test         # run QA checks before publishing
```

## Documentation

| Document | Description |
|----------|-------------|
| `docs/index.md` | **Full evidence report and GitHub Pages landing page** |
| `docs/index-update-prompt.md` | Reusable AI prompt for refreshing the public report from data outputs |
| `docs/methodology-note.md` | Full methodology, data sources, limitations |
| `docs/future-plan.md` | Roadmap and extension plan |
| `docs/project-history.md` | Consolidated implementation history from the original planning and phase docs |

## Core evidence-pack status

- ✅ Six core indicators comparing 2007 with latest
- ✅ One regional indicator comparing 2007 with latest (12 regions)
- ✅ Reproducible absolute and percentage change calculations
- ✅ At least one chart (9 generated)
- ✅ Claims-evidence matrix (8 rated, all non-TBD)
- ✅ Methodology note

## Data principle

ONS is the primary source of truth. Non-ONS sources may be added only when ONS does not cover the indicator or when an official source is more appropriate for the domain.

All data is fetched programmatically — no manual data entry. The ONS v0 API was retired in November 2024; this project uses the generator CSV and direct file endpoints instead.
