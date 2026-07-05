"""
ONS data fetch helpers for the UK Economic Change POC.

Provides caching-aware download functions for each indicator, plus
general-purpose helpers for CSV/XLSX downloads from ONS sources.

All raw data is saved to data/raw/ for auditability and reproducibility.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class FetchResult:
    """Metadata about a single fetch operation."""

    indicator_id: str
    url: str
    path: Path
    status_code: int
    cached: bool = False
    error: Optional[str] = None


@dataclass
class FetchReport:
    """Aggregate report from fetch_all()."""

    results: list[FetchResult] = field(default_factory=list)

    @property
    def ok(self) -> int:
        return sum(1 for r in self.results if r.status_code == 200 and r.error is None)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.error is not None)

    @property
    def cached(self) -> int:
        return sum(1 for r in self.results if r.cached)

    def summary(self) -> str:
        lines = ["Fetch report:"]
        for r in self.results:
            status = "CACHED" if r.cached else f"HTTP {r.status_code}"
            if r.error:
                status = f"ERROR: {r.error}"
            lines.append(f"  [{status}] {r.indicator_id} → {r.path.name}")
        lines.append(
            f"  Total: {len(self.results)} | OK: {self.ok} | Cached: {self.cached} | Failed: {self.failed}"
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core download helpers
# ---------------------------------------------------------------------------


def _download(
    url: str, path: Path, timeout: int = 60
) -> tuple[int, Optional[str]]:
    """Download url to path. Returns (status_code, error_message_or_None)."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
        return response.status_code, None
    except requests.RequestException as exc:
        return getattr(exc.response, "status_code", 0), str(exc)


def _fetch(
    indicator_id: str,
    url: str,
    filename: str,
    *,
    force: bool = False,
    timeout: int = 60,
) -> FetchResult:
    """Generic fetch with caching.

    Args:
        indicator_id: Stable identifier for the indicator.
        url: Source URL to download.
        filename: Local filename in data/raw/.
        force: If True, re-download even if local file exists.
        timeout: Request timeout in seconds.

    Returns:
        FetchResult with metadata about the operation.
    """
    path = RAW_DIR / filename

    if path.exists() and not force:
        logger.info("Using cached %s → %s", indicator_id, filename)
        return FetchResult(
            indicator_id=indicator_id,
            url=url,
            path=path,
            status_code=200,
            cached=True,
        )

    logger.info("Downloading %s → %s", indicator_id, filename)
    status_code, error = _download(url, path, timeout=timeout)
    return FetchResult(
        indicator_id=indicator_id,
        url=url,
        path=path,
        status_code=status_code,
        cached=False,
        error=error,
    )


# ---------------------------------------------------------------------------
# Indicator-specific fetch functions
# ---------------------------------------------------------------------------

# --- National indicators ---

ONS_GENERATOR_BASE = "https://www.ons.gov.uk/generator"


def fetch_gdp_per_head(*, force: bool = False) -> FetchResult:
    """Download Real GDP per head (IHXW) from ONS time-series CSV generator.

    Source: UK Economic Accounts (UKEA), chained volume measure, 2023 prices.
    """
    return _fetch(
        indicator_id="gdp_per_head",
        url=f"{ONS_GENERATOR_BASE}?uri=/economy/grossdomesticproductgdp/timeseries/ihxw/ukea&format=csv",
        filename="ihxw.csv",
        force=force,
    )


def fetch_ndp_per_head(*, force: bool = False) -> FetchResult:
    """Download Real NDP per head (MWB6) from ONS time-series CSV generator.

    Source: UK Economic Accounts (UKEA), chained volume measure, 2023 prices.
    """
    return _fetch(
        indicator_id="real_ndp_per_head",
        url=f"{ONS_GENERATOR_BASE}?uri=/economy/grossdomesticproductgdp/timeseries/mwb6/ukea&format=csv",
        filename="mwb6.csv",
        force=force,
    )


ONS_FILE_BASE = "https://www.ons.gov.uk/file"


def fetch_labour_productivity(*, force: bool = False) -> FetchResult:
    """Download labour productivity dataset (PRDY) from ONS direct CSV.

    Contains UK Whole Economy output per hour worked (CDID: LZVB).
    """
    return _fetch(
        indicator_id="labour_productivity_output_per_hour",
        url=f"{ONS_FILE_BASE}?uri=/employmentandlabourmarket/peopleinwork/labourproductivity/datasets/labourproductivity/current/prdy.csv",
        filename="prdy.csv",
        force=force,
    )


def fetch_regional_productivity(*, force: bool = False) -> FetchResult:
    """Download regional labour productivity (PRODBYREG) from ONS XLSX.

    Table_2 contains Output per hour, Index UK=100 by ITL1 region.
    Latest available: 2023 (published June 2025).
    """
    return _fetch(
        indicator_id="regional_productivity_output_per_hour",
        url=f"{ONS_FILE_BASE}?uri=/economy/economicoutputandproductivity/productivitymeasures/datasets/annualregionallabourproductivity/1998to2023/prodbyregaccessiblefinal.xlsx",
        filename="prodbyreg.xlsx",
        force=force,
    )


def fetch_awe_nominal(*, force: bool = False) -> FetchResult:
    """Download nominal Average Weekly Earnings (KAB9) from ONS.

    Used as the base for computing real earnings (CPI-deflated).
    """
    return _fetch(
        indicator_id="real_earnings",
        url=f"{ONS_GENERATOR_BASE}?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/timeseries/kab9/lms&format=csv",
        filename="kab9_awe.csv",
        force=force,
    )


def fetch_cpi(*, force: bool = False) -> FetchResult:
    """Download CPI all-items index (D7BT) for deflating nominal earnings."""
    return _fetch(
        indicator_id="real_earnings",
        url=f"{ONS_GENERATOR_BASE}?uri=/economy/inflationandpriceindices/timeseries/d7bt/mm23&format=csv",
        filename="d7bt_cpi.csv",
        force=force,
    )


def fetch_housing_affordability(*, force: bool = False) -> FetchResult:
    """Download housing affordability ratios (house price to earnings).

    ONS dataset: Ratio of median house price to median gross annual
    workplace-based earnings, England and Wales, 1997–2025.
    """
    return _fetch(
        indicator_id="housing_affordability",
        url=f"{ONS_FILE_BASE}?uri=/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian/current/aff1ratioofhousepricetoworkplacebasedearnings.xlsx",
        filename="housing_affordability.xlsx",
        force=force,
    )


def fetch_public_sector_employment(*, force: bool = False) -> FetchResult:
    """Download ONS public sector employment time-series dataset.

    Used to test whether public sector employment has grown since 2007.
    """
    return _fetch(
        indicator_id="public_sector_employment",
        url=f"{ONS_FILE_BASE}?uri=/employmentandlabourmarket/peopleinwork/publicsectorpersonnel/datasets/publicsectoremploymenttimeseriesdataset/current/pse.csv",
        filename="pse.csv",
        force=force,
    )


def fetch_nhs_waiting_list(*, force: bool = False) -> FetchResult:
    """Verify NHS waiting list CSV is present (data committed to repo).

    NHS England RTT data is compiled from two sources:
    - NHS monthly Incomplete Commissioner files where available
    - NHS historical RTT time-series values for older periods not available
      through the current monthly pages

    Both are combined into data/raw/nhs_waiting_list.csv.
    """
    path = RAW_DIR / "nhs_waiting_list.csv"
    if path.exists():
        return FetchResult(
            indicator_id="nhs_waiting_list",
            url="compiled from NHS England RTT data",
            path=path,
            status_code=200,
            cached=True,
        )
    return FetchResult(
        indicator_id="nhs_waiting_list",
        url="compiled from NHS England RTT data",
        path=path,
        status_code=0,
        error="nhs_waiting_list.csv not found — run make fetch to restore",
    )


def fetch_ae_monthly_timeseries(*, force: bool = False) -> FetchResult:
    """Download NHS England A&E monthly time-series workbook.

    Used for the A&E four-hour performance extension indicator.
    """
    return _fetch(
        indicator_id="ae_four_hour_performance",
        url="https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/06/Monthly-AE-Time-Series-May-2026-wlgnE2.xls",
        filename="ae_monthly_timeseries.xls",
        force=force,
    )


def fetch_world_bank_gdp_per_capita(*, force: bool = False) -> FetchResult:
    """Download World Bank GDP per capita data for the Phase 7 peer group.

    Indicator: NY.GDP.PCAP.KD, GDP per capita in constant 2015 US dollars.
    Countries: UK, US, Germany, France, Italy and Canada.
    """
    return _fetch(
        indicator_id="international_gdp_per_capita",
        url="https://api.worldbank.org/v2/en/indicator/NY.GDP.PCAP.KD?downloadformat=csv",
        filename="world_bank_gdp_per_capita.zip",
        force=force,
        timeout=120,
    )


# ---------------------------------------------------------------------------
# Bulk fetch
# ---------------------------------------------------------------------------


def fetch_all(*, force: bool = False) -> FetchReport:
    """Download all indicator source files.

    Returns a FetchReport summarising results.
    """
    report = FetchReport()

    fetchers = [
        fetch_gdp_per_head,
        fetch_ndp_per_head,
        fetch_labour_productivity,
        fetch_regional_productivity,
        fetch_awe_nominal,
        fetch_cpi,
        fetch_housing_affordability,
        fetch_public_sector_employment,
        fetch_nhs_waiting_list,
        fetch_ae_monthly_timeseries,
        fetch_world_bank_gdp_per_capita,
    ]

    for fn in fetchers:
        result = fn(force=force)
        report.results.append(result)

    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    report = fetch_all()
    print(report.summary())
    if report.failed > 0:
        raise SystemExit(1)
