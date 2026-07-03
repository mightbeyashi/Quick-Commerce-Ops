from __future__ import annotations

import html
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "zepto_v2.csv"
PROCESSED = ROOT / "data" / "processed"
EXCEL = ROOT / "excel"
REPORT = ROOT / "report"
CHARTS = REPORT / "assets" / "charts"
TABLES = REPORT / "assets" / "tables"

SCENARIO_SEED = 42
SCENARIO_DAYS = 30
SCENARIO_ORDER_LINES = 8000
SCENARIO_LABEL = "SIMULATED_SCENARIO_NOT_ACTUAL_ORDER_HISTORY"


def ensure_dirs() -> None:
    for path in [PROCESSED, EXCEL, CHARTS, TABLES]:
        path.mkdir(parents=True, exist_ok=True)


def money(series: pd.Series) -> pd.Series:
    return (series.astype(float) / 100).round(2)


def load_and_clean() -> pd.DataFrame:
    raw = pd.read_csv(RAW_CSV, encoding="cp1252")
    df = raw.rename(
        columns={
            "Category": "category",
            "name": "product_name",
            "mrp": "mrp_paise",
            "discountPercent": "discount_percent",
            "availableQuantity": "available_quantity",
            "discountedSellingPrice": "discounted_selling_price_paise",
            "weightInGms": "weight_gms",
            "outOfStock": "out_of_stock",
            "quantity": "pack_quantity",
        }
    ).copy()

    text_columns = ["category", "product_name"]
    for column in text_columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.replace("\u2019", "'", regex=False)
            .str.replace("\u2018", "'", regex=False)
            .str.replace("\u201c", '"', regex=False)
            .str.replace("\u201d", '"', regex=False)
            .str.strip()
        )

    numeric_columns = [
        "mrp_paise",
        "discount_percent",
        "available_quantity",
        "discounted_selling_price_paise",
        "weight_gms",
        "pack_quantity",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["sku_id"] = np.arange(1, len(df) + 1)
    df["mrp_rupees"] = money(df["mrp_paise"])
    df["selling_price_rupees"] = money(df["discounted_selling_price_paise"])
    df["discount_amount_rupees"] = (df["mrp_rupees"] - df["selling_price_rupees"]).round(2)
    df["out_of_stock"] = df["out_of_stock"].astype(bool)
    df["is_out_of_stock"] = (df["out_of_stock"]) | (df["available_quantity"].fillna(0) <= 0)
    df["has_invalid_commercials"] = (
        (df["mrp_paise"].fillna(0) <= 0)
        | (df["discounted_selling_price_paise"].fillna(0) <= 0)
        | (df["weight_gms"].fillna(0) <= 0)
    )
    df["price_per_100g"] = np.where(
        df["weight_gms"] > 0,
        df["selling_price_rupees"] / (df["weight_gms"] / 100),
        np.nan,
    )
    df["price_per_100g"] = df["price_per_100g"].round(2)
    df["available_inventory_value_rupees"] = np.where(
        df["available_quantity"] > 0,
        df["available_quantity"] * df["selling_price_rupees"],
        0,
    ).round(2)

    df["weight_bucket"] = np.select(
        [
            df["weight_gms"] <= 0,
            df["weight_gms"] < 100,
            df["weight_gms"] < 500,
            df["weight_gms"] <= 1000,
            df["weight_gms"] > 1000,
        ],
        ["unknown", "tiny", "small", "standard", "bulk"],
        default="unknown",
    )
    df["discount_band"] = np.select(
        [
            df["discount_percent"] == 0,
            df["discount_percent"] < 10,
            df["discount_percent"] < 25,
            df["discount_percent"] >= 25,
        ],
        ["no discount", "low", "medium", "high"],
        default="unknown",
    )
    df["availability_status"] = np.select(
        [
            df["is_out_of_stock"],
            df["available_quantity"] <= 2,
            df["available_quantity"] <= 4,
            df["available_quantity"] > 4,
        ],
        ["out of stock", "low stock", "medium stock", "healthy stock"],
        default="unknown",
    )

    ordered_columns = [
        "sku_id",
        "category",
        "product_name",
        "mrp_paise",
        "discounted_selling_price_paise",
        "mrp_rupees",
        "selling_price_rupees",
        "discount_percent",
        "discount_amount_rupees",
        "available_quantity",
        "weight_gms",
        "pack_quantity",
        "out_of_stock",
        "is_out_of_stock",
        "has_invalid_commercials",
        "price_per_100g",
        "weight_bucket",
        "discount_band",
        "availability_status",
        "available_inventory_value_rupees",
    ]
    return df[ordered_columns]


def build_data_quality_tables(
    clean: pd.DataFrame,
    category_health: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    commercial_signature = [
        "product_name",
        "mrp_rupees",
        "selling_price_rupees",
        "discount_percent",
        "available_quantity",
        "weight_gms",
        "is_out_of_stock",
    ]
    distinct_commercial_records = clean[commercial_signature].drop_duplicates().shape[0]

    multi_category_products = (
        clean.groupby("product_name", as_index=False)
        .agg(
            sku_rows=("sku_id", "count"),
            category_count=("category", "nunique"),
            categories=("category", lambda s: ", ".join(sorted(set(s)))),
            min_mrp_rupees=("mrp_rupees", "min"),
            max_mrp_rupees=("mrp_rupees", "max"),
        )
        .query("category_count > 1")
        .sort_values(["category_count", "sku_rows", "product_name"], ascending=[False, False, True])
    )

    duplicate_catalog_signatures = (
        clean.groupby(commercial_signature, as_index=False)
        .agg(
            sku_rows=("sku_id", "count"),
            category_count=("category", "nunique"),
            categories=("category", lambda s: ", ".join(sorted(set(s)))),
        )
        .query("sku_rows > 1")
        .sort_values(["category_count", "sku_rows", "product_name"], ascending=[False, False, True])
    )

    category_metric_columns = [
        "total_skus",
        "available_skus",
        "out_of_stock_skus",
        "avg_discount_pct",
        "avg_mrp_rupees",
        "available_inventory_value_rupees",
        "avg_price_per_100g",
        "stockout_rate_pct",
    ]
    category_metric_duplicates = (
        category_health.groupby(category_metric_columns, as_index=False)
        .agg(
            category_count=("category", "nunique"),
            categories=("category", lambda s: ", ".join(sorted(set(s)))),
        )
        .query("category_count > 1")
        .sort_values(["category_count", "total_skus"], ascending=[False, False])
    )

    data_quality_summary = pd.DataFrame(
        [
            {
                "metric": "raw_inventory_rows",
                "value": len(clean),
                "interpretation": "Rows present in the source inventory export.",
            },
            {
                "metric": "commercially_valid_rows",
                "value": int((~clean["has_invalid_commercials"]).sum()),
                "interpretation": "Rows usable for price, discount, inventory value, and stockout analysis.",
            },
            {
                "metric": "invalid_commercial_rows",
                "value": int(clean["has_invalid_commercials"].sum()),
                "interpretation": "Rows excluded from commercial calculations because price or weight is invalid.",
            },
            {
                "metric": "unique_product_names",
                "value": clean["product_name"].nunique(),
                "interpretation": "Distinct product names after basic text cleaning.",
            },
            {
                "metric": "distinct_commercial_records",
                "value": distinct_commercial_records,
                "interpretation": "Distinct product-price-quantity-weight-stock signatures.",
            },
            {
                "metric": "duplicate_like_rows",
                "value": len(clean) - distinct_commercial_records,
                "interpretation": "Rows that repeat an existing commercial signature. This is a data-quality limitation, not a business claim.",
            },
            {
                "metric": "products_in_multiple_categories",
                "value": len(multi_category_products),
                "interpretation": "Product names that appear under more than one category in the raw dataset.",
            },
            {
                "metric": "category_metric_duplicate_groups",
                "value": len(category_metric_duplicates),
                "interpretation": "Category groups with identical aggregate KPIs. These should be called out in interviews.",
            },
        ]
    )

    return {
        "data_quality_summary": data_quality_summary,
        "multi_category_products": multi_category_products,
        "duplicate_catalog_signatures": duplicate_catalog_signatures,
        "category_metric_duplicates": category_metric_duplicates,
    }


def build_scenario_order_layer(
    valid: pd.DataFrame,
    category_health: pd.DataFrame,
    watchlist: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(SCENARIO_SEED)
    sku_pool = valid.merge(
        category_health[["category", "stockout_rate_pct", "total_skus"]],
        on="category",
        how="left",
    ).copy()

    price_weight = 1 / np.sqrt(sku_pool["selling_price_rupees"].clip(lower=1))
    discount_weight = 1 + (sku_pool["discount_percent"].fillna(0) / 100)
    category_pressure_weight = 1 + (sku_pool["stockout_rate_pct"].fillna(0) / 100)
    availability_weight = np.where(sku_pool["is_out_of_stock"], 0.75, 1.0)
    weights = price_weight * discount_weight * category_pressure_weight * availability_weight
    weights = weights / weights.sum()

    selected_positions = rng.choice(sku_pool.index.to_numpy(), size=SCENARIO_ORDER_LINES, replace=True, p=weights)
    selected = sku_pool.loc[selected_positions].reset_index(drop=True)

    ordered_units = rng.choice([1, 1, 1, 1, 2, 2, 3], size=SCENARIO_ORDER_LINES)
    stockout_probability = np.select(
        [
            selected["is_out_of_stock"],
            selected["available_quantity"] <= 2,
            selected["available_quantity"] <= 4,
            selected["available_quantity"] > 4,
        ],
        [1.00, 0.55, 0.22, 0.06],
        default=0.10,
    )
    stockout_flag = rng.random(SCENARIO_ORDER_LINES) < stockout_probability
    units_fulfilled = np.where(stockout_flag, 0, ordered_units)
    substitution_accepted = np.where(stockout_flag, rng.random(SCENARIO_ORDER_LINES) < 0.32, False)

    delivery_minutes = np.clip(rng.normal(17, 4, SCENARIO_ORDER_LINES), 8, 35).round(0)
    delivery_minutes = np.where(stockout_flag & substitution_accepted, delivery_minutes + 4, delivery_minutes)
    delivery_minutes = np.where(stockout_flag & ~substitution_accepted, np.nan, delivery_minutes)

    order_dates = pd.Timestamp("2026-01-01") + pd.to_timedelta(
        rng.integers(0, SCENARIO_DAYS, SCENARIO_ORDER_LINES),
        unit="D",
    )
    selling_price = selected["selling_price_rupees"].to_numpy()
    gross_demand_value = (ordered_units * selling_price).round(2)
    fulfilled_revenue = (units_fulfilled * selling_price).round(2)
    unfulfilled_value = (gross_demand_value - fulfilled_revenue).round(2)

    scenario_order_events = pd.DataFrame(
        {
            "order_id": [f"QCO-SCN-{i:05d}" for i in range(1, SCENARIO_ORDER_LINES + 1)],
            "sku_id": selected["sku_id"].to_numpy(),
            "customer_id": [f"C{value:05d}" for value in rng.integers(1, 1801, SCENARIO_ORDER_LINES)],
            "dark_store_id": [f"DS_{value:02d}" for value in rng.integers(1, 6, SCENARIO_ORDER_LINES)],
            "order_date": order_dates.strftime("%Y-%m-%d"),
            "category": selected["category"].to_numpy(),
            "product_name": selected["product_name"].to_numpy(),
            "units_ordered": ordered_units,
            "units_fulfilled": units_fulfilled,
            "stockout_flag": stockout_flag,
            "substitution_accepted": substitution_accepted,
            "selling_price_rupees": selling_price.round(2),
            "gross_demand_value_rupees": gross_demand_value,
            "fulfilled_revenue_rupees": fulfilled_revenue,
            "unfulfilled_value_rupees": unfulfilled_value,
            "delivery_minutes": delivery_minutes,
            "data_origin": SCENARIO_LABEL,
        }
    )

    scenario_category_metrics = (
        scenario_order_events.groupby("category", as_index=False)
        .agg(
            scenario_order_lines=("order_id", "count"),
            scenario_units_ordered=("units_ordered", "sum"),
            scenario_units_fulfilled=("units_fulfilled", "sum"),
            scenario_stockout_orders=("stockout_flag", "sum"),
            scenario_unfulfilled_value_rupees=("unfulfilled_value_rupees", "sum"),
            scenario_fulfilled_revenue_rupees=("fulfilled_revenue_rupees", "sum"),
            substitution_acceptances=("substitution_accepted", "sum"),
        )
        .assign(
            scenario_fill_rate_pct=lambda x: (
                x["scenario_units_fulfilled"] / x["scenario_units_ordered"] * 100
            ).round(2),
            scenario_order_stockout_rate_pct=lambda x: (
                x["scenario_stockout_orders"] / x["scenario_order_lines"] * 100
            ).round(2),
            scenario_unfulfilled_value_rupees=lambda x: x["scenario_unfulfilled_value_rupees"].round(2),
            scenario_fulfilled_revenue_rupees=lambda x: x["scenario_fulfilled_revenue_rupees"].round(2),
            data_origin=SCENARIO_LABEL,
        )
        .sort_values("scenario_unfulfilled_value_rupees", ascending=False)
    )

    scenario_sku_impact = (
        scenario_order_events.groupby(["sku_id", "category", "product_name"], as_index=False)
        .agg(
            scenario_order_lines=("order_id", "count"),
            scenario_units_ordered=("units_ordered", "sum"),
            scenario_units_fulfilled=("units_fulfilled", "sum"),
            scenario_stockout_orders=("stockout_flag", "sum"),
            scenario_unfulfilled_value_rupees=("unfulfilled_value_rupees", "sum"),
            scenario_fulfilled_revenue_rupees=("fulfilled_revenue_rupees", "sum"),
        )
        .assign(
            scenario_fill_rate_pct=lambda x: (
                x["scenario_units_fulfilled"] / x["scenario_units_ordered"] * 100
            ).round(2),
            scenario_unfulfilled_value_rupees=lambda x: x["scenario_unfulfilled_value_rupees"].round(2),
            scenario_fulfilled_revenue_rupees=lambda x: x["scenario_fulfilled_revenue_rupees"].round(2),
            data_origin=SCENARIO_LABEL,
        )
        .merge(
            watchlist[["sku_id", "priority_rank", "priority_score"]],
            on="sku_id",
            how="left",
        )
        .sort_values(["scenario_unfulfilled_value_rupees", "scenario_stockout_orders"], ascending=[False, False])
    )
    scenario_sku_impact["priority_rank"] = scenario_sku_impact["priority_rank"].fillna(0).astype(int)
    scenario_sku_impact["priority_score"] = scenario_sku_impact["priority_score"].fillna(0).astype(int)

    total_units = scenario_order_events["units_ordered"].sum()
    total_fulfilled_units = scenario_order_events["units_fulfilled"].sum()
    stockout_orders = int(scenario_order_events["stockout_flag"].sum())
    scenario_executive_metrics = pd.DataFrame(
        [
            {"metric": "scenario_data_origin", "value": SCENARIO_LABEL},
            {"metric": "scenario_seed", "value": SCENARIO_SEED},
            {"metric": "scenario_days", "value": SCENARIO_DAYS},
            {"metric": "scenario_order_lines", "value": SCENARIO_ORDER_LINES},
            {"metric": "scenario_units_ordered", "value": int(total_units)},
            {"metric": "scenario_units_fulfilled", "value": int(total_fulfilled_units)},
            {"metric": "scenario_fill_rate_pct", "value": round(total_fulfilled_units / total_units * 100, 2)},
            {"metric": "scenario_stockout_order_rate_pct", "value": round(stockout_orders / SCENARIO_ORDER_LINES * 100, 2)},
            {
                "metric": "scenario_unfulfilled_value_rupees",
                "value": round(scenario_order_events["unfulfilled_value_rupees"].sum(), 2),
            },
            {
                "metric": "scenario_substitution_acceptance_rate_pct",
                "value": round(
                    scenario_order_events.loc[scenario_order_events["stockout_flag"], "substitution_accepted"].mean()
                    * 100,
                    2,
                ),
            },
        ]
    )

    top_priority = scenario_sku_impact.loc[scenario_sku_impact["priority_rank"] > 0].sort_values(
        ["priority_rank", "scenario_unfulfilled_value_rupees"],
        ascending=[True, False],
    )
    top_25_priority_value = round(top_priority.head(25)["scenario_unfulfilled_value_rupees"].sum(), 2)
    top_50_priority_value = round(top_priority.head(50)["scenario_unfulfilled_value_rupees"].sum(), 2)
    total_unfulfilled_value = round(scenario_order_events["unfulfilled_value_rupees"].sum(), 2)
    scenario_what_if_model = pd.DataFrame(
        [
            {
                "scenario": "Reduce stockout failures by 20% for top 25 priority SKUs",
                "baseline_scope_unfulfilled_value_rupees": top_25_priority_value,
                "assumed_stockout_reduction_pct": 20,
                "scenario_recovered_value_rupees": round(top_25_priority_value * 0.20, 2),
                "data_origin": SCENARIO_LABEL,
                "honesty_note": "Scenario estimate only. The source dataset has no historical orders or margins.",
            },
            {
                "scenario": "Reduce stockout failures by 20% for top 50 priority SKUs",
                "baseline_scope_unfulfilled_value_rupees": top_50_priority_value,
                "assumed_stockout_reduction_pct": 20,
                "scenario_recovered_value_rupees": round(top_50_priority_value * 0.20, 2),
                "data_origin": SCENARIO_LABEL,
                "honesty_note": "Scenario estimate only. The source dataset has no historical orders or margins.",
            },
            {
                "scenario": "Reduce all scenario stockout failures by 10%",
                "baseline_scope_unfulfilled_value_rupees": total_unfulfilled_value,
                "assumed_stockout_reduction_pct": 10,
                "scenario_recovered_value_rupees": round(total_unfulfilled_value * 0.10, 2),
                "data_origin": SCENARIO_LABEL,
                "honesty_note": "Scenario estimate only. The source dataset has no historical orders or margins.",
            },
        ]
    )

    experiment_design = pd.DataFrame(
        [
            {
                "experiment_area": "Replenishment alert",
                "hypothesis": "Showing a daily priority alert for high-risk SKUs will reduce stockout order rate.",
                "primary_metric": "Stockout order rate",
                "guardrail_metric": "Average delivery minutes",
                "success_rule": "Treatment stores reduce stockout order rate without worsening delivery time.",
            },
            {
                "experiment_area": "Substitution prompt",
                "hypothesis": "Suggesting substitutes for unavailable SKUs will recover some abandoned demand.",
                "primary_metric": "Substitution acceptance rate",
                "guardrail_metric": "Refund or complaint rate",
                "success_rule": "Substitution acceptance improves while complaint rate does not increase.",
            },
            {
                "experiment_area": "Category operations focus",
                "hypothesis": "Focusing replenishment work on high-stockout and high-value categories improves fill rate faster.",
                "primary_metric": "Fill rate",
                "guardrail_metric": "Inventory value tied up",
                "success_rule": "Fill rate improves while inventory value does not grow disproportionately.",
            },
        ]
    )

    return {
        "scenario_order_events": scenario_order_events,
        "scenario_category_metrics": scenario_category_metrics,
        "scenario_sku_impact_watchlist": scenario_sku_impact,
        "scenario_executive_metrics": scenario_executive_metrics,
        "scenario_what_if_model": scenario_what_if_model,
        "experiment_design": experiment_design,
    }


def build_tables(clean: pd.DataFrame) -> dict[str, pd.DataFrame]:
    valid = clean.loc[~clean["has_invalid_commercials"]].copy()

    category_health = (
        valid.groupby("category", as_index=False)
        .agg(
            total_skus=("sku_id", "count"),
            available_skus=("is_out_of_stock", lambda s: int((~s).sum())),
            out_of_stock_skus=("is_out_of_stock", lambda s: int(s.sum())),
            avg_discount_pct=("discount_percent", "mean"),
            avg_mrp_rupees=("mrp_rupees", "mean"),
            available_inventory_value_rupees=("available_inventory_value_rupees", "sum"),
            avg_price_per_100g=("price_per_100g", "mean"),
        )
        .assign(
            stockout_rate_pct=lambda x: (x["out_of_stock_skus"] / x["total_skus"] * 100).round(2),
            avg_discount_pct=lambda x: x["avg_discount_pct"].round(2),
            avg_mrp_rupees=lambda x: x["avg_mrp_rupees"].round(2),
            available_inventory_value_rupees=lambda x: x["available_inventory_value_rupees"].round(2),
            avg_price_per_100g=lambda x: x["avg_price_per_100g"].round(2),
        )
        .sort_values(["stockout_rate_pct", "total_skus"], ascending=[False, False])
    )

    with_context = valid.merge(
        category_health[["category", "stockout_rate_pct"]],
        on="category",
        how="left",
    )
    with_context["priority_score"] = (
        np.where(with_context["is_out_of_stock"], 45, 0)
        + np.where(with_context["available_quantity"].between(1, 2), 20, 0)
        + np.where(with_context["mrp_rupees"] >= 500, 15, 0)
        + np.where(with_context["stockout_rate_pct"] >= 15, 10, 0)
        + np.where(with_context["discount_percent"].between(5, 25), 5, 0)
        + np.where(with_context["weight_bucket"].isin(["standard", "bulk"]), 5, 0)
    )
    watchlist = (
        with_context.loc[
            with_context["is_out_of_stock"] | (with_context["available_quantity"] <= 2),
            [
                "sku_id",
                "category",
                "product_name",
                "mrp_rupees",
                "selling_price_rupees",
                "discount_percent",
                "available_quantity",
                "weight_gms",
                "is_out_of_stock",
                "stockout_rate_pct",
                "available_inventory_value_rupees",
                "priority_score",
            ],
        ]
        .sort_values(["priority_score", "mrp_rupees", "category", "product_name"], ascending=[False, False, True, True])
        .reset_index(drop=True)
    )
    watchlist.insert(0, "priority_rank", np.arange(1, len(watchlist) + 1))

    discount_exposure = valid.loc[valid["discount_percent"] >= 25].copy()
    discount_exposure["available_discount_exposure_rupees"] = (
        discount_exposure["discount_amount_rupees"] * discount_exposure["available_quantity"]
    ).round(2)
    discount_exposure = discount_exposure[
        [
            "sku_id",
            "category",
            "product_name",
            "mrp_rupees",
            "selling_price_rupees",
            "discount_percent",
            "discount_amount_rupees",
            "available_quantity",
            "available_discount_exposure_rupees",
            "discount_band",
            "is_out_of_stock",
        ]
    ].sort_values(["available_discount_exposure_rupees", "discount_percent"], ascending=[False, False])

    audit = pd.DataFrame(
        [
            {"metric": "raw_rows", "value": len(clean)},
            {"metric": "valid_commercial_rows", "value": int((~clean["has_invalid_commercials"]).sum())},
            {"metric": "invalid_commercial_rows", "value": int(clean["has_invalid_commercials"].sum())},
            {"metric": "categories", "value": clean["category"].nunique()},
            {"metric": "unique_product_names", "value": clean["product_name"].nunique()},
            {"metric": "raw_stockout_rate_pct", "value": round(clean["is_out_of_stock"].mean() * 100, 2)},
            {"metric": "avg_discount_pct", "value": round(valid["discount_percent"].mean(), 2)},
            {
                "metric": "available_inventory_value_rupees",
                "value": round(valid["available_inventory_value_rupees"].sum(), 2),
            },
        ]
    )

    quality_tables = build_data_quality_tables(clean, category_health)
    scenario_tables = build_scenario_order_layer(valid, category_health, watchlist)

    decision_inputs = category_health.copy()
    decision_inputs["target_stockout_rate_pct"] = 10.0
    decision_inputs["stockout_gap_pct"] = (
        decision_inputs["stockout_rate_pct"] - decision_inputs["target_stockout_rate_pct"]
    ).clip(lower=0).round(2)
    decision_inputs["priority_category_flag"] = np.where(
        (decision_inputs["stockout_gap_pct"] > 0)
        & (decision_inputs["available_inventory_value_rupees"] >= decision_inputs["available_inventory_value_rupees"].median()),
        "priority",
        "monitor",
    )

    return {
        "clean_inventory": clean,
        "valid_inventory": valid,
        "category_health": category_health,
        "replenishment_watchlist": watchlist,
        "discount_exposure": discount_exposure,
        "data_audit": audit,
        "excel_decision_model_inputs": decision_inputs,
        **quality_tables,
        **scenario_tables,
    }


def save_tables(tables: dict[str, pd.DataFrame]) -> None:
    clean_for_sql = tables["clean_inventory"][
        [
            "category",
            "product_name",
            "mrp_paise",
            "discount_percent",
            "available_quantity",
            "discounted_selling_price_paise",
            "weight_gms",
            "out_of_stock",
            "pack_quantity",
        ]
    ].copy()
    clean_for_sql["out_of_stock"] = clean_for_sql["out_of_stock"].map({True: "TRUE", False: "FALSE"})
    clean_for_sql.to_csv(PROCESSED / "zepto_inventory_utf8.csv", index=False)

    for name, table in tables.items():
        table.to_csv(PROCESSED / f"{name}.csv", index=False)

    excel_exports = {
        "category_health_for_excel.csv": tables["category_health"],
        "replenishment_watchlist_for_excel.csv": tables["replenishment_watchlist"],
        "discount_exposure_for_excel.csv": tables["discount_exposure"],
        "excel_decision_model_inputs.csv": tables["excel_decision_model_inputs"],
        "data_quality_summary_for_excel.csv": tables["data_quality_summary"],
        "multi_category_products_for_excel.csv": tables["multi_category_products"],
        "scenario_order_events_for_power_bi.csv": tables["scenario_order_events"],
        "scenario_category_metrics_for_power_bi.csv": tables["scenario_category_metrics"],
        "scenario_sku_impact_watchlist_for_excel.csv": tables["scenario_sku_impact_watchlist"],
        "scenario_what_if_model_for_excel.csv": tables["scenario_what_if_model"],
        "experiment_design_for_excel.csv": tables["experiment_design"],
    }
    for filename, table in excel_exports.items():
        table.to_csv(EXCEL / filename, index=False)


def make_charts(tables: dict[str, pd.DataFrame]) -> None:
    plt.rcParams.update({"figure.figsize": (11, 6), "axes.grid": True})

    category = tables["category_health"].sort_values("stockout_rate_pct", ascending=True)
    plt.figure()
    plt.barh(category["category"], category["stockout_rate_pct"], color="#174d7c")
    plt.xlabel("Stockout rate (%)")
    plt.title("Category Stockout Rate")
    plt.tight_layout()
    plt.savefig(CHARTS / "category_stockout_rate.png", dpi=160)
    plt.close()

    valid = tables["valid_inventory"]
    plt.figure()
    plt.hist(valid["discount_percent"], bins=20, color="#0f6b4f", edgecolor="white")
    plt.xlabel("Discount percent")
    plt.ylabel("SKU count")
    plt.title("Discount Distribution")
    plt.tight_layout()
    plt.savefig(CHARTS / "discount_distribution.png", dpi=160)
    plt.close()

    plt.figure()
    sample = valid.sample(min(1200, len(valid)), random_state=7)
    colors = np.where(sample["is_out_of_stock"], "#a33232", "#174d7c")
    plt.scatter(sample["mrp_rupees"], sample["discount_percent"], c=colors, alpha=0.65, s=22)
    plt.xlabel("MRP (rupees)")
    plt.ylabel("Discount percent")
    plt.title("Price vs Discount by Stock Status")
    plt.tight_layout()
    plt.savefig(CHARTS / "price_discount_stock_status.png", dpi=160)
    plt.close()

    top_watchlist = tables["replenishment_watchlist"].head(15).sort_values("priority_score")
    labels = top_watchlist["product_name"].str.slice(0, 38)
    plt.figure()
    plt.barh(labels, top_watchlist["priority_score"], color="#a45b00")
    plt.xlabel("Priority score")
    plt.title("Top Replenishment Watchlist SKUs")
    plt.tight_layout()
    plt.savefig(CHARTS / "top_replenishment_watchlist.png", dpi=160)
    plt.close()

    scenario_category = tables["scenario_category_metrics"].head(10).sort_values("scenario_unfulfilled_value_rupees")
    plt.figure()
    plt.barh(
        scenario_category["category"],
        scenario_category["scenario_unfulfilled_value_rupees"],
        color="#7a3e9d",
    )
    plt.xlabel("Scenario unfulfilled value (rupees)")
    plt.title("Scenario Revenue-at-Risk by Category")
    plt.tight_layout()
    plt.savefig(CHARTS / "scenario_unfulfilled_value_by_category.png", dpi=160)
    plt.close()

    what_if = tables["scenario_what_if_model"].sort_values("scenario_recovered_value_rupees")
    plt.figure()
    plt.barh(what_if["scenario"], what_if["scenario_recovered_value_rupees"], color="#0a7f83")
    plt.xlabel("Scenario recovered value (rupees)")
    plt.title("What-If Recovery Scenarios")
    plt.tight_layout()
    plt.savefig(CHARTS / "scenario_what_if_recovery.png", dpi=160)
    plt.close()


def html_table(df: pd.DataFrame, max_rows: int = 10) -> str:
    display = df.head(max_rows).copy()
    return display.to_html(index=False, classes="data-table", border=0, escape=True)


def format_number(value: float | int) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.2f}"
    return f"{value:,.0f}"


def generate_report(tables: dict[str, pd.DataFrame]) -> None:
    audit = tables["data_audit"].set_index("metric")["value"].to_dict()
    quality = tables["data_quality_summary"].set_index("metric")["value"].to_dict()
    scenario_summary = tables["scenario_executive_metrics"].set_index("metric")["value"].to_dict()
    category = tables["category_health"]
    watchlist = tables["replenishment_watchlist"]
    discount = tables["discount_exposure"]
    scenario_category = tables["scenario_category_metrics"]
    scenario_sku = tables["scenario_sku_impact_watchlist"]
    what_if = tables["scenario_what_if_model"]
    experiment = tables["experiment_design"]
    multi_category = tables["multi_category_products"]

    top_category = category.iloc[0]
    highest_value_category = category.sort_values("available_inventory_value_rupees", ascending=False).iloc[0]
    top_sku = watchlist.iloc[0]
    top_scenario_category = scenario_category.iloc[0]
    top_scenario_sku = scenario_sku.iloc[0]

    for name, table in {
        "category_health_top.csv": category.head(12),
        "replenishment_watchlist_top.csv": watchlist.head(25),
        "discount_exposure_top.csv": discount.head(25),
        "data_quality_summary.csv": tables["data_quality_summary"],
        "multi_category_products_top.csv": multi_category.head(50),
        "scenario_category_metrics_top.csv": scenario_category.head(12),
        "scenario_sku_impact_top.csv": scenario_sku.head(50),
        "scenario_what_if_model.csv": what_if,
        "experiment_design.csv": experiment,
    }.items():
        table.to_csv(TABLES / name, index=False)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>QuickCommerceOps Inventory Analytics</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Entry-Level DA + PA Portfolio Project</p>
      <h1>QuickCommerceOps</h1>
      <p class="subtitle">A quick-commerce analytics project that turns a real SKU inventory export into category health KPIs, replenishment priorities, data-quality findings, and a clearly labeled product analytics scenario model.</p>
      <div>
        <span class="badge">SQL</span>
        <span class="badge">Power BI-ready CSV</span>
        <span class="badge">Python pandas</span>
        <span class="badge">numpy</span>
        <span class="badge">matplotlib</span>
        <span class="badge">Experiment design</span>
        <span class="badge">Scenario modeling</span>
      </div>
    </section>

    <section>
      <h2>Executive Snapshot</h2>
      <div class="grid grid-4">
        <div class="card"><div class="metric-label">Raw SKU rows</div><div class="metric-value">{format_number(audit["raw_rows"])}</div></div>
        <div class="card"><div class="metric-label">Categories</div><div class="metric-value">{format_number(audit["categories"])}</div></div>
        <div class="card"><div class="metric-label">Observed stockout rate</div><div class="metric-value metric-bad">{format_number(audit["raw_stockout_rate_pct"])}%</div></div>
        <div class="card"><div class="metric-label">Observed inventory value proxy</div><div class="metric-value metric-good">Rs {format_number(audit["available_inventory_value_rupees"])}</div></div>
        <div class="card"><div class="metric-label">Distinct commercial records</div><div class="metric-value">{format_number(quality["distinct_commercial_records"])}</div></div>
        <div class="card"><div class="metric-label">Duplicate-like rows</div><div class="metric-value metric-warn">{format_number(quality["duplicate_like_rows"])}</div></div>
        <div class="card"><div class="metric-label">Scenario fill rate</div><div class="metric-value metric-good">{format_number(float(scenario_summary["scenario_fill_rate_pct"]))}%</div></div>
        <div class="card"><div class="metric-label">Scenario unfulfilled value</div><div class="metric-value metric-bad">Rs {format_number(float(scenario_summary["scenario_unfulfilled_value_rupees"]))}</div></div>
      </div>
      <div class="callout">
        <strong>Honesty note:</strong> the source file is an inventory snapshot, not company order history. Observed stockout, price, discount, and inventory-value numbers come from the dataset. Order-level demand, fill rate, and unfulfilled value are scenario outputs generated from transparent assumptions and must not be presented as actual sales.
      </div>
    </section>

    <section>
      <h2>Business Problem</h2>
      <p>Quick-commerce customers expect products to be available immediately. Stockouts can reduce conversion, hurt trust, and push customers to substitute or leave. The goal of this project is to help an operations or category team identify which SKUs and categories need attention first.</p>
      <ol>
        <li>Find categories with weak availability.</li>
        <li>Rank out-of-stock and low-stock SKUs by operational priority.</li>
        <li>Highlight high-discount products where discount exposure is concentrated.</li>
        <li>Estimate what a Product Analyst would measure if order data were available.</li>
        <li>Prepare clean tables for Excel, SQL practice, and Power BI dashboards.</li>
      </ol>
    </section>

    <section>
      <h2>Observed Inventory Findings</h2>
      <div class="grid grid-2">
        <div class="card">
          <h3>Highest stockout category</h3>
          <p><strong>{html.escape(str(top_category["category"]))}</strong> has a stockout rate of <strong>{top_category["stockout_rate_pct"]}%</strong> across <strong>{int(top_category["total_skus"])}</strong> SKUs.</p>
        </div>
        <div class="card">
          <h3>Highest inventory value category</h3>
          <p><strong>{html.escape(str(highest_value_category["category"]))}</strong> carries the highest available inventory value proxy at <strong>Rs {format_number(highest_value_category["available_inventory_value_rupees"])}</strong>.</p>
        </div>
        <div class="card">
          <h3>Top replenishment SKU</h3>
          <p><strong>{html.escape(str(top_sku["product_name"]))}</strong> is ranked first in the watchlist with a priority score of <strong>{int(top_sku["priority_score"])}</strong>.</p>
        </div>
        <div class="card">
          <h3>Discount exposure</h3>
          <p>The high-discount table contains <strong>{format_number(len(discount))}</strong> SKUs with discount percent at or above 25%.</p>
        </div>
      </div>
    </section>

    <section>
      <h2>Data Quality Findings</h2>
      <p>This section is intentionally included because a strong analyst does not hide data limitations. The source has repeated commercial signatures and products that appear under multiple categories, so category-level analysis should be treated as useful but imperfect.</p>
      <div class="table-wrap">{html_table(tables["data_quality_summary"], 12)}</div>
      <h3>Products Appearing In Multiple Categories</h3>
      <div class="table-wrap">{html_table(multi_category, 10)}</div>
    </section>

    <section>
      <h2>Product Analytics Scenario</h2>
      <p>The scenario order layer creates interview-ready Product Analyst metrics without pretending they are real company sales. It lets the project answer fill-rate, unfulfilled demand, substitution, and what-if questions using reproducible assumptions.</p>
      <div class="grid grid-2">
        <div class="card">
          <h3>Highest scenario unfulfilled category</h3>
          <p><strong>{html.escape(str(top_scenario_category["category"]))}</strong> has the highest scenario unfulfilled value at <strong>Rs {format_number(float(top_scenario_category["scenario_unfulfilled_value_rupees"]))}</strong>.</p>
        </div>
        <div class="card">
          <h3>Highest scenario SKU impact</h3>
          <p><strong>{html.escape(str(top_scenario_sku["product_name"]))}</strong> has the highest scenario unfulfilled value at <strong>Rs {format_number(float(top_scenario_sku["scenario_unfulfilled_value_rupees"]))}</strong>.</p>
        </div>
      </div>
      <div class="table-wrap">{html_table(scenario_category, 12)}</div>
    </section>

    <section>
      <h2>What-If Model</h2>
      <p>This is a Product Analyst decision layer: if operations reduces stockout failures for priority SKUs, what value could be recovered in the scenario model?</p>
      <div class="table-wrap">{html_table(what_if, 5)}</div>
    </section>

    <section>
      <h2>Experiment Design</h2>
      <p>This section turns the analysis into Product Analyst thinking: define a hypothesis, primary metric, guardrail metric, and success rule before shipping an operational change.</p>
      <div class="table-wrap">{html_table(experiment, 10)}</div>
    </section>

    <section>
      <h2>Power BI Dashboard Plan</h2>
      <div class="grid grid-2">
        <div class="card"><h3>Page 1: Executive Overview</h3><p>Observed stockout rate, inventory value proxy, scenario fill rate, scenario unfulfilled value, and priority SKU count.</p></div>
        <div class="card"><h3>Page 2: Category Health</h3><p>Category stockout rate, available inventory value, discount exposure, and scenario unfulfilled value.</p></div>
        <div class="card"><h3>Page 3: SKU Watchlist</h3><p>Priority-ranked SKUs with category, stock status, price band, scenario unfulfilled value, and filters.</p></div>
        <div class="card"><h3>Page 4: Product Experiment</h3><p>What-if recovery model, experiment design, primary metrics, and guardrails.</p></div>
      </div>
    </section>

    <section>
      <h2>Charts</h2>
      <div class="grid grid-2">
        <div><h3>Category Stockout Rate</h3><img class="chart" src="assets/charts/category_stockout_rate.png" alt="Category stockout rate chart"></div>
        <div><h3>Discount Distribution</h3><img class="chart" src="assets/charts/discount_distribution.png" alt="Discount distribution chart"></div>
        <div><h3>Price vs Discount</h3><img class="chart" src="assets/charts/price_discount_stock_status.png" alt="Price discount stock status chart"></div>
        <div><h3>Top SKU Watchlist</h3><img class="chart" src="assets/charts/top_replenishment_watchlist.png" alt="Top replenishment watchlist chart"></div>
        <div><h3>Scenario Category Risk</h3><img class="chart" src="assets/charts/scenario_unfulfilled_value_by_category.png" alt="Scenario unfulfilled value by category chart"></div>
        <div><h3>What-If Recovery</h3><img class="chart" src="assets/charts/scenario_what_if_recovery.png" alt="Scenario what-if recovery chart"></div>
      </div>
    </section>

    <section>
      <h2>Core Tables</h2>
      <h3>Category Health</h3>
      <p>Category-level availability, stockout rate, average discount, MRP, available inventory value, and price per 100g.</p>
      <div class="table-wrap">{html_table(category, 12)}</div>
      <h3>Replenishment Watchlist</h3>
      <p>Transparent rule-based score using out-of-stock status, low quantity, high MRP, category stockout pressure, discount, and weight bucket.</p>
      <div class="table-wrap">{html_table(watchlist, 15)}</div>
      <h3>Scenario SKU Impact</h3>
      <p>Scenario-based SKU ranking by unfulfilled value. This is useful for Product Analyst storytelling, but it is not actual historical revenue loss.</p>
      <div class="table-wrap">{html_table(scenario_sku, 15)}</div>
      <h3>Discount Exposure</h3>
      <p>This table identifies heavy discounting. It does not claim margin impact because cost and margin data are not available.</p>
      <div class="table-wrap">{html_table(discount, 15)}</div>
    </section>

    <section>
      <h2>How To Explain This In Interview</h2>
      <ul>
        <li><strong>Problem:</strong> quick-commerce availability and replenishment prioritization.</li>
        <li><strong>Data:</strong> 3.7K+ observed SKU inventory rows with category, price, discount, quantity, weight, and stock flag.</li>
        <li><strong>Data honesty:</strong> the dataset has no true orders, so Product Analyst metrics are scenario estimates, not actual company performance.</li>
        <li><strong>SQL:</strong> clean inventory view, category health view, discount exposure view, and replenishment watchlist.</li>
        <li><strong>Python:</strong> encoding fix, paise-to-rupee conversion, EDA, scoring, scenario simulation, charts, and exports.</li>
        <li><strong>Excel/Power BI:</strong> CSV outputs for dashboards, pivot tables, conditional formatting, and what-if analysis.</li>
        <li><strong>Product thinking:</strong> define fill rate, unfulfilled value, substitution acceptance, experiment metrics, and guardrails.</li>
      </ul>
    </section>

    <section>
      <h2>Limitations</h2>
      <p>This is an inventory snapshot, not a full company warehouse. It lacks actual demand, historical orders, gross margin, replenishment lead time, expiry, and real dark-store operations. Because of that, the report separates observed inventory facts from scenario-estimated product metrics.</p>
    </section>

    <p class="footer">Generated locally from the QuickCommerceOps project files.</p>
  </main>
</body>
</html>
"""
    (REPORT / "index.html").write_text(html_doc, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    clean = load_and_clean()
    tables = build_tables(clean)
    save_tables(tables)
    make_charts(tables)
    generate_report(tables)
    print("Generated QuickCommerceOps processed tables, charts, Excel-ready CSVs, and HTML report.")


if __name__ == "__main__":
    main()
