# 🥑 Avocado Sales Dashboard

Interactive multi-page Dash dashboard for US avocado sales data (2015–2023).

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place your data file
#    The app expects:  avocado_dashboard/data/avocado.csv
mkdir -p data
cp /path/to/avocado.csv data/avocado.csv

# 4. Run the dashboard
python app.py
```

Then open **http://127.0.0.1:8050** in your browser.

---

## Project Structure

```
avocado_dashboard/
├── app.py                  # Dash entry point, sidebar layout, global CSS
├── data.py                 # All pandas logic (unchanged from notebook)
├── pages/
│   ├── overview.py         # Page 1 – KPI cards & top-5 tables
│   ├── seasonal.py         # Page 2 – Monthly volume & price line charts
│   ├── organic_vs_conv.py  # Page 3 – Yearly trends & YoY growth
│   ├── regional.py         # Page 4 – Regional bar chart & US map
│   └── sku_elasticity.py   # Page 5 – SKU volumes, OLS scatter, heatmap
├── requirements.txt
└── README.md
```

---

## Pages & Features

| Page | URL | Key Interactions |
|---|---|---|
| Overview | `/` | Year range slider, type radio, KPI cards, top-5 tables |
| Seasonal Trends | `/seasonal` | Multi-year overlay dropdown, metric toggle (Volume/Price/Both) |
| Organic vs Conventional | `/organic-vs-conventional` | Year range slider, organic premium banner, CSV download |
| Regional Analysis | `/regional` | Year range, type radio, Top-N slider, bar chart + US map |
| SKU & Elasticity | `/sku-elasticity` | Type checkboxes, region multi-select, log-scale toggle, heatmap |

---

## Notes

- All analytical logic in `data.py` is **identical** to `06_avocado_analysis.py` — only
  rendering changed (matplotlib/seaborn → Plotly/Dash).
- The `statsmodels` package is required for Plotly's built-in OLS trendlines.
- The US map uses approximate lat/lon centroids for the 59 metro regions.
