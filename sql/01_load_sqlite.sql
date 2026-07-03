-- Run from the project root:
-- sqlite3 data/processed/quick_commerce_ops.db < sql/01_load_sqlite.sql

DROP TABLE IF EXISTS raw_inventory;

CREATE TABLE raw_inventory (
  category TEXT,
  product_name TEXT,
  mrp_paise INTEGER,
  discount_percent INTEGER,
  available_quantity INTEGER,
  discounted_selling_price_paise INTEGER,
  weight_gms INTEGER,
  out_of_stock TEXT,
  pack_quantity INTEGER
);

.mode csv
.import --skip 1 data/processed/zepto_inventory_utf8.csv raw_inventory

DROP TABLE IF EXISTS scenario_order_events;

CREATE TABLE scenario_order_events (
  order_id TEXT,
  sku_id INTEGER,
  customer_id TEXT,
  dark_store_id TEXT,
  order_date TEXT,
  category TEXT,
  product_name TEXT,
  units_ordered INTEGER,
  units_fulfilled INTEGER,
  stockout_flag TEXT,
  substitution_accepted TEXT,
  selling_price_rupees REAL,
  gross_demand_value_rupees REAL,
  fulfilled_revenue_rupees REAL,
  unfulfilled_value_rupees REAL,
  delivery_minutes REAL,
  data_origin TEXT
);

.import --skip 1 data/processed/scenario_order_events.csv scenario_order_events
