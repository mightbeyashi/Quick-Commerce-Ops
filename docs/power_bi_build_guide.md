# Power BI Build Guide

Use this guide to build the QuickCommerceOps dashboard in Power BI Desktop.

## Import These CSVs

From the `excel/` folder:

- `category_health_for_excel.csv`
- `replenishment_watchlist_for_excel.csv`
- `discount_exposure_for_excel.csv`
- `data_quality_summary_for_excel.csv`
- `scenario_order_events_for_power_bi.csv`
- `scenario_category_metrics_for_power_bi.csv`
- `scenario_sku_impact_watchlist_for_excel.csv`
- `scenario_what_if_model_for_excel.csv`
- `experiment_design_for_excel.csv`

## Data Honesty Label

Add a small text box on the dashboard:

`Observed metrics come from the inventory dataset. Scenario order metrics are simulated for analysis practice and are not actual sales history.`

This protects the project from overclaiming.

## Page 1: Executive Overview

Goal: show the business situation in one screen.

Recommended cards:

- Total SKUs: `COUNTROWS(clean inventory)` or use raw row count from processed outputs.
- Observed stockout rate: average of `is_out_of_stock` or use category summary.
- Observed inventory value proxy: sum of `available_inventory_value_rupees`.
- Scenario fill rate: `SUM(units_fulfilled) / SUM(units_ordered)`.
- Scenario unfulfilled value: `SUM(unfulfilled_value_rupees)`.
- Priority SKU count: count of rows in `replenishment_watchlist_for_excel.csv`.

Recommended visuals:

- Bar chart: stockout rate by category.
- Bar chart: scenario unfulfilled value by category.
- Table: top 10 priority SKUs.

## Page 2: Category Health

Goal: compare categories and identify where operations should focus.

Recommended visuals:

- Bar chart: `stockout_rate_pct` by `category`.
- Bar chart: `available_inventory_value_rupees` by `category`.
- Scatter plot:
  - X-axis: `stockout_rate_pct`
  - Y-axis: `available_inventory_value_rupees`
  - Size: `total_skus`
  - Legend: `priority_category_flag`
- Matrix: category, total SKUs, available SKUs, out-of-stock SKUs, average discount, stockout rate.

Filters:

- Category
- Priority category flag
- Stockout rate range

## Page 3: SKU Watchlist

Goal: show the action list.

Recommended visuals:

- Table with:
  - `priority_rank`
  - `product_name`
  - `category`
  - `available_quantity`
  - `is_out_of_stock`
  - `mrp_rupees`
  - `discount_percent`
  - `stockout_rate_pct`
  - `priority_score`
- Bar chart: top SKUs by `priority_score`.
- Bar chart: scenario SKU impact by `scenario_unfulfilled_value_rupees`.

Filters:

- Category
- Stock status
- Discount band
- Priority score

## Page 4: Product Experiment

Goal: make the project useful for Product Analyst interviews.

Recommended visuals:

- Table: `scenario_what_if_model_for_excel.csv`.
- Table: `experiment_design_for_excel.csv`.
- Card: scenario unfulfilled value.
- Card: scenario recovered value for selected what-if row.
- Bar chart: what-if scenario vs recovered value.

Talk track:

- "If this were real company data, I would validate the scenario using historical orders."
- "The experiment would test whether replenishment alerts reduce stockout order rate."
- "The guardrail is delivery time or inventory value tied up, so we do not optimize one metric blindly."

## Suggested DAX Measures

```DAX
Scenario Units Ordered = SUM(scenario_order_events_for_power_bi[units_ordered])

Scenario Units Fulfilled = SUM(scenario_order_events_for_power_bi[units_fulfilled])

Scenario Fill Rate % =
DIVIDE([Scenario Units Fulfilled], [Scenario Units Ordered]) * 100

Scenario Stockout Orders =
CALCULATE(
    COUNTROWS(scenario_order_events_for_power_bi),
    scenario_order_events_for_power_bi[stockout_flag] = TRUE()
)

Scenario Stockout Order Rate % =
DIVIDE([Scenario Stockout Orders], COUNTROWS(scenario_order_events_for_power_bi)) * 100

Scenario Unfulfilled Value =
SUM(scenario_order_events_for_power_bi[unfulfilled_value_rupees])
```

If Power BI reads `stockout_flag` as text instead of boolean, use:

```DAX
Scenario Stockout Orders =
CALCULATE(
    COUNTROWS(scenario_order_events_for_power_bi),
    scenario_order_events_for_power_bi[stockout_flag] = "True"
)
```

## Presentation Order In Interviews

1. Explain the business problem.
2. Show the Executive Overview.
3. Show Category Health.
4. Show the SKU Watchlist.
5. Explain the data-quality audit.
6. Explain that scenario metrics are not actual sales.
7. Show the Product Experiment page.
8. Close with limitations and next steps if real company data were available.
