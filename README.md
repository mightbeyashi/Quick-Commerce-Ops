# QuickCommerceOps

QuickCommerceOps is a quick-commerce analytics portfolio project for entry-level Data Analyst and Product Analyst roles. It uses a real SKU inventory export to analyze stockout risk, category health, discount exposure, replenishment priority, data-quality limitations, and a clearly labeled Product Analyst scenario model.

This project is built for fresher/on-campus placements where interviewers expect SQL, Excel, Power BI, Python, business thinking, and honest communication about data limitations.

## Dashboard

![QuickCommerceOps Power BI Dashboard](images/dashboard.png)

*Interactive Power BI dashboard: category stockout rates, replenishment watchlist, and discount exposure. (Add your screenshot at `images/dashboard.png`.)*

## What This Project Proves

- Data cleaning: encoding fix, price conversion from paise to rupees, invalid commercial flags, reusable cleaned outputs.
- SQL: views, CTEs, ranking, grouping, KPI queries, scenario queries.
- Python: pandas EDA, deterministic scoring, scenario generation, charting, report automation.
- Excel/Power BI: ready-to-import CSVs for dashboards, pivots, filters, and what-if analysis.
- Product thinking: fill rate, stockout order rate, unfulfilled value, substitution acceptance, experiment design, and guardrail metrics.
- Analyst judgment: observed inventory facts are separated from scenario-estimated metrics.

## Data Honesty

The source dataset is an inventory snapshot. It does not contain actual customer orders, revenue, margin, lead time, delivery operations, or dark-store history.

Because of that:

- Observed metrics such as stockout rate, price, discount, category health, and inventory value proxy come from the source data.
- Product Analyst metrics such as fill rate, unfulfilled value, substitution acceptance, and what-if recovery come from a deterministic scenario layer.
- Scenario outputs are useful for interview storytelling and dashboard practice, but they must not be presented as actual company performance.

## Dataset

Primary dataset:

- `data/raw/zepto_v2.csv`
- Rows: 3,732 SKU inventory rows
- Main fields: category, product name, MRP, discount percent, available quantity, discounted selling price, weight, out-of-stock flag, package quantity

Important data notes:

- The raw CSV has non-UTF-8 characters. The Python pipeline reads it with `cp1252` and writes a UTF-8 cleaned copy to `data/processed/zepto_inventory_utf8.csv`.
- Prices are stored in paise, so the pipeline converts them into rupees.
- The dataset has duplicate-like commercial records and products appearing across multiple categories. The report includes this as a data-quality finding instead of hiding it.

## Project Stack

- SQL: SQLite views, CTEs, KPI queries, scenario queries
- Python: pandas, numpy, matplotlib
- Excel: CSV exports for pivots, lookups, conditional formatting, and what-if analysis
- Power BI: dashboard-ready fact and summary tables
- HTML/CSS: local portfolio report at `report/index.html`

## Main Outputs

Observed inventory outputs:

- `data/processed/clean_inventory.csv`
- `data/processed/category_health.csv`
- `data/processed/replenishment_watchlist.csv`
- `data/processed/discount_exposure.csv`
- `data/processed/data_quality_summary.csv`
- `data/processed/multi_category_products.csv`
- `data/processed/duplicate_catalog_signatures.csv`

Product Analyst scenario outputs:

- `data/processed/scenario_order_events.csv`
- `data/processed/scenario_category_metrics.csv`
- `data/processed/scenario_sku_impact_watchlist.csv`
- `data/processed/scenario_executive_metrics.csv`
- `data/processed/scenario_what_if_model.csv`
- `data/processed/experiment_design.csv`

Excel and Power BI-ready outputs:

- `excel/category_health_for_excel.csv`
- `excel/replenishment_watchlist_for_excel.csv`
- `excel/discount_exposure_for_excel.csv`
- `excel/data_quality_summary_for_excel.csv`
- `excel/scenario_order_events_for_power_bi.csv`
- `excel/scenario_category_metrics_for_power_bi.csv`
- `excel/scenario_sku_impact_watchlist_for_excel.csv`
- `excel/scenario_what_if_model_for_excel.csv`
- `excel/experiment_design_for_excel.csv`

Portfolio report:

- `report/index.html`

## How To Run

From the project root:

```bash
cd quick-commerce-ops
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python python/eda_quick_commerce_ops.py
sqlite3 data/processed/quick_commerce_ops.db < sql/01_load_sqlite.sql
sqlite3 data/processed/quick_commerce_ops.db < sql/02_clean_views.sql
sqlite3 data/processed/quick_commerce_ops.db < sql/03_business_questions.sql
sqlite3 data/processed/quick_commerce_ops.db < sql/04_export_analysis_tables.sql
python python/eda_quick_commerce_ops.py
```

Why run Python twice?

- The first Python run creates cleaned CSVs, scenario order events, product metrics, charts, and report assets.
- SQL then imports the cleaned inventory and scenario order data, builds SQL views, and exports SQL-built outputs.
- The second Python run refreshes the report after all processed outputs exist.

## Recommended Power BI Dashboard

Build four pages:

1. Executive Overview
   - Observed stockout rate
   - Observed inventory value proxy
   - Total SKUs
   - Scenario fill rate
   - Scenario unfulfilled value
   - Priority SKU count

2. Category Health
   - Stockout rate by category
   - Available inventory value by category
   - Average discount by category
   - Scenario unfulfilled value by category

3. SKU Watchlist
   - Priority-ranked SKU table
   - Filters for category, stock status, discount band, and price band
   - Scenario unfulfilled value
   - Priority score

4. Product Experiment
   - What-if recovery table
   - Experiment design
   - Primary metrics and guardrails
   - Recommendation section

See `docs/power_bi_build_guide.md` for the dashboard build plan.

## Resume Positioning

Use this as one strong fresher project, not as five small projects.

### Data Analyst Resume Bullet

Built `QuickCommerceOps`, a quick-commerce inventory analytics project using SQL, Python, Excel-ready outputs, and Power BI-ready datasets to analyze stockout risk, category health, discount exposure, and replenishment priorities across 3.7K+ SKU inventory rows.

### Product Analyst Resume Bullet

Extended `QuickCommerceOps` with a clearly labeled scenario order layer to model fill rate, stockout order rate, unfulfilled value, substitution acceptance, and what-if recovery, while separating observed inventory facts from simulated product metrics.

### Strong Combined Bullet

Built `QuickCommerceOps`, an end-to-end quick-commerce analytics project using SQL, Python, Excel, and Power BI-ready outputs to identify stockout-prone SKUs, analyze category health, build a replenishment watchlist, audit data-quality issues, and model Product Analyst scenarios for fill rate, unfulfilled value, and experiment design.

## Interview Pitch

QuickCommerceOps is an inventory and product analytics project for quick commerce. I used a real SKU inventory dataset to analyze availability, stockouts, discounts, category health, and replenishment priority. I cleaned encoding issues, converted prices from paise to rupees, built SQL KPI views, created Python EDA and charts, exported Excel/Power BI-ready tables, and built a local HTML report. Since the dataset does not contain actual orders, I added a clearly labeled scenario order layer to demonstrate Product Analyst thinking around fill rate, unfulfilled value, substitution, what-if modeling, and experiment design without pretending the scenario numbers are actual sales.

## Limitations

This is not a full company warehouse. The source data lacks actual demand, customer sessions, orders, delivery time, margin, lead time, dark-store history, expiry, and substitution behavior. With real company data, the next version should connect inventory snapshots with orders, customer demand, replenishment lead time, gross margin, and dark-store operations.
