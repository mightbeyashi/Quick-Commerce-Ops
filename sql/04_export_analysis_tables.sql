-- Export SQL-built analysis tables for Excel, Power BI, and report use.
-- Run from project root after sql/02_clean_views.sql.

.headers on
.mode csv

.once data/processed/sql_category_health.csv
SELECT * FROM category_health ORDER BY stockout_rate_pct DESC, total_skus DESC;

.once data/processed/sql_replenishment_watchlist.csv
SELECT * FROM replenishment_watchlist ORDER BY priority_rank;

.once data/processed/sql_discount_exposure.csv
SELECT * FROM discount_exposure ORDER BY available_discount_exposure_rupees DESC;

.once data/processed/sql_clean_inventory_sample.csv
SELECT * FROM clean_inventory ORDER BY sku_id LIMIT 500;

.once data/processed/sql_scenario_category_metrics.csv
SELECT
  category,
  COUNT(*) AS scenario_order_lines,
  SUM(units_ordered) AS scenario_units_ordered,
  SUM(units_fulfilled) AS scenario_units_fulfilled,
  ROUND(100.0 * SUM(units_fulfilled) / NULLIF(SUM(units_ordered), 0), 2) AS scenario_fill_rate_pct,
  ROUND(SUM(unfulfilled_value_rupees), 2) AS scenario_unfulfilled_value_rupees
FROM scenario_order_events
GROUP BY category
ORDER BY scenario_unfulfilled_value_rupees DESC;

.once data/processed/sql_scenario_sku_impact.csv
SELECT
  sku_id,
  product_name,
  category,
  SUM(units_ordered) AS scenario_units_ordered,
  SUM(units_fulfilled) AS scenario_units_fulfilled,
  SUM(CASE WHEN LOWER(stockout_flag) = 'true' THEN 1 ELSE 0 END) AS scenario_stockout_orders,
  ROUND(SUM(unfulfilled_value_rupees), 2) AS scenario_unfulfilled_value_rupees
FROM scenario_order_events
GROUP BY sku_id, product_name, category
ORDER BY scenario_unfulfilled_value_rupees DESC;
