from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "learning-pack"
ASSETS = PACK / "assets"
SCREENSHOTS = ASSETS / "screenshots"
OUT = PACK / "QuickCommerceOps-Learning-Interview-Pack.html"


def esc(value: object) -> str:
    return html.escape(str(value))


def load_metrics() -> dict[str, object]:
    audit = pd.read_csv(ROOT / "data" / "processed" / "data_audit.csv").set_index("metric")["value"].to_dict()
    category = pd.read_csv(ROOT / "data" / "processed" / "category_health.csv")
    watchlist = pd.read_csv(ROOT / "data" / "processed" / "replenishment_watchlist.csv")
    discount = pd.read_csv(ROOT / "data" / "processed" / "discount_exposure.csv")
    return {
        "audit": audit,
        "category": category,
        "watchlist": watchlist,
        "discount": discount,
        "top_category": category.iloc[0].to_dict(),
        "top_sku": watchlist.iloc[0].to_dict(),
        "highest_value_category": category.sort_values("available_inventory_value_rupees", ascending=False).iloc[0].to_dict(),
    }


def load_sources() -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for path in sorted((ROOT / "research").glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        for item in data.get("data", {}).get("web", [])[:4]:
            title = item.get("title")
            url = item.get("url")
            if title and url:
                sources.append({"title": title, "url": url})
    seen = set()
    unique = []
    for source in sources:
        if source["url"] not in seen:
            seen.add(source["url"])
            unique.append(source)
    return unique[:28]


def table_html(df: pd.DataFrame, rows: int = 8) -> str:
    return df.head(rows).to_html(index=False, escape=True, classes="data-table", border=0)


def code_block(code: str) -> str:
    return f"<pre><code>{esc(code.strip())}</code></pre>"


def section(title: str, body: str, cls: str = "") -> str:
    return f'<section class="page {cls}"><h2>{esc(title)}</h2>{body}</section>'


def read_file(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def explain_python_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return "Technical: Blank line. Simple: It separates blocks so your eyes can read the code in chunks."
    if stripped.startswith("#"):
        return "Technical: Comment. Simple: A note for humans; Python skips it."
    if stripped.startswith("from __future__"):
        return "Technical: Future import for postponed annotations. Simple: It makes type hints safer and cleaner; it does not change the business logic."
    if stripped == "import html":
        return "Technical: Standard-library HTML helper import. Simple: Used when building the report so special characters like < and > do not break the HTML page."
    if stripped == "from pathlib import Path":
        return "Technical: Imports Path for object-based file paths. Simple: Lets the code handle folders and files cleanly instead of hard-coding messy strings."
    if stripped == "import matplotlib":
        return "Technical: Imports the base matplotlib plotting package. Simple: This is the chart-making library."
    if stripped == 'matplotlib.use("Agg")':
        return "Technical: Sets matplotlib to the non-GUI Agg backend before importing pyplot. Simple: It saves chart images without opening a window, which is needed for automated reports."
    if stripped == "import matplotlib.pyplot as plt":
        return "Technical: Imports matplotlib's charting interface as plt. Simple: plt is the short name used for commands like bar charts, histograms and saving images."
    if stripped == "import numpy as np":
        return "Technical: Imports NumPy as np for vectorized numeric operations. Simple: It helps apply math and if/else rules to whole columns quickly."
    if stripped == "import pandas as pd":
        return "Technical: Imports pandas as pd for DataFrame operations. Simple: pandas is the main table tool; it reads CSVs, cleans columns, groups data and exports results."
    if stripped.startswith("import "):
        return "Technical: Import statement. Simple: Loads a toolbox so the script can use code that already exists."
    if stripped.startswith("from ") and " import " in stripped:
        return "Technical: Selective import. Simple: Takes one specific tool from a larger toolbox."
    if stripped.startswith("ROOT =") or stripped.startswith("PACK =") or stripped.startswith("OUT ="):
        return "Technical: Path constant. Simple: Stores an important folder/file location once so the rest of the script can reuse it."
    if stripped.startswith("RAW_CSV ="):
        return "Technical: Raw input path. Simple: Points to the original Zepto CSV file."
    if stripped.startswith("PROCESSED =") or stripped.startswith("EXCEL =") or stripped.startswith("REPORT =") or stripped.startswith("CHARTS =") or stripped.startswith("TABLES ="):
        return "Technical: Output folder path. Simple: Tells the script where to save cleaned data, Excel files, report files, charts or tables."
    if stripped.startswith("def "):
        return "Technical: Function definition. Simple: Creates a named recipe that can be reused later."
    if stripped.startswith("return "):
        return "Technical: Return statement. Simple: Sends the final result of a function back to the part of the code that asked for it."
    if stripped.startswith("for "):
        return "Technical: For loop. Simple: Repeats the same action for each item in a list, table or folder."
    if stripped.startswith("if "):
        return "Technical: If condition. Simple: Runs this block only when the rule is true."
    if stripped.startswith("elif ") or stripped.startswith("else"):
        return "Technical: Conditional branch. Simple: Handles the other possible cases."
    if stripped.startswith("try:") or stripped.startswith("except "):
        return "Technical: Error handling. Simple: If something fails, the script can handle it instead of crashing immediately."
    if "pd.read_csv" in stripped:
        return "Technical: pandas CSV import into a DataFrame. Simple: Opens the raw CSV as a table Python can work with."
    if ".to_csv" in stripped:
        return "Technical: DataFrame CSV export. Simple: Saves the table so Excel, SQL, Power BI or the report can use it."
    if ".groupby" in stripped:
        return "Technical: pandas groupby. Simple: Puts rows into buckets, such as one bucket per category."
    if ".agg" in stripped:
        return "Technical: Aggregation. Simple: Turns many rows into summary numbers like count, sum and average."
    if "np.where" in stripped:
        return "Technical: Vectorized if/else. Simple: Applies a rule to every row in a column at once."
    if "np.select" in stripped:
        return "Technical: Multi-rule vectorized condition. Simple: Creates labels like low, medium and high from several rules."
    if "plt." in stripped:
        return "Technical: matplotlib plotting command. Simple: Draws or saves one part of a chart."
    if ".assign" in stripped:
        return "Technical: DataFrame assign. Simple: Adds or updates columns while keeping the transformation readable."
    if ".merge" in stripped:
        return "Technical: DataFrame merge. Simple: Combines two tables using a common column, like category."
    if ".sort_values" in stripped:
        return "Technical: DataFrame sorting. Simple: Orders rows so the most important items appear first."
    if ".copy" in stripped:
        return "Technical: DataFrame copy. Simple: Makes a separate version so later edits do not accidentally affect the original table."
    if ".astype" in stripped:
        return "Technical: Type conversion. Simple: Changes a column into the right kind of value, such as text, number or boolean."
    if ".str." in stripped:
        return "Technical: pandas string operation. Simple: Cleans text values across a full column."
    if ".fillna" in stripped:
        return "Technical: Missing-value replacement. Simple: Treats blank values safely before doing logic or math."
    if ".round" in stripped:
        return "Technical: Rounding numeric values. Simple: Makes numbers readable for reports."
    if ".head" in stripped:
        return "Technical: Takes first rows. Simple: Shows a small preview instead of the whole table."
    if ".iloc" in stripped:
        return "Technical: Position-based row selection. Simple: Picks a row by its order number."
    if "=" in stripped:
        return "Technical: Assignment. Simple: Stores a value, table, column or calculation result under a name so it can be reused."
    if stripped in {")", "}", "]", "):"}:
        return "Technical: Closing bracket. Simple: Ends a function call, list, dictionary or grouped block."
    return "Technical: Implementation line. Simple: One step in cleaning data, calculating KPIs, exporting files or building the report."


def explain_sql_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return "Technical: Blank line. Simple: Separates SQL blocks so the script is easier to read."
    if stripped.startswith("--"):
        return "Technical: SQL comment. Simple: A note for humans; SQLite ignores it."
    if stripped.startswith("."):
        return "Technical: SQLite CLI dot-command. Simple: A command for the sqlite3 terminal tool, not normal SQL."
    upper = stripped.upper()
    if upper.startswith("DROP "):
        return "Technical: DROP statement. Simple: Deletes the old table or view so you can rerun the script cleanly."
    if upper.startswith("CREATE TABLE"):
        return "Technical: CREATE TABLE. Simple: Defines the empty table structure before loading CSV rows."
    if upper.startswith("CREATE VIEW"):
        return "Technical: CREATE VIEW. Simple: Saves a query like a reusable virtual table."
    if upper.startswith("SELECT"):
        return "Technical: SELECT clause. Simple: Chooses which columns or calculations you want in the result."
    if upper.startswith("FROM"):
        return "Technical: FROM clause. Simple: Tells SQL which table or view to read from."
    if upper.startswith("WHERE"):
        return "Technical: WHERE filter. Simple: Keeps only rows that match the rule."
    if upper.startswith("GROUP BY"):
        return "Technical: GROUP BY. Simple: Combines rows into summary groups, such as one row per category."
    if upper.startswith("ORDER BY"):
        return "Technical: ORDER BY. Simple: Sorts the result so top or important rows appear first."
    if upper.startswith("WITH"):
        return "Technical: CTE start. Simple: Creates a named temporary mini-table inside the query."
    if upper.startswith("CASE"):
        return "Technical: CASE expression. Simple: SQL's if/else logic."
    if upper.startswith("WHEN") or upper.startswith("ELSE") or upper.startswith("END"):
        return "Technical: CASE branch. Simple: One condition or fallback inside SQL if/else logic."
    if "ROW_NUMBER()" in upper:
        return "Technical: ROW_NUMBER window function. Simple: Gives rows a rank/order number based on the sorting rule."
    if "CAST(" in upper:
        return "Technical: CAST. Simple: Converts a value into the needed type, such as number or decimal."
    if "ROUND(" in upper:
        return "Technical: ROUND. Simple: Makes decimal numbers cleaner for reports."
    if "SUM(" in upper or "COUNT(" in upper or "AVG(" in upper:
        return "Technical: Aggregate function. Simple: Calculates KPI totals, counts or averages from many rows."
    if "JOIN" in upper:
        return "Technical: JOIN. Simple: Combines two tables using a shared column."
    if stripped.endswith(";"):
        return "Technical: SQL statement terminator. Simple: The semicolon tells SQL this command is finished."
    return "Technical: SQL implementation line. Simple: Part of loading data, cleaning fields, calculating KPIs or exporting results."


def code_walkthrough_table(relative_path: str, language: str, max_lines: int | None = None) -> str:
    text = read_file(relative_path)
    lines = text.splitlines()
    if max_lines is not None:
        lines = lines[:max_lines]
    rows = []
    for idx, line in enumerate(lines, 1):
        explanation = explain_python_line(line) if language == "python" else explain_sql_line(line)
        if " Simple: " in explanation:
            technical, simple = explanation.split(" Simple: ", 1)
            technical = technical.replace("Technical: ", "")
        else:
            technical, simple = explanation, "Same idea in plain language: this line helps the script complete the project workflow."
        rows.append(
            "<tr>"
            f"<td class='ln'>{idx}</td>"
            f"<td><code>{esc(line) if line else '&nbsp;'}</code></td>"
            f"<td><strong>{esc(technical)}</strong><br><span class='plain'>{esc(simple)}</span></td>"
            "</tr>"
        )
    return "<table class='code-walk'><tr><th>Line</th><th>Code</th><th>Technical Term + Simple Meaning</th></tr>" + "".join(rows) + "</table>"


def svg_pipeline() -> str:
    return """
<svg viewBox="0 0 1000 230" role="img" aria-label="QuickCommerceOps pipeline" class="vector">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#111"/>
    </marker>
  </defs>
  <rect x="30" y="55" width="145" height="90" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="102" y="90" text-anchor="middle" font-size="20" font-weight="700">Raw CSV</text>
  <text x="102" y="118" text-anchor="middle" font-size="14">cp1252, paise</text>
  <line x1="175" y1="100" x2="250" y2="100" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="250" y="55" width="145" height="90" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="322" y="90" text-anchor="middle" font-size="20" font-weight="700">Python</text>
  <text x="322" y="118" text-anchor="middle" font-size="14">clean + EDA</text>
  <line x1="395" y1="100" x2="470" y2="100" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="470" y="55" width="145" height="90" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="542" y="90" text-anchor="middle" font-size="20" font-weight="700">SQL</text>
  <text x="542" y="118" text-anchor="middle" font-size="14">views + KPIs</text>
  <line x1="615" y1="100" x2="690" y2="100" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="690" y="55" width="145" height="90" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="762" y="90" text-anchor="middle" font-size="20" font-weight="700">Excel/BI</text>
  <text x="762" y="118" text-anchor="middle" font-size="14">decision tables</text>
  <line x1="835" y1="100" x2="910" y2="100" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="910" y="55" width="70" height="90" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="945" y="88" text-anchor="middle" font-size="16" font-weight="700">Memo</text>
  <text x="945" y="116" text-anchor="middle" font-size="13">action</text>
</svg>
"""


def svg_score() -> str:
    return """
<svg viewBox="0 0 900 210" role="img" aria-label="Priority score formula" class="vector small-vector">
  <rect x="20" y="25" width="860" height="160" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="450" y="65" text-anchor="middle" font-size="24" font-weight="700">Priority Score</text>
  <text x="450" y="105" text-anchor="middle" font-size="18">out of stock + low quantity + high MRP + weak category + useful discount + weight bucket</text>
  <text x="450" y="145" text-anchor="middle" font-size="15">Designed as an explainable business rule because order-level demand and margin are not available.</text>
</svg>
"""


def svg_business_loop() -> str:
    return """
<svg viewBox="0 0 980 260" class="vector" role="img" aria-label="Business decision loop">
  <defs>
    <marker id="arrow2" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#111"/>
    </marker>
  </defs>
  <rect x="30" y="70" width="150" height="80" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="105" y="104" text-anchor="middle" font-size="18" font-weight="700">Customer</text>
  <text x="105" y="128" text-anchor="middle" font-size="14">wants item now</text>
  <line x1="180" y1="110" x2="260" y2="110" stroke="#111" stroke-width="2" marker-end="url(#arrow2)"/>
  <rect x="260" y="70" width="150" height="80" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="335" y="104" text-anchor="middle" font-size="18" font-weight="700">Inventory</text>
  <text x="335" y="128" text-anchor="middle" font-size="14">available or not</text>
  <line x1="410" y1="110" x2="490" y2="110" stroke="#111" stroke-width="2" marker-end="url(#arrow2)"/>
  <rect x="490" y="70" width="150" height="80" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="565" y="104" text-anchor="middle" font-size="18" font-weight="700">Decision</text>
  <text x="565" y="128" text-anchor="middle" font-size="14">restock / monitor</text>
  <line x1="640" y1="110" x2="720" y2="110" stroke="#111" stroke-width="2" marker-end="url(#arrow2)"/>
  <rect x="720" y="70" width="210" height="80" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>
  <text x="825" y="104" text-anchor="middle" font-size="18" font-weight="700">Business Impact</text>
  <text x="825" y="128" text-anchor="middle" font-size="14">conversion, trust, repeat</text>
  <path d="M825 150 C825 220 105 220 105 150" fill="none" stroke="#d21f32" stroke-width="3" marker-end="url(#arrow2)"/>
  <text x="465" y="235" text-anchor="middle" font-size="15" fill="#d21f32" font-weight="700">new data refreshes the next decision</text>
</svg>
"""


def svg_topic_map() -> str:
    topics = [
        ("Business", 80, 55),
        ("Data Quality", 285, 55),
        ("Python EDA", 490, 55),
        ("SQL KPIs", 695, 55),
        ("Excel/BI", 285, 160),
        ("Interview", 490, 160),
        ("Recommendation", 695, 160),
    ]
    nodes = []
    for label, x, y in topics:
        nodes.append(f'<rect x="{x}" y="{y}" width="145" height="58" rx="8" fill="#fff" stroke="#111" stroke-width="2"/>')
        nodes.append(f'<text x="{x+72}" y="{y+36}" text-anchor="middle" font-size="16" font-weight="700">{label}</text>')
    lines = """
  <path d="M225 84 H285" stroke="#111" stroke-width="2"/>
  <path d="M430 84 H490" stroke="#111" stroke-width="2"/>
  <path d="M635 84 H695" stroke="#111" stroke-width="2"/>
  <path d="M357 113 V160" stroke="#111" stroke-width="2"/>
  <path d="M430 189 H490" stroke="#111" stroke-width="2"/>
  <path d="M635 189 H695" stroke="#111" stroke-width="2"/>
"""
    return f"""
<svg viewBox="0 0 920 250" class="vector" role="img" aria-label="Topic map">
  {lines}
  {''.join(nodes)}
  <text x="460" y="235" text-anchor="middle" font-size="14" fill="#d21f32" font-weight="700">Learn in this order: context -> clean data -> analyze -> model KPIs -> communicate decisions</text>
</svg>
"""


def toc_section() -> str:
    return section(
        "How To Use This Book",
        f"""
{svg_topic_map()}
<div class="rule-box"><strong>Study rule:</strong> do not memorize the project. Learn the chain: business problem -> raw data -> cleaning -> features -> SQL KPIs -> outputs -> recommendation -> limitations.</div>
<table>
  <tr><th>Part</th><th>What You Learn</th><th>Why Interviewers Care</th></tr>
  <tr><td>1</td><td>Resume and ATS wording</td><td>Shortlisting depends on clear keywords and business impact.</td></tr>
  <tr><td>2</td><td>Business fundamentals</td><td>DA/PA interviews reward context, not just code.</td></tr>
  <tr><td>3</td><td>Data dictionary and jargon</td><td>You must explain every column and metric simply.</td></tr>
  <tr><td>4</td><td>Python from basics to advanced</td><td>Cleaning, feature engineering and EDA are common fresher checks.</td></tr>
  <tr><td>5</td><td>SQL from basics to advanced</td><td>SQL is the hardest-screened DA/PA skill.</td></tr>
  <tr><td>6</td><td>Excel and BI</td><td>Business teams still expect Excel, pivots, dashboards and readable outputs.</td></tr>
  <tr><td>7</td><td>LeetCode-style practice</td><td>You need to solve variations, not only explain finished code.</td></tr>
  <tr><td>8</td><td>85 interview questions</td><td>Covers easy, medium and hard follow-ups.</td></tr>
</table>
""",
    )


def jargon_section() -> str:
    rows = [
        ("Quick commerce", "Delivery model where users expect groceries or essentials very quickly.", "Zepto/Blinkit/Instamart-style business."),
        ("SKU", "A specific sellable product variant.", "Amul milk 500ml and Amul milk 1L are different SKUs."),
        ("Inventory", "How much stock exists for products.", "Available quantity in this project."),
        ("Stockout", "When an item is unavailable.", "A product with out_of_stock = TRUE or quantity <= 0."),
        ("Category health", "A category-level view of availability and risk.", "Biscuits stockout rate, average discount, SKU count."),
        ("MRP", "Maximum retail price before discount.", "Stored in paise in raw data."),
        ("Selling price", "Customer-facing discounted price.", "Also stored in paise before cleaning."),
        ("Discount exposure", "Potential commercial pressure created by discounted available stock.", "Discount amount x available quantity."),
        ("Proxy metric", "A substitute metric used when the perfect metric is missing.", "Inventory value proxy because true revenue/margin is absent."),
        ("KPI", "Metric used to monitor performance.", "Stockout rate, available SKUs, inventory value."),
        ("Guardrail", "Metric that should not get worse while optimizing another metric.", "Margin risk while improving availability."),
        ("Watchlist", "Ranked action table.", "Top SKUs operations should investigate."),
        ("CTE", "Temporary named SQL result inside one query.", "Used to make scoring query readable."),
        ("Window function", "SQL function that calculates over a partition without collapsing rows.", "ROW_NUMBER for ranking."),
        ("EDA", "Exploratory data analysis.", "Initial checks, distributions, patterns and outliers."),
    ]
    body = "<p>This section lets you explain jargon in plain language. Interviewers often check whether you can simplify technical terms.</p>"
    body += "<table><tr><th>Term</th><th>Simplest Meaning</th><th>In This Project</th></tr>"
    body += "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in rows)
    body += "</table>"
    return section("Jargon Decoder", body)


def business_fundamentals_section(metrics: dict[str, object]) -> str:
    audit = metrics["audit"]
    return section(
        "Business Fundamentals: From Zero To Interview-Ready",
        f"""
{svg_business_loop()}
<h3>The simplest explanation</h3>
<p>A quick-commerce app is useful only if customers can find and receive the product they want. If a product is unavailable, the business may lose the order. If many products in a category are unavailable, the category feels unreliable.</p>

<h3>The analyst's job</h3>
<ol>
  <li>Measure the current availability problem.</li>
  <li>Find where the problem is concentrated.</li>
  <li>Rank actions so teams know what to fix first.</li>
  <li>Explain what the data can and cannot prove.</li>
</ol>

<h3>Core metrics in QuickCommerceOps</h3>
<table>
  <tr><th>Metric</th><th>Formula</th><th>Plain-English Meaning</th></tr>
  <tr><td>Stockout rate</td><td>out-of-stock SKUs / total SKUs</td><td>How much of the assortment is unavailable.</td></tr>
  <tr><td>Available inventory value</td><td>selling price x available quantity</td><td>Rough value of stock currently available.</td></tr>
  <tr><td>Discount exposure</td><td>discount amount x available quantity</td><td>Where high discounts are concentrated.</td></tr>
  <tr><td>Priority score</td><td>weighted rule</td><td>Which SKU should be investigated first.</td></tr>
</table>

<div class="rule-box"><strong>Current project numbers:</strong> {int(audit["raw_rows"]):,} SKU rows, {int(audit["valid_commercial_rows"]):,} valid commercial rows, {audit["raw_stockout_rate_pct"]}% stockout rate.</div>

<h3>What you must never overclaim</h3>
<ul>
  <li>Do not say this directly increased revenue. The dataset does not include revenue after intervention.</li>
  <li>Do not say stockout caused churn. The dataset does not include users or retention.</li>
  <li>Do not say high discount is bad. Without margin and demand, it is only a signal to investigate.</li>
</ul>
""",
    )


def data_dictionary_section(metrics: dict[str, object]) -> str:
    cols = [
        ("category", "Product category", "Group by this to find category health.", "Can be duplicated across products."),
        ("product_name", "Name of the product", "Used for SKU watchlist.", "Names may repeat across categories."),
        ("mrp_paise", "MRP in paise", "Converted to rupees.", "Must divide by 100."),
        ("discount_percent", "Discount percentage", "Used for discount bands and exposure.", "High discount needs margin context."),
        ("available_quantity", "Available inventory count", "Used for low-stock and value calculations.", "Snapshot only, not historical."),
        ("discounted_selling_price_paise", "Selling price in paise", "Converted to rupees.", "Zero values are invalid for KPI analysis."),
        ("weight_gms", "Product weight in grams", "Used for price per 100g and weight bucket.", "Zero values are invalid."),
        ("out_of_stock", "Stockout flag", "Used for stockout rate.", "Also cross-checked with quantity."),
        ("pack_quantity", "Package quantity field", "Context for pack size.", "May need business interpretation."),
    ]
    body = "<h3>Raw Data Dictionary</h3><table><tr><th>Column</th><th>Meaning</th><th>How Used</th><th>Interview Warning</th></tr>"
    body += "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td></tr>" for a, b, c, d in cols)
    body += "</table>"
    engineered = [
        ("mrp_rupees", "mrp_paise / 100", "Makes price readable."),
        ("selling_price_rupees", "discounted_selling_price_paise / 100", "Makes selling price readable."),
        ("is_out_of_stock", "out_of_stock OR available_quantity <= 0", "Creates robust stockout flag."),
        ("has_invalid_commercials", "price or weight <= 0", "Excludes invalid rows from commercial KPIs."),
        ("price_per_100g", "selling_price / weight x 100", "Compares package sizes."),
        ("discount_band", "no/low/medium/high", "Simplifies dashboard filtering."),
        ("available_inventory_value_rupees", "selling price x quantity", "Proxy for available commercial value."),
        ("priority_score", "weighted risk score", "Ranks replenishment actions."),
    ]
    body += "<h3>Engineered Features</h3><table><tr><th>Feature</th><th>Logic</th><th>Why It Exists</th></tr>"
    body += "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in engineered)
    body += "</table>"
    body += "<div class='rule-box'><strong>Interview line:</strong> I did not jump straight to charts. I first converted units, cleaned text, created flags, and separated valid commercial rows from raw rows.</div>"
    return section("Data Dictionary and Feature Engineering", body)


def interviewer_depth_section() -> str:
    return section(
        "Depth Map: How Far An Interviewer Can Go",
        """
<table>
  <tr><th>Topic</th><th>Basic Ask</th><th>Deep Ask</th><th>Best Answer Direction</th></tr>
  <tr><td>Encoding</td><td>Why cp1252?</td><td>How did you discover UTF-8 failed?</td><td>Explain read failure, non-UTF character, then safe conversion to UTF-8 output.</td></tr>
  <tr><td>Unit conversion</td><td>Why divide by 100?</td><td>What if some rows are already rupees?</td><td>Validate ranges and source documentation; do sanity checks before conversion.</td></tr>
  <tr><td>Stockout</td><td>What is stockout rate?</td><td>What if out_of_stock conflicts with quantity?</td><td>Create a robust flag and document the rule.</td></tr>
  <tr><td>Priority score</td><td>How did you score SKUs?</td><td>How would you validate weights?</td><td>Backtest on historical outcomes or run sensitivity analysis.</td></tr>
  <tr><td>Discount</td><td>What is discount exposure?</td><td>Can high discount be good?</td><td>Yes. It may clear inventory or drive demand; need margin and sales velocity.</td></tr>
  <tr><td>SQL</td><td>What is a CTE?</td><td>How would you optimize this at scale?</td><td>Indexes, partitions, pre-aggregates and incremental refresh.</td></tr>
  <tr><td>Dashboard</td><td>What charts did you build?</td><td>How would you design for executives vs ops?</td><td>Executives need KPIs and trend; ops needs SKU action table.</td></tr>
  <tr><td>Product analytics</td><td>How does inventory affect product?</td><td>How would you prove availability affects conversion?</td><td>Join availability with user event funnel and compare exposed sessions.</td></tr>
  <tr><td>ZS case</td><td>What recommendation?</td><td>How would you quantify impact?</td><td>Estimate lost sales with demand, margin, lead time and scenario assumptions.</td></tr>
</table>
""",
    )


def ats_section() -> str:
    return section(
        "ATS-Friendly Resume Content",
        """
<h3>Best Project Title</h3>
<div class="resume-box"><strong>QuickCommerceOps - Quick-Commerce Inventory, Stockout and SKU Performance Analytics</strong><br>
SQL | Python | Excel | Power BI | pandas | numpy | matplotlib | EDA</div>

<h3>ATS Keyword Bank</h3>
<p class="keywords">SQL, Excel, Power BI, Python, pandas, numpy, matplotlib, EDA, data cleaning, data validation, inventory analytics, stockout analysis, SKU performance, quick commerce, category analytics, KPI dashboard, business intelligence, replenishment priority, discount analysis, window functions, CTEs, CASE WHEN, stakeholder reporting, decision analytics, root cause analysis, data storytelling.</p>

<h3>Resume Bullets - Data Analyst Version</h3>
<ul>
  <li>Built <strong>QuickCommerceOps</strong>, a quick-commerce inventory analytics project using SQL, Python, Excel-ready outputs and Power BI-ready datasets to identify stockout-prone SKUs, category availability gaps and discount exposure across 3.7K+ SKU records.</li>
  <li>Cleaned raw inventory data by resolving CSV encoding issues, converting prices from paise to rupees, validating commercial fields and creating reusable SQL views for stockout, discount and category-health KPIs.</li>
  <li>Designed a replenishment watchlist using out-of-stock status, available quantity, MRP, category stockout rate, discount band and weight bucket to prioritize operational action.</li>
</ul>

<h3>Resume Bullets - ZS / Decision Analytics Version</h3>
<ul>
  <li>Framed a quick-commerce inventory problem as a decision analytics case, ranking SKUs by replenishment priority and translating category-level stockout patterns into business recommendations.</li>
  <li>Built Excel-ready decision inputs and SQL KPI tables to support scenario analysis for improving availability in high-risk categories.</li>
</ul>

<h3>Resume Bullets - Product Analyst Version</h3>
<ul>
  <li>Analyzed SKU availability and stockout patterns as product reliability signals for a quick-commerce journey, identifying categories where unavailability may affect conversion and repeat usage.</li>
  <li>Created an explainable priority score to recommend which unavailable or low-stock products should be fixed first to protect user experience.</li>
</ul>

<h3>Bad vs Better Resume Writing</h3>
<table><tr><th>Weak</th><th>Better</th></tr>
<tr><td>Made a Zepto dashboard using Python and SQL.</td><td>Built a quick-commerce inventory analytics project to identify stockout-prone SKUs, category availability gaps and replenishment priorities across 3.7K+ SKU records.</td></tr>
<tr><td>Used pandas and matplotlib for EDA.</td><td>Used pandas to clean encoded CSV data, derive inventory value and price-per-100g features, then used matplotlib to explain category stockout and discount patterns.</td></tr>
</table>
""",
    )


def learning_path_section(metrics: dict[str, object]) -> str:
    audit = metrics["audit"]
    return section(
        "Step-by-Step Learning Path",
        f"""
{svg_pipeline()}
<h3>What You Should Learn First</h3>
<ol>
  <li><strong>Business context:</strong> Quick-commerce companies care about availability, SKU mix, stockouts, discounts and replenishment speed.</li>
  <li><strong>Dataset context:</strong> This project has {int(audit["raw_rows"]):,} raw SKU rows, {int(audit["categories"])} categories and {audit["raw_stockout_rate_pct"]}% stockout rate.</li>
  <li><strong>Data quality:</strong> The CSV is not UTF-8 clean. You must explain why <code>encoding="cp1252"</code> was used.</li>
  <li><strong>Feature engineering:</strong> Convert paise to rupees, create stock flags, discount bands, weight buckets and inventory value.</li>
  <li><strong>SQL modeling:</strong> Build clean views first, then category KPIs, then watchlist ranking.</li>
  <li><strong>Dashboard thinking:</strong> Show health first, then diagnosis, then action list.</li>
  <li><strong>Interview story:</strong> Explain limitation honestly: no orders, margin, demand, lead time or dark-store IDs.</li>
</ol>

<h3>Beginner to Advanced Roadmap</h3>
<table>
  <tr><th>Level</th><th>What To Learn</th><th>How It Appears In QuickCommerceOps</th></tr>
  <tr><td>Beginner</td><td>Rows, columns, data types, missing values</td><td>Schema check and raw data audit</td></tr>
  <tr><td>Beginner</td><td>Basic SQL SELECT, WHERE, GROUP BY</td><td>Category SKU counts and stockout rate</td></tr>
  <tr><td>Intermediate</td><td>CASE WHEN, CTEs, views, ranking</td><td>Clean inventory view and replenishment watchlist</td></tr>
  <tr><td>Intermediate</td><td>pandas cleaning and feature creation</td><td>Price conversion, flags, buckets, inventory value</td></tr>
  <tr><td>Advanced</td><td>Decision scoring and stakeholder explanation</td><td>Priority score and business recommendation</td></tr>
  <tr><td>Advanced</td><td>Limitations and next-version design</td><td>Add demand, margin, expiry, lead time and dark-store IDs</td></tr>
</table>
""",
    )


def output_screenshots_section() -> str:
    def output_page(title: str, src: str, callouts: list[tuple[str, str]]) -> str:
        callout_html = "".join(
            f"<div class='arrow-callout'><div class='arrow-mark'>-></div><div><strong>{esc(label)}</strong><br>{esc(text)}</div></div>"
            for label, text in callouts
        )
        return section(
            title,
            f"""
<p class="photo-note">Captured from the local report with headless Chrome at high device scale. The image is placed full-width to keep text and tables readable.</p>
<div class="annotated-output">
  <div class="output-image-wrap">
    <img src="{esc(src)}" alt="{esc(title)} screenshot">
  </div>
  <div class="output-callouts">
    {callout_html}
  </div>
</div>
""",
            "output-page",
        )

    return "\n".join(
        [
            section(
                "Output Photos: How To Read Them",
                """
<div class="rule-box"><strong>Blur fix:</strong> The first version placed screenshots in a small two-column grid. This version captures each section at high scale and gives each output its own learning page.</div>
<p>The goal is not decoration. Each output is tied to an interview explanation: what it shows, why it matters, and what action it supports.</p>
""",
            ),
            output_page(
                "Output 1: Executive Snapshot",
                "assets/screenshots/executive_snapshot.png",
                [
                    ("KPI row", "This is the first thing a manager reads: raw rows, categories, stockout rate and inventory value proxy."),
                    ("Business problem", "The report states why availability matters before showing charts."),
                    ("Key findings", "The cards convert analysis into a short decision summary."),
                ],
            ),
            output_page(
                "Output 2: Charts",
                "assets/screenshots/charts.png",
                [
                    ("Stockout bar chart", "Ranks categories by availability problem; this tells where to investigate first."),
                    ("Discount histogram", "Shows whether most products have no, low, medium or high discount."),
                    ("Scatter plot", "Checks whether high price and high discount products behave differently by stock status."),
                    ("Watchlist chart", "Shows which SKUs are highest priority for operational review."),
                ],
            ),
            output_page(
                "Output 3: Category Health Table",
                "assets/screenshots/category_health.png",
                [
                    ("Category grain", "Each row is one category, not one SKU."),
                    ("Stockout rate", "Main health metric: out-of-stock SKUs divided by total SKUs."),
                    ("Inventory value proxy", "Useful for business prioritization, but not the same as revenue or margin."),
                ],
            ),
            output_page(
                "Output 4: Replenishment Watchlist",
                "assets/screenshots/replenishment_watchlist.png",
                [
                    ("Priority rank", "The action order for operations teams."),
                    ("Priority score", "Explainable weighted score, not a black-box model."),
                    ("SKU context", "Includes product, category, price, stock flag and category stockout rate."),
                ],
            ),
        ]
    )


def python_section() -> str:
    snippets = [
        (
            "1. Read the CSV with the correct encoding",
            """raw = pd.read_csv(RAW_CSV, encoding="cp1252")""",
            [
                "The raw file contains Windows-style characters, so UTF-8 fails.",
                "In interview, say you diagnosed an encoding issue and used cp1252 to load the file safely.",
            ],
        ),
        (
            "2. Rename columns into analysis-friendly names",
            '''df = raw.rename(columns={
    "Category": "category",
    "name": "product_name",
    "mrp": "mrp_paise",
    "discountedSellingPrice": "discounted_selling_price_paise"
})''',
            [
                "Raw column names are made consistent and snake_case.",
                "This reduces confusion when writing SQL and Python later.",
            ],
        ),
        (
            "3. Convert paise to rupees",
            '''df["mrp_rupees"] = (df["mrp_paise"].astype(float) / 100).round(2)
df["selling_price_rupees"] = (
    df["discounted_selling_price_paise"].astype(float) / 100
).round(2)''',
            [
                "The dataset stores prices in paise, not rupees.",
                "This is a common real-world data interpretation issue.",
            ],
        ),
        (
            "4. Create stock and commercial quality flags",
            '''df["is_out_of_stock"] = df["out_of_stock"] | (df["available_quantity"] <= 0)
df["has_invalid_commercials"] = (
    (df["mrp_paise"] <= 0)
    | (df["discounted_selling_price_paise"] <= 0)
    | (df["weight_gms"] <= 0)
)''',
            [
                "One flag supports business stockout analysis.",
                "The other prevents invalid price or weight rows from polluting commercial KPIs.",
            ],
        ),
        (
            "5. Use numpy to create buckets",
            '''df["discount_band"] = np.select(
    [
        df["discount_percent"] == 0,
        df["discount_percent"] < 10,
        df["discount_percent"] < 25,
        df["discount_percent"] >= 25,
    ],
    ["no discount", "low", "medium", "high"],
    default="unknown",
)''',
            [
                "Buckets convert continuous values into business-readable groups.",
                "This makes dashboards and Excel pivots easier for stakeholders.",
            ],
        ),
        (
            "6. Build category-health KPIs",
            '''category_health = (
    valid.groupby("category", as_index=False)
    .agg(
        total_skus=("sku_id", "count"),
        out_of_stock_skus=("is_out_of_stock", lambda s: int(s.sum())),
        avg_discount_pct=("discount_percent", "mean"),
        available_inventory_value_rupees=("available_inventory_value_rupees", "sum"),
    )
)''',
            [
                "This is the Python version of a SQL GROUP BY.",
                "It tells which categories have availability and discount risk.",
            ],
        ),
        (
            "7. Create the priority score",
            '''with_context["priority_score"] = (
    np.where(with_context["is_out_of_stock"], 45, 0)
    + np.where(with_context["available_quantity"].between(1, 2), 20, 0)
    + np.where(with_context["mrp_rupees"] >= 500, 15, 0)
    + np.where(with_context["stockout_rate_pct"] >= 15, 10, 0)
)''',
            [
                "This is not machine learning; it is an explainable decision rule.",
                "That is appropriate because the dataset lacks historical demand and margin.",
            ],
        ),
    ]
    body = "<h3>Python: Basic to Advanced</h3>"
    for title, code, bullets in snippets:
        body += f"<h4>{esc(title)}</h4>{code_block(code)}<ul>" + "".join(f"<li>{esc(b)}</li>" for b in bullets) + "</ul>"
    body += """
<h3>How To Answer If Asked Why Python Was Needed</h3>
<p>SQL is excellent for repeatable KPI tables. Python is stronger for data diagnosis, feature engineering, chart generation and automated report creation. In this project, Python creates the clean CSV, EDA charts, Excel-ready outputs and the local report.</p>
"""
    return section("Python Code Explained", body)


def sql_section() -> str:
    body = """
<h3>SQL: Basic to Advanced</h3>
<h4>1. Create a clean analysis view</h4>
""" + code_block(
        """
CREATE VIEW clean_inventory AS
SELECT
  ROW_NUMBER() OVER (ORDER BY category, product_name) AS sku_id,
  TRIM(category) AS category,
  TRIM(product_name) AS product_name,
  CAST(mrp_paise AS REAL) / 100.0 AS mrp_rupees,
  CASE
    WHEN LOWER(TRIM(out_of_stock)) = 'true'
      OR CAST(available_quantity AS INTEGER) <= 0 THEN 1
    ELSE 0
  END AS is_out_of_stock
FROM raw_inventory;
"""
    ) + """
<ul><li><code>ROW_NUMBER()</code> creates a stable SKU ID for analysis.</li><li><code>TRIM</code> cleans text fields.</li><li><code>CASE WHEN</code> turns business logic into a reusable flag.</li></ul>

<h4>2. Create category-health KPIs</h4>
""" + code_block(
        """
SELECT
  category,
  COUNT(*) AS total_skus,
  SUM(CASE WHEN is_out_of_stock = 1 THEN 1 ELSE 0 END) AS out_of_stock_skus,
  ROUND(100.0 * SUM(CASE WHEN is_out_of_stock = 1 THEN 1 ELSE 0 END) / COUNT(*), 2)
    AS stockout_rate_pct,
  ROUND(AVG(discount_percent), 2) AS avg_discount_pct
FROM valid_inventory
GROUP BY category
ORDER BY stockout_rate_pct DESC;
"""
    ) + """
<ul><li>This is the main KPI query for stockout diagnosis.</li><li>It is interview-friendly because it uses aggregation plus conditional logic.</li></ul>

<h4>3. Build the replenishment watchlist with a CTE</h4>
""" + code_block(
        """
WITH category_context AS (
  SELECT category, stockout_rate_pct
  FROM category_health
),
scored AS (
  SELECT
    v.product_name,
    v.category,
    v.mrp_rupees,
    v.available_quantity,
    (
      CASE WHEN v.is_out_of_stock = 1 THEN 45 ELSE 0 END +
      CASE WHEN v.available_quantity BETWEEN 1 AND 2 THEN 20 ELSE 0 END +
      CASE WHEN v.mrp_rupees >= 500 THEN 15 ELSE 0 END +
      CASE WHEN c.stockout_rate_pct >= 15 THEN 10 ELSE 0 END
    ) AS priority_score
  FROM valid_inventory v
  JOIN category_context c ON v.category = c.category
)
SELECT *
FROM scored
ORDER BY priority_score DESC, mrp_rupees DESC;
"""
    ) + f"""
{svg_score()}
<h3>How To Explain SQL Design</h3>
<p>I separated the SQL into layers: raw table, clean view, valid commercial view, category KPI view, watchlist view and exports. This is easier to debug and resembles how BI-ready tables are usually built.</p>
"""
    return section("SQL Code Explained", body)


def excel_powerbi_section() -> str:
    return section(
        "Excel and Power BI Learning Path",
        """
<h3>Excel: Basic to Advanced</h3>
<table>
  <tr><th>Level</th><th>Skill</th><th>Use In Project</th></tr>
  <tr><td>Basic</td><td>Open CSV, format table, freeze header</td><td>Use files in the <code>excel/</code> folder.</td></tr>
  <tr><td>Basic</td><td>Sort and filter</td><td>Sort watchlist by priority score and stockout flag.</td></tr>
  <tr><td>Intermediate</td><td>Pivot table</td><td>Category vs stockout rate, inventory value and SKU count.</td></tr>
  <tr><td>Intermediate</td><td>XLOOKUP</td><td>Lookup category and price from SKU ID or product name.</td></tr>
  <tr><td>Advanced</td><td>What-if model</td><td>Estimate how many high-risk SKUs need action to hit a target stockout rate.</td></tr>
  <tr><td>Advanced</td><td>Decision memo</td><td>Summarize the top 3 categories, top 10 SKUs and recommended action.</td></tr>
</table>

<h3>Power BI Dashboard Structure</h3>
<ol>
  <li><strong>Executive Overview:</strong> total SKUs, stockout rate, valid rows, available inventory value.</li>
  <li><strong>Category Health:</strong> category stockout rate, available SKUs, inventory value and average discount.</li>
  <li><strong>SKU Watchlist:</strong> top priority SKUs with filters for category, stock status and price band.</li>
  <li><strong>Pricing and Discount:</strong> discount bands, high-discount SKUs and price-per-100g analysis.</li>
</ol>

<h3>Useful DAX-Style Measures</h3>
""" + code_block(
            """
Total SKUs = COUNTROWS(clean_inventory)

Out of Stock SKUs =
CALCULATE(COUNTROWS(clean_inventory), clean_inventory[is_out_of_stock] = TRUE())

Stockout Rate % =
DIVIDE([Out of Stock SKUs], [Total SKUs])

Available Inventory Value =
SUM(clean_inventory[available_inventory_value_rupees])
"""
        ) + """
<p>Use these as Power BI logic references. The current local project exports Power BI-ready CSVs; it does not require a PBIX file to learn the analytics logic.</p>
""",
    )


def python_libraries_deep_section() -> str:
    return section(
        "Python Libraries: From Simplest Level To Interview Depth",
        """
<div class="lesson-card">
  <h4>What is a library?</h4>
  <p>A Python library is pre-written code you import instead of writing everything yourself. In this project, libraries do three jobs: read data, calculate features, and draw charts.</p>
</div>

<h3>pandas</h3>
<table>
  <tr><th>Concept</th><th>Simplest Explanation</th><th>Used In Project</th><th>Interview Depth</th></tr>
  <tr><td>DataFrame</td><td>A table in Python.</td><td>Raw CSV becomes a DataFrame.</td><td>Rows are observations, columns are variables.</td></tr>
  <tr><td>Series</td><td>One column from a DataFrame.</td><td><code>df["mrp_paise"]</code></td><td>Most vectorized operations happen on Series.</td></tr>
  <tr><td><code>read_csv</code></td><td>Reads CSV into a table.</td><td>Loads Zepto dataset.</td><td>Encoding, dtype inference, missing values and parsing errors matter.</td></tr>
  <tr><td><code>rename</code></td><td>Changes column names.</td><td>Converts raw names to snake_case.</td><td>Good naming reduces downstream errors.</td></tr>
  <tr><td><code>astype</code></td><td>Changes data type.</td><td>Converts numeric columns.</td><td>Important before math, grouping or exports.</td></tr>
  <tr><td><code>groupby</code></td><td>Groups rows.</td><td>Category health KPIs.</td><td>Equivalent to SQL GROUP BY.</td></tr>
  <tr><td><code>merge</code></td><td>Joins tables.</td><td>Adds category stockout context to SKU rows.</td><td>Equivalent to SQL JOIN; validate row counts.</td></tr>
  <tr><td><code>to_csv</code></td><td>Saves table.</td><td>Exports Excel/Power BI-ready files.</td><td>Turns analysis into stakeholder artifact.</td></tr>
</table>

<h3>numpy</h3>
<table>
  <tr><th>Concept</th><th>Simplest Explanation</th><th>Used In Project</th></tr>
  <tr><td><code>np.where</code></td><td>Column-wise if/else.</td><td>Adds score points when a condition is true.</td></tr>
  <tr><td><code>np.select</code></td><td>Column-wise multi-rule if/else.</td><td>Creates discount and weight buckets.</td></tr>
  <tr><td><code>np.arange</code></td><td>Creates number sequence.</td><td>Creates SKU IDs and ranks.</td></tr>
</table>

<h3>matplotlib</h3>
<table>
  <tr><th>Function</th><th>Simplest Explanation</th><th>Used In Project</th></tr>
  <tr><td><code>plt.barh</code></td><td>Horizontal bar chart.</td><td>Category stockout rate and watchlist chart.</td></tr>
  <tr><td><code>plt.hist</code></td><td>Distribution chart.</td><td>Discount percent distribution.</td></tr>
  <tr><td><code>plt.scatter</code></td><td>Relationship chart.</td><td>MRP vs discount by stock status.</td></tr>
  <tr><td><code>plt.savefig</code></td><td>Saves chart image.</td><td>Creates PNGs for the report.</td></tr>
</table>

<h3>Why <code>matplotlib.use("Agg")</code> exists</h3>
<p><code>Agg</code> is a non-GUI rendering backend. It lets Python save chart images without opening a window. This matters when scripts run in terminals, servers, or automated report jobs.</p>
""",
    )


def syntax_decoder_section() -> str:
    return section(
        "Syntax Decoder: Quotes, Brackets, Dots, Commas, Semicolons",
        """
<p>This chapter is for reading code calmly. Most beginners struggle because small symbols feel mysterious. Here is what the symbols do in this project.</p>
<table>
  <tr><th>Symbol</th><th>Where</th><th>Meaning</th><th>Example</th></tr>
  <tr><td><code>"text"</code></td><td>Python/SQL</td><td>A string: text value.</td><td><code>"category"</code></td></tr>
  <tr><td><code>[ ]</code></td><td>Python</td><td>Select column or create list.</td><td><code>df["mrp_paise"]</code></td></tr>
  <tr><td><code>( )</code></td><td>Python/SQL</td><td>Function call or grouping.</td><td><code>round(value)</code></td></tr>
  <tr><td><code>{ }</code></td><td>Python</td><td>Dictionary or formatted block.</td><td><code>{"mrp": "mrp_paise"}</code></td></tr>
  <tr><td><code>.</code></td><td>Python</td><td>Access method/property.</td><td><code>df.rename()</code></td></tr>
  <tr><td><code>,</code></td><td>Python/SQL</td><td>Separates items.</td><td><code>category, product_name</code></td></tr>
  <tr><td><code>=</code></td><td>Python</td><td>Assignment.</td><td><code>ROOT = Path(...)</code></td></tr>
  <tr><td><code>==</code></td><td>Python/SQL</td><td>Equality check.</td><td><code>discount == 0</code></td></tr>
  <tr><td><code>|</code></td><td>Python pandas</td><td>OR condition between Series.</td><td><code>a | b</code></td></tr>
  <tr><td><code>&</code></td><td>Python pandas</td><td>AND condition between Series.</td><td><code>a & b</code></td></tr>
  <tr><td><code>:</code></td><td>Python</td><td>Starts indented block.</td><td><code>def main():</code></td></tr>
  <tr><td><code>;</code></td><td>SQL</td><td>Ends SQL statement.</td><td><code>SELECT * FROM table;</code></td></tr>
  <tr><td><code>--</code></td><td>SQL</td><td>Comment.</td><td><code>-- Run after cleaning</code></td></tr>
</table>
""",
    )


def full_python_walkthrough_section() -> str:
    return section(
        "Full Python File: Line-By-Line Walkthrough",
        f"""
<p>This is the actual file used in the project: <code>python/eda_quick_commerce_ops.py</code>. Read it in blocks. The right column explains the role of each line.</p>
{code_walkthrough_table("python/eda_quick_commerce_ops.py", "python")}
""",
        "wide-code",
    )


def full_sql_walkthrough_section() -> str:
    parts = []
    for path in [
        "sql/01_load_sqlite.sql",
        "sql/02_clean_views.sql",
        "sql/03_business_questions.sql",
        "sql/04_export_analysis_tables.sql",
    ]:
        parts.append(f"<h3>{esc(path)}</h3>{code_walkthrough_table(path, 'sql')}")
    return section(
        "Full SQL Files: Line-By-Line Walkthrough",
        "<p>These are the actual SQL scripts. Learn the file order first: load raw CSV, create clean views, answer business questions, export analysis tables.</p>"
        + "\n".join(parts),
        "wide-code",
    )


def excel_deep_dive_section() -> str:
    return section(
        "Excel Deep Dive: What To Actually Do With The CSVs",
        """
<h3>Files To Open In Excel</h3>
<ul>
  <li><code>excel/category_health_for_excel.csv</code></li>
  <li><code>excel/replenishment_watchlist_for_excel.csv</code></li>
  <li><code>excel/discount_exposure_for_excel.csv</code></li>
  <li><code>excel/excel_decision_model_inputs.csv</code></li>
</ul>

<h3>Workbook Tabs To Create</h3>
<table>
  <tr><th>Tab</th><th>Purpose</th><th>What To Add</th></tr>
  <tr><td>01 Data Audit</td><td>Prove you checked the dataset.</td><td>Row counts, valid rows, invalid rows, categories.</td></tr>
  <tr><td>02 Category Pivot</td><td>Summarize category health.</td><td>Pivot: category rows, stockout rate, inventory value, SKU count.</td></tr>
  <tr><td>03 Watchlist</td><td>Operational action table.</td><td>Conditional formatting on priority score and stockout flag.</td></tr>
  <tr><td>04 What-If</td><td>Decision modeling.</td><td>Target stockout rate, gap, category priority flag.</td></tr>
  <tr><td>05 Memo</td><td>Business recommendation.</td><td>Top 3 findings, top 3 actions, limitations.</td></tr>
</table>

<h3>Excel Formulas To Know</h3>
""" + code_block(
            """
=XLOOKUP(A2, Watchlist[sku_id], Watchlist[product_name])
=IF([@[stockout_rate_pct]]>15,"High Risk","Monitor")
=SUMIFS([available_inventory_value_rupees],[category],A2)
=COUNTIFS([category],A2,[is_out_of_stock],TRUE)
=RANK.EQ([@[priority_score]],[priority_score])
"""
        ) + """
<h3>Pivot Table Interview Explanation</h3>
<p>A pivot table lets a business user summarize data without writing SQL. For this project, I would put category in rows and show SKU count, stockout rate and inventory value as values. Then I would filter to categories above the target stockout threshold.</p>
""",
    )


def powerbi_deep_dive_section() -> str:
    return section(
        "Power BI Deep Dive: Data Model, Measures, Dashboard Logic",
        """
<h3>Data Model</h3>
<p>For this project, keep the model simple. Use <code>clean_inventory.csv</code> as the SKU-level fact table. Use <code>category_health.csv</code> and <code>replenishment_watchlist.csv</code> as reporting tables. If building a more formal model, create a category dimension and a SKU dimension.</p>

<h3>Page 1: Executive Overview</h3>
<ul>
  <li>KPI cards: total SKUs, valid SKUs, stockout rate, available inventory value, watchlist size.</li>
  <li>One bar chart: category stockout rate.</li>
  <li>One table: top 10 watchlist SKUs.</li>
</ul>

<h3>Page 2: Category Health</h3>
<ul>
  <li>Bar chart: stockout rate by category.</li>
  <li>Bar chart: available inventory value by category.</li>
  <li>Scatter: average MRP vs stockout rate.</li>
  <li>Slicers: category, discount band, weight bucket.</li>
</ul>

<h3>Page 3: SKU Watchlist</h3>
<ul>
  <li>Table: priority rank, product name, category, MRP, available quantity, stockout flag, priority score.</li>
  <li>Conditional formatting: red for out of stock, dark for high score.</li>
  <li>Drillthrough: SKU detail page.</li>
</ul>

<h3>DAX Measures Explained</h3>
""" + code_block(
            """
Total SKUs = COUNTROWS(clean_inventory)
-- Counts rows in the SKU table.

Out of Stock SKUs =
CALCULATE(COUNTROWS(clean_inventory), clean_inventory[is_out_of_stock] = TRUE())
-- Counts only rows where the stockout flag is true.

Stockout Rate % =
DIVIDE([Out of Stock SKUs], [Total SKUs])
-- DIVIDE prevents divide-by-zero errors.

Available Inventory Value =
SUM(clean_inventory[available_inventory_value_rupees])
-- Adds the inventory value proxy across selected filters.
"""
        ) + """
<h3>Dashboard Design Rule</h3>
<div class="rule-box"><strong>Do not build chart decoration.</strong> Build a decision path: health -> diagnosis -> ranked action -> limitation.</div>
""",
    )


def project_story_section() -> str:
    return section(
        "How To Tell The Project Story Smoothly",
        """
<h3>10-Second Version</h3>
<p>I built QuickCommerceOps to analyze SKU availability, stockout risk and replenishment priorities for a quick-commerce inventory dataset.</p>

<h3>30-Second Version</h3>
<p>I used a Zepto-style SKU inventory dataset with 3.7K+ rows. I cleaned encoding and unit issues, converted prices from paise to rupees, created stockout and commercial validity flags, built SQL KPI views and created a replenishment watchlist. The final output helps operations teams prioritize unavailable or low-stock SKUs.</p>

<h3>2-Minute Version</h3>
<ol>
  <li><strong>Problem:</strong> Quick-commerce depends on availability. Stockouts hurt customer trust and conversion.</li>
  <li><strong>Data:</strong> SKU-level inventory data: category, product, MRP, selling price, discount, quantity, weight and stock flag.</li>
  <li><strong>Cleaning:</strong> Fixed encoding, standardized columns, converted paise to rupees, removed invalid commercial rows from KPI views.</li>
  <li><strong>Analysis:</strong> Calculated category stockout rate, inventory value proxy, discount exposure and SKU priority score.</li>
  <li><strong>Output:</strong> Excel-ready tables, SQL exports, charts, HTML report and Power BI-ready CSVs.</li>
  <li><strong>Recommendation:</strong> Start with highest-ranked unavailable and low-stock SKUs in high-stockout categories.</li>
  <li><strong>Limitation:</strong> Need demand, margin, lead time and dark-store data for true lost-sales estimation.</li>
</ol>

<h3>STAR Answer For HR / Manager Round</h3>
<p><strong>Situation:</strong> I wanted a portfolio project that felt close to quick-commerce operations.</p>
<p><strong>Task:</strong> Build a project that went beyond charts and ended in an action list.</p>
<p><strong>Action:</strong> I cleaned the dataset, built SQL views, created Python EDA, generated Excel-ready outputs and designed a replenishment score.</p>
<p><strong>Result:</strong> The project produces a ranked SKU watchlist and category-health view that can be discussed as a real business decision model.</p>
""",
    )


def leetcode_section() -> str:
    snippets = [
        ("Top categories by stockout rate", "GROUP BY + ORDER BY", "Find top 3 categories by stockout rate, excluding categories with fewer than 50 SKUs."),
        ("Second highest MRP without LIMIT", "DENSE_RANK", "Find products with the second-highest MRP in each category."),
        ("Products out of stock but high discount", "WHERE + CASE", "List products that are out of stock and have discount above category average."),
        ("Category MoM stockout trend", "LAG", "If a daily snapshot table existed, calculate month-over-month stockout rate change."),
        ("Duplicate product names", "GROUP BY HAVING", "Find products appearing in more than one category."),
        ("Price outliers", "AVG + standard deviation logic", "Find products priced far above category average."),
        ("Watchlist rank", "ROW_NUMBER", "Rank low-stock SKUs by priority score within each category."),
        ("Inventory value share", "SUM window", "Calculate category inventory value as a percent of total inventory value."),
        ("Missing commercial fields", "NULL/zero checks", "Count products with invalid MRP, selling price or weight."),
        ("Category discount exposure", "CTE", "Compute total discount exposure by category and rank categories."),
    ]
    rows = "".join(f"<tr><td>{i+1}</td><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for i, (a, b, c) in enumerate(snippets))
    return section(
        "LeetCode-Style SQL Practice Snippets",
        f"""
<p>These are not copied proprietary interview questions. They are LeetCode-style practice patterns adapted to QuickCommerceOps so you can explain your own project under interview pressure.</p>
<table><tr><th>#</th><th>Problem</th><th>Pattern</th><th>Task</th></tr>{rows}</table>
<h3>Example Solution: Rank Watchlist SKUs Within Category</h3>
{code_block('''
WITH scored AS (
  SELECT
    category,
    product_name,
    priority_score,
    mrp_rupees,
    ROW_NUMBER() OVER (
      PARTITION BY category
      ORDER BY priority_score DESC, mrp_rupees DESC
    ) AS category_rank
  FROM replenishment_watchlist
)
SELECT *
FROM scored
WHERE category_rank <= 3;
''')}
<p>What this tests: partitioning, ranking, business sorting logic and the ability to explain why a SKU is important.</p>
""",
    )


def question_bank() -> list[tuple[str, str, str]]:
    easy = [
        ("Easy", "What business problem does QuickCommerceOps solve?", "It prioritizes SKU availability issues by identifying stockout-prone categories, unavailable products and replenishment watchlist items."),
        ("Easy", "What is a SKU?", "A stock keeping unit: a unique product or package variant that can be tracked in inventory."),
        ("Easy", "Why did you convert paise to rupees?", "The raw data stores price in paise; converting to rupees makes KPIs readable and prevents misinterpretation."),
        ("Easy", "What is stockout rate?", "Out-of-stock SKUs divided by total valid SKUs, usually shown as a percentage."),
        ("Easy", "What is EDA?", "Exploratory data analysis: checking data shape, distributions, missing values, outliers and early patterns."),
        ("Easy", "Why use SQL in this project?", "To create repeatable KPI views and business queries for category health, discount exposure and watchlist ranking."),
        ("Easy", "Why use Python in this project?", "For data cleaning, encoding handling, feature creation, charts and report generation."),
        ("Easy", "Why use Excel outputs?", "Stakeholders often use Excel for pivots, lookups, conditional formatting and what-if decisions."),
        ("Easy", "What is the difference between MRP and selling price?", "MRP is listed price; selling price is post-discount customer-facing price."),
        ("Easy", "What does discount percent mean?", "The percentage reduction from MRP to selling price."),
        ("Easy", "What is a KPI?", "A key performance indicator used to track business performance."),
        ("Easy", "Which KPI matters most here?", "Stockout rate, because availability is central to quick-commerce reliability."),
        ("Easy", "What is a data audit?", "A check of rows, columns, missing values, invalid values and transformations before analysis."),
        ("Easy", "What is a view in SQL?", "A saved query that can be reused like a table."),
        ("Easy", "What is CASE WHEN used for?", "Creating conditional business logic, such as stock flags or quality flags."),
        ("Easy", "What does GROUP BY do?", "Aggregates rows by a dimension, such as category."),
        ("Easy", "What does ROW_NUMBER do?", "Assigns a rank-like sequence based on a defined sort order."),
        ("Easy", "Why is the project not just a dashboard?", "It includes cleaning, SQL modeling, scoring, Excel outputs, visual report and recommendations."),
        ("Easy", "What is the final decision output?", "A replenishment watchlist that ranks SKUs for action."),
        ("Easy", "What is the biggest limitation?", "No order history, demand, margin, expiry, lead time or dark-store ID."),
        ("Easy", "What is inventory value proxy?", "Selling price multiplied by available quantity, used as a rough commercial signal."),
        ("Easy", "Why make discount bands?", "They simplify interpretation and filtering in dashboards and Excel."),
        ("Easy", "What is price per 100g?", "A normalized price metric that helps compare different package sizes."),
        ("Easy", "How many raw rows are in the dataset?", "3,732 rows."),
        ("Easy", "What is the raw stockout rate?", "12.14% in the current run."),
    ]
    medium = [
        ("Medium", "How did you handle encoding issues?", "The default UTF-8 read failed, so the pipeline reads the file with cp1252 and writes a UTF-8 cleaned CSV."),
        ("Medium", "Why exclude invalid commercial rows from KPI views?", "Zero or invalid price/weight can distort averages, price-per-weight and inventory value."),
        ("Medium", "Explain your priority score.", "It is a transparent weighted rule using stockout status, low quantity, high MRP, category risk, discount and weight bucket."),
        ("Medium", "Why not use machine learning for stockout prediction?", "The dataset is a snapshot without historical demand, so an explainable rule is more honest than a weak ML model."),
        ("Medium", "How would you build this in Power BI?", "Import clean inventory and KPI CSVs, create measures, build overview, category health, watchlist and discount pages."),
        ("Medium", "How do you validate SQL output?", "Check row counts, compare Python and SQL aggregates, inspect top categories and verify no invalid rows enter KPI views."),
        ("Medium", "What does a high category stockout rate indicate?", "Potential availability risk, replenishment issues or category assortment problems."),
        ("Medium", "How would you use XLOOKUP in this project?", "Lookup SKU details from watchlist into clean inventory or category health tables."),
        ("Medium", "How would you create an Excel what-if model?", "Set a target stockout rate and calculate the gap by category to estimate action priority."),
        ("Medium", "What is the difference between stockout rate and available quantity?", "Stockout rate is category-level availability health; available quantity is SKU-level stock count."),
        ("Medium", "How would you prioritize between two unavailable SKUs?", "Compare MRP, category stockout rate, likely demand proxy, discount and business criticality."),
        ("Medium", "What is a CTE and why use it?", "A common table expression structures multi-step SQL logic, making the query readable and debuggable."),
        ("Medium", "What is the difference between RANK and DENSE_RANK?", "RANK skips numbers after ties; DENSE_RANK does not."),
        ("Medium", "How do window functions help analysts?", "They calculate rankings, running totals, lag values and partitioned metrics without collapsing rows."),
        ("Medium", "How would you detect duplicate products?", "Group by product name and count distinct categories or package attributes."),
        ("Medium", "How would you explain the charts?", "Stockout chart diagnoses weak categories; discount chart shows promotional intensity; scatter shows price-discount-stock relationships."),
        ("Medium", "What question would you ask the business team?", "Which SKUs are high-demand or high-margin, and what lead times apply by category?"),
        ("Medium", "What extra data would improve this most?", "Order history, sales velocity, margin, dark-store ID, expiry date and replenishment lead time."),
        ("Medium", "How is this relevant to Zepto/Blinkit?", "Quick commerce depends on SKU availability, stockout reduction and fast operational decisions."),
        ("Medium", "How is this relevant to ZS Decision Analytics?", "It frames data into a business decision, uses transparent modeling and communicates recommendations."),
        ("Medium", "How is this relevant to Product Analyst roles?", "Stockouts can affect user experience, conversion, retention and product reliability."),
        ("Medium", "How would you calculate lost sales if you had demand?", "Expected demand during stockout multiplied by selling price or margin."),
        ("Medium", "What is a guardrail metric here?", "Discount exposure or margin risk while improving availability."),
        ("Medium", "How would you automate this?", "Schedule ingestion, refresh SQL views, export dashboard datasets and alert categories above threshold."),
        ("Medium", "How would you handle missing values?", "Separate missing because unknown from invalid zeros; document assumptions and avoid silent deletion."),
        ("Medium", "What makes a dashboard executive-friendly?", "Clear KPIs, small number of charts, filters and an action list."),
        ("Medium", "What is the difference between analysis and recommendation?", "Analysis states what happened; recommendation states what action should be taken."),
        ("Medium", "How would you test if discounts reduce stockout risk?", "Join historical demand and inventory snapshots, compare stockout rates by discount bands while controlling for category."),
        ("Medium", "What SQL pattern would answer top N per category?", "Use ROW_NUMBER or DENSE_RANK partitioned by category."),
        ("Medium", "How do you avoid misleading conclusions?", "State limitations, avoid causal claims and separate proxy metrics from true business impact."),
        ("Medium", "How would you explain price-per-100g?", "It normalizes price across package sizes to make products comparable."),
        ("Medium", "What is the strongest insight from this run?", "Biscuits have the highest stockout rate among categories in the current output."),
        ("Medium", "What is the strongest action item?", "Review top-ranked unavailable and low-stock SKUs in the replenishment watchlist."),
        ("Medium", "How do you make this ATS-friendly?", "Use keywords: SQL, Excel, Power BI, Python, stockout analysis, SKU performance, KPI dashboard and decision analytics."),
        ("Medium", "What is one mistake to avoid in resume bullets?", "Do not say you improved revenue unless the dataset proves revenue impact."),
    ]
    hard = [
        ("Hard", "Design a true stockout prediction model.", "Use historical inventory snapshots, sales velocity, price, promotions, seasonality, dark-store ID and lead time; predict stockout probability per SKU-store-day."),
        ("Hard", "How would you estimate lost sales from stockouts?", "Estimate expected demand during unavailable windows using comparable available periods, then multiply by margin or selling price."),
        ("Hard", "How would you validate priority score weights?", "Backtest against historical stockout recovery, sales loss or operations outcomes; tune weights with stakeholder constraints."),
        ("Hard", "How would you handle category duplicates in the dataset?", "Investigate whether duplicates are true multi-category listings or data quality issues; define a canonical product-category rule."),
        ("Hard", "How would you build an alerting system?", "Trigger alerts when category stockout rate, high-value unavailable SKUs or discount exposure crosses threshold."),
        ("Hard", "How would you calculate replenishment quantity?", "Use forecast demand during lead time plus safety stock minus current inventory, adjusted for pack size and expiry risk."),
        ("Hard", "How would you optimize inventory under limited storage?", "Rank SKUs by expected margin, demand, substitution risk and space usage; solve as a constrained allocation problem."),
        ("Hard", "How would you connect this to product conversion?", "Join product availability with sessions/search/add-to-cart events and compare conversion when items are available versus unavailable."),
        ("Hard", "How would you prove stockouts cause lower retention?", "Use user-level exposure to unavailable items, control for category and user intent, and compare repeat behavior with matched groups."),
        ("Hard", "How would you present this to a CEO?", "Lead with stockout rate, high-risk categories, expected business risk, top actions and required data gaps."),
        ("Hard", "How would you present this to an operations manager?", "Lead with SKU watchlist, category priority, reorder inputs and execution plan."),
        ("Hard", "How would you present this to a product manager?", "Lead with availability as user experience, conversion risk, guardrails and experiment ideas."),
        ("Hard", "How would you convert this into an A/B test?", "Test availability intervention or substitution feature for exposed users, with conversion and retention as metrics and margin as guardrail."),
        ("Hard", "What if a high stockout category has low demand?", "Do not prioritize blindly; combine stockout with demand, margin or customer search signals."),
        ("Hard", "What if discounts are high because products are slow-moving?", "Join sales velocity and expiry data before assuming discount exposure is bad."),
        ("Hard", "How would you detect data leakage in a future ML model?", "Avoid using future stockout status, future sales or post-decision variables as predictors."),
        ("Hard", "How would you build a star schema?", "Fact inventory snapshot with dimensions for SKU, category, store, date, price and promotion."),
        ("Hard", "How would you scale SQL to millions of rows?", "Partition by date/store, index join keys, pre-aggregate KPI tables and avoid repeated full scans."),
        ("Hard", "How would you investigate a sudden stockout spike?", "Slice by category, store, supplier, delivery date, promotions, demand spike and data pipeline failures."),
        ("Hard", "How would you distinguish operational stockout from catalog issue?", "Use inventory, listing status, search visibility and order attempt logs."),
        ("Hard", "How would you create a North Star metric for this?", "Reliable availability rate for high-intent/high-demand SKUs, with margin and wastage guardrails."),
        ("Hard", "What would be your SQL approach for cohort retention?", "Create first activity cohort, join future activity, compute retained users by cohort age using date differences."),
        ("Hard", "What ZS-style case can this become?", "Client has poor availability in quick commerce; estimate business impact and recommend inventory investment priorities."),
        ("Hard", "How would you quantify confidence in recommendations?", "Use sensitivity analysis across priority weights and thresholds; report stable top categories/SKUs."),
        ("Hard", "What would you do differently with company data?", "Build SKU-store-day model, lost sales estimate, margin-aware replenishment recommendation and automated dashboard refresh."),
    ]
    return easy + medium + hard


def questions_section() -> str:
    qs = question_bank()
    assert len(qs) == 85, len(qs)
    sections = []
    for level in ["Easy", "Medium", "Hard"]:
        items = [(i + 1, q, a) for i, (lvl, q, a) in enumerate(qs) if lvl == level]
        body = "".join(f"<div class='qa'><p><strong>Q{n}. {esc(q)}</strong></p><p>{esc(a)}</p></div>" for n, q, a in items)
        sections.append(f"<h3>{level} Questions</h3>{body}")
    return section("85 Interview Questions: Easy to Hard", "\n".join(sections), "questions")


def source_section(sources: list[dict[str, str]]) -> str:
    rows = "".join(f"<li>{esc(s['title'])}<br><span>{esc(s['url'])}</span></li>" for s in sources)
    return section(
        "Firecrawl Research Sources",
        f"""
<p>Used to identify current public interview patterns for DA, PA, quick-commerce, e-commerce and ZS Decision Analytics roles. Questions in this pack are synthesized and adapted to QuickCommerceOps.</p>
<ol class="sources">{rows}</ol>
""",
    )


def build_html() -> str:
    metrics = load_metrics()
    sources = load_sources()
    category = metrics["category"]
    watchlist = metrics["watchlist"]
    discount = metrics["discount"]
    audit = metrics["audit"]
    top = metrics["top_category"]
    top_sku = metrics["top_sku"]

    css = """
@page { size: A4; margin: 13mm 12mm; }
* { box-sizing: border-box; }
body { margin: 0; color: #151515; background: #fff; font-family: Arial, Helvetica, sans-serif; font-size: 10.2pt; line-height: 1.42; }
h1 { font-size: 34pt; line-height: 1.02; margin: 0 0 8px; }
h2 { font-size: 19pt; margin: 0 0 10px; border-bottom: 3px solid #111; padding-bottom: 5px; text-transform: uppercase; letter-spacing: .2px; }
h3 { font-size: 13.5pt; margin: 14px 0 7px; color: #d21f32; }
h4 { font-size: 11.5pt; margin: 12px 0 5px; }
p { margin: 0 0 8px; }
ul, ol { margin-top: 4px; padding-left: 20px; }
li { margin-bottom: 4px; }
.cover { min-height: 95vh; display: flex; flex-direction: column; justify-content: center; border: 3px solid #111; padding: 32px; position: relative; }
.cover:before { content: "BOOK"; position: absolute; right: 24px; top: 22px; color: #fff; background: #d21f32; padding: 5px 9px; font-weight: 800; }
.eyebrow { text-transform: uppercase; letter-spacing: 1.2px; font-weight: 700; font-size: 9.5pt; color: #d21f32; }
.subtitle { font-size: 14pt; max-width: 690px; }
.page { page-break-before: always; border-top: 6px solid #111; padding-top: 10px; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 12px 0; }
.metric { border: 1px solid #111; padding: 9px; min-height: 74px; }
.metric strong { display: block; font-size: 18pt; }
.resume-box, .callout, .rule-box { border: 2px solid #111; padding: 10px; margin: 8px 0; background: #f7f7f7; }
.rule-box { border-color: #d21f32; }
.rule-box strong { color: #d21f32; }
.keywords { font-weight: 700; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; table-layout: fixed; }
th, td { border: 1px solid #111; padding: 6px; vertical-align: top; word-wrap: break-word; }
th { background: #111; color: #fff; border-color: #111; }
pre { background: #1d1d1d; color: #f5f5f5; border: 3px solid #111; border-top: 12px solid #d21f32; padding: 10px; white-space: pre-wrap; font-size: 8.4pt; line-height: 1.35; border-radius: 4px; }
code { font-family: Menlo, Consolas, monospace; }
.vector { width: 100%; max-height: 190px; margin: 8px 0; }
.small-vector { max-height: 150px; }
.shot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.shot { border: 1px solid #111; padding: 7px; break-inside: avoid; }
.shot img { width: 100%; filter: grayscale(100%); border: 1px solid #777; }
.photo-note { font-size: 9.5pt; color: #333; }
.annotated-output { display: grid; grid-template-columns: 64% 36%; gap: 10px; align-items: start; }
.output-image-wrap { border: 3px solid #111; padding: 7px; background: #fff; }
.output-image-wrap img { width: 100%; display: block; filter: grayscale(100%) contrast(1.08); }
.output-callouts { display: flex; flex-direction: column; gap: 8px; }
.arrow-callout { display: grid; grid-template-columns: 28px 1fr; gap: 6px; border: 2px solid #d21f32; padding: 8px; background: #fff; break-inside: avoid; }
.arrow-callout strong { color: #d21f32; }
.arrow-mark { color: #d21f32; font-weight: 900; font-size: 15pt; line-height: 1; }
.output-page h2 { color: #111; }
.qa { border-bottom: 1px solid #ccc; padding: 5px 0; break-inside: avoid; }
.sources li { font-size: 8.6pt; }
.sources span { color: #333; word-break: break-all; }
.data-table { font-size: 8.2pt; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.chapter-label { display: inline-block; color: #fff; background: #d21f32; padding: 3px 7px; font-size: 8.5pt; font-weight: 800; margin-bottom: 8px; }
.lesson-card { border: 2px solid #111; padding: 10px; margin: 10px 0; break-inside: avoid; }
.lesson-card h4 { color: #d21f32; margin-top: 0; }
.code-walk { table-layout: fixed; font-size: 7.2pt; }
.code-walk th:nth-child(1), .code-walk td:nth-child(1) { width: 36px; text-align: right; }
.code-walk th:nth-child(2), .code-walk td:nth-child(2) { width: 48%; }
.code-walk code { white-space: pre-wrap; font-size: 7.2pt; }
.plain { display: inline-block; margin-top: 3px; color: #222; }
.wide-code { break-inside: auto; }
.wide-code table { break-inside: auto; }
.wide-code tr { break-inside: avoid; page-break-inside: avoid; }
.ln { color: #d21f32; font-weight: 800; }
"""

    cover = f"""
<section class="cover">
  <p class="eyebrow">ATS Resume + Learning + Interview Pack</p>
  <h1>QuickCommerceOps</h1>
  <p class="subtitle">A complete black-and-white guide for learning, explaining and interviewing with the quick-commerce inventory analytics project.</p>
  <div class="grid">
    <div class="metric"><span>Rows</span><strong>{int(audit["raw_rows"]):,}</strong></div>
    <div class="metric"><span>Categories</span><strong>{int(audit["categories"])}</strong></div>
    <div class="metric"><span>Stockout</span><strong>{audit["raw_stockout_rate_pct"]}%</strong></div>
    <div class="metric"><span>Watchlist</span><strong>{len(watchlist):,}</strong></div>
  </div>
  <p><strong>Stack:</strong> SQL, Excel, Power BI-ready CSVs, Python, pandas, numpy, matplotlib, EDA, HTML/CSS.</p>
  <p><strong>Core decision:</strong> identify category availability gaps and rank SKUs for replenishment action.</p>
</section>
"""

    overview = section(
        "Project Overview",
        f"""
<div class="callout"><strong>Business context:</strong> Quick-commerce platforms need product availability. If important SKUs are unavailable, customers may abandon, substitute or shift to another platform.</div>
<h3>Actual Output Summary</h3>
<ul>
  <li>Raw rows: <strong>{int(audit["raw_rows"]):,}</strong></li>
  <li>Valid commercial rows: <strong>{int(audit["valid_commercial_rows"]):,}</strong></li>
  <li>Invalid commercial rows excluded from KPI views: <strong>{int(audit["invalid_commercial_rows"])}</strong></li>
  <li>Highest stockout category: <strong>{esc(top["category"])}</strong> at <strong>{top["stockout_rate_pct"]}%</strong></li>
  <li>Top watchlist SKU: <strong>{esc(top_sku["product_name"])}</strong></li>
</ul>
<h3>Category Health Preview</h3>{table_html(category, 8)}
<h3>Replenishment Watchlist Preview</h3>{table_html(watchlist, 8)}
<h3>Discount Exposure Preview</h3>{table_html(discount, 8)}
""",
    )

    final_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>QuickCommerceOps Learning Interview Pack</title>
  <style>{css}</style>
</head>
<body>
{cover}
{toc_section()}
{overview}
{ats_section()}
{business_fundamentals_section(metrics)}
{jargon_section()}
{data_dictionary_section(metrics)}
{learning_path_section(metrics)}
{output_screenshots_section()}
{syntax_decoder_section()}
{project_story_section()}
{python_libraries_deep_section()}
{python_section()}
{full_python_walkthrough_section()}
{sql_section()}
{full_sql_walkthrough_section()}
{excel_powerbi_section()}
{excel_deep_dive_section()}
{powerbi_deep_dive_section()}
{leetcode_section()}
{interviewer_depth_section()}
{questions_section()}
{source_section(sources)}
</body>
</html>
"""
    return final_html


def main() -> None:
    PACK.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_html(), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
