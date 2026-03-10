"""
pages/organic_vs_conv.py — Page 3: Organic vs Conventional
Converts yearly trend + YoY growth sns.relplots to Plotly subplots.
"""

import dash
from dash import html, dcc, callback, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data as D

dash.register_page(__name__, path="/organic-vs-conventional",
                   name="Organic vs Conventional", order=2)

_df = D.load_data("data/avocado.csv")
ALL_YEARS = sorted(_df["year"].unique())

BROWN = "#8b5e3c"
GREEN = "#4a7c59"
AVOCADO_DARK = "#2c4a35"

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

layout = html.Div([
    html.H1("Organic vs Conventional", className="page-header"),
    html.P("Compare pricing, volume, and year-over-year growth between the two avocado types.",
           className="page-sub"),

    # Premium banner (dynamic)
    html.Div(id="ovc-premium-banner"),

    # Year filter
    html.Div([
        html.Label("Year Range", style={"fontSize": "0.78rem", "fontWeight": 500,
                   "letterSpacing": "0.06em", "color": "#666",
                   "textTransform": "uppercase", "marginBottom": "6px"}),
        dcc.RangeSlider(
            id="ovc-year-slider",
            min=ALL_YEARS[0], max=ALL_YEARS[-1],
            value=[ALL_YEARS[0], ALL_YEARS[-1]],
            marks={y: str(y) for y in ALL_YEARS},
            step=1,
            tooltip={"placement": "bottom"},
        ),
    ], className="card", style={"padding": "18px 24px 24px"}),

    # Yearly trend chart
    html.Div([
        html.P("Yearly Trends: Volume & Average Price", className="section-title"),
        html.P("Total volume (billions) and average price by year and type",
               className="section-sub"),
        dcc.Graph(id="ovc-yearly-chart", style={"height": "420px"}),
    ], className="card"),

    # YoY growth chart
    html.Div([
        html.P("Year-over-Year Growth (%)", className="section-title"),
        html.P("Annual % change in volume and price for each avocado type",
               className="section-sub"),
        dcc.Graph(id="ovc-growth-chart", style={"height": "380px"}),
    ], className="card"),

    # Download
    html.Div([
        html.Button("⬇ Download Filtered Data as CSV", id="ovc-download-btn",
                    style={"background": AVOCADO_DARK, "color": "#fff",
                           "border": "none", "borderRadius": "8px",
                           "padding": "10px 22px", "cursor": "pointer",
                           "fontFamily": "DM Sans, sans-serif", "fontSize": "0.88rem"}),
        dcc.Download(id="ovc-download"),
    ], style={"textAlign": "right", "marginTop": "-8px", "marginBottom": "8px"}),
])

# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("ovc-premium-banner", "children"),
    Output("ovc-yearly-chart",   "figure"),
    Output("ovc-growth-chart",   "figure"),
    Input("ovc-year-slider",     "value"),
)
def update_ovc(year_range):
    df = D.filter_df(_df, year_range=tuple(year_range))

    # Premium banner
    premium = D.organic_premium(df)
    banner = html.Div([
        html.Span("🌿", style={"fontSize": "2rem"}),
        html.Div([
            html.Div(f"+{premium:.1f}% organic price premium",
                     style={"fontFamily": "Syne, sans-serif", "fontWeight": 700,
                            "fontSize": "1.1rem", "color": "#fff"}),
            html.Div(f"Organic avocados cost {premium:.1f}% more on average "
                     f"over {year_range[0]}–{year_range[1]}",
                     style={"fontSize": "0.82rem", "color": "rgba(255,255,255,0.75)",
                            "marginTop": "2px"}),
        ]),
    ], className="premium-banner", style={"marginBottom": "20px"})

    # ---- Yearly trend chart ----
    ys = D.yearly_stats(df)
    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Volume (Billions)", "Average Price ($)"],
        shared_xaxes=False,
    )
    for avtype, colour in [("conventional", BROWN), ("organic", GREEN)]:
        sub = ys[ys["type"] == avtype]
        fig1.add_trace(
            go.Scatter(x=sub["year"], y=sub["vol_bil"], name=avtype,
                       mode="lines+markers",
                       line={"color": colour, "width": 3},
                       marker={"size": 8},
                       legendgroup=avtype,
                       hovertemplate=f"{avtype}<br>Year: %{{x}}<br>Volume: %{{y:.2f}}B<extra></extra>"),
            row=1, col=1,
        )
        fig1.add_trace(
            go.Scatter(x=sub["year"], y=sub["average_price"], name=avtype,
                       mode="lines+markers",
                       line={"color": colour, "width": 3},
                       marker={"size": 8, "symbol": "diamond"},
                       legendgroup=avtype,
                       showlegend=False,
                       hovertemplate=f"{avtype}<br>Year: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>"),
            row=1, col=2,
        )

    _style_fig(fig1, "Yearly Volume and Price by Avocado Type")

    # ---- YoY growth chart ----
    growth = D.yoy_growth(df)
    fig2 = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Volume Growth (%)", "Price Growth (%)"],
        shared_yaxes=False,
    )
    for avtype, colour in [("conventional", BROWN), ("organic", GREEN)]:
        sub = growth[growth["type"] == avtype]
        for col_idx, (metric, label) in enumerate(
            [("vol_growth", "Volume Growth"), ("price_growth", "Price Growth")], start=1
        ):
            fig2.add_trace(
                go.Scatter(x=sub["year"], y=sub[metric], name=avtype,
                           mode="lines+markers",
                           line={"color": colour, "width": 2.5},
                           marker={"size": 7},
                           legendgroup=avtype,
                           showlegend=(col_idx == 1),
                           hovertemplate=f"{avtype}<br>%{{x}}: %{{y:.1f}}%<extra></extra>"),
                row=1, col=col_idx,
            )
        # Zero baseline
        fig2.add_hline(y=0, line_dash="dot", line_color="gray",
                       line_width=1, opacity=0.5, row=1, col=1)
        fig2.add_hline(y=0, line_dash="dot", line_color="gray",
                       line_width=1, opacity=0.5, row=1, col=2)

    _style_fig(fig2, "Year-over-Year Growth (%)")

    return banner, fig1, fig2


def _style_fig(fig, title):
    fig.update_layout(
        template="plotly_white",
        font={"family": "DM Sans, sans-serif"},
        legend={"orientation": "h", "y": -0.18, "x": 0.5, "xanchor": "center"},
        margin={"t": 60, "b": 40, "l": 50, "r": 30},
        plot_bgcolor="#fafaf8",
        paper_bgcolor="rgba(0,0,0,0)",
        title={
            "text": title,
            "font": {"family": "Syne, sans-serif", "size": 16, "color": AVOCADO_DARK},
            "x": 0.5, "xanchor": "center",
        },
    )


@callback(
    Output("ovc-download", "data"),
    Input("ovc-download-btn", "n_clicks"),
    Input("ovc-year-slider", "value"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, year_range):
    if not n_clicks:
        return dash.no_update
    df = D.filter_df(_df, year_range=tuple(year_range))
    ys = D.yearly_stats(df)
    return dcc.send_data_frame(ys.to_csv, "yearly_avocado_stats.csv", index=False)
