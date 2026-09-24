"""
Amazon Sales Dashboard — Backend (Simplified Teaching Version)
================================================================
This file has 4 sections:
  1. Load data
  2. Clean data
  3. Add useful columns (feature engineering)
  4. Make charts

The big idea in Section 4: instead of writing a brand-new function for every
single chart, we notice that almost every chart is really just one of THREE
types:
    - a BAR chart   (compare totals across categories, e.g. sales per city)
    - a LINE chart  (show a trend over time, e.g. sales per month)
    - a HISTOGRAM   (show the spread of one numeric column, e.g. prices)

So we write ONE function per chart type, and then just tell each function
which columns to use. This keeps the code short and easy to extend — adding
a new chart is often just one new line in CHART_LIST, not a whole new
function.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from itertools import combinations

sns.set_theme(style="whitegrid")

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# ---------------------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------------------

import pandas as pd

def load_single_file(file):

    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)

    else:
        return None


# ---------------------------------------------------------------------------
# 2. CLEAN DATA
# ---------------------------------------------------------------------------

def clean_data(df):
    """Remove blank rows, fix numeric columns, and calculate Sales."""
    df = df.copy()
    df.dropna(how="all", inplace=True)

    # Some exports repeat the header row in the middle of the data — remove it.
    if "Quantity Ordered" in df.columns:
        df = df[df["Quantity Ordered"] != "Quantity Ordered"]

    for col in ["Quantity Ordered", "Price Each"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    numeric_cols_present = [c for c in ["Quantity Ordered", "Price Each"] if c in df.columns]
    if numeric_cols_present:
        df.dropna(subset=numeric_cols_present, inplace=True)
    df.drop_duplicates(inplace=True)

    if "Sales" not in df.columns and "Quantity Ordered" in df.columns and "Price Each" in df.columns:
        df["Sales"] = df["Quantity Ordered"] * df["Price Each"]

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. ADD USEFUL COLUMNS
# ---------------------------------------------------------------------------

def feature_engineering(df):
    """Break 'Order Date' into separate Year / Month / Day / Hour columns."""
    df = df.copy()
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        df.dropna(subset=["Order Date"], inplace=True)
        df["Year"] = df["Order Date"].dt.year
        df["Month"] = df["Order Date"].dt.month
        df["MonthName"] = df["Month"].apply(lambda m: MONTH_NAMES[m - 1])
        df["DayName"] = df["Order Date"].dt.dayofweek.apply(lambda d: DAY_NAMES[d])
        df["Hour"] = df["Order Date"].dt.hour
    return df


def add_city_state_column(df, address_column="Purchase Address"):
    """Split '123 Main St, City, ST 00000' into 'City' and 'State' columns."""
    df = df.copy()
    if address_column not in df.columns:
        return df

    parts = df[address_column].str.split(",", expand=True)
    df["City"] = parts[1].str.strip()
    df["State"] = parts[2].str.strip().str.split(" ").str[0]
    return df


def get_kpis(df):
    """Return a small dict of headline numbers for the KPI cards."""
    return {
        "total_sales": df["Sales"].sum() if "Sales" in df else 0,
        "total_orders": df["Order ID"].nunique() if "Order ID" in df else len(df),
        "unique_products": df["Product"].nunique() if "Product" in df else 0,
        "avg_order_value": df["Sales"].mean() if "Sales" in df else 0,
        "top_product": df.groupby("Product")["Sales"].sum().idxmax() if "Product" in df and "Sales" in df else "N/A",
        "top_city": df.groupby("City")["Sales"].sum().idxmax() if "City" in df and "Sales" in df else "N/A",
    }


# ---------------------------------------------------------------------------
# 4. CHARTS — three generic building blocks
# ---------------------------------------------------------------------------

def bar_chart(df, group_col, value_col, title, agg="sum", rotate=75, top_n=None, horizontal=False):
    """Group `value_col` by `group_col` and plot as a bar chart.
    Used for: sales by city/state, top products, sales by day, etc.
    """
    data = df.groupby(group_col)[value_col].agg(agg).sort_values(ascending=False)
    if top_n:
        data = data.head(top_n)

    fig, ax = plt.subplots(figsize=(9, 5))
    if horizontal:
        sns.barplot(x=data.values, y=data.index, hue=data.index, ax=ax, legend=False)
    else:
        sns.barplot(x=data.index, y=data.values, hue=data.index, ax=ax, legend=False)
        ax.tick_params(axis="x", rotation=rotate)

    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return fig


def line_chart(df, group_col, value_col, title, agg="sum", sort_order=None):
    """Group `value_col` by `group_col` and plot as a line chart.
    Used for: sales trend by month, orders by hour, etc.
    """
    data = df.groupby(group_col)[value_col].agg(agg)
    if sort_order:
        data = data.reindex(sort_order)
    else:
        data = data.sort_index()

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.lineplot(x=data.index, y=data.values, marker="o", ax=ax)
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return fig


def histogram(df, col, title):
    """Plot the distribution of a single numeric column.
    Used for: order quantity spread, price spread, etc.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(df[col], kde=True, ax=ax)
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Sold-together analysis (its own thing — not a bar/line/histogram)
# ---------------------------------------------------------------------------

def analyze_sold_together(df, top_n=10):
    """Find which two products most often appear in the same order."""
    if "Order ID" not in df.columns or "Product" not in df.columns:
        return []

    dup = df[df["Order ID"].duplicated(keep=False)]
    grouped = dup.groupby("Order ID")["Product"].apply(lambda x: sorted(set(x)))

    counter = Counter()
    for products in grouped:
        if len(products) > 1:
            counter.update(combinations(products, 2))

    return counter.most_common(top_n)


def sold_together_chart(df, top_n=10):
    combos = analyze_sold_together(df, top_n)
    if not combos:
        return None
    labels = [f"{a} + {b}" for (a, b), _ in combos]
    counts = [c for _, c in combos]

    fig, ax = plt.subplots(figsize=(9, max(4, 0.4 * len(labels))))
    sns.barplot(x=counts, y=labels, hue=labels, ax=ax, legend=False)
    ax.set_title("Most Frequently Bought Together", fontweight="bold")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Master chart list — this is the only place you need to touch to add,
# remove, or change a chart.
# ---------------------------------------------------------------------------

def create_visualizations(df):
    """Build every chart that this dataset has the columns for.

    Each entry below says: "if these columns exist, build this chart".
    To add a new chart, add one line here — no new function needed.
    """
    figs = {}

    chart_list = [
        ("Monthly Sales Trend", ["Month", "Sales"],
         lambda: line_chart(df, "Month", "Sales", "Monthly Sales Trend")),

        ("Sales by Day of Week", ["DayName", "Sales"],
         lambda: bar_chart(df, "DayName", "Sales", "Sales by Day of Week", rotate=0)),

        ("Best Hour for Ads", ["Hour", "Quantity Ordered"],
         lambda: line_chart(df, "Hour", "Quantity Ordered", "Best Hour for Ads")),

        ("Sales by City", ["City", "Sales"],
         lambda: bar_chart(df, "City", "Sales", "Sales by City")),

        ("Sales by State", ["State", "Sales"],
         lambda: bar_chart(df, "State", "Sales", "Sales by State", rotate=45)),

        ("Top Products by Revenue", ["Product", "Sales"],
         lambda: bar_chart(df, "Product", "Sales", "Top Products by Revenue")),

        ("Most Sold Products (Quantity)", ["Product", "Quantity Ordered"],
         lambda: bar_chart(df, "Product", "Quantity Ordered", "Most Sold Products (Quantity)")),

        ("Order Quantity Distribution", ["Quantity Ordered"],
         lambda: histogram(df, "Quantity Ordered", "Order Quantity Distribution")),

        ("Product Price Distribution", ["Price Each"],
         lambda: histogram(df, "Price Each", "Product Price Distribution")),

        ("Most Frequently Bought Together", ["Order ID", "Product"],
         lambda: sold_together_chart(df)),
    ]

    for title, required_cols, build_fn in chart_list:
        if all(col in df.columns for col in required_cols):
            try:
                fig = build_fn()
                if fig is not None:
                    figs[title] = fig
            except Exception:
                pass  # skip a chart that fails rather than crash the whole page

    return figs
