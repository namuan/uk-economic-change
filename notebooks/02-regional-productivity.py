# %% [markdown]
# # 02 - Regional productivity
#
# Purpose: create a 2007 vs latest available regional productivity comparison.
#
# Initial target dataset:
# - ONS Annual regional labour productivity, dataset PRODBYREG

# %%
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
regional_skeleton = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "regional_productivity_skeleton.csv")
regional_skeleton.head()

# %% [markdown]
# Next implementation step:
# - select the correct output-per-hour measure;
# - extract 2007 and latest available year;
# - calculate percentage change;
# - chart regional change.
