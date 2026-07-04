"""
Process raw ONS source files into canonical comparison tables.

Reads downloaded data from data/raw/ and populates:
- data/processed/national_comparison_skeleton.csv
- data/processed/regional_productivity_skeleton.csv

Each output row contains indicator_id, geography, baseline_year,
baseline_value, latest_year, and latest_value. The build_outputs.py
script then computes absolute_change, percentage_change, and
evidence_strength.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Column names for processed output
# ---------------------------------------------------------------------------

PROCESSED_COLS = [
    "indicator_id",
    "geography",
    "baseline_year",
    "baseline_value",
    "latest_year",
    "latest_value",
    "absolute_change",
    "percentage_change",
    "evidence_strength",
    "caveat",
]


def _read_ons_generator_csv(path: Path) -> pd.DataFrame:
    """Read a time-series CSV from the ONS generator endpoint.

    These CSVs have 7 metadata rows (Title, CDID, Source dataset ID,
    PreUnit, Unit, Release date, Next release, Important notes) followed
    by year/value data in two columns.
    """
    df = pd.read_csv(path, skiprows=7)
    df.columns = ["period", "value"]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["period"] = df["period"].astype(str).str.strip()
    return df


def _latest_annual(df: pd.DataFrame, after: int = 2006) -> tuple[str, float]:
    """Return (year, value) for the latest annual observation after *after*.

    Annual rows are those whose period label is a plain 4-digit year
    (no 'Q', no month abbreviation, no space).
    """
    is_annual = df["period"].str.match(r"^\d{4}$", na=False)
    annual = df[is_annual & df["value"].notna()].copy()
    annual = annual[annual["period"].astype(int) > after]
    if annual.empty:
        raise ValueError("No annual observations found")
    row = annual.iloc[-1]
    return str(row["period"]), float(row["value"])


def _annual_value(df: pd.DataFrame, year: int) -> float:
    """Return the annual value for *year*."""
    row = df[df["period"] == str(year)]
    if row.empty:
        raise ValueError(f"Year {year} not found in data")
    return float(row["value"].iloc[0])


# ---------------------------------------------------------------------------
# National indicators
# ---------------------------------------------------------------------------


def process_gdp_per_head() -> dict:
    """Extract GDP per head (IHXW): 2007 vs latest annual."""
    df = _read_ons_generator_csv(RAW_DIR / "ihxw.csv")
    baseline = _annual_value(df, 2007)
    latest_year, latest_val = _latest_annual(df)
    return {
        "indicator_id": "gdp_per_head",
        "geography": "UK",
        "baseline_year": 2007,
        "baseline_value": baseline,
        "latest_year": int(latest_year),
        "latest_value": latest_val,
    }


def process_ndp_per_head() -> dict:
    """Extract NDP per head (MWB6): 2007 vs latest annual."""
    df = _read_ons_generator_csv(RAW_DIR / "mwb6.csv")
    baseline = _annual_value(df, 2007)
    latest_year, latest_val = _latest_annual(df)
    return {
        "indicator_id": "real_ndp_per_head",
        "geography": "UK",
        "baseline_year": 2007,
        "baseline_value": baseline,
        "latest_year": int(latest_year),
        "latest_value": latest_val,
    }


def process_labour_productivity() -> dict:
    """Extract output per hour worked (PRDY, CDID LZVB): 2007 vs 2025 annual.

    The PRDY CSV has 6 metadata rows; the first row is the column
    titles.  The target column is 'UK Whole Economy: Output per hour
    worked SA: Index 2023 = 100'.
    """
    df = pd.read_csv(
        RAW_DIR / "prdy.csv",
        header=0,
        skiprows=lambda x: x in [1, 2, 3, 4, 5, 6],
    )
    cols = list(df.columns)
    cols[0] = "period"
    df.columns = cols

    target = "UK Whole Economy: Output per hour worked SA: Index 2023 = 100"
    if target not in df.columns:
        raise KeyError(f"Column '{target[:60]}…' not found in PRDY")

    df["value"] = pd.to_numeric(df[target], errors="coerce")
    df["period"] = df["period"].astype(str).str.strip()

    # Annual observations have plain-year period labels.
    row_2007 = df[df["period"] == "2007"]
    row_2025 = df[df["period"] == "2025"]

    if row_2007.empty:
        raise ValueError("2007 not found in PRDY annual data")
    if row_2025.empty:
        # Fall back to latest available annual
        annual = df[~df["period"].str.contains("Q", na=False)][["period", "value"]].dropna()
        annual = annual[annual["period"].astype(int) > 2006]
        latest = annual.iloc[-1]
    else:
        latest = row_2025.iloc[0]

    return {
        "indicator_id": "labour_productivity_output_per_hour",
        "geography": "UK",
        "baseline_year": 2007,
        "baseline_value": float(row_2007["value"].iloc[0]),
        "latest_year": int(latest["period"]),
        "latest_value": float(latest["value"]),
    }


def process_real_earnings() -> dict:
    """Compute real Average Weekly Earnings (CPI-deflated) for 2007 vs 2025.

    Uses nominal AWE (KAB9) deflated by CPI all-items index (D7BT).
    Both series are expressed in 2025 prices for comparability.
    """
    # Nominal AWE
    awe = _read_ons_generator_csv(RAW_DIR / "kab9_awe.csv")
    awe_nominal_2007 = _annual_value(awe, 2007)
    awe_latest_year, awe_nominal_latest = _latest_annual(awe)

    # CPI index
    cpi = _read_ons_generator_csv(RAW_DIR / "d7bt_cpi.csv")
    cpi_2007 = _annual_value(cpi, 2007)
    _, cpi_latest = _latest_annual(cpi)

    # Deflate to latest-year prices
    real_2007 = awe_nominal_2007 * (cpi_latest / cpi_2007)
    real_latest = awe_nominal_latest  # already in latest-year prices

    return {
        "indicator_id": "real_earnings",
        "geography": "UK",
        "baseline_year": 2007,
        "baseline_value": round(real_2007, 0),
        "latest_year": int(awe_latest_year),
        "latest_value": round(real_latest, 0),
    }


def build_national_table() -> pd.DataFrame:
    """Build the populated national comparison table."""
    rows = [
        process_gdp_per_head(),
        process_ndp_per_head(),
        process_labour_productivity(),
        process_real_earnings(),
    ]
    df = pd.DataFrame(rows)
    # Add remaining columns with empty placeholders
    for col in PROCESSED_COLS:
        if col not in df.columns:
            df[col] = ""
    # Add caveats
    df["caveat"] = [
        "CVM 2023 prices, seasonally adjusted. 2025 is latest full year.",
        "CVM 2023 prices, seasonally adjusted. NDP = GDP minus capital consumption.",
        "Index 2023=100, seasonally adjusted, whole economy. Quarterly data available.",
        "Nominal AWE (KAB9) deflated by CPI (D7BT) to 2025 prices. Whole economy, total pay, seasonally adjusted. Monthly data available.",
    ]
    return df[PROCESSED_COLS]


# ---------------------------------------------------------------------------
# Regional productivity
# ---------------------------------------------------------------------------


# Mapping from ONS region labels to project geography names.
REGION_MAP = {
    "North East": "North East",
    "North West": "North West",
    "Yorkshire and the Humber": "Yorkshire and The Humber",
    "East Midlands": "East Midlands",
    "West Midlands": "West Midlands",
    "East of England": "East of England",
    "London": "London",
    "South East": "South East",
    "South West": "South West",
    "Wales": "Wales",
    "Scotland": "Scotland",
    "Northern Ireland": "Northern Ireland",
}


def process_regional_productivity() -> list[dict]:
    """Extract regional output per hour (PRODBYREG Table_2).

    Table_2 contains Output per hour, Index UK=100 for ITL1 regions.
    Returns one dict per region (12 regions; England excluded as
    it is the baseline reference).
    """
    df = pd.read_excel(
        RAW_DIR / "prodbyreg.xlsx",
        sheet_name="Table_2",
        header=None,
    )

    # Row 5: region names; Row 17: 2007 data; Row 33: 2023 data
    regions = df.iloc[5, 1:].tolist()
    values_2007 = df.iloc[17, 1:].tolist()
    values_2023 = df.iloc[33, 1:].tolist()

    rows = []
    for region, v07, v23 in zip(regions, values_2007, values_2023):
        if region == "England":
            continue  # Baseline reference, not a region in our framework
        if region not in REGION_MAP:
            continue
        rows.append({
            "indicator_id": "regional_productivity_output_per_hour",
            "geography": REGION_MAP[region],
            "baseline_year": 2007,
            "baseline_value": round(float(v07), 2),
            "latest_year": 2023,
            "latest_value": round(float(v23), 2),
        })

    return rows


def build_regional_table() -> pd.DataFrame:
    """Build the populated regional productivity comparison table."""
    rows = process_regional_productivity()
    df = pd.DataFrame(rows)
    for col in PROCESSED_COLS:
        if col not in df.columns:
            df[col] = ""
    df["caveat"] = (
        "Output per hour, Index UK=100, ITL1 regions. "
        "Latest available 2023 (published June 2025). "
        "UK=100 baseline."
    )
    return df[PROCESSED_COLS]


# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------


def write_processed() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Process all indicators and write to data/processed/.

    Returns (national_df, regional_df).
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    national = build_national_table()
    regional = build_regional_table()

    national.to_csv(PROCESSED_DIR / "national_comparison_skeleton.csv", index=False)
    regional.to_csv(PROCESSED_DIR / "regional_productivity_skeleton.csv", index=False)

    return national, regional


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    national, regional = write_processed()

    print("National comparison table (4 indicators):")
    print(national[["indicator_id", "baseline_value", "latest_value"]].to_string(index=False))

    print(f"\nRegional productivity table ({len(regional)} regions):")
    print(regional[["geography", "baseline_value", "latest_value"]].to_string(index=False))

    print(f"\nWritten to:")
    print(f"  {PROCESSED_DIR / 'national_comparison_skeleton.csv'}")
    print(f"  {PROCESSED_DIR / 'regional_productivity_skeleton.csv'}")


if __name__ == "__main__":
    main()
