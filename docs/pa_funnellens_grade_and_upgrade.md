# Product Analyst Grade: FunnelLens Upgrade Review

Source reviewed: `/Users/mac/Downloads/Final-Analytics-Project-Suite-DA-PA.pdf`

## Honest Rating

Current PDF as a strategy document: **84/100**

Current FunnelLens as proof for Product Analyst roles: **55/100**

Potential after building the deliverables below: **95-97/100**

Why the gap exists: the PDF names the right PA themes, but it does not yet prove them with a working repo, SQL outputs, dashboard screenshots, cohort tables, experiment math, or a decision memo. For big-company fresher roles, the idea is strong, but the evidence must be stronger.

## What Is Already Strong

- Clear PA positioning: funnel, retention, experimentation, activation, product decision.
- Good dataset choice: RetailRocket-style event data maps well to e-commerce product analytics.
- Strong target-company fit for Myntra, Meesho, Eternal/Zomato-style consumer product analytics.
- Correct tooling stack: SQL, Python, Power BI, Excel, memo.
- Good honesty rule: do not fake numbers and label simulated metrics.

## What Is Missing For A 5/5 Fresher PA Project

1. A real event data model, not only a project description.
2. SQL scripts that build funnel, session, cohort, and experiment tables.
3. A product metric tree: North Star, input metrics, guardrails.
4. Segment-level funnel analysis: new vs returning, category, device/source if available.
5. Retention cohort heatmap with exact definitions.
6. Time-to-convert analysis.
7. Experiment design with hypothesis, primary metric, guardrail metric, MDE, sample size note, and ship/no-ship rule.
8. Product decision memo with one clear recommendation.
9. Dashboard screenshots or Power BI file.
10. Resume bullets using actual output numbers from the final analysis.

## 5-Star Rubric

| Area | Weight | Current | 5-Star Requirement |
| --- | ---: | ---: | --- |
| Product problem framing | 10 | 8 | One sharp product problem with user/business impact. |
| Event data model | 15 | 5 | Clean event fact table, user table, item/category table, session table. |
| SQL depth | 20 | 7 | CTEs, window functions, sessionization, funnel, retention, experiment tables. |
| Funnel diagnosis | 15 | 8 | Step conversion, drop-off, time-to-convert, segment comparisons. |
| Retention analysis | 15 | 7 | Weekly cohorts, D1/D7/W1/W2 retention, cohort quality explanation. |
| Experiment thinking | 15 | 6 | Hypothesis, primary metric, guardrail, MDE/sample size, decision rule. |
| Dashboard/storytelling | 5 | 3 | Four-page dashboard with screenshots and clear narrative. |
| Interview packaging | 5 | 4 | README, memo, resume bullets, 30-second pitch. |

## Upgrade Target

Build `FunnelLens` as:

**FunnelLens: E-commerce Activation, Retention and Experiment Analytics**

One-line pitch:

> Built a product analytics project on e-commerce event data to diagnose view-to-cart-to-purchase drop-off, measure cohort retention, identify high-intent user segments, and design an experiment to improve add-to-cart conversion with guardrail metrics.

## Non-Negotiable Honesty Rules

- If RetailRocket data is used, mention actual row counts only after loading the data.
- Do not claim real A/B test data unless the dataset contains true control/variant assignment.
- If you create variants for practice, label them as `scenario_experiment_not_actual_ab_test`.
- Say "scenario unfulfilled impact" or "estimated impact", not "actual revenue lift", unless proven from real orders.

## Source Basis

- Meesho analytics role language emphasizes Advanced SQL, Excel, Python as plus, statistics/probability, metrics, root cause analysis, and strategic planning: https://www.meesho.io/jobs/lead-business-analyst?id=ca616a8a-eeb4-4fbb-b0f8-596e17d8ed9a
- Mixpanel describes funnel analysis as measuring conversions through event sequences, finding drop-off, segment conversion, and user journey behavior: https://docs.mixpanel.com/docs/reports/funnels/funnels-overview
- Mixpanel retention documentation emphasizes engagement over time, retention rate, cohort buckets, and retention heatmaps: https://docs.mixpanel.com/docs/reports/retention
- Optimizely describes A/B testing as random traffic split, conversion-goal measurement, statistical analysis, clear goals, hypothesis, implementation checks, and result documentation: https://www.optimizely.com/optimization-glossary/ab-testing
- EY's hiring guidance emphasizes analytics mindset: extracting, transforming, interpreting data, translating complex data into useful insights, and communicating to stakeholders: https://www.ey.com/en_in/careers/what-we-look-for
