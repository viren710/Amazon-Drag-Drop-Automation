# 📊 Amazon Sales Dashboard

A Streamlit dashboard for exploring Amazon-style sales data (CSV/Excel), with automatic cleaning, feature engineering, KPI tracking, and chart generation.

## Features
- **Upload & process** — drag in a CSV or XLSX file; the app cleans it and builds derived columns automatically
- **Data cleaning** — drops blank rows, removes duplicated header rows, coerces numeric columns, computes `Sales` from `Quantity Ordered × Price Each`
- **Feature engineering** — splits `Order Date` into Year/Month/Day/Hour columns, and parses `Purchase Address` into City/State
- **Interactive filters** — sidebar filters by City and Product
- **KPI cards** — total sales, total orders, unique products, average order value, top product, top city
- **Auto-generated charts** — built from three reusable chart types (bar, line, histogram); each chart is added with a single line in a config list, so extending the dashboard doesn't require new functions
- **Sold-together analysis** — finds which product pairs are most frequently bought in the same order

## Tech Stack
- **Frontend:** Streamlit
- **Backend:** Pandas, Matplotlib, Seaborn

## Project Structure
```
├── Amazon_frontend_simple.py   # Streamlit UI — upload, filters, KPIs, charts
└── Amazon_backend_simple.py    # Data loading, cleaning, feature engineering, chart builders
```

## Run Locally
```bash
pip install streamlit pandas matplotlib seaborn openpyxl
streamlit run Amazon_frontend_simple.py
```

## Design Notes
Charts are generated from a single config list (`CHART_LIST` in the backend) that maps required columns → chart type. Adding a new chart is a one-line addition rather than a new function, and any chart whose required columns are missing is skipped automatically.
