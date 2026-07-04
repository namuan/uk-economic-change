# %% [markdown]
# # 01 - National indicators
#
# Purpose: pull or import national ONS indicators and create a 2007 vs latest comparison table.
#
# Initial POC indicators:
# - Real GDP per head
# - Real net domestic product per head
# - Output per hour worked

# %%
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
indicator_register = pd.read_csv(PROJECT_ROOT / "data" / "indicator_register.csv")
indicator_register.query("geography_level == 'national'")

# %% [markdown]
# Next implementation step:
# - resolve direct ONS CSV/API endpoints for each series;
# - save raw data to `data/raw/`;
# - standardise into long format;
# - create 2007 vs latest comparison.
