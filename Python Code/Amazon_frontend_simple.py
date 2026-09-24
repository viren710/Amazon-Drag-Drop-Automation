"""
Amazon Sales Dashboard — Frontend (Streamlit, Simplified Teaching Version)
============================================================================
This file just does 5 things, in order:
  1. Let the user upload a file
  2. Run it through the backend pipeline (load -> clean -> feature engineer)
  3. Show a few filters in the sidebar
  4. Show KPI numbers
  5. Loop over every chart the backend built and display it
"""

import streamlit as st
from Amazon_backend_simple import (
    load_single_file,
    clean_data,
    feature_engineering,
    add_city_state_column,
    get_kpis,
    analyze_sold_together,
    create_visualizations,
)

st.set_page_config(page_title="Amazon Sales Dashboard", layout="wide")
st.title("📊 Amazon Sales Dashboard")

# ---------------------------------------------------------------------------
# 1 & 2. Upload and process the file
# ---------------------------------------------------------------------------

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if not uploaded_file:
    st.info("⬆ Please upload a CSV or Excel file to begin.")
    st.stop()

df = load_single_file(uploaded_file)
df = clean_data(df)
df = feature_engineering(df)
if "Purchase Address" in df.columns:
    df = add_city_state_column(df)

# ---------------------------------------------------------------------------
# 3. Sidebar filters (optional — just narrows down `df` before we use it).................................................


































# ---------------------------------------------------------------------------

st.sidebar.header("Filters")

if "City" in df.columns:
    cities = sorted(df["City"].dropna().unique())
    chosen_cities = st.sidebar.multiselect("City", cities)
    if chosen_cities:
        df = df[df["City"].isin(chosen_cities)]

if "Product" in df.columns:
    products = sorted(df["Product"].dropna().unique())
    chosen_products = st.sidebar.multiselect("Product", products)
    if chosen_products:
        df = df[df["Product"].isin(chosen_products)]

# ---------------------------------------------------------------------------
# 4. KPI numbers
# ---------------------------------------------------------------------------

st.subheader("📌 Key Metrics")
kpis = get_kpis(df)
st.metric("Total Sales", f"${kpis['total_sales']:,.2f}")
st.metric("Total Orders", f"{kpis['total_orders']:,}")
st.metric("Unique Products", f"{kpis['unique_products']:,}")
st.metric("Avg Order Value", f"${kpis['avg_order_value']:,.2f}")
st.metric("Top Product", str(kpis["top_product"]))
st.metric("Top City", str(kpis["top_city"]))

# ---------------------------------------------------------------------------
# 5. Charts — just loop over whatever the backend gives us, two per row
# ---------------------------------------------------------------------------

st.subheader("📈 Charts")
charts = create_visualizations(df)
titles = list(charts.keys())

for i in range(0, len(titles), 2):
    col1, col2 = st.columns(2)
    for col, title in zip([col1, col2], titles[i:i + 2]):
        with col:
            st.markdown(f"**{title}**")
            st.pyplot(charts[title])

# ---------------------------------------------------------------------------
# Sold-together list (text version, alongside the chart above)
# ---------------------------------------------------------------------------

st.subheader("🤝 Most Often Sold Together")
combos = analyze_sold_together(df)
if combos:
    for (product_a, product_b), count in combos:
        st.write(f"- **{product_a} + {product_b}** → bought together **{count}** times")
else:
    st.info("No product combination data available.")

# ---------------------------------------------------------------------------
# Raw data preview
# ---------------------------------------------------------------------------

st.subheader("📝 Data Preview")
st.dataframe(df.head(20))
