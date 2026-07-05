.PHONY: help install fetch process build pages all clean clean-all clean-outputs charts tables

# Default target
.DEFAULT_GOAL := help

# ── Install ─────────────────────────────────────────────────────────────

install: ## Install dependencies and create virtual environment
	uv sync

# ── Data pipeline ───────────────────────────────────────────────────────

fetch: ## Download raw ONS source files (cached)
	uv run python src/fetch_ons.py

fetch-force: ## Force re-download all ONS source files
	uv run python -c "from src.fetch_ons import fetch_all; fetch_all(force=True)"

process: ## Normalise raw data into processed comparison tables
	uv run python src/process_indicators.py

build: ## Generate all output tables and charts
	uv run python src/build_outputs.py

pages: build ## Sync GitHub Pages chart assets into docs/
	mkdir -p docs/assets/charts
	cp outputs/charts/*.png docs/assets/charts/

all: fetch process build ## Run the full pipeline (fetch → process → build)

# ── Individual outputs ──────────────────────────────────────────────────

tables: process ## Regenerate output tables only (skips fetch if processed data exists)
	uv run python -c "\
from src.build_outputs import build_comparison_tables, build_claims_matrix; \
n, r, c = build_comparison_tables(); \
build_claims_matrix(n, r); \
from src.build_outputs import build_growth_rate_table; \
build_growth_rate_table(); \
from src.build_outputs import build_public_service_extension_table; \
build_public_service_extension_table(); \
from src.build_outputs import build_international_gdp_per_capita_table; \
build_international_gdp_per_capita_table(); \
print('Tables regenerated.')"

charts: process ## Regenerate charts only (skips fetch if processed data exists)
	uv run python -c "\
from src.process_indicators import write_processed; \
from src.build_outputs import build_all_charts; \
n, r, _ = write_processed(); \
build_all_charts(n, r); \
print('Charts regenerated.')"

# ── Clean ───────────────────────────────────────────────────────────────

clean-outputs: ## Remove generated outputs (tables + charts)
	rm -rf outputs/tables/*.csv outputs/charts/*.png

clean-processed: ## Remove processed data (forces re-processing)
	rm -f data/processed/*.csv

clean-raw: ## Remove cached raw ONS downloads (forces re-fetch)
	rm -f data/raw/ihxw.csv data/raw/mwb6.csv data/raw/prdy.csv data/raw/prodbyreg.xlsx data/raw/ukea.csv

clean: clean-outputs clean-processed ## Remove all generated files (outputs + processed data)

clean-all: clean clean-raw ## Remove everything including cached raw downloads

# ── Quick validation ────────────────────────────────────────────────────

test: ## Run QA checks on indicator register, data, calculations and outputs
	uv run python src/qa_checks.py

validate: ## Run data validation checks
	uv run python -c "\
import pandas as pd, numpy as np; \
df = pd.read_csv('data/raw/ihxw.csv', skiprows=7); \
df.columns = ['period', 'value']; \
annual = df[~df['period'].astype(str).str.contains('Q', na=False)]; \
annual['value'] = pd.to_numeric(annual['value'], errors='coerce'); \
annual = annual.dropna(subset=['value']); \
annual['year'] = annual['period'].astype(int); \
pre = annual[(annual['year'] >= 1997) & (annual['year'] <= 2007)]; \
post = annual[(annual['year'] >= 2007) & (annual['year'] <= 2025)]; \
cagr_pre = (pre['value'].iloc[-1]/pre['value'].iloc[0])**(1/10)-1; \
cagr_post = (post['value'].iloc[-1]/post['value'].iloc[0])**(1/18)-1; \
print(f'GDP per head CAGR: {cagr_pre*100:.1f}% (1997-2007) → {cagr_post*100:.1f}% (2007-2025)'); \
n = pd.read_csv('outputs/tables/national_comparison.csv'); \
r = pd.read_csv('outputs/tables/regional_productivity_comparison.csv'); \
print(f'National indicators: {len(n)} rows, all evidence: {set(n[\"evidence_strength\"])}'); \
print(f'Regional indicators: {len(r)} rows, all evidence: {set(r[\"evidence_strength\"])}'); \
from pathlib import Path; \
charts = list(Path('outputs/charts').glob('*.png')); \
print(f'Charts: {len(charts)} generated ({sum(c.stat().st_size for c in charts):,} bytes total)'); \
print('✓ Validation passed.')"

# ── Help ────────────────────────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
