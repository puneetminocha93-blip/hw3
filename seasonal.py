"""
pages/seasonal.py — Page 2: Seasonal Trends
Converts the FacetGrid lineplot (monthly volume & price × type) to Plotly subplots.
"""

import dash
from dash import html, dcc, callback, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data as D

dash.register_page(__name__, path="/seasonal", name="Seasonal Trends", order=1)

_df = D.load_data("data/avocado.csv")
ALL_YEARS  = sorted(_df["year"].unique())
MONTH_NAMES = D.MONTH_NAMES

COLORS_YEAR = [
    "#4a7c59", "#e8d44d", "#8b5e3c", "#5b9bd5", "#e87d4a",
    "#9b59b6", "#1abc9c", "#e74c3c", "#3498db",
]
AVOCADO_DARK  = "#2c4a35"
AVOCADO_GREEN = "#4a7c59"

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

layout = html.Div([
    html.H1("Seasonal Trends", className="page-header"),
    html.P("Monthly volume and price patterns across conventional and organic avocados.",
           className="page-sub"),

    # Filters
    html.Div([
        html.Div([
            html.Label("Years to compare", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.Dropdown(
                id="seasonal-year-dropdown",
                options=[{"label": str(y), "value": y} for y in ALL_YEARS],
                value=ALL_YEARS,
                multi=True,
                placeholder="Select year(s)…",
                style={"fontSize": "0.88rem"},
            ),
        ], style={"flex": 2, "marginRight": "32px"}),

        html.Div([
            html.Label("Metric", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.RadioItems(
                id="seasonal-metric-radio",
                options=[
                    {"label": "Volume", "value": "volume"},
                    {"label": "Price",  "value": "price"},
                    {"label": "Both",   "value": "both"},
                ],
                value="both",
                inline=True,
                inputStyle={"marginRight": "4px"},
                labelStyle={"marginRight": "16px", "fontSize": "0.88rem"},
            ),
        ], style={"flex": 1}),
    ], className="card", style={"display": "flex", "alignItems": "center", "padding": "18px 24px"}),

    # Charts
    html.Div([
        dcc.Graph(id="seasonal-chart", style={"height": "620px"}),
    ], className="card"),
])

# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------

@callback(
    Output("seasonal-chart", "figure"),
    Input("seasonal-year-dropdown", "value"),
    Input("seasonal-metric-radio", "value"),
)
def update_seasonal(selected_years, metric):
    if not selected_years:
        selected_years = ALL_YEARS

    types = ["conventional", "organic"]

    show_vol   = metric in ("volume", "both")
    show_price = metric in ("price", "both")
    n_rows     = (1 if not show_vol or not show_price else 2)
    row_titles = []
    if show_vol:   row_titles.append("Total Volume")
    if show_price: row_titles.append("Average Price ($)")

    fig = make_subplots(
        rows=n_rows, cols=2,
        shared_xaxes=True,
        column_titles=["Conventional", "Organic"],
        row_titles=row_titles,
        vertical_spacing=0.10,
        horizontal_spacing=0.08,
    )

    for yi, year in enumerate(sorted(selected_years)):
        df_year = _df[_df["year"] == year]
        monthly = D.monthly_aggregates(df_year)
        color   = COLORS_YEAR[yi % len(COLORS_YEAR)]

        for ci, avtype in enumerate(types, start=1):
            sub = monthly[monthly["type"] == avtype].sort_values("month")
            x   = sub["month_name"]

            row_cursor = 1
            if show_vol:
                fig.add_trace(
                    go.Scatter(
                        x=x, y=sub["total_volume"],
                        mode="lines+markers",
                        name=str(year),
                        line={"color": color, "width": 2},
                        marker={"size": 6},
                        legendgroup=str(year),
                        showlegend=(ci == 1 and row_cursor == 1),
                        hovertemplate=f"{year} {avtype}<br>%{{x}}: %{{y:,.0f}} units<extra></extra>",
                    ),
                    row=row_cursor, col=ci,
                )
                if show_price:
                    row_cursor += 1

            if show_price:
                fig.add_trace(
                    go.Scatter(
                        x=x, y=sub["average_price"],
                        mode="lines+markers",
                        name=str(year),
                        line={"color": color, "width": 2, "dash": "dot"},
                        marker={"size": 6, "symbol": "diamond"},
                        legendgroup=str(year),
                        showlegend=(ci == 1 and not show_vol),
                        hovertemplate=f"{year} {avtype}<br>%{{x}}: $%{{y:.2f}}<extra></extra>",
                    ),
                    row=row_cursor, col=ci,
                )

    fig.update_layout(
        template="plotly_white",
        font={"family": "DM Sans, sans-serif"},
        legend={"title": "Year", "orientation": "h",
                "y": -0.12, "x": 0.5, "xanchor": "center"},
        margin={"t": 60, "b": 60, "l": 60, "r": 30},
        plot_bgcolor="#fafaf8",
        paper_bgcolor="rgba(0,0,0,0)",
        title={
            "text": "Monthly Volume and Price Trends",
            "font": {"family": "Syne, sans-serif", "size": 18, "color": AVOCADO_DARK},
            "x": 0.5, "xanchor": "center",
        },
    )
    return fig
