# Britain Since 2007: Key Findings

**One-page evidence summary from the evidence framework.**  
Baseline: 2007 | Data source: ONS | Latest: 2025 (national), 2023 (regional)

---

## 1. Growth collapsed after the financial crisis

GDP per head grew at **2.3% per year** in the decade before 2007. Since then, it has grown at just **0.4% per year** — a near-total collapse in the trend rate of growth.

| Period    | GDP per head CAGR | Output per hour CAGR |
| --------- | ----------------- | -------------------- |
| 1997–2007 | 2.3% pa           | 2.1% pa              |
| 2007–2025 | 0.4% pa           | 0.4% pa              |

If pre-2007 growth had continued, GDP per head would be roughly **£55,000** today instead of **£40,537** — a gap of about £14,500 per person.

---

## 2. Net domestic product grew at half the rate of GDP

NDP per head (GDP minus capital consumption) rose only **3.7%** since 2007, compared with **7.7%** for GDP per head. This suggests that a growing share of economic output has been absorbed by depreciation — more of what Britain produces is going to maintain the existing capital stock rather than generate new income.

| Measure      | 2007    | 2025    | Change |
| ------------ | ------- | ------- | ------ |
| GDP per head | £37,625 | £40,537 | +7.7%  |
| NDP per head | £33,070 | £34,300 | +3.7%  |

---

## 3. Productivity stagnation is real and persistent

Output per hour worked — the central measure of labour productivity — rose only **6.9% over 18 years** (0.4% per year). Before the crisis, productivity grew at roughly 2% per year. The UK's productivity performance since 2007 is historically weak and internationally poor.

- 2007: 93.0 (Index 2023 = 100)
- 2025: 99.4
- Total gain: 6.4 index points in 18 years.

---

## 4. Real earnings have barely grown — living standards diverged from GDP

Real average weekly earnings (CPI-deflated) rose only **2.3%** since 2007, compared with **7.7%** for GDP per head. In 2025 prices, the average worker earned the equivalent of **£711 per week** in 2007 and **£727 per week** in 2025 — a gain of just £16 per week over 18 years.

| Measure                | 2007    | 2025    | Change |
| ---------------------- | ------- | ------- | ------ |
| Real AWE (2025 prices) | £711/wk | £727/wk | +2.3%  |
| GDP per head           | £37,625 | £40,537 | +7.7%  |

This gap between output growth and pay growth is the central disconnect in the post-2007 economy. The economy produces more per person, but the average worker's real pay has barely moved.

---

## 5. Regional productivity inequality is narrowing — slowly

The standard deviation of regional output per hour fell from 15.1 to 12.2, suggesting modest convergence. But the story is mixed:

### Regions gaining ground (relative to UK average)

| Region           | 2007 | 2023 | Change    |
| ---------------- | ---- | ---- | --------- |
| Northern Ireland | 81.1 | 87.6 | **+8.1%** |
| Scotland         | 92.2 | 98.9 | **+7.3%** |
| Wales            | 82.4 | 84.9 | +3.0%     |
| North West       | 93.2 | 94.8 | +1.7%     |

### Regions losing ground

| Region                 | 2007  | 2023  | Change    |
| ---------------------- | ----- | ----- | --------- |
| London                 | 138.7 | 128.5 | **−7.3%** |
| East of England        | 97.4  | 94.7  | −2.8%     |
| Yorkshire & The Humber | 90.4  | 87.9  | −2.8%     |
| North East             | 86.8  | 85.4  | −1.6%     |

London remains the clear outlier at 28.5% above the UK average, but its advantage has shrunk from 38.7%.

---

## 6. Housing affordability: worse than 2007 for most of the post-crisis period

The ratio of median house prices to median earnings stood at **7.17×** in 2007 and **7.55×** in 2025 — a modest increase of 5.3%. But this endpoint comparison severely understates the deterioration:

| Year        | Ratio     |
| ----------- | --------- |
| 2007        | 7.17×     |
| 2015        | 7.37×     |
| 2021 (peak) | **8.95×** |
| 2025        | 7.55×     |
| 5-year avg  | **8.19×** |

The ratio peaked nearly 25% above 2007 levels before declining. The five-year average of 8.19× confirms that housing affordability was substantially worse than 2007 for most of the recent period. The partial recovery since 2021 reflects both cooling prices and earnings growth, but the long-run picture is one of structural deterioration.

**Caveat:** This data covers England and Wales only.

---

## 7. What is still left

- **Distributional living standards** — real earnings are measured, but household disposable income, inequality, poverty, and wealth are not.
- **Full UK housing coverage** — housing affordability is measured for England and Wales only; Scotland, Northern Ireland, and local breakdowns remain out of scope.
- **Broader public services** — NHS RTT waiting lists are measured for England only; A&E, social care, local authority finance, courts, and schools are not.
- **Sub-regional variation** — city-region and local authority breakdowns.

---

## About this evidence

All data sourced from the Office for National Statistics via programmatic download. No manual data entry. The full pipeline is reproducible with:

```bash
uv sync && uv run python src/fetch_ons.py && uv run python src/process_indicators.py && uv run python src/build_outputs.py
```

See `docs/methodology-note.md` for full source details, methodology, and limitations.

---

_UK Economic Change — Britain Since 2007: Evidence Framework. July 2026._
