# Expected results

These are the lab checkpoints next to the values a full run actually produced (31 Oct 2026). Your AI output may vary slightly between runs.

## Step 1 – Row counts

| Table | Rows |
|---|---|
| ORDERS | 247,741 |
| ORDER_ITEMS | 521,607 |
| REFUNDS | 15,057 |
| SUPPORT_CHATS | 6,728 |
| WEATHER_HOURLY | 43,776 |
| CUSTOMERS | 30,000 |
| RIDERS | 2,828 |
| RESTAURANTS | 1,386 |
| CITIES_ZONES | 40 |
| APP_RELEASES | 15 |

## Step 3 – Monthly refunds (by order month)

| Metric | Lab | Actual |
|---|---|---|
| Aug refunds | ≈ ₹5.08 L | ₹5,08,259 |
| Oct refunds | ≈ ₹7.13 L | ₹7,12,841 |
| Increase | ≈ 40% | +40.3% (₹2,04,582) |
| Refund % of GMV | 3.71% → 4.76% | 3.71% → 4.76% |
| Order growth | ≈ 9% | +9.5% |

## Step 4 – Attribution

| Metric | Lab | Actual |
|---|---|---|
| Top city | Bengaluru | Bengaluru (+₹1,69,148) |
| Top zone | Whitefield-East | Whitefield-East: ₹55,180 → ₹2,13,845 |
| Zone share of increase | ≈ 78% | 77.6% (₹1,58,665) |
| Zone reasons | Late, Cold food | Late +₹98,187 · Cold food +₹61,362 |
| Cloud Kitchens Hub | ≈ ₹4,000 | Total ₹10,264 (all new since launch, 5.0%); excess vs Standard rate ₹2,735 (1.3%); missing-item ₹2,746 |

## Step 5 – Root cause (late = > 45 min, minute-based)

| Metric | Lab | Actual |
|---|---|---|
| Release | rider-assign v2.3, 8 Sep | rider-assign v2.3, 2026-09-08 |
| WFE assignment distance | 2.1 → 6.0 km | 2.10 → 6.01 km |
| WFE pickup wait | — | 15.2 → 21.3 min |
| WFE late % | ≈6% → 20–28% | 6.8% → 26.4% |
| Other zones late % | ≈6% | 6.2% → 6.5% |
| WFE after 8 Sep: rainy vs dry | ≈56% vs ≈14% | 55.9% vs 14.2% |

## Step 6 – Cortex AI

| Theme | Chats | % |
|---|---|---|
| Rider assigned too far away | 237 | 53.1 |
| General late delivery | 111 | 24.9 |
| Food arrived cold | 47 | 10.5 |
| Missing or wrong item | 35 | 7.8 |
| Food quality | 16 | 3.6 |
| **Total** | **446** | |

The `AI_SUMMARIZE_AGG` summary mentions long waits, cold food, riders assigned from far away, wrong or missing items, and rain being "no excuse".

## Common pitfalls

- **Late % definition:** `DATEDIFF('second') > 2700` gives late % about 1 point higher than `DATEDIFF('minute') > 45`.
- **AI_CLASSIFY labels:** adding category descriptions shifts results (e.g. 290 instead of 237 for "rider too far"). Plain labels match the lab.
- **Percentage bug:** if late % appears about 10× too high, the value is already a percentage. Don't multiply it by 100 again.
- **Before/after metrics:** weekly buckets straddle 8 Sep. Split at order level instead.
