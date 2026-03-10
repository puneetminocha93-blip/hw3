"""
data.py — Single source of truth for all data loading and transformation.
All analytical logic is preserved exactly from 06_avocado_analysis.py.
No Dash or Plotly imports here.
"""

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Approximate lat/lon centroids for the 59 regions in the dataset
REGION_COORDS = {
    "Albany":               (42.65, -73.75),
    "Atlanta":              (33.75, -84.39),
    "BaltimoreWashington":  (39.10, -76.85),
    "BirminghamMontgomery": (33.25, -86.80),
    "Boise":                (43.62, -116.20),
    "Boston":               (42.36, -71.06),
    "BuffaloRochester":     (43.00, -78.18),
    "California":           (36.78, -119.42),
    "Charlotte":            (35.23, -80.84),
    "Chicago":              (41.88, -87.63),
    "CincinnatiDayton":     (39.35, -84.40),
    "Columbus":             (39.96, -82.99),
    "DallasFtWorth":        (32.78, -97.09),
    "Denver":               (39.74, -104.98),
    "Detroit":              (42.33, -83.05),
    "GrandRapids":          (42.96, -85.67),
    "GreatLakes":           (43.50, -84.00),
    "HarrisburgScranton":   (40.65, -76.90),
    "HartfordSpringfield":  (41.95, -72.58),
    "Houston":              (29.76, -95.37),
    "Indianapolis":         (39.77, -86.16),
    "Jacksonville":         (30.33, -81.66),
    "LasVegas":             (36.17, -115.14),
    "LosAngeles":           (34.05, -118.24),
    "Louisville":           (38.25, -85.76),
    "Miami":                (25.77, -80.19),
    "MiamiFtLauderdale":    (26.00, -80.20),
    "Midsouth":             (35.50, -89.00),
    "Nashville":            (36.17, -86.78),
    "NewOrleans":           (29.95, -90.07),
    "NewYork":              (40.71, -74.01),
    "Northeast":            (42.00, -73.50),
    "NorthernNewEngland":   (44.50, -71.50),
    "Orlando":              (28.54, -81.38),
    "PeoriaSpringfield":    (40.15, -89.50),
    "Philadelphia":         (39.95, -75.17),
    "PhoenixTucson":        (33.45, -112.08),
    "Pittsburgh":           (40.44, -79.99),
    "Plains":               (41.50, -99.00),
    "Portland":             (45.52, -122.68),
    "Providence":           (41.82, -71.42),
    "RaleighGreensboro":    (35.85, -79.40),
    "RichmondNorfolk":      (37.35, -77.40),
    "Roanoke":              (37.27, -79.94),
    "Sacramento":           (38.58, -121.49),
    "SanDiego":             (32.72, -117.15),
    "SanFrancisco":         (37.77, -122.42),
    "Seattle":              (47.61, -122.33),
    "SouthCarolina":        (33.84, -80.90),
    "SouthCentral":         (32.00, -97.00),
    "Southeast":            (33.00, -85.00),
    "Spokane":              (47.66, -117.43),
    "StLouis":              (38.63, -90.20),
    "Syracuse":             (43.05, -76.15),
    "Tampa":                (27.95, -82.46),
    "Toledo":               (41.66, -83.56),
    "West":                 (39.00, -120.00),
    "WestTexNewMexico":     (32.00, -106.00),
    "Wichita":              (37.69, -97.34),
}

# ---------------------------------------------------------------------------
# Core loader — runs once, result cached at module level
# ---------------------------------------------------------------------------

def load_data(csv_path: str = "data/avocado.csv") -> pd.DataFrame:
    """
    Load and clean the avocado dataset.
    Preserves all logic from the original notebook exactly.
    """
    df = pd.read_csv(csv_path)

    # Normalise column names (replicate janitor.clean_names behaviour)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[\s\-]+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
    )

    # Type conversion and derived columns (from .assign block in notebook)
    df["date"]    = pd.to_datetime(df["date"], dayfirst=True)
    df["type"]    = df["type"].astype("category")
    df["region"]  = df["region"].astype("category")
    df["revenue"] = df["total_volume"] * df["average_price"]
    df["month"]   = df["date"].dt.month
    df["year"]    = df["date"].dt.year

    # Filter out aggregate region (from .query in notebook)
    df = df[df["region"] != "TotalUS"]

    # Month name helper
    df["month_name"] = df["month"].map(lambda x: MONTH_NAMES[x - 1]).astype("category")

    return df


# ---------------------------------------------------------------------------
# Aggregation helpers (mirror each analysis block from the notebook)
# ---------------------------------------------------------------------------

def top_volume(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Top N region×type pairs by total volume."""
    return (
        df.groupby(["region", "type"], observed=True)["total_volume"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
        .rename(columns={"total_volume": "Total Volume"})
    )


def top_revenue(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Top N region×type pairs by total revenue."""
    return (
        df.groupby(["region", "type"], observed=True)["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
        .rename(columns={"revenue": "Total Revenue"})
    )


def organic_premium(df: pd.DataFrame) -> float:
    """Percentage price premium of organic over conventional."""
    avg = df.groupby("type", observed=True)["average_price"].mean()
    return (avg["organic"] / avg["conventional"] - 1) * 100


def monthly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly avg price and total volume aggregated by month×type."""
    return (
        df.groupby(["month", "type", "month_name"], observed=True)
        .agg(total_volume=("total_volume", "sum"),
             average_price=("average_price", "mean"))
        .reset_index()
        .sort_values(["month", "type"])
    )


def yearly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Yearly total volume and avg price by type, with vol in billions."""
    return (
        df.groupby(["year", "type"], observed=True)
        .agg(total_volume=("total_volume", "sum"),
             average_price=("average_price", "mean"))
        .assign(vol_bil=lambda d: d["total_volume"] / 1e9)
        .reset_index()
    )


def yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year % growth in volume and price, by type."""
    ys = yearly_stats(df).sort_values(["type", "year"])
    result = (
        ys.groupby("type", observed=True)
        .apply(lambda x: x.assign(
            vol_growth=x["total_volume"].pct_change() * 100,
            price_growth=x["average_price"].pct_change() * 100,
        ))
        .dropna()
        .reset_index(drop=True)
    )
    return result


def regional_avg_price(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Top N regions by average price."""
    return (
        df.groupby("region", observed=True)["average_price"]
        .mean()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )


def regional_all(df: pd.DataFrame) -> pd.DataFrame:
    """All regions with avg price, total volume, and coordinates."""
    base = (
        df.groupby("region", observed=True)
        .agg(average_price=("average_price", "mean"),
             total_volume=("total_volume", "sum"))
        .reset_index()
    )
    base["lat"] = base["region"].map(lambda r: REGION_COORDS.get(str(r), (None, None))[0])
    base["lon"] = base["region"].map(lambda r: REGION_COORDS.get(str(r), (None, None))[1])
    return base


def sku_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Total volume per SKU / bag bucket."""
    sku_cols = ["plu4046", "plu4225", "plu4770", "total_bags"]
    return (
        df[sku_cols]
        .sum()
        .reset_index()
        .rename(columns={"index": "sku", 0: "volume"})
    )


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Numeric correlation matrix (mirrors notebook exactly)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df[numeric_cols].corr()


def skim_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Basic descriptive stats (replaces skimpy.skim for display)."""
    numeric = df.select_dtypes(include=[np.number])
    summary = numeric.describe().T
    summary["missing"] = df[numeric.columns].isna().sum()
    summary["missing_pct"] = (summary["missing"] / len(df) * 100).round(1)
    return summary.reset_index().rename(columns={"index": "column"})


# ---------------------------------------------------------------------------
# Filter helper
# ---------------------------------------------------------------------------

def filter_df(df: pd.DataFrame,
              year_range: tuple = None,
              avocado_type: str = "All",
              regions: list = None) -> pd.DataFrame:
    """Apply standard dashboard filters to the base dataframe."""
    out = df.copy()
    if year_range:
        out = out[(out["year"] >= year_range[0]) & (out["year"] <= year_range[1])]
    if avocado_type != "All":
        out = out[out["type"] == avocado_type]
    if regions:
        out = out[out["region"].isin(regions)]
    return out
