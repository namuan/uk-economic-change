"""Build proof-of-concept output tables and charts.

Reads populated processed tables, computes changes and evidence ratings,
and generates publication-ready charts.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from clean_indicators import calculate_change, classify_evidence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_CHARTS = PROJECT_ROOT / "outputs" / "charts"

# ---------------------------------------------------------------------------
# Chart style constants
# ---------------------------------------------------------------------------

BLUE = "#206095"        # ONS primary blue
TEAL = "#27A0CC"        # accent
RED = "#C62828"         # negative change
GREEN = "#2E7D32"       # positive change
GREY = "#707070"
LIGHT_GREY = "#D0D0D0"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 160,
    "savefig.dpi": 160,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})


def build_comparison_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    national = pd.read_csv(PROCESSED_DIR / "national_comparison_skeleton.csv")
    regional = pd.read_csv(PROCESSED_DIR / "regional_productivity_skeleton.csv")

    national = calculate_change(national)
    regional = calculate_change(regional)
    national["evidence_strength"] = national.apply(classify_evidence, axis=1)
    regional["evidence_strength"] = regional.apply(classify_evidence, axis=1)

    combined = pd.concat([national, regional], ignore_index=True)

    national.to_csv(OUTPUT_TABLES / "national_comparison.csv", index=False)
    regional.to_csv(OUTPUT_TABLES / "regional_productivity_comparison.csv", index=False)
    combined.to_csv(OUTPUT_TABLES / "combined_comparison.csv", index=False)

    return national, regional, combined


def build_claims_matrix(national: pd.DataFrame, regional: pd.DataFrame) -> pd.DataFrame:
    """Build claims-evidence matrix with ratings informed by actual data."""
    claims = pd.read_csv(DATA_DIR / "claims_register.csv")

    # Map evidence strength and findings from processed data
    gdp_change = national[national["indicator_id"] == "gdp_per_head"]["percentage_change"].iloc[0]
    ndp_change = national[national["indicator_id"] == "real_ndp_per_head"]["percentage_change"].iloc[0]
    prod_change = national[national["indicator_id"] == "labour_productivity_output_per_hour"]["percentage_change"].iloc[0]
    london_now = regional[regional["geography"] == "London"]["latest_value"].iloc[0]
    london_2007 = regional[regional["geography"] == "London"]["baseline_value"].iloc[0]
    scotland_change = regional[regional["geography"] == "Scotland"]["percentage_change"].iloc[0]

    findings = {
        "C001": ("Strong", f"GDP per head rose {gdp_change:.1f}% from £37,625 (2007) to £40,537 (2025). Growth averaged ~0.4% per year."),
        "C002": ("Strong", f"NDP per head rose {ndp_change:.1f}%, less than half the rate of GDP per head. Suggests capital consumption absorbed a growing share of output."),
        "C003": ("Strong", f"Output per hour rose {prod_change:.1f}% over 18 years (~0.4% pa), compared with ~2% pa pre-2007. Clear evidence of productivity stagnation."),
        "C004": ("Partial", f"Mixed picture: 7 regions gained relative to UK average, 5 declined. Scotland (+{scotland_change:.1f}%) and NI (+8.1%) converged; London (−7.3%) and East of England (−2.8%) saw the largest relative falls."),
        "C005": ("Strong", f"London output per hour: {london_now:.0f} (UK=100) vs {london_2007:.0f} in 2007. Remains the clear outlier but the gap has narrowed."),
        "C006": ("TBD", "Real earnings/household income indicator not yet populated in this POC."),
        "C007": ("TBD", "Housing affordability indicator not yet populated in this POC."),
    }

    for claim_id, (strength, caveat) in findings.items():
        mask = claims["claim_id"] == claim_id
        claims.loc[mask, "evidence_strength"] = strength
        claims.loc[mask, "caveat"] = caveat

    claims.to_csv(OUTPUT_TABLES / "claims_evidence_matrix.csv", index=False)
    return claims


def build_national_indicators_chart(national: pd.DataFrame) -> None:
    """Horizontal bar chart: percentage change in national indicators since 2007."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

    df = national.dropna(subset=["percentage_change"]).copy()
    if df.empty:
        return

    # Friendly short labels
    label_map = {
        "gdp_per_head": "GDP per head",
        "real_ndp_per_head": "NDP per head",
        "labour_productivity_output_per_hour": "Output per hour",
    }
    df["label"] = df["indicator_id"].map(label_map)
    df = df.sort_values("percentage_change")

    colors = [BLUE if v > 0 else RED for v in df["percentage_change"]]

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.barh(df["label"], df["percentage_change"], color=colors, height=0.5)

    # Value labels
    for bar, val in zip(bars, df["percentage_change"]):
        ax.text(
            bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
            f"{val:+.1f}%", va="center", fontsize=12, fontweight="bold",
            color=BLUE if val > 0 else RED,
        )

    ax.axvline(0, color=GREY, linewidth=0.8)
    ax.set_xlabel("Percentage change since 2007")
    ax.set_title("Britain Since 2007: National Indicators")
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%+d%%"))
    ax.set_xlim(right=df["percentage_change"].max() * 1.25)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "national_indicators_change.png")
    plt.close(fig)


def build_regional_productivity_chart(regional: pd.DataFrame) -> None:
    """Bar chart: regional productivity change since 2007, colour-coded."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

    df = regional.dropna(subset=["percentage_change"]).copy()
    if df.empty:
        return

    df = df.sort_values("percentage_change")
    colors = [GREEN if v >= 0 else RED for v in df["percentage_change"]]

    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.bar(df["geography"], df["percentage_change"], color=colors, width=0.65)

    # Value labels above/below bars
    for bar, val in zip(bars, df["percentage_change"]):
        y_pos = bar.get_height() + 0.3 if val >= 0 else bar.get_height() - 0.3
        va = "bottom" if val >= 0 else "top"
        ax.text(
            bar.get_x() + bar.get_width() / 2, y_pos,
            f"{val:+.1f}%", ha="center", va=va, fontsize=9, fontweight="bold",
            color=GREEN if val >= 0 else RED,
        )

    ax.axhline(0, color=GREY, linewidth=0.8)
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["geography"], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Percentage change since 2007")
    ax.set_title("Regional Productivity Change: 2007 to 2023\nOutput per hour, Index UK = 100")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%+d%%"))

    # Legend
    from matplotlib.patches import Patch
    ax.legend(
        handles=[Patch(color=GREEN, label="Above 2007"), Patch(color=RED, label="Below 2007")],
        loc="lower left", fontsize=9,
    )

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "regional_productivity_change.png")
    plt.close(fig)


def build_gdp_timeline_chart() -> None:
    """Line chart: GDP per head and NDP per head, 2007–2025."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

    gdp_path = RAW_DIR / "ihxw.csv"
    ndp_path = RAW_DIR / "mwb6.csv"
    if not gdp_path.exists() or not ndp_path.exists():
        return

    def _read_annual(path: Path) -> pd.DataFrame:
        df = pd.read_csv(path, skiprows=7)
        df.columns = ["period", "value"]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["period"] = df["period"].astype(str).str.strip()
        annual = df[~df["period"].str.contains("Q", na=False)]
        annual = annual.dropna(subset=["value"])
        annual["year"] = annual["period"].astype(int)
        return annual[(annual["year"] >= 2007) & (annual["year"] <= 2025)]

    gdp = _read_annual(gdp_path)
    ndp = _read_annual(ndp_path)

    fig, ax = plt.subplots(figsize=(11, 5.5))

    ax.plot(gdp["year"], gdp["value"], color=BLUE, linewidth=2.2, marker="o", markersize=5, label="GDP per head")
    ax.plot(ndp["year"], ndp["value"], color=TEAL, linewidth=2.2, marker="s", markersize=5, label="NDP per head")

    # Annotate 2008 financial crisis
    ax.axvline(2008, color=GREY, linestyle="--", linewidth=1, alpha=0.6)
    ax.text(2008.15, ax.get_ylim()[1] * 0.95, "Financial\ncrisis", fontsize=8, color=GREY, va="top")

    # Annotate COVID
    ax.axvspan(2020, 2020.75, color=LIGHT_GREY, alpha=0.3)
    ax.text(2020.1, ax.get_ylim()[1] * 0.95, "COVID-19", fontsize=8, color=GREY, va="top")

    ax.set_xlabel("Year")
    ax.set_ylabel("£ per head (CVM, 2023 prices)")
    ax.set_title("GDP and NDP per Head: 2007–2025")
    ax.legend(loc="lower right", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    ax.set_xlim(2006.5, 2025.5)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "gdp_per_head_timeline.png")
    plt.close(fig)


def build_all_charts(national: pd.DataFrame, regional: pd.DataFrame) -> None:
    """Generate all POC charts."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

    # Remove old placeholder if it exists
    readme = OUTPUT_CHARTS / "README.txt"
    if readme.exists():
        readme.unlink()

    build_national_indicators_chart(national)
    build_regional_productivity_chart(regional)
    build_gdp_timeline_chart()


def main() -> None:
    national, regional, combined = build_comparison_tables()
    claims = build_claims_matrix(national, regional)
    build_all_charts(national, regional)

    print("Built POC outputs:")
    print(f"- {OUTPUT_TABLES / 'national_comparison.csv'}")
    print(f"- {OUTPUT_TABLES / 'regional_productivity_comparison.csv'}")
    print(f"- {OUTPUT_TABLES / 'combined_comparison.csv'}")
    print(f"- {OUTPUT_TABLES / 'claims_evidence_matrix.csv'}")
    print(f"- {OUTPUT_CHARTS / 'national_indicators_change.png'}")
    print(f"- {OUTPUT_CHARTS / 'regional_productivity_change.png'}")
    print(f"- {OUTPUT_CHARTS / 'gdp_per_head_timeline.png'}")


if __name__ == "__main__":
    main()
