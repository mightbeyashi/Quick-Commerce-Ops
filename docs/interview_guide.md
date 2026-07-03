# QuickCommerceOps Interview Guide

## 30-Second Pitch

QuickCommerceOps is a quick-commerce inventory and product analytics project. I used a real SKU inventory dataset to analyze category availability, stockout rate, discount exposure, and replenishment priority. I cleaned the data, handled encoding issues, converted paise to rupees, built SQL views, created Python EDA and charts, exported Excel/Power BI-ready tables, and built a local report. Since the dataset has no actual orders, I added a clearly labeled scenario layer to practice Product Analyst metrics like fill rate, unfulfilled value, substitution acceptance, what-if recovery, and experiment design without presenting those numbers as real sales.

## 2-Minute Walkthrough

The business problem is that quick-commerce platforms depend heavily on product availability. If important SKUs are unavailable, customers may abandon the order, choose a substitute, or move to another app. The source dataset is an inventory snapshot, so I first focused on observed inventory facts: category stockout rate, available inventory value, discount exposure, and a replenishment watchlist.

I started by cleaning the raw data. The file had a non-UTF-8 encoding issue, so I read it with `cp1252`. I standardized text fields, converted price columns from paise to rupees, created flags for invalid commercial rows, and created derived fields such as price per 100g, discount amount, availability status, and inventory value proxy.

In SQL, I built reusable views for clean inventory, valid inventory, category health, discount exposure, and the replenishment watchlist. In Python, I used pandas and numpy to reproduce the KPI tables, create charts, export Excel-ready CSVs, and generate the HTML report.

For Product Analyst readiness, I added a deterministic scenario order layer. This is not actual order history. It is a transparent scenario dataset that allows me to demonstrate how I would measure fill rate, stockout order rate, substitution acceptance, unfulfilled value, and what-if recovery if real orders were available.

## How To Say The Data Honesty Part

Use this exact idea:

> The inventory metrics are observed from the dataset. The order and revenue-impact metrics are scenario estimates because the source does not contain actual orders. I separated them intentionally so I do not overclaim.

That answer is strong for fresher interviews because it shows judgment.

## What Makes This A Data Analyst Project

- Starts with a business problem, not just charts.
- Uses real inventory data.
- Handles encoding and commercial data-quality issues.
- Builds reusable SQL views.
- Produces category-level and SKU-level KPI tables.
- Creates Excel and Power BI-ready outputs.
- Ends with an action-oriented replenishment watchlist.

## What Makes This A Product Analyst Project

- Defines product/ops metrics: fill rate, stockout order rate, substitution acceptance, unfulfilled value.
- Separates observed metrics from scenario metrics.
- Includes a what-if model for operational improvement.
- Includes experiment design with primary and guardrail metrics.
- Connects analysis to a decision: which SKUs/categories should the team act on first?

## SQL Concepts To Mention

- `CREATE VIEW` for reusable analysis layers.
- `CASE WHEN` for stockout, invalid-commercial, and scoring flags.
- `GROUP BY` for category KPIs.
- `ROW_NUMBER()` for priority ranking.
- CTEs for readable scoring logic.
- `NULLIF` for safe division in fill-rate calculations.

## Python Concepts To Mention

- `pandas.read_csv(..., encoding="cp1252")` to handle the raw file encoding.
- Price conversion from paise to rupees.
- Derived features like `inventory_value`, `price_per_100g`, `discount_band`, and `availability_status`.
- `numpy.select` for buckets and scoring.
- Reproducible scenario generation using a fixed random seed.
- Matplotlib charts and automated HTML report generation.

## Excel And Power BI Concepts To Mention

- Excel-ready CSV outputs for pivots and conditional formatting.
- Power BI-ready CSV outputs for dashboard pages.
- Suggested dashboard pages:
  1. Executive Overview
  2. Category Health
  3. SKU Watchlist
  4. Product Experiment
- Filters: category, availability status, discount band, priority score, stockout flag.

## Likely Interview Questions

### Why did you choose this project?

Quick commerce depends on availability and fast operational decisions. I wanted a project closer to real business analytics than a generic sales dashboard.

### Are the lost revenue numbers real?

No. The source data does not contain actual orders or customer demand. I call them scenario unfulfilled value, not actual lost revenue. The scenario layer is for Product Analyst practice and dashboard modeling.

### Why did you create a scenario order layer?

Because Product Analyst interviews often ask about fill rate, impact sizing, and experiments. The original dataset cannot answer those directly, so I created a transparent scenario layer and labeled it clearly instead of pretending the numbers are real.

### What is the biggest limitation?

The dataset lacks actual orders, demand, customer sessions, margin, dark-store history, lead time, expiry, and substitutions. With company data, I would connect inventory snapshots with orders and calculate true lost sales and replenishment impact.

### Why not use machine learning?

The available data is a point-in-time inventory snapshot, not historical demand data. A transparent scoring and scenario model is more honest and explainable for this dataset.

### How would you improve this with real company data?

I would add order history, impressions/searches, add-to-cart events, substitutions, gross margin, replenishment lead time, dark-store IDs, and delivery SLAs. Then I would measure true fill rate, lost sales, substitution recovery, and inventory tradeoffs.

### What decision should the business take?

Start with SKUs that are out of stock or low stock, especially in categories with high stockout rates and meaningful inventory value. Then test whether replenishment alerts or category-level operations focus improves fill rate without increasing delivery time or overstock.

## Fresher Resume Version

Built `QuickCommerceOps`, an end-to-end quick-commerce analytics project using SQL, Python, Excel, and Power BI-ready outputs to analyze 3.7K+ SKU inventory rows, identify stockout-prone categories, create a replenishment watchlist, audit data-quality limitations, and model Product Analyst scenarios for fill rate, unfulfilled value, and experiment design.

## Do Not Say

- Do not say the project has actual sales data.
- Do not say the scenario unfulfilled value is real lost revenue.
- Do not say the model predicts demand.
- Do not say it is production-ready.

## Say Instead

- The source dataset is real inventory data.
- The product metrics are scenario estimates.
- The project shows how I would structure the analysis if real order data were available.
- The important part is the workflow: cleaning, SQL modeling, dashboarding, decision framing, and honest limitations.
