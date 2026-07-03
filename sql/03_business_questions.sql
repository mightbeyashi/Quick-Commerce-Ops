-- Business questions for interview practice.
-- Run after sql/02_clean_views.sql.

.headers on
.mode column

-- 1. Data audit: how many rows are valid for commercial analysis?
SELECT
  COUNT(*) AS raw_rows,
  SUM(CASE WHEN has_invalid_commercials = 1 THEN 1 ELSE 0 END) AS invalid_commercial_rows,
  SUM(CASE WHEN has_invalid_commercials = 0 THEN 1 ELSE 0 END) AS valid_rows,
  ROUND(100.0 * SUM(CASE WHEN is_out_of_stock = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS raw_stockout_rate_pct
FROM clean_inventory;

-- 2. Which categories have the highest stockout rate?
SELECT
  category,
  total_skus,
  out_of_stock_skus,
  stockout_rate_pct,
  avg_discount_pct,
  available_inventory_value_rupees
FROM category_health
ORDER BY stockout_rate_pct DESC, total_skus DESC
LIMIT 10;

-- 3. Which high-MRP SKUs are currently unavailable?
SELECT
  product_name,
  category,
  mrp_rupees,
  selling_price_rupees,
  discount_percent,
  stockout_rate_pct
FROM replenishment_watchlist
WHERE is_out_of_stock = 1
ORDER BY mrp_rupees DESC
LIMIT 20;

-- 4. Which SKUs should the operations team prioritize first?
SELECT
  priority_rank,
  product_name,
  category,
  priority_score,
  available_quantity,
  is_out_of_stock,
  mrp_rupees,
  discount_percent,
  stockout_rate_pct
FROM replenishment_watchlist
ORDER BY priority_rank
LIMIT 25;

-- 5. Where is discount exposure concentrated?
SELECT
  category,
  COUNT(*) AS high_discount_skus,
  ROUND(AVG(discount_percent), 2) AS avg_discount_pct,
  ROUND(SUM(available_discount_exposure_rupees), 2) AS discount_exposure_rupees
FROM discount_exposure
GROUP BY category
ORDER BY discount_exposure_rupees DESC;

-- 6. Which categories carry the highest available inventory value?
SELECT
  category,
  available_inventory_value_rupees,
  total_skus,
  available_skus,
  stockout_rate_pct
FROM category_health
ORDER BY available_inventory_value_rupees DESC
LIMIT 10;

-- 7. How do weight buckets behave across stock status?
SELECT
  weight_bucket,
  COUNT(*) AS sku_count,
  ROUND(100.0 * SUM(CASE WHEN is_out_of_stock = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS stockout_rate_pct,
  ROUND(AVG(price_per_100g), 2) AS avg_price_per_100g
FROM valid_inventory
GROUP BY weight_bucket
ORDER BY sku_count DESC;

-- 8. Product Analyst scenario: what is the scenario fill rate by category?
-- Note: scenario_order_events is simulated for interview practice.
-- It is not actual company order history.
SELECT
  category,
  COUNT(*) AS scenario_order_lines,
  SUM(units_ordered) AS scenario_units_ordered,
  SUM(units_fulfilled) AS scenario_units_fulfilled,
  ROUND(100.0 * SUM(units_fulfilled) / NULLIF(SUM(units_ordered), 0), 2) AS scenario_fill_rate_pct,
  ROUND(SUM(unfulfilled_value_rupees), 2) AS scenario_unfulfilled_value_rupees
FROM scenario_order_events
GROUP BY category
ORDER BY scenario_unfulfilled_value_rupees DESC
LIMIT 10;

-- 9. Which SKUs drive the highest scenario unfulfilled value?
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
ORDER BY scenario_unfulfilled_value_rupees DESC
LIMIT 20;

-- 10. What substitution acceptance rate appears in the scenario?
SELECT
  COUNT(*) AS scenario_stockout_order_lines,
  SUM(CASE WHEN LOWER(substitution_accepted) = 'true' THEN 1 ELSE 0 END) AS scenario_substitution_acceptances,
  ROUND(
    100.0 * SUM(CASE WHEN LOWER(substitution_accepted) = 'true' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
    2
  ) AS scenario_substitution_acceptance_rate_pct
FROM scenario_order_events
WHERE LOWER(stockout_flag) = 'true';
