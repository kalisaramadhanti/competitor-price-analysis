# Competitor Price Analysis — Business Summary

## Executive Summary

This project develops an end-to-end competitor pricing intelligence pipeline to automate marketplace price collection, standardise product information, analyse competitive positioning, and generate indicative pricing recommendations.

Live product observations were collected from Blibli and Tokopedia, while KlikIndomaret was represented by a clearly labelled synthetic fixture after automated access was restricted.

The latest verified pipeline results include:

| Metric | Result |
|---|---:|
| Raw observations in PostgreSQL | 923 |
| Blibli raw observations | 786 |
| Tokopedia raw observations | 134 |
| KlikIndomaret synthetic observations | 3 |
| Gold price competitiveness records | 880 |
| Product-date records evaluated for recommendations | 856 |
| Valid indicative recommendations | 24 |
| Records with insufficient platform coverage | 832 |

The results demonstrate the feasibility of automated competitor monitoring while highlighting the importance of product matching, data coverage, and pricing constraints.

## 1. Competitive Price Monitoring

The pipeline transforms marketplace observations into comparable product-level pricing information across Blibli and Tokopedia.

The analytical layer supports monitoring of:

- **Price competitiveness:** Identifying products priced above or below the cross-platform benchmark.
- **Price dispersion:** Measuring price differences between marketplaces.
- **Discount behaviour:** Comparing promotional intensity and observed discounts.
- **Price movements:** Tracking changes between available observation dates.

These indicators help pricing teams identify products that warrant further commercial review.

However, cross-platform comparisons are only meaningful when product identity, size, variant, and packaging are sufficiently consistent.

## 2. Price Recommendation Results

A transparent, rule-based pricing recommendation model was implemented using the cross-platform median price.

**Recommended Price = 95% × Competitor Median Price**

A recommendation is generated only when at least two platforms have valid observations for the same normalised product on the same date.

The latest recommendation batch evaluated **856 product-date records**, producing **24 indicative recommendations**. The remaining **832 records** did not meet the minimum cross-platform coverage requirement.

This conservative approach avoids generating recommendations from insufficient competitor evidence.

The 5% reduction is a predefined pricing strategy assumption, not an empirically optimised discount.

## 3. Business Implications

The solution offers three potential business benefits:

1. **Operational efficiency:** Reduces reliance on manual marketplace price monitoring through reusable ingestion and transformation pipelines.
2. **Competitive visibility:** Provides a structured view of price positioning, discounts, and product-level pricing differences.
3. **Decision support:** Identifies eligible pricing opportunities and produces explainable, indicative recommendations.

The limited recommendation coverage also reveals an important operational priority: improving matching accuracy and synchronising observations across platforms could increase the number of products eligible for reliable price comparison.

The recommendation model should support human pricing decisions rather than automatically determine selling prices.

## 4. Data Quality, Limitations and Next Steps

Several limitations remain:

- **Data provenance:** Historical Blibli and Tokopedia records were ingested before explicit source-status labels were introduced. Their provenance should be fully verified before production use.
- **Restricted source access:** KlikIndomaret uses synthetic fixture data for technical demonstration, not actual observed market prices.
- **Product matching:** Rule-based normalisation cannot guarantee identical variants, pack sizes, or promotional bundles across marketplaces.
- **Observation coverage:** Differences in crawl dates and incomplete cross-platform matching restrict meaningful price comparisons.
- **Commercial constraints:** Recommendations do not yet incorporate cost of goods sold, minimum margins, inventory, demand elasticity, or promotional strategy.
- **Historical analysis:** The available observations do not establish robust long-term trends or seasonality.

With additional development time, priorities would include stronger product entity matching, scheduled incremental crawling, source-quality monitoring, margin-aware recommendations, and more comprehensive historical price coverage.

## Conclusion

The project demonstrates a functioning end-to-end pricing intelligence architecture, from marketplace data collection and dbt dimensional modelling to analytical dashboards and rule-based price recommendations.

Its main contribution is a reusable foundation for translating competitor observations into structured, explainable pricing insights. Further improvements in data coverage, product matching, and commercial constraints would be required before using its recommendations for operational pricing decisions.
