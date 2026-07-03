# FunnelLens 5-Star Product Analyst Blueprint

## Goal

Turn FunnelLens from a strong idea into a recruiter-visible Product Analyst project for fresher roles.

Target roles:

- Product Analyst
- Business Analyst, Product
- Growth Analyst
- Category/Product Analytics Intern
- Decision Analytics Associate

Target companies:

- Meesho
- Myntra
- Eternal/Zomato
- Blinkit-style consumer products
- ZS
- EY analytics/GDS roles
- Other MNC analytics teams

## Final Project Title

`FunnelLens: E-commerce Activation, Retention and Experiment Analytics`

## Business Problem

An e-commerce product team wants to improve purchase conversion. Users view products, but many do not add to cart or complete purchase. The analyst must identify the largest funnel drop-off, measure whether new users return, find high-intent segments, and recommend one experiment.

## Dataset

Recommended dataset:

- RetailRocket E-commerce Events Dataset
- Required fields: `visitorid`, `event`, `itemid`, `timestamp`
- Optional useful fields: category tree, item properties

Do not hardcode row counts in the resume. Load the dataset first, then report actual counts.

## Folder Structure

```text
funnellens/
  README.md
  data/
    raw/
    processed/
  sql/
    01_event_cleaning.sql
    02_sessionization.sql
    03_funnel_metrics.sql
    04_retention_cohorts.sql
    05_experiment_scorecard.sql
  python/
    funnellens_eda.py
  excel/
    experiment_decision_model.xlsx
  dashboard/
    screenshots/
  memo/
    product_decision_memo.md
```

## Metric Tree

North Star:

- Successful purchase sessions

Primary product metrics:

- View-to-cart conversion rate
- Cart-to-purchase conversion rate
- View-to-purchase conversion rate
- Weekly returning user rate
- Activated user rate

Activation definition:

- A user is activated if they view at least 3 items and add at least 1 item to cart within the first 7 days.

Guardrail metrics:

- Refund/cancel proxy if available
- Session duration extreme outliers
- Repeat rate
- Revenue per buyer if transaction value exists
- Event tracking completeness

## SQL Deliverables

### 1. Event Cleaning

Create:

- `clean_events`
- `event_date`
- `event_timestamp`
- `event_week`
- `user_id`
- `item_id`
- event validity flags

Quality checks:

- total events
- unique users
- unique items
- event type distribution
- missing timestamp count
- duplicate event count

### 2. Sessionization

Create sessions using 30-minute inactivity gap:

- `session_id`
- `session_start_time`
- `session_end_time`
- `session_duration_minutes`
- `events_in_session`
- `viewed_flag`
- `carted_flag`
- `purchased_flag`

### 3. Funnel Metrics

Required funnel:

1. Product view
2. Add to cart
3. Purchase

Required outputs:

- users at each step
- sessions at each step
- step conversion rate
- drop-off count
- drop-off percentage
- view-to-cart conversion
- cart-to-purchase conversion
- view-to-purchase conversion

Segment cuts:

- new vs returning users
- first week cohort
- top categories/items if category data is available
- high-activity vs low-activity users

### 4. Retention Cohorts

Create:

- `first_active_week`
- `activity_week`
- `week_number`
- active users by cohort week
- retention percentage

Required views:

- W1 retention
- W2 retention
- W3 retention
- retention heatmap table

### 5. Experiment Scorecard

If the dataset has no real A/B assignment, create a scenario-only scorecard and label it:

`scenario_experiment_not_actual_ab_test`

Experiment:

- Hypothesis: simplifying the product page or showing stronger delivery/price cues will improve add-to-cart conversion.
- Primary metric: view-to-cart conversion rate.
- Secondary metric: view-to-purchase conversion rate.
- Guardrail metric: cart-to-purchase conversion rate should not drop.
- Decision rule: ship only if primary metric improves and guardrail does not worsen.

## Python Deliverables

Create charts:

- daily event volume
- event type distribution
- funnel conversion bar
- drop-off bar
- retention heatmap
- time-to-cart distribution
- time-to-purchase distribution
- segment conversion comparison

Optional advanced piece:

- logistic regression for purchase likelihood using session count, views, cart behavior, recency, and category interactions.

Use it only as an explanation tool, not as the main project.

## Power BI Dashboard

Page 1: Product Health

- active users
- active buyers
- sessions
- view-to-cart conversion
- cart-to-purchase conversion
- repeat user rate

Page 2: Funnel Diagnosis

- funnel chart
- drop-off bar
- conversion by segment
- time-to-convert distribution

Page 3: Retention

- weekly cohort heatmap
- retention curve
- new vs returning user split

Page 4: Experiment Scorecard

- hypothesis
- primary metric
- guardrail metric
- scenario lift table
- ship/no-ship recommendation

## Product Decision Memo

One page only.

Required sections:

1. Product problem
2. Metric affected
3. Diagnosis
4. User segment affected
5. Recommendation
6. Experiment design
7. Guardrail
8. Limitation

Example decision:

> The largest leakage is between product view and add-to-cart. I recommend testing stronger product-page trust cues or offer visibility for new users, because the issue appears before cart intent is formed. The primary metric is view-to-cart conversion, and the guardrail is cart-to-purchase conversion.

## Final Resume Bullet

Use only after actual outputs exist:

> Built `FunnelLens`, a Product Analyst project using SQL, Python, Excel, and Power BI to analyze e-commerce event behavior, sessionized user journeys, measure view-to-cart-to-purchase funnel conversion, build weekly retention cohorts, and design an experiment scorecard for improving activation.

If actual numbers exist, upgrade it:

> Built `FunnelLens` on X event records and Y users, identifying the largest funnel drop-off between A and B, measuring W1 retention at Z%, and recommending an activation experiment with primary and guardrail metrics.

## 30-Second Interview Pitch

FunnelLens is a Product Analyst project where I analyze e-commerce user events from view to cart to purchase. I clean and sessionize event data in SQL, calculate funnel conversion and retention cohorts, use Python for EDA and heatmaps, and build a Power BI dashboard. The final output is a product decision memo recommending which part of the funnel to improve and how to test it using an experiment with primary and guardrail metrics.

## What Makes This 5/5

- It uses event-level product data, not only sales data.
- It has SQL depth through sessionization, funnel queries, cohorts, and window functions.
- It shows product judgment: metric tree, diagnosis, experiment, guardrail.
- It avoids fake claims.
- It ends with a decision, not only charts.
