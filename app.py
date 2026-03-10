"""
app.py — Avocado Sales Dashboard entry point.
Run with: python app.py
Then open http://127.0.0.1:8050 in your browser.
"""

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="🥑 Avocado Dashboard",
)

server = app.server  # expose for production WSGI

# ---------------------------------------------------------------------------
# Colour palette & theme (CSS variables injected via style tag)
# ---------------------------------------------------------------------------

AVOCADO_GREEN  = "#4a7c59"
AVOCADO_DARK   = "#2c4a35"
AVOCADO_LIGHT  = "#a8d5b5"
AVOCADO_CREAM  = "#f7f3e9"
AVOCADO_BROWN  = "#8b5e3c"
AVOCADO_YELLOW = "#e8d44d"
BG_DARK        = "#1a2520"
TEXT_LIGHT     = "#f0ede6"

NAV_PAGES = [
    {"label": "Overview",                "href": "/"},
    {"label": "Seasonal Trends",         "href": "/seasonal"},
    {"label": "Organic vs Conventional", "href": "/organic-vs-conventional"},
    {"label": "Regional Analysis",       "href": "/regional"},
    {"label": "SKU & Elasticity",        "href": "/sku-elasticity"},
]

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

sidebar = html.Div(
    [
        # Logo / brand
        html.Div(
            [
                html.Span("🥑", style={"fontSize": "2.4rem"}),
                html.Div([
                    html.P("AVOCADO", style={
                        "margin": 0, "fontFamily": "Syne, sans-serif",
                        "fontWeight": 800, "fontSize": "1rem",
                        "letterSpacing": "0.18em", "color": AVOCADO_YELLOW,
                    }),
                    html.P("SALES DASHBOARD", style={
                        "margin": 0, "fontFamily": "DM Sans, sans-serif",
                        "fontSize": "0.62rem", "letterSpacing": "0.12em",
                        "color": AVOCADO_LIGHT, "fontWeight": 300,
                    }),
                ]),
            ],
            style={"display": "flex", "alignItems": "center",
                   "gap": "12px", "padding": "28px 20px 24px"},
        ),

        html.Hr(style={"borderColor": AVOCADO_DARK, "margin": "0 16px 20px"}),

        # Nav links
        html.Nav(
            [
                dcc.Link(
                    p["label"],
                    href=p["href"],
                    className="nav-link",
                    id=f"nav-{i}",
                )
                for i, p in enumerate(NAV_PAGES)
            ],
            style={"display": "flex", "flexDirection": "column", "gap": "4px",
                   "padding": "0 12px"},
        ),

        # Footer
        html.Div(
            "US Avocado Sales · 2015–2023",
            style={
                "position": "absolute", "bottom": "20px", "left": 0, "right": 0,
                "textAlign": "center", "fontSize": "0.68rem",
                "color": AVOCADO_LIGHT, "opacity": 0.5,
                "fontFamily": "DM Sans, sans-serif", "letterSpacing": "0.06em",
            },
        ),
    ],
    style={
        "width": "220px", "minWidth": "220px", "height": "100vh",
        "backgroundColor": BG_DARK, "position": "sticky", "top": 0,
        "overflowY": "auto",
    },
)

# ---------------------------------------------------------------------------
# Root layout
# ---------------------------------------------------------------------------

app.layout = html.Div(
    [
        # Global CSS
        html.Style(f"""
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0; padding: 0;
                background-color: {AVOCADO_CREAM};
                font-family: 'DM Sans', sans-serif;
                color: #2a2a2a;
            }}
            a.nav-link {{
                display: block;
                padding: 10px 14px;
                border-radius: 8px;
                color: {AVOCADO_LIGHT};
                font-family: 'DM Sans', sans-serif;
                font-size: 0.85rem;
                font-weight: 400;
                text-decoration: none;
                transition: background 0.18s, color 0.18s;
                letter-spacing: 0.02em;
            }}
            a.nav-link:hover {{
                background-color: {AVOCADO_DARK};
                color: {AVOCADO_YELLOW};
            }}
            a.nav-link.active {{
                background-color: {AVOCADO_GREEN};
                color: #fff;
                font-weight: 500;
            }}
            .card {{
                background: #fff;
                border-radius: 14px;
                box-shadow: 0 2px 16px rgba(0,0,0,0.06);
                padding: 20px 24px;
                margin-bottom: 20px;
            }}
            .kpi-card {{
                background: #fff;
                border-radius: 14px;
                box-shadow: 0 2px 16px rgba(0,0,0,0.06);
                padding: 22px 24px;
                text-align: center;
            }}
            .kpi-value {{
                font-family: 'Syne', sans-serif;
                font-weight: 800;
                font-size: 2rem;
                color: {AVOCADO_DARK};
                margin: 4px 0;
            }}
            .kpi-label {{
                font-size: 0.76rem;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                color: #888;
                font-weight: 500;
            }}
            .section-title {{
                font-family: 'Syne', sans-serif;
                font-weight: 700;
                font-size: 1.35rem;
                color: {AVOCADO_DARK};
                margin-bottom: 4px;
            }}
            .section-sub {{
                font-size: 0.83rem;
                color: #777;
                margin-bottom: 18px;
            }}
            .page-header {{
                font-family: 'Syne', sans-serif;
                font-weight: 800;
                font-size: 1.9rem;
                color: {AVOCADO_DARK};
                margin-bottom: 4px;
            }}
            .page-sub {{
                font-size: 0.88rem;
                color: #666;
                margin-bottom: 24px;
            }}
            .premium-banner {{
                background: linear-gradient(135deg, {AVOCADO_DARK} 0%, {AVOCADO_GREEN} 100%);
                border-radius: 12px;
                padding: 18px 28px;
                color: #fff;
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 20px;
            }}
            .Select-control {{
                border-radius: 8px !important;
                border: 1.5px solid #ddd !important;
            }}
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td {{
                font-family: 'DM Sans', sans-serif;
                font-size: 0.85rem;
            }}
        """),

        # Shell: sidebar + content
        html.Div(
            [
                sidebar,
                html.Div(
                    dash.page_container,
                    style={"flex": 1, "overflowY": "auto",
                           "padding": "36px 40px", "minWidth": 0},
                ),
            ],
            style={"display": "flex", "height": "100vh", "overflow": "hidden"},
        ),
    ]
)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8050)
