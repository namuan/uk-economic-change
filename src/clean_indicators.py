"""Cleaning and comparison utilities for the UK Economic Change POC."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def calculate_change(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate absolute and percentage change for comparison tables.

    Expected columns:
    - baseline_value
    - latest_value

    Missing values are left blank.
    """
    out = df.copy()
    out["baseline_value"] = pd.to_numeric(out["baseline_value"], errors="coerce")
    out["latest_value"] = pd.to_numeric(out["latest_value"], errors="coerce")
    out["absolute_change"] = out["latest_value"] - out["baseline_value"]
    out["percentage_change"] = (out["absolute_change"] / out["baseline_value"]) * 100
    return out


def classify_evidence(row: pd.Series) -> str:
    """Apply a simple first-pass evidence strength rating.

    This is intentionally conservative for the POC.
    """
    has_baseline = pd.notna(row.get("baseline_value"))
    has_latest = pd.notna(row.get("latest_value"))
    has_years = pd.notna(row.get("baseline_year")) and pd.notna(row.get("latest_year"))

    if has_baseline and has_latest and has_years:
        return "Strong candidate"
    if has_baseline or has_latest:
        return "Partial"
    return "TBD"


def load_table(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def save_table(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def process_comparison_file(input_path: str | Path, output_path: str | Path) -> pd.DataFrame:
    df = load_table(input_path)
    df = calculate_change(df)
    df["evidence_strength"] = df.apply(classify_evidence, axis=1)
    save_table(df, output_path)
    return df


def combine_tables(paths: Iterable[str | Path]) -> pd.DataFrame:
    frames = [pd.read_csv(path) for path in paths]
    return pd.concat(frames, ignore_index=True)
