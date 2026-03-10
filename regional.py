"""
pages/regional.py — Page 4: Regional Price & Volume Analysis
Bar chart (top-N regions) + US scatter-map choropleth.
"""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data as D

dash.register_page(__name__, path="/regional", name="Regional Analysis", order=3)

_df = D.load_data("data/avocado.csv")
ALL_YEARS = sorted(_df["year"].unique())

AVOCADO_DARK  = "#2c4a35"
AVOCADO_GREEN = "#4a7c59"

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

layout = html.Div([
    html.H1("Regional Analysis", className="page-header"),
    html.P("Explore which US markets command the highest avocado prices and volumes.",
           className="page-sub"),

    # Filters
    html.Div([
        html.Div([
            html.Label("Year Range", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.RangeSlider(
                id="reg-year-slider",
                min=ALL_YEARS[0], max=ALL_YEARS[-1],
                value=[ALL_YEARS[0], ALL_YEARS[-1]],
                marks={y: str(y) for y in ALL_YEARS},
                step=1, tooltip={"placement": "bottom"},
            ),
        ], style={"flex": 2, "marginRight": "32px"}),

        html.Div([
            html.Label("Avocado Type", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.RadioItems(
                id="reg-type-radio",
                options=[{"label": t, "value": t} for t in ["All", "conventional", "organic"]],
                value="All", inline=True,
                inputStyle={"marginRight": "4px"},
                labelStyle={"marginRight": "16px", "fontSize": "0.88rem"},
            ),
        ], style={"flex": 1, "marginRight": "24px"}),

        html.Div([
            html.Label("Top N Regions", style={"fontSize": "0.78rem", "fontWeight": 500,
                       "letterSpacing": "0.06em", "color": "#666",
                       "textTransform": "uppercase", "marginBottom": "6px"}),
            dcc.Slider(
                id="reg-topn-slider",
                min=5, max=30, step=5, value=15,
                marks={i: str(i) for i in range(5, 31, 5)},
                tooltip={"placement": "bottom"},
            ),
        ], style={"flex": 1}),
    ], className="card", style={"display": "flex", "alignItems": "flex-start",
                                "padding": "18px 24px 24px"}),

    # Bar chart
    html.Div([
        html.P("Most Expensive Markets — Avg Price", className="section-title"),
        html.P("Ranked by average avocado price across selected filters",
               className="section-sub"),
        dcc.Graph(id="reg-bar-chart", style={"height": "520px"}),
    ], className="card"),

    # Map
    html.Div([
        html.P("US Regional Price Map", className="section-title"),
        html.P("Bubble size = total volume · colour = average price",
               className="section-sub"),
        dcc.Graph(id="reg-map-chart", style={"height": "520px"}),
    ], className="card"),
])

# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------

@callback(
    Output("reg-bar-chart",  "figure"),
    Output("reg-map-chart",  "figure"),
    Input("reg-year-slider", "value"),
    Input("reg-type-radio",  "value"),
    Input("reg-topn-slider", "value"),
)
def update_regional(year_range, avocado_type, top_n):
    df = D.filter_df(_df, year_range=tuple(year_range), avocado_type=avocado_type)

    # ---- Bar chart (mirrors notebook's barplot) ----
    top = D.regional_avg_price(df, n=top_n)

    fig_bar = px.bar(
        top,
        x="average_price",
        y="region",
        orientation="h",
        color="average_price",
        color_continuous_scale="Reds",
        labels={"average_price": "Avg Price ($)", "region": ""},
        text="average_price",
    )
    fig_bar.update_traces(
        texttemplate="$%{text:.2f}", textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg Price: $%{x:.2f}<extra></extra>",
    )
    fig_bar.update_yaxes(categoryorder="total ascending")
    fig_bar.update_coloraxes(showscale=False)
    fig_bar.update_layout(
        template="plotly_white",
        font={"family": "DM Sans, sans-serif"},
        margin={"t": 30, "b": 40, "l": 150, "r": 80},
        plot_bgcolor="#fafaf8",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Average Price ($)",
        title={
            "text": f"Top {top_n} Most Expensive Avocado Markets",
            "font": {"family": "Syne, sans-serif", "size": 16, "color": AVOCADO_DARK},
            "x": 0.5, "xanchor": "center",
        },
    )

    # ---- Map ----
    reg_all = D.regional_all(df)
    reg_all = reg_all.dropna(subset=["lat", "lon"])

    fig_map = px.scatter_geo(
        reg_all,
        lat="lat",
        lon="lon",
        size="total_volume",
        color="average_price",
        hover_name="region",
        color_continuous_scale="YlGn",
        size_max=40,
        scope="usa",
        labels={"average_price": "Avg Price ($)", "total_volume": "Total Volume"},
        custom_data=["average_price", "total_volume"],
    )
    fig_map.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Avg Price: $%{customdata[0]:.2f}"
                      "<br>Total Volume: %{customdata[1]:,.0f}<extra></extra>",
    )
    fig_map.update_layout(
        template="plotly_white",
        font={"family": "DM Sans, sans-serif"},
        margin={"t": 30, "b": 10, "l": 0, "r": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        geo={"bgcolor": "rgba(0,0,0,0)", "lakecolor": "#d4e8f0",
             "landcolor": "#f0ede6", "showlakes": True},
        coloraxis_colorbar={"title": "Avg Price ($)", "tickprefix": "$"},
        title={
            "text": "Average Price by US Region",
            "font": {"family": "Syne, sans-serif", "size": 16, "color": AVOCADO_DARK},
            "x": 0.5, "xanchor": "center",
        },
    )
    return fig_bar, fig_map
