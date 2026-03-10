"""
pages/sku_elasticity.py — Page 5: SKU Breakdown & Price–Volume Elasticity
Converts SNS barplot, lmplot, and heatmap to Plotly.
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data as D

dash.register_page(__name__, path="/sku-elasticity", name="SKU & Elasticity", order=4)

_df = D.load_data("data/avocado.csv")
ALL_YEARS   = sorted(_df["year"].unique())
ALL_REGIONS = sorted(_df["region"].astype(str).unique())

AVOCADO_DARK  = "#2c4a35"
AVOCADO_GREEN = "#4a7c59"
BROWN         = "#8b5e3c"

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

layout = html.Div([
    html.H1("SKU Breakdown & Price–Volume Elasticity", className="page-header"),
    html.P("Understand which avocado sizes drive volume, and how price responds to quantity.",
           className="page-sub"),

    # Filters
    html.Div([
        html.Div([
            html.Label("Avocado Type", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.Checklist(
                id="sku-type-check",
                options=[{"label": " Conventional", "value": "conventional"},
                         {"label": " Organic",       "value": "organic"}],
                value=["conventional", "organic"],
                inline=True,
                inputStyle={"marginRight": "4px"},
                labelStyle={"marginRight": "20px", "fontSize": "0.88rem"},
            ),
        ], style={"flex": 1, "marginRight": "32px"}),

        html.Div([
            html.Label("Regions", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.Dropdown(
                id="sku-region-dropdown",
                options=[{"label": r, "value": r} for r in ALL_REGIONS],
                value=None,
                multi=True,
                placeholder="All regions (default)…",
                style={"fontSize": "0.85rem"},
            ),
        ], style={"flex": 2, "marginRight": "32px"}),

        html.Div([
            html.Label("Volume X-axis", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.RadioItems(
                id="sku-log-radio",
                options=[{"label": "Linear", "value": "linear"},
                         {"label": "Log",    "value": "log"}],
                value="linear", inline=True,
                inputStyle={"marginRight": "4px"},
                labelStyle={"marginRight": "14px", "fontSize": "0.88rem"},
            ),
        ], style={"flex": 1}),
    ], className="card", style={"display": "flex", "alignItems": "flex-start",
                                "padding": "18px 24px 22px"}),

    # SKU bar chart
    html.Div([
        html.P("Volume Breakdown by SKU / Bag Size", className="section-title"),
        html.P("Aggregate units sold per product type", className="section-sub"),
        dcc.Graph(id="sku-bar-chart", style={"height": "320px"}),
    ], className="card"),

    # Scatter / elasticity
    html.Div([
        html.P("Price–Volume Relationship (Elasticity)", className="section-title"),
        html.P("Scatter with OLS trendline — does higher volume push prices down?",
               className="section-sub"),
        dcc.Graph(id="sku-scatter-chart", style={"height": "440px"}),
    ], className="card"),

    # Correlation heatmap (collapsible)
    html.Details([
        html.Summary("▶ Correlation Heatmap", style={
            "fontFamily": "Syne, sans-serif", "fontWeight": 700,
            "fontSize": "1.1rem", "color": AVOCADO_DARK,
            "cursor": "pointer", "marginBottom": "12px",
        }),
        dcc.Graph(id="sku-heatmap", style={"height": "520px"}),
    ], className="card", style={"padding": "20px 24px"}),
])

# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------

@callback(
    Output("sku-bar-chart",    "figure"),
    Output("sku-scatter-chart","figure"),
    Output("sku-heatmap",      "figure"),
    Input("sku-type-check",    "value"),
    Input("sku-region-dropdown","value"),
    Input("sku-log-radio",     "value"),
)
def update_sku(types, regions, log_scale):
    df = _df.copy()
    if types:
        df = df[df["type"].isin(types)]
    if regions:
        df = D.filter_df(df, regions=regions)

    # ---- SKU bar chart (mirrors notebook) ----
    sku = D.sku_totals(df)
    sku_labels = {
        "plu4046": "PLU 4046\n(Hass Small)",
        "plu4225": "PLU 4225\n(Hass Large)",
        "plu4770": "PLU 4770\n(Hass XL)",
        "total_bags": "Total Bags",
    }
    sku["sku_label"] = sku["sku"].map(sku_labels)

    fig_sku = px.bar(
        sku,
        x="sku_label", y="volume",
        color="sku",
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={"sku_label": "", "volume": "Total Units"},
        text="volume",
    )
    fig_sku.update_traces(
        texttemplate="%{text:,.0f}", textposition="outside",
        hovertemplate="<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>",
    )
    fig_sku.update_layout(**_base_layout("Volume Breakdown by SKU / Bag Size"))
    fig_sku.update_coloraxes(showscale=False)
    fig_sku.update_traces(showlegend=False)

    # ---- Scatter + OLS trendline (mirrors sns.lmplot) ----
    scatter_df = df.assign(vol_mil=lambda d: d["total_volume"] / 1e6).copy()

    color_map = {"conventional": BROWN, "organic": AVOCADO_GREEN}
    fig_scatter = px.scatter(
        scatter_df,
        x="vol_mil", y="average_price",
        color="type",
        facet_col="type",
        color_discrete_map=color_map,
        trendline="ols",
        trendline_color_override="red",
        opacity=0.25,
        labels={"vol_mil": "Volume (Millions)", "average_price": "Average Price ($)", "type": "Type"},
        log_x=(log_scale == "log"),
    )
    fig_scatter.update_traces(
        selector={"mode": "markers"},
        hovertemplate="Volume: %{x:.2f}M<br>Price: $%{y:.2f}<extra></extra>",
    )
    fig_scatter.update_layout(**_base_layout("Price–Volume Relationship by Avocado Type"))
    fig_scatter.update_layout(showlegend=False)

    # ---- Correlation heatmap (mirrors sns.heatmap) ----
    corr = D.correlation_matrix(df)
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu_r",
            zmid=0,
            text=np.round(corr.values, 2),
            texttemplate="%{text:.2f}",
            hovertemplate="<b>%{y} × %{x}</b><br>r = %{z:.3f}<extra></extra>",
        )
    )
    fig_heat.update_layout(
        **_base_layout("Correlation Matrix of Numeric Features"),
        xaxis={"tickangle": -35},
        margin={"t": 60, "b": 100, "l": 120, "r": 30},
    )

    return fig_sku, fig_scatter, fig_heat


def _base_layout(title_text: str) -> dict:
    return dict(
        template="plotly_white",
        font={"family": "DM Sans, sans-serif"},
        margin={"t": 60, "b": 50, "l": 60, "r": 30},
        plot_bgcolor="#fafaf8",
        paper_bgcolor="rgba(0,0,0,0)",
        title={
            "text": title_text,
            "font": {"family": "Syne, sans-serif", "size": 16, "color": AVOCADO_DARK},
            "x": 0.5, "xanchor": "center",
        },
    )
