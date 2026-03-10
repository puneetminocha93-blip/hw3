"""
pages/overview.py — Page 1: Overview & KPIs
"""

import dash
from dash import html, dcc, callback, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data as D

dash.register_page(__name__, path="/", name="Overview", order=0)

# ---------------------------------------------------------------------------
# Load data once at module level
# ---------------------------------------------------------------------------
_df = D.load_data("data/avocado.csv")
ALL_YEARS = sorted(_df["year"].unique())

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AVOCADO_GREEN  = "#4a7c59"
AVOCADO_DARK   = "#2c4a35"
AVOCADO_CREAM  = "#f7f3e9"
AVOCADO_YELLOW = "#e8d44d"

def fmt_billions(n):
    if n >= 1e9: return f"{n/1e9:.1f}B"
    if n >= 1e6: return f"{n/1e6:.1f}M"
    return f"{n:,.0f}"

def fmt_dollars(n):
    if n >= 1e9: return f"${n/1e9:.1f}B"
    if n >= 1e6: return f"${n/1e6:.1f}M"
    return f"${n:,.0f}"

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

layout = html.Div([
    html.H1("Overview", className="page-header"),
    html.P("A high-level summary of US avocado sales.", className="page-sub"),

    # Filters row
    html.Div([
        html.Div([
            html.Label("Year Range", style={"fontSize": "0.78rem", "fontWeight": 500,
                                            "letterSpacing": "0.06em", "color": "#666",
                                            "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.RangeSlider(
                id="overview-year-slider",
                min=ALL_YEARS[0], max=ALL_YEARS[-1],
                value=[ALL_YEARS[0], ALL_YEARS[-1]],
                marks={y: str(y) for y in ALL_YEARS},
                step=1,
                tooltip={"placement": "bottom"},
            ),
        ], style={"flex": 2, "marginRight": "32px"}),

        html.Div([
            html.Label("Avocado Type", style={"fontSize": "0.78rem", "fontWeight": 500,
                                              "letterSpacing": "0.06em", "color": "#666",
                                              "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.RadioItems(
                id="overview-type-radio",
                options=[{"label": t, "value": t} for t in ["All", "conventional", "organic"]],
                value="All",
                inline=True,
                inputStyle={"marginRight": "4px"},
                labelStyle={"marginRight": "16px", "fontSize": "0.88rem"},
            ),
        ], style={"flex": 1}),
    ], className="card", style={"display": "flex", "alignItems": "center", "padding": "18px 24px"}),

    # KPI cards
    html.Div(id="overview-kpis", style={"display": "grid",
        "gridTemplateColumns": "repeat(4, 1fr)", "gap": "16px", "marginBottom": "20px"}),

    # Tables row
    html.Div([
        html.Div([
            html.P("Top 5 Regions by Volume", className="section-title"),
            html.P("Total units sold by region & type", className="section-sub"),
            dash_table.DataTable(
                id="overview-vol-table",
                style_header={"backgroundColor": AVOCADO_DARK, "color": "#fff",
                              "fontWeight": 600, "fontSize": "0.8rem",
                              "letterSpacing": "0.04em"},
                style_cell={"fontSize": "0.85rem", "padding": "8px 12px",
                            "fontFamily": "DM Sans, sans-serif"},
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
                ],
            ),
        ], className="card", style={"flex": 1}),

        html.Div([
            html.P("Top 5 Regions by Revenue", className="section-title"),
            html.P("Estimated revenue (volume × avg price)", className="section-sub"),
            dash_table.DataTable(
                id="overview-rev-table",
                style_header={"backgroundColor": AVOCADO_DARK, "color": "#fff",
                              "fontWeight": 600, "fontSize": "0.8rem",
                              "letterSpacing": "0.04em"},
                style_cell={"fontSize": "0.85rem", "padding": "8px 12px",
                            "fontFamily": "DM Sans, sans-serif"},
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
                ],
            ),
        ], className="card", style={"flex": 1}),
    ], style={"display": "flex", "gap": "20px"}),

    # Dataset summary
    html.Div([
        html.P("Dataset Summary", className="section-title"),
        html.P("Descriptive statistics for all numeric columns", className="section-sub"),
        dash_table.DataTable(
            id="overview-skim-table",
            style_header={"backgroundColor": AVOCADO_GREEN, "color": "#fff",
                          "fontWeight": 600, "fontSize": "0.78rem"},
            style_cell={"fontSize": "0.8rem", "padding": "7px 10px",
                        "fontFamily": "DM Sans, sans-serif"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
            ],
        ),
    ], className="card"),
])

# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("overview-kpis", "children"),
    Output("overview-vol-table", "data"),
    Output("overview-vol-table", "columns"),
    Output("overview-rev-table", "data"),
    Output("overview-rev-table", "columns"),
    Output("overview-skim-table", "data"),
    Output("overview-skim-table", "columns"),
    Input("overview-year-slider", "value"),
    Input("overview-type-radio", "value"),
)
def update_overview(year_range, avocado_type):
    df = D.filter_df(_df, year_range=tuple(year_range), avocado_type=avocado_type)

    # KPIs
    total_vol  = df["total_volume"].sum()
    total_rev  = df["revenue"].sum()
    avg_price  = df["average_price"].mean()
    premium    = D.organic_premium(_df)  # always show global premium

    kpi_data = [
        ("🥑", "Total Volume",  fmt_billions(total_vol),  AVOCADO_GREEN),
        ("💵", "Est. Revenue",  fmt_dollars(total_rev),   AVOCADO_DARK),
        ("🏷️", "Avg Price",    f"${avg_price:.2f}",       "#8b5e3c"),
        ("🌿", "Organic Premium", f"+{premium:.1f}%",    "#5a7a40"),
    ]
    kpi_cards = [
        html.Div([
            html.Div(icon, style={"fontSize": "1.6rem", "marginBottom": "6px"}),
            html.Div(val,  className="kpi-value", style={"color": col}),
            html.Div(lbl,  className="kpi-label"),
        ], className="kpi-card")
        for icon, lbl, val, col in kpi_data
    ]

    # Top volume table
    tv = D.top_volume(df, n=5)
    tv["Total Volume"] = tv["Total Volume"].map(lambda x: f"{x:,.0f}")
    tv_cols = [{"name": c, "id": c} for c in tv.columns]

    # Top revenue table
    tr = D.top_revenue(df, n=5)
    tr["Total Revenue"] = tr["Total Revenue"].map(lambda x: f"${x:,.0f}")
    tr_cols = [{"name": c, "id": c} for c in tr.columns]

    # Dataset summary
    skim = D.skim_summary(df)
    for col in skim.select_dtypes(include="float").columns:
        skim[col] = skim[col].round(3)
    skim_cols = [{"name": c, "id": c} for c in skim.columns]

    return kpi_cards, tv.to_dict("records"), tv_cols, \
           tr.to_dict("records"), tr_cols, \
           skim.to_dict("records"), skim_cols
