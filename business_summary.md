# Competitor Price Analysis — Business Summary

## Executive Summary

This analysis demonstrates how competitor pricing data can be transformed into comparable pricing, discount, dispersion, and price-change metrics. The dataset used for this take-home is **synthetic** and was created to exercise the end-to-end pipeline; therefore, the findings below demonstrate analytical capability and should not be interpreted as actual historical pricing behaviour on Blibli or Tokopedia.

The analysis covers four Unilever products across two platforms and six observation dates, producing 48 daily price observations.

## 1. Which platform is cheapest on average?

Blibli has the lower price index in the synthetic dataset.

| Platform | Comparable observations | Price index |
|---|---:|---:|
| Blibli | 24 | 98.80 |
| Tokopedia | 24 | 101.20 |

The index benchmarks each product-date price against the cross-platform average for the same product and date, where **100 represents the market benchmark**.

Across the 24 comparable product-date observations per platform, Blibli prices are therefore approximately **1.2% below the benchmark**, while Tokopedia prices are approximately **1.2% above it**.

## 2. How deep and frequent are discounts?

Hair Care products are discounted in **100% of observations on both platforms**, with an average discount depth of **12.67%** and a maximum observed discount of **17%**.

Personal Care shows greater platform variation. Tokopedia records discounts in **100% of observations**, averaging **12.00%**, compared with **83.33%** of observations and an average **7.80%** discount on Blibli.

Discount data is available for all observations in the synthetic dataset, so the calculated frequencies are not affected by missing discount fields.

## 3. Which products show the largest price dispersion?

**Lifebuoy Body Wash 500ml** has the largest observed cross-platform price dispersion.

The maximum difference is **Rp3,000**, equivalent to **7.41% of the cross-platform average price**, observed on both 31 August and 30 September.

**Dove Shampoo 340ml** also shows a recurring Rp2,000 cross-platform difference across several observation dates, representing approximately 4.3% of its average price.

This demonstrates how dispersion monitoring can identify products where competitor positioning differs most significantly.

## 4. How frequently do prices change?

Across periods where a previous price is available:

| Platform | Comparable periods | Price changes | Change frequency |
|---|---:|---:|---:|
| Blibli | 20 | 9 | 45.00% |
| Tokopedia | 20 | 6 | 30.00% |

Blibli therefore exhibits more frequent price movement in this synthetic sample.

The day-of-week aggregation shows observed change frequencies of 50% on Monday, Wednesday, and Friday, 37.5% on Tuesday, and 0% on Sunday. However, **these figures should not be interpreted as evidence of a real weekday pricing pattern**.

The historical fixture is deliberately sparse and concentrated around month-end dates. Each represented weekday has only eight comparable observations, while Thursday has no comparable observations. A production analysis would require substantially denser daily observations before evaluating weekday behaviour.

## Business Implications

The pipeline demonstrates how competitor monitoring can surface three useful signals: relative platform price positioning, promotional intensity, and products with unusually large cross-platform price gaps.

In a production setting, these signals could support pricing teams in prioritising products for review rather than automatically determining prices. The accompanying recommendation model therefore remains intentionally simple and transparent: it recommends 95% of the cross-platform competitor median when sufficient platform coverage exists.

The recommendation should not be treated as a production pricing decision because it does not currently incorporate cost, margin requirements, inventory, demand elasticity, or commercial strategy.

## Data Limitations

All historical observations included in this repository are synthetic and intended for technical demonstration only. The sample contains four products, two platforms, and six observation dates. Product matching is rule-based, and the temporal sampling is insufficient for robust seasonality or weekday analysis.

The analytical models are designed so that the same metrics can be applied to larger, real-world datasets once reliable marketplace observations are available.