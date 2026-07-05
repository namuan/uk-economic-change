"""Quality assurance checks for the UK Economic Change framework.

Validates indicator register integrity, data completeness, calculation
correctness, and output file generation. Run with:

    uv run python src/qa_checks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_CHARTS = PROJECT_ROOT / "outputs" / "charts"

# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}  — {detail}")


# ---------------------------------------------------------------------------
# 1. Indicator register integrity
# ---------------------------------------------------------------------------

def test_indicator_register() -> None:
    print("\n── Indicator register ──")
    df = pd.read_csv(DATA_DIR / "indicator_register.csv")

    check("indicator_id values are unique",
          df["indicator_id"].is_unique,
          f"Duplicates: {df['indicator_id'][df['indicator_id'].duplicated()].tolist()}")

    required_cols = ["indicator_id", "indicator_name", "domain",
                     "source_owner", "source_url", "dataset_id",
                     "series_code", "geography_level", "unit",
                     "baseline_year_available", "latest_year_available",
                     "update_frequency", "comparability_status", "priority"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    check("Required columns present",
          len(missing_cols) == 0,
          f"Missing: {missing_cols}")

    check("No missing indicator_id values",
          df["indicator_id"].notna().all(),
          f"Missing in rows: {df[df['indicator_id'].isna()].index.tolist()}")

    check("No missing baseline_year_available values",
          df["baseline_year_available"].notna().all())

    check("All available baseline years are 2007",
          (df["baseline_year_available"].astype(str).str.strip() == "2007").all(),
          f"Non-2007: {df[df['baseline_year_available'].astype(str).str.strip() != '2007']['indicator_id'].tolist()}")

    check("Priority indicators are 1, 2, or 3",
          df["priority"].dropna().astype(str).isin(["1", "2", "3"]).all(),
          f"Values: {df['priority'].dropna().tolist()}")

    # Source URLs for priority indicators must be valid (non-TBD)
    priority = df[df["priority"].isin([1, 2])]
    tbd_urls = priority[priority["source_url"].astype(str).str.contains("TBD", na=False)]
    check("Priority indicators have confirmed source URLs",
          len(tbd_urls) == 0,
          f"TBD sources: {tbd_urls['indicator_id'].tolist()}")

    # Expanded fields
    valid_domains = {"Economy", "Productivity", "Wages", "Housing", "Public Services", ""}
    check("Domain values are valid",
          df["domain"].isin(valid_domains).all(),
          f"Invalid: {df[~df['domain'].isin(valid_domains)]['domain'].tolist()}")

    check("Series codes populated for priority indicators",
          priority["series_code"].notna().all())

    valid_comparability = {"OK", "OK (methodology note)", "partial", "methodology break", "TBD"}
    check("Comparability status values are valid",
          df["comparability_status"].astype(str).isin(valid_comparability).all())

    valid_frequency = {"Monthly", "Quarterly", "Annual", "TBD"}
    check("Update frequency values are valid",
          df["update_frequency"].astype(str).isin(valid_frequency).all())


# ---------------------------------------------------------------------------
# 2. Processed data completeness
# ---------------------------------------------------------------------------

def test_processed_data() -> None:
    print("\n── Processed data ──")
    national = pd.read_csv(PROCESSED_DIR / "national_comparison_skeleton.csv")
    regional = pd.read_csv(PROCESSED_DIR / "regional_productivity_skeleton.csv")

    check("National table has 6 rows",
          len(national) == 6,
          f"Got {len(national)}")

    check("Regional table has 12 rows",
          len(regional) == 12,
          f"Got {len(regional)}")

    # All rows should have populated baseline and latest values
    for label, df in [("national", national), ("regional", regional)]:
        check(f"{label}: baseline_value populated for all rows",
              df["baseline_value"].notna().all(),
              f"Missing in: {df[df['baseline_value'].isna()]['indicator_id'].tolist() if 'indicator_id' in df.columns else df[df['baseline_value'].isna()].index.tolist()}")

        check(f"{label}: latest_value populated for all rows",
              df["latest_value"].notna().all())

        check(f"{label}: baseline_year populated for all rows",
              df["baseline_year"].notna().all())

        check(f"{label}: latest_year populated for all rows",
              df["latest_year"].notna().all())

    # National indicators baseline year should be 2007
    check("National baseline year is 2007",
          (national["baseline_year"] == 2007).all())

    # Regional baseline year should be 2007
    check("Regional baseline year is 2007",
          (regional["baseline_year"] == 2007).all())

    # Numeric checks
    for label, df in [("national", national), ("regional", regional)]:
        check(f"{label}: baseline_value can be parsed as numeric",
              pd.to_numeric(df["baseline_value"], errors="coerce").notna().all())
        check(f"{label}: latest_value can be parsed as numeric",
              pd.to_numeric(df["latest_value"], errors="coerce").notna().all())

    # No dividing by zero in percentage calculations
    zero_baseline = pd.to_numeric(national["baseline_value"], errors="coerce") == 0
    check("No zero baseline values in national table",
          not zero_baseline.any())

    zero_baseline_r = pd.to_numeric(regional["baseline_value"], errors="coerce") == 0
    check("No zero baseline values in regional table",
          not zero_baseline_r.any())


def test_long_format() -> None:
    """Validate the long-format analytical dataset."""
    print("\n── Long-format dataset ──")
    path = PROCESSED_DIR / "long_format.csv"
    check("long_format.csv exists", path.exists())
    if not path.exists():
        return

    df = pd.read_csv(path)

    required_cols = ["indicator_id", "indicator_name", "domain",
                     "geography_code", "geography_name", "geography_type",
                     "period_type", "period", "year",
                     "value", "unit", "source_url", "quality_flag"]
    missing = [c for c in required_cols if c not in df.columns]
    check("All required columns present", len(missing) == 0, f"Missing: {missing}")

    check("Dataset is not empty", len(df) > 0)
    check("At least 300 rows (national + regional time series)",
          len(df) >= 300, f"Got {len(df)}")

    check("All values are numeric",
          pd.to_numeric(df["value"], errors="coerce").notna().all())

    check("No missing indicator_id", df["indicator_id"].notna().all())
    check("No missing geography_name", df["geography_name"].notna().all())
    check("No missing year", df["year"].notna().all())

    check("All quality flags are OK",
          (df["quality_flag"] == "OK").all(),
          f"Non-OK: {df[df['quality_flag'] != 'OK']['quality_flag'].unique().tolist()}")

    register = pd.read_csv(DATA_DIR / "indicator_register.csv")
    valid_ids = set(register["indicator_id"])
    dataset_ids = set(df["indicator_id"].unique())
    orphan = dataset_ids - valid_ids
    check("All indicator_ids exist in register",
          len(orphan) == 0, f"Orphan: {orphan}")

    valid_geo_codes = {"K02000001", "E12000001", "E12000002", "E12000003",
                       "E12000004", "E12000005", "E12000006", "E12000007",
                       "E12000008", "E12000009", "W92000004", "S92000003",
                       "N92000002"}
    dataset_geo = set(df["geography_code"].unique())
    invalid_geo = dataset_geo - valid_geo_codes
    check("All geography codes are valid ONS codes",
          len(invalid_geo) == 0, f"Invalid: {invalid_geo}")

    check("geography_type is national or region",
          df["geography_type"].isin(["national", "region"]).all())

    check("period_type is annual", (df["period_type"] == "annual").all())

    gdp_2007 = df[(df["indicator_id"] == "gdp_per_head") & (df["year"] == 2007)]
    if not gdp_2007.empty:
        check("Spot-check: GDP per head 2007 = 37625",
              abs(float(gdp_2007["value"].iloc[0]) - 37625) < 1,
              f"Got {gdp_2007['value'].iloc[0]}")

    lon_2007 = df[(df["geography_name"] == "London") & (df["year"] == 2007)]
    if not lon_2007.empty:
        check("Spot-check: London 2007 ≈ 139",
              abs(float(lon_2007["value"].iloc[0]) - 138.66) < 1)


# ---------------------------------------------------------------------------
# 3. Output table integrity
# ---------------------------------------------------------------------------

def test_output_tables() -> None:
    print("\n── Output tables ──")
    expected_tables = [
        "national_comparison.csv",
        "regional_productivity_comparison.csv",
        "combined_comparison.csv",
        "claims_evidence_matrix.csv",
        "growth_rate_comparison.csv",
    ]

    for table in expected_tables:
        path = OUTPUT_TABLES / table
        exists = path.exists()
        check(f"{table} exists", exists, f"Missing: {path}")

        if exists:
            df = pd.read_csv(path)
            check(f"{table} is not empty", len(df) > 0, f"0 rows")

    # Combined table should have national + regional rows
    combined = pd.read_csv(OUTPUT_TABLES / "combined_comparison.csv")
    national = pd.read_csv(OUTPUT_TABLES / "national_comparison.csv")
    regional = pd.read_csv(OUTPUT_TABLES / "regional_productivity_comparison.csv")
    check("Combined table row count = national + regional",
          len(combined) == len(national) + len(regional),
          f"Expected {len(national) + len(regional)}, got {len(combined)}")

    # All output tables should have calculated columns
    for label, df in [("national", national), ("regional", regional)]:
        for col in ["absolute_change", "percentage_change", "evidence_strength"]:
            check(f"{label}: {col} column exists",
                  col in df.columns)
            if col in df.columns:
                check(f"{label}: {col} is populated",
                      df[col].notna().any())

    # No evidence_strength should be "TBD" in populated tables
    tbd_national = national[national["evidence_strength"].str.contains("TBD", na=False)]
    check("National table: no TBD evidence ratings",
          len(tbd_national) == 0,
          f"TBD in: {tbd_national['indicator_id'].tolist()}")

    # Claims matrix should have evidence ratings
    claims = pd.read_csv(OUTPUT_TABLES / "claims_evidence_matrix.csv")
    rated = claims[~claims["evidence_strength"].str.contains("TBD", na=False)]
    tbd_claims = claims[claims["evidence_strength"].str.contains("TBD", na=False)]
    check(f"Claims matrix: {len(rated)}/{len(claims)} claims rated (non-TBD)",
          len(rated) >= 8,
          f"Only {len(rated)} rated, {len(tbd_claims)} TBD")

    growth = pd.read_csv(OUTPUT_TABLES / "growth_rate_comparison.csv")
    check("Growth-rate comparison has 2 rows",
          len(growth) == 2,
          f"Got {len(growth)}")
    check("Growth-rate comparison has pre/post CAGR columns",
          {"pre_2007_cagr_pct", "post_2007_cagr_pct", "slowdown_pct_points"}.issubset(growth.columns))
    check("Growth-rate comparison shows post-2007 slowdown",
          (growth["slowdown_pct_points"] < 0).all())


# ---------------------------------------------------------------------------
# 4. Chart generation
# ---------------------------------------------------------------------------

def test_charts() -> None:
    print("\n── Charts ──")
    expected_charts = [
        "national_indicators_change.png",
        "regional_productivity_change.png",
        "regional_ranking.png",
        "gdp_per_head_timeline.png",
        "productivity_timeline.png",
        "regional_productivity_small_multiples.png",
        "housing_affordability_timeline.png",
        "nhs_waiting_list_timeline.png",
        "growth_rate_comparison.png",
    ]

    for chart in expected_charts:
        path = OUTPUT_CHARTS / chart
        exists = path.exists()
        check(f"{chart} exists", exists)
        if exists:
            size = path.stat().st_size
            check(f"{chart} has content (>10KB)", size > 10_000,
                  f"Only {size:,} bytes — likely empty or corrupt")


# ---------------------------------------------------------------------------
# 5. Claims register integrity
# ---------------------------------------------------------------------------

def test_claims_register() -> None:
    print("\n── Claims register ──")
    df = pd.read_csv(DATA_DIR / "claims_register.csv")

    check("claim_id values are unique",
          df["claim_id"].is_unique)

    check("All claims have a primary_indicator_id",
          df["primary_indicator_id"].notna().all())

    # Each claim should reference an indicator that exists
    indicators = pd.read_csv(DATA_DIR / "indicator_register.csv")
    valid_ids = set(indicators["indicator_id"])
    claim_refs = set(df["primary_indicator_id"])
    orphan_refs = claim_refs - valid_ids
    check("All claim indicator references are valid",
          len(orphan_refs) == 0,
          f"Orphan refs: {orphan_refs}")


# ---------------------------------------------------------------------------
# 6. Calculation correctness (spot-check)
# ---------------------------------------------------------------------------

def test_calculations() -> None:
    print("\n── Calculation spot-checks ──")
    national = pd.read_csv(OUTPUT_TABLES / "national_comparison.csv")

    for _, row in national.iterrows():
        baseline = float(row["baseline_value"])
        latest = float(row["latest_value"])
        expected_abs = latest - baseline
        expected_pct = (expected_abs / baseline) * 100 if baseline != 0 else 0
        actual_abs = float(row["absolute_change"])
        actual_pct = float(row["percentage_change"])

        check(f"{row['indicator_id']}: absolute_change correct",
              abs(actual_abs - expected_abs) < 0.01,
              f"Expected {expected_abs:.2f}, got {actual_abs:.2f}")
        check(f"{row['indicator_id']}: percentage_change correct",
              abs(actual_pct - expected_pct) < 0.01,
              f"Expected {expected_pct:.2f}%, got {actual_pct:.2f}%")

    # Spot-check one regional value
    regional = pd.read_csv(OUTPUT_TABLES / "regional_productivity_comparison.csv")
    london = regional[regional["geography"] == "London"].iloc[0]
    check("London absolute change is negative",
          float(london["absolute_change"]) < 0)


# ---------------------------------------------------------------------------
# 7. Source data availability
# ---------------------------------------------------------------------------

def test_raw_data() -> None:
    print("\n── Raw data availability ──")
    raw_dir = DATA_DIR / "raw"

    raw_files = {
        "ihxw.csv": "GDP per head",
        "mwb6.csv": "NDP per head",
        "prdy.csv": "Labour productivity",
        "prodbyreg.xlsx": "Regional productivity",
        "kab9_awe.csv": "Nominal AWE",
        "d7bt_cpi.csv": "CPI index",
        "housing_affordability.xlsx": "Housing affordability",
        "nhs_waiting_list.csv": "NHS waiting list",
    }

    for filename, label in raw_files.items():
        path = raw_dir / filename
        exists = path.exists()
        if exists:
            size = path.stat().st_size
            check(f"{label} ({filename}) — {size:,} bytes",
                  size > 500,
                  f"File too small: {size} bytes")
        else:
            # Raw data is optional (may be gitignored). Warn, don't fail.
            print(f"  ⚠️  {label} ({filename}) — not found (run make fetch)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 55)
    print("UK Economic Change — QA Checks")
    print("=" * 55)

    test_indicator_register()
    test_raw_data()
    test_processed_data()
    test_long_format()
    test_calculations()
    test_output_tables()
    test_charts()
    test_claims_register()

    print(f"\n{'=' * 55}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed > 0:
        print("❌ Some checks failed — review the details above.")
    else:
        print("✅ All checks passed.")
    print("=" * 55)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
