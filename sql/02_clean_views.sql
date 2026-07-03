-- Clean views and reusable KPI views.
-- Run after sql/01_load_sqlite.sql.

DROP VIEW IF EXISTS clean_inventory;

CREATE VIEW clean_inventory AS
SELECT
  ROW_NUMBER() OVER (ORDER BY category, product_name, mrp_paise, discounted_selling_price_paise) AS sku_id,
  TRIM(category) AS category,
  TRIM(product_name) AS product_name,
  CAST(mrp_paise AS REAL) / 100.0 AS mrp_rupees,
  CAST(discounted_selling_price_paise AS REAL) / 100.0 AS selling_price_rupees,
  CAST(discount_percent AS INTEGER) AS discount_percent,
  (CAST(mrp_paise AS REAL) - CAST(discounted_selling_price_paise AS REAL)) / 100.0 AS discount_amount_rupees,
  CAST(available_quantity AS INTEGER) AS available_quantity,
  CAST(weight_gms AS INTEGER) AS weight_gms,
  CAST(pack_quantity AS INTEGER) AS pack_quantity,
  CASE
    WHEN LOWER(TRIM(out_of_stock)) = 'true' OR CAST(available_quantity AS INTEGER) <= 0 THEN 1
    ELSE 0
  END AS is_out_of_stock,
  CASE
    WHEN CAST(mrp_paise AS INTEGER) <= 0 THEN 1
    WHEN CAST(discounted_selling_price_paise AS INTEGER) <= 0 THEN 1
    WHEN CAST(weight_gms AS INTEGER) <= 0 THEN 1
    ELSE 0
  END AS has_invalid_commercials,
  CASE
    WHEN CAST(weight_gms AS INTEGER) <= 0 THEN NULL
    ELSE (CAST(discounted_selling_price_paise AS REAL) / 100.0) / (CAST(weight_gms AS REAL) / 100.0)
  END AS price_per_100g,
  CASE
    WHEN CAST(weight_gms AS INTEGER) <= 0 THEN 'unknown'
    WHEN CAST(weight_gms AS INTEGER) < 100 THEN 'tiny'
    WHEN CAST(weight_gms AS INTEGER) < 500 THEN 'small'
    WHEN CAST(weight_gms AS INTEGER) <= 1000 THEN 'standard'
    ELSE 'bulk'
  END AS weight_bucket,
  CASE
    WHEN CAST(discount_percent AS INTEGER) = 0 THEN 'no discount'
    WHEN CAST(discount_percent AS INTEGER) < 10 THEN 'low'
    WHEN CAST(discount_percent AS INTEGER) < 25 THEN 'medium'
    ELSE 'high'
  END AS discount_band,
  CASE
    WHEN CAST(available_quantity AS INTEGER) <= 0 THEN 0
    ELSE (CAST(discounted_selling_price_paise AS REAL) / 100.0) * CAST(available_quantity AS INTEGER)
  END AS available_inventory_value_rupees
FROM raw_inventory;

DROP VIEW IF EXISTS valid_inventory;

CREATE VIEW valid_inventory AS
SELECT *
FROM clean_inventory
WHERE has_invalid_commercials = 0;

DROP VIEW IF EXISTS category_health;

CREATE VIEW category_health AS
SELECT
  category,
  COUNT(*) AS total_skus,
  SUM(CASE WHEN is_out_of_stock = 0 THEN 1 ELSE 0 END) AS available_skus,
  SUM(CASE WHEN is_out_of_stock = 1 THEN 1 ELSE 0 END) AS out_of_stock_skus,
  ROUND(100.0 * SUM(CASE WHEN is_out_of_stock = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS stockout_rate_pct,
  ROUND(AVG(discount_percent), 2) AS avg_discount_pct,
  ROUND(AVG(mrp_rupees), 2) AS avg_mrp_rupees,
  ROUND(SUM(available_inventory_value_rupees), 2) AS available_inventory_value_rupees,
  ROUND(AVG(price_per_100g), 2) AS avg_price_per_100g
FROM valid_inventory
GROUP BY category;

DROP VIEW IF EXISTS replenishment_watchlist;

CREATE VIEW replenishment_watchlist AS
WITH category_context AS (
  SELECT
    category,
    stockout_rate_pct,
    available_inventory_value_rupees
  FROM category_health
),
scored AS (
  SELECT
    v.sku_id,
    v.category,
    v.product_name,
    v.mrp_rupees,
    v.selling_price_rupees,
    v.discount_percent,
    v.available_quantity,
    v.weight_gms,
    v.is_out_of_stock,
    c.stockout_rate_pct,
    ROUND(v.available_inventory_value_rupees, 2) AS available_inventory_value_rupees,
    (
      CASE WHEN v.is_out_of_stock = 1 THEN 45 ELSE 0 END +
      CASE WHEN v.available_quantity BETWEEN 1 AND 2 THEN 20 ELSE 0 END +
      CASE WHEN v.mrp_rupees >= 500 THEN 15 ELSE 0 END +
      CASE WHEN c.stockout_rate_pct >= 15 THEN 10 ELSE 0 END +
      CASE WHEN v.discount_percent BETWEEN 5 AND 25 THEN 5 ELSE 0 END +
      CASE WHEN v.weight_bucket IN ('standard', 'bulk') THEN 5 ELSE 0 END
    ) AS priority_score
  FROM valid_inventory v
  JOIN category_context c
    ON v.category = c.category
)
SELECT
  ROW_NUMBER() OVER (ORDER BY priority_score DESC, mrp_rupees DESC, category, product_name) AS priority_rank,
  *
FROM scored
WHERE is_out_of_stock = 1 OR available_quantity <= 2
ORDER BY priority_score DESC, mrp_rupees DESC, category, product_name;

DROP VIEW IF EXISTS discount_exposure;

CREATE VIEW discount_exposure AS
SELECT
  sku_id,
  category,
  product_name,
  mrp_rupees,
  selling_price_rupees,
  discount_percent,
  discount_amount_rupees,
  available_quantity,
  ROUND(discount_amount_rupees * available_quantity, 2) AS available_discount_exposure_rupees,
  discount_band,
  is_out_of_stock
FROM valid_inventory
WHERE discount_percent >= 25
ORDER BY available_discount_exposure_rupees DESC, discount_percent DESC;

