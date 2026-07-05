"""Build proof-of-concept output tables and charts.

Reads populated processed tables, computes changes and evidence ratings,
and generates publication-ready charts.
"""

from __future__ import annotations

import zipfile
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
    earnings_change = national[national["indicator_id"] == "real_earnings"]["percentage_change"].iloc[0]
    housing_raw = national[national["indicator_id"] == "housing_affordability"]
    housing_change = housing_raw["percentage_change"].iloc[0] if not housing_raw.empty else 0
    housing_2007 = housing_raw["baseline_value"].iloc[0] if not housing_raw.empty else 0
    housing_2025 = housing_raw["latest_value"].iloc[0] if not housing_raw.empty else 0
    nhs_raw = national[national["indicator_id"] == "nhs_waiting_list"]
    nhs_change = nhs_raw["percentage_change"].iloc[0] if not nhs_raw.empty else 0
    nhs_2007 = nhs_raw["baseline_value"].iloc[0] if not nhs_raw.empty else 0
    nhs_latest = nhs_raw["latest_value"].iloc[0] if not nhs_raw.empty else 0
    pse_raw = national[national["indicator_id"] == "public_sector_employment"]
    pse_change = pse_raw["percentage_change"].iloc[0] if not pse_raw.empty else 0
    pse_2007 = pse_raw["baseline_value"].iloc[0] if not pse_raw.empty else 0
    pse_latest = pse_raw["latest_value"].iloc[0] if not pse_raw.empty else 0
    london_now = regional[regional["geography"] == "London"]["latest_value"].iloc[0]
    london_2007 = regional[regional["geography"] == "London"]["baseline_value"].iloc[0]
    scotland_change = regional[regional["geography"] == "Scotland"]["percentage_change"].iloc[0]

    findings = {
        "C001": ("Strong", f"GDP per head rose {gdp_change:.1f}% from £37,625 (2007) to £40,537 (2025). Growth averaged ~0.4% per year."),
        "C002": ("Strong", f"NDP per head rose {ndp_change:.1f}%, less than half the rate of GDP per head. Suggests capital consumption absorbed a growing share of output."),
        "C003": ("Strong", f"Output per hour rose {prod_change:.1f}% over 18 years (~0.4% pa), compared with ~2% pa pre-2007. Clear evidence of productivity stagnation."),
        "C004": ("Partial", f"Mixed picture: 7 regions gained relative to UK average, 5 declined. Scotland (+{scotland_change:.1f}%) and NI (+8.1%) converged; London (−7.3%) and East of England (−2.8%) saw the largest relative falls."),
        "C005": ("Strong", f"London output per hour: {london_now:.0f} (UK=100) vs {london_2007:.0f} in 2007. Remains the clear outlier but the gap has narrowed."),
        "C006": ("Strong", f"Real earnings (CPI-deflated AWE) rose only {earnings_change:.1f}% since 2007, compared with GDP per head growth of {gdp_change:.1f}%. Living standards, as measured by real pay, have barely improved."),
        "C007": ("Partial", f"Median house price to earnings ratio rose from {housing_2007:.1f} (2007) to {housing_2025:.1f} (2025), but peaked at 8.95 in 2021 before declining. The 5-year average of 8.19 confirms sustained pressure above 2007 levels, though the endpoint comparison alone understates the deterioration experienced during 2015–2023."),
        "C008": ("Strong", f"NHS England waiting list rose from {nhs_2007/1e6:.2f}M (Aug 2007) to {nhs_latest/1e6:.2f}M (Mar 2026), an increase of {nhs_change:.0f}%. The post-2020 COVID backlog accounts for much of the increase, but the pre-COVID trend was already upward (2.4M in 2010 to 4.2M in 2020)."),
        "C010": ("Partial", f"Public sector employment rose from {pse_2007/1000:.2f}M in 2007 to {pse_latest/1000:.2f}M in 2025, an increase of {pse_latest - pse_2007:.0f} thousand ({pse_change:.1f}%). The public sector share of total employment fell from 20.5% to 18.0%, so headcount grew but the sector shrank as a share of employment."),
    }

    for claim_id, (strength, caveat) in findings.items():
        mask = claims["claim_id"] == claim_id
        claims.loc[mask, "evidence_strength"] = strength
        claims.loc[mask, "caveat"] = caveat

    claims.to_csv(OUTPUT_TABLES / "claims_evidence_matrix.csv", index=False)
    return claims


def _read_prdy_output_per_hour() -> pd.DataFrame:
    """Read annual UK output per hour from the ONS PRDY file."""
    df = pd.read_csv(
        RAW_DIR / "prdy.csv",
        header=0,
        skiprows=lambda x: x in [1, 2, 3, 4, 5, 6],
    )
    cols = list(df.columns)
    cols[0] = "period"
    df.columns = cols

    target = "UK Whole Economy: Output per hour worked SA: Index 2023 = 100"
    series = pd.DataFrame({
        "period": df["period"].astype(str).str.strip(),
        "value": pd.to_numeric(df[target], errors="coerce"),
    })
    annual = series[series["period"].str.match(r"^\d{4}$", na=False) & series["value"].notna()].copy()
    annual["year"] = annual["period"].astype(int)
    return annual[["year", "value"]].sort_values("year")


def _read_ons_annual(path: Path) -> pd.DataFrame:
    """Read annual rows from an ONS generator CSV."""
    df = pd.read_csv(path, skiprows=7)
    df.columns = ["period", "value"]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["period"] = df["period"].astype(str).str.strip()
    annual = df[df["period"].str.match(r"^\d{4}$", na=False) & df["value"].notna()].copy()
    annual["year"] = annual["period"].astype(int)
    return annual[["year", "value"]].sort_values("year")


def _calculate_cagr(series: pd.DataFrame, start_year: int, end_year: int) -> float:
    start = float(series.loc[series["year"] == start_year, "value"].iloc[0])
    end = float(series.loc[series["year"] == end_year, "value"].iloc[0])
    years = end_year - start_year
    return ((end / start) ** (1 / years) - 1) * 100


def build_growth_rate_table() -> pd.DataFrame:
    """Compare pre- and post-2007 annual growth rates for key indicators."""
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    specs = [
        ("gdp_per_head", "GDP per head", _read_ons_annual(RAW_DIR / "ihxw.csv"), 1997, 2007, 2025),
        ("labour_productivity_output_per_hour", "Output per hour", _read_prdy_output_per_hour(), 1997, 2007, 2025),
    ]

    rows = []
    for indicator_id, label, series, pre_start, baseline, latest in specs:
        rows.append({
            "indicator_id": indicator_id,
            "indicator": label,
            "pre_period": f"{pre_start}-{baseline}",
            "post_period": f"{baseline}-{latest}",
            "pre_2007_cagr_pct": round(_calculate_cagr(series, pre_start, baseline), 2),
            "post_2007_cagr_pct": round(_calculate_cagr(series, baseline, latest), 2),
            "slowdown_pct_points": round(
                _calculate_cagr(series, baseline, latest) - _calculate_cagr(series, pre_start, baseline), 2
            ),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_TABLES / "growth_rate_comparison.csv", index=False)
    return df


def read_ae_four_hour_performance() -> pd.DataFrame:
    """Read NHS England monthly A&E four-hour performance time series."""
    path = RAW_DIR / "ae_monthly_timeseries.xls"
    df = pd.read_excel(path, sheet_name="Performance", header=13)
    df = df[pd.to_datetime(df["Period"], errors="coerce").notna()].copy()
    df["date"] = pd.to_datetime(df["Period"])
    df["year"] = df["date"].dt.year
    df["percentage_within_4h"] = pd.to_numeric(
        df["Percentage in 4 hours or less (all)"], errors="coerce"
    ) * 100
    df = df.dropna(subset=["percentage_within_4h"])
    return df[["date", "year", "percentage_within_4h"]].sort_values("date")


def build_public_service_extension_table() -> pd.DataFrame:
    """Build Phase 5 public-service extension table."""
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    ae = read_ae_four_hour_performance()
    annual = ae.groupby("year", as_index=False)["percentage_within_4h"].mean()
    baseline_year = 2011
    latest_year = 2025
    baseline = float(annual.loc[annual["year"] == baseline_year, "percentage_within_4h"].iloc[0])
    latest = float(annual.loc[annual["year"] == latest_year, "percentage_within_4h"].iloc[0])

    rows = [{
        "indicator_id": "ae_four_hour_performance",
        "indicator": "A&E attendances within 4 hours",
        "geography": "England",
        "baseline_period": baseline_year,
        "baseline_value": round(baseline, 1),
        "latest_period": latest_year,
        "latest_value": round(latest, 1),
        "absolute_change": round(latest - baseline, 1),
        "unit": "percentage points",
        "evidence_strength": "Partial",
        "caveat": "Nearest defensible annual baseline is 2011. Pre-June 2015 monthly values are estimated from weekly data. Four-hour performance from May 2019 to May 2023 excludes clinical standards field-test trusts.",
    }]
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_TABLES / "public_service_extension.csv", index=False)
    return df


def read_world_bank_gdp_per_capita() -> pd.DataFrame:
    """Read World Bank GDP per capita data for the Phase 7 peer group."""
    path = RAW_DIR / "world_bank_gdp_per_capita.zip"
    with zipfile.ZipFile(path) as zf:
        data_name = next(name for name in zf.namelist() if name.startswith("API_NY.GDP.PCAP.KD") and name.endswith(".csv"))
        with zf.open(data_name) as f:
            wide = pd.read_csv(f, skiprows=4)

    peer_order = {
        "GBR": "United Kingdom",
        "USA": "United States",
        "DEU": "Germany",
        "FRA": "France",
        "ITA": "Italy",
        "CAN": "Canada",
    }
    wide = wide[wide["Country Code"].isin(peer_order)].copy()
    year_cols = [col for col in wide.columns if str(col).isdigit()]
    df = wide.melt(
        id_vars=["Country Code"],
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    ).rename(columns={"Country Code": "country_code"})
    df = df.dropna(subset=["value"])
    df["year"] = df["year"].astype(int)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["country"] = df["country_code"].map(peer_order)
    return df.sort_values(["country", "year"])


def build_international_gdp_per_capita_table() -> pd.DataFrame:
    """Build Phase 7 international GDP per capita comparison table."""
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    df = read_world_bank_gdp_per_capita()
    baseline_year = 2007
    latest_year = int(
        df[df["year"] > baseline_year]
        .dropna(subset=["value"])
        .groupby("year")["country_code"]
        .nunique()
        .loc[lambda s: s == 6]
        .index.max()
    )

    rows = []
    for country_code, group in df.groupby("country_code"):
        baseline = float(group.loc[group["year"] == baseline_year, "value"].iloc[0])
        latest = float(group.loc[group["year"] == latest_year, "value"].iloc[0])
        absolute = latest - baseline
        percentage = (absolute / baseline) * 100
        cagr = ((latest / baseline) ** (1 / (latest_year - baseline_year)) - 1) * 100
        rows.append({
            "indicator_id": "international_gdp_per_capita",
            "country": group["country"].iloc[0],
            "country_code": country_code,
            "baseline_year": baseline_year,
            "baseline_value": round(baseline, 0),
            "latest_year": latest_year,
            "latest_value": round(latest, 0),
            "absolute_change": round(absolute, 0),
            "percentage_change": round(percentage, 1),
            "cagr_pct": round(cagr, 2),
            "unit": "constant 2015 US dollars per person",
            "source": "World Bank NY.GDP.PCAP.KD",
        })

    out = pd.DataFrame(rows).sort_values("percentage_change", ascending=False)
    out.to_csv(OUTPUT_TABLES / "international_gdp_per_capita_comparison.csv", index=False)
    return out


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
        "real_earnings": "Real earnings (AWE)",
        "housing_affordability": "House price / earnings",
        "nhs_waiting_list": "NHS waiting list",
        "public_sector_employment": "Public sector employment",
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


def build_productivity_timeline_chart() -> None:
    """Standalone line chart: UK output per hour, 1997–2025."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    if not (RAW_DIR / "prdy.csv").exists():
        return

    df = _read_prdy_output_per_hour()
    df = df[(df["year"] >= 1997) & (df["year"] <= 2025)].copy()
    if df.empty:
        return

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(df["year"], df["value"], color=BLUE, linewidth=2.4, marker="o", markersize=4)
    ax.axvline(2007, color=GREY, linestyle="--", linewidth=1)
    ax.text(2007.2, ax.get_ylim()[1] * 0.98, "2007 baseline", fontsize=9, color=GREY, va="top")
    ax.axvspan(2020, 2020.75, color=LIGHT_GREY, alpha=0.3)
    ax.text(2020.1, ax.get_ylim()[1] * 0.98, "COVID-19", fontsize=9, color=GREY, va="top")
    ax.set_xlabel("Year")
    ax.set_ylabel("Output per hour (Index 2023 = 100)")
    ax.set_title("UK Productivity Has Barely Grown Since 2007")
    ax.set_xlim(1996.5, 2025.5)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "productivity_timeline.png")
    plt.close(fig)


def build_regional_productivity_small_multiples() -> None:
    """Small-multiple line chart: regional productivity paths, 2007–2023."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    long_path = PROCESSED_DIR / "long_format.csv"
    if not long_path.exists():
        return

    df = pd.read_csv(long_path)
    df = df[
        (df["indicator_id"] == "regional_productivity_output_per_hour")
        & (df["year"] >= 2007)
        & (df["year"] <= 2023)
    ].copy()
    if df.empty:
        return

    latest_order = (
        df[df["year"] == 2023]
        .sort_values("value", ascending=False)["geography_name"]
        .tolist()
    )
    fig, axes = plt.subplots(4, 3, figsize=(12, 10), sharex=True, sharey=True)
    axes = axes.flatten()

    for ax, region in zip(axes, latest_order):
        sub = df[df["geography_name"] == region].sort_values("year")
        latest = float(sub[sub["year"] == 2023]["value"].iloc[0])
        baseline = float(sub[sub["year"] == 2007]["value"].iloc[0])
        color = GREEN if latest >= baseline else RED
        ax.plot(sub["year"], sub["value"], color=color, linewidth=2)
        ax.axhline(100, color=LIGHT_GREY, linewidth=0.8)
        ax.set_title(region, fontsize=10, loc="left")
        ax.text(0.98, 0.08, f"{baseline:.0f} → {latest:.0f}", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=8, color=color)
        ax.tick_params(labelsize=8)

    for ax in axes[len(latest_order):]:
        ax.axis("off")

    fig.suptitle("Regional Productivity Paths: 2007–2023\nOutput per hour, UK = 100", fontsize=14, y=0.995)
    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "regional_productivity_small_multiples.png")
    plt.close(fig)


def build_housing_affordability_timeline_chart() -> None:
    """Line chart: house price to earnings ratio, England and Wales."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / "housing_affordability.xlsx"
    if not path.exists():
        return

    df = pd.read_excel(path, sheet_name="1c", header=1)
    row = df[df["Name"] == "England and Wales"].iloc[0]
    years = list(range(2007, 2026))
    values = [float(row[str(year)]) for year in years]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(years, values, color=BLUE, linewidth=2.4, marker="o", markersize=4)
    ax.axhline(values[0], color=GREY, linestyle="--", linewidth=1, label="2007 level")
    peak_idx = int(np.argmax(values))
    ax.scatter([years[peak_idx]], [values[peak_idx]], color=RED, zorder=3)
    ax.text(years[peak_idx] + 0.2, values[peak_idx], f"Peak: {values[peak_idx]:.2f}×", color=RED, fontsize=9)
    ax.set_xlabel("Year")
    ax.set_ylabel("House price to earnings ratio")
    ax.set_title("Housing Affordability Worsened Sharply Before a Partial Recovery")
    ax.set_xlim(2006.5, 2025.5)
    ax.legend(loc="upper left", fontsize=9)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "housing_affordability_timeline.png")
    plt.close(fig)


def build_nhs_waiting_list_timeline_chart() -> None:
    """Line chart: NHS England RTT incomplete pathways, 2007–2026."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / "nhs_waiting_list.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["period"] + "-01")
    df["value_millions"] = pd.to_numeric(df["value"], errors="coerce") / 1_000_000
    df = df.dropna(subset=["value_millions"])

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(df["date"], df["value_millions"], color=BLUE, linewidth=2.2)
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2021-03-01"), color=LIGHT_GREY, alpha=0.35)
    ax.text(pd.Timestamp("2020-04-01"), ax.get_ylim()[1] * 0.95, "COVID-19 shock", fontsize=9, color=GREY, va="top")
    peak = df.loc[df["value_millions"].idxmax()]
    ax.scatter([peak["date"]], [peak["value_millions"]], color=RED, zorder=3)
    ax.text(peak["date"], peak["value_millions"] + 0.15,
            f"Peak: {peak['value_millions']:.2f}M", color=RED, fontsize=9, ha="center")
    ax.set_xlabel("Year")
    ax.set_ylabel("Incomplete pathways (millions)")
    ax.set_title("NHS England Waiting List Pressure Rose Sharply After 2020")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1fM"))

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "nhs_waiting_list_timeline.png")
    plt.close(fig)


def build_ae_four_hour_performance_chart() -> None:
    """Line chart: A&E attendances within four hours, England."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / "ae_monthly_timeseries.xls"
    if not path.exists():
        return

    df = read_ae_four_hour_performance()
    if df.empty:
        return

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(df["date"], df["percentage_within_4h"], color=BLUE, linewidth=2.0)
    ax.axhline(95, color=GREY, linestyle="--", linewidth=1, label="95% operational standard")
    ax.axvspan(pd.Timestamp("2019-05-01"), pd.Timestamp("2023-05-01"), color=LIGHT_GREY, alpha=0.25)
    ax.text(pd.Timestamp("2019-07-01"), 98, "Clinical standards\nfield test", fontsize=8, color=GREY, va="top")
    ax.set_xlabel("Year")
    ax.set_ylabel("Attendances within 4 hours")
    ax.set_title("A&E Four-Hour Performance Has Fallen Since the Early 2010s")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.set_ylim(50, 100)
    ax.legend(loc="lower left", fontsize=9)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "ae_four_hour_performance_timeline.png")
    plt.close(fig)


def build_growth_rate_comparison_chart(growth_rates: pd.DataFrame) -> None:
    """Grouped bar chart comparing pre- and post-2007 CAGRs."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    if growth_rates.empty:
        return

    x = np.arange(len(growth_rates))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, growth_rates["pre_2007_cagr_pct"], width, color=LIGHT_GREY, label="1997–2007")
    ax.bar(x + width / 2, growth_rates["post_2007_cagr_pct"], width, color=BLUE, label="2007–2025")
    ax.set_xticks(x)
    ax.set_xticklabels(growth_rates["indicator"])
    ax.set_ylabel("Compound annual growth rate")
    ax.set_title("Growth Rates Collapsed After 2007")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.legend(fontsize=10)
    for i, row in growth_rates.iterrows():
        ax.text(i - width / 2, row["pre_2007_cagr_pct"] + 0.05, f"{row['pre_2007_cagr_pct']:.1f}%", ha="center", fontsize=9)
        ax.text(i + width / 2, row["post_2007_cagr_pct"] + 0.05, f"{row['post_2007_cagr_pct']:.1f}%", ha="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "growth_rate_comparison.png")
    plt.close(fig)


def build_international_gdp_per_capita_chart(international: pd.DataFrame) -> None:
    """Bar chart: peer-country GDP per capita growth since 2007."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    if international.empty:
        return

    df = international.sort_values("percentage_change").copy()
    colors = [BLUE if country == "United Kingdom" else LIGHT_GREY for country in df["country"]]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh(df["country"], df["percentage_change"], color=colors, height=0.55)
    for bar, value in zip(bars, df["percentage_change"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{value:+.1f}%", va="center", fontsize=10)

    ax.axvline(0, color=GREY, linewidth=0.8)
    ax.set_xlabel("Percentage change since 2007")
    ax.set_title("GDP per Capita Growth in Peer Countries")
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%+d%%"))
    ax.set_xlim(right=max(df["percentage_change"]) * 1.18)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "international_gdp_per_capita_comparison.png")
    plt.close(fig)


def build_regional_ranking_chart(regional: pd.DataFrame) -> None:
    """Side-by-side bar chart: regional productivity ranking, 2007 vs 2023."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

    df = regional.dropna(subset=["baseline_value", "latest_value"]).copy()
    if df.empty:
        return

    df = df.sort_values("latest_value")
    x = range(len(df))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh([i + width/2 for i in x], df["baseline_value"],
            width, color=LIGHT_GREY, label="2007")
    ax.barh([i - width/2 for i in x], df["latest_value"],
            width, color=BLUE, label="2023")

    ax.set_yticks(x)
    ax.set_yticklabels(df["geography"], fontsize=9)
    ax.axvline(100, color=GREY, linewidth=0.8, linestyle="--")
    ax.set_xlabel("Output per hour (UK = 100)")
    ax.set_title("Regional Productivity: 2007 vs 2023")
    ax.legend(loc="lower right", fontsize=10)

    fig.tight_layout()
    fig.savefig(OUTPUT_CHARTS / "regional_ranking.png")
    plt.close(fig)


def build_all_charts(national: pd.DataFrame, regional: pd.DataFrame, growth_rates: pd.DataFrame | None = None) -> None:
    """Generate all evidence-pack charts."""
    OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
    if growth_rates is None:
        growth_rates = build_growth_rate_table()

    # Remove old placeholder if it exists
    readme = OUTPUT_CHARTS / "README.txt"
    if readme.exists():
        readme.unlink()

    build_national_indicators_chart(national)
    build_regional_productivity_chart(regional)
    build_gdp_timeline_chart()
    build_regional_ranking_chart(regional)
    build_productivity_timeline_chart()
    build_regional_productivity_small_multiples()
    build_housing_affordability_timeline_chart()
    build_nhs_waiting_list_timeline_chart()
    build_ae_four_hour_performance_chart()
    build_growth_rate_comparison_chart(growth_rates)
    international_path = OUTPUT_TABLES / "international_gdp_per_capita_comparison.csv"
    if international_path.exists():
        build_international_gdp_per_capita_chart(pd.read_csv(international_path))


def main() -> None:
    national, regional, combined = build_comparison_tables()
    claims = build_claims_matrix(national, regional)
    growth_rates = build_growth_rate_table()
    public_service = build_public_service_extension_table()
    international = build_international_gdp_per_capita_table()
    build_all_charts(national, regional, growth_rates)

    print("Built evidence-pack outputs:")
    print(f"- {OUTPUT_TABLES / 'national_comparison.csv'}")
    print(f"- {OUTPUT_TABLES / 'regional_productivity_comparison.csv'}")
    print(f"- {OUTPUT_TABLES / 'combined_comparison.csv'}")
    print(f"- {OUTPUT_TABLES / 'claims_evidence_matrix.csv'}")
    print(f"- {OUTPUT_TABLES / 'growth_rate_comparison.csv'}")
    print(f"- {OUTPUT_TABLES / 'public_service_extension.csv'}")
    print(f"- {OUTPUT_TABLES / 'international_gdp_per_capita_comparison.csv'}")
    print(f"- {OUTPUT_CHARTS / 'national_indicators_change.png'}")
    print(f"- {OUTPUT_CHARTS / 'regional_productivity_change.png'}")
    print(f"- {OUTPUT_CHARTS / 'gdp_per_head_timeline.png'}")
    print(f"- {OUTPUT_CHARTS / 'regional_ranking.png'}")
    print(f"- {OUTPUT_CHARTS / 'productivity_timeline.png'}")
    print(f"- {OUTPUT_CHARTS / 'regional_productivity_small_multiples.png'}")
    print(f"- {OUTPUT_CHARTS / 'housing_affordability_timeline.png'}")
    print(f"- {OUTPUT_CHARTS / 'nhs_waiting_list_timeline.png'}")
    print(f"- {OUTPUT_CHARTS / 'ae_four_hour_performance_timeline.png'}")
    print(f"- {OUTPUT_CHARTS / 'growth_rate_comparison.png'}")
    print(f"- {OUTPUT_CHARTS / 'international_gdp_per_capita_comparison.png'}")


if __name__ == "__main__":
    main()
