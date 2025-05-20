"""App to monitor the emissions in the Panama Canal."""

# ========== 🔧 Standard Libraries ==========
import os
import io
import json
import time
import logging
from copy import deepcopy
from io import StringIO

# ========== 📦 Third-Party Libraries ==========
import dash
from dash import html, callback, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.graph_objects as go
import geopandas as gpd
import boto3
import psutil
from dotenv import load_dotenv

from shapely.geometry import Polygon
from h3.api.basic_int import cell_to_boundary

# ========== 🧩 Custom Modules ==========
import charts
import layout



# ========================== LOGS CONFIGURATION ==========================

# Configure logging to show up in nohup.out
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Memory and CPU ustage
process = psutil.Process(os.getpid())

def log_step(step_name, start_time):
    """Function to log the time and memory usage of a step"""
    elapsed = time.time() - start_time
    mem = process.memory_info().rss / 1024 / 1024
    logger.info("✅ Step: %s | Time: %.2fs | Memory: %.1fMB", step_name, elapsed, mem)
    return time.time()

# ========================== 1️⃣ APP INITIALIZATION ==========================

# ✅ Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

load_dotenv()

access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
bucket_name = os.getenv("bucket_name")
file_name_emissions = os.getenv("key")

# ========================== 2️⃣ DATABASE CONNECTION ==========================

# ✅ Set up AWS S3 client

s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

def read_csv_from_s3(bucket, file):
    """Reads CSV from an S3 bucket and returns a DataFrame"""
    obj = s3_client.get_object(Bucket=bucket, Key=file)
    data = obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(data))

def read_parquet_from_s3(bucket, file):
    """Reads parket from an S3 bucket and returns a DataFrame"""
    obj = s3_client.get_object(Bucket=bucket, Key=file)
    data = obj['Body'].read()
    return pd.read_parquet(io.BytesIO(data))


# ========================== 3️⃣ READ & PREPROCESS DATA ==========================

# ✅ Read the data
df_emissions = read_parquet_from_s3(bucket_name, file_name_emissions)

# ✅ Convert `year` and `month` to `YYYYMM` integer format
df_emissions["year_month"] = (
    df_emissions["year"].astype(str) + df_emissions["month"].astype(str).str.zfill(2)
).astype(int)

# 🟡 Create unique master lists for filters - Delete the one with emissions
master_emissions_vessel_types = df_emissions['StandardVesselType'].unique()
#master_emission_types = df_emissions['emission_type'].unique()

# ✅ Create a sorted list of unique `YYYYMM` values for the date slider
unique_year_months = sorted(df_emissions["year_month"].unique())

# ✅ Create mappings for date filtering
year_month_map = {ym: i for i, ym in enumerate(unique_year_months)}  # YYYYMM → index
index_to_year_month = {i: ym for ym, i in year_month_map.items()}  # index → YYYYMM

# ✅ Define min and max values for the slider
min_index = min(year_month_map.values())  # First index (start date)
max_index = max(year_month_map.values())  # Last index (end date)


# ========================== 5️⃣ MAP PROCESSING ==========================

def h3_to_polygon(h3_index):
    """Converts an H3 index to a Shapely Polygon."""
    boundary = cell_to_boundary(h3_index)
    return Polygon([(lng, lat) for lat, lng in boundary])

def generate_unique_polygons(df_with_resolution_id):
    """
    Generates a GeoDataFrame with unique resolution_id polygons.
    Only needs to be run once at app startup.
    """
    unique_ids = df_with_resolution_id[["resolution_id"]].drop_duplicates().copy()
    unique_ids["geometry"] = unique_ids["resolution_id"].apply(h3_to_polygon)
    return gpd.GeoDataFrame(unique_ids, geometry="geometry", crs="EPSG:4326")

def create_geojson_template(geo_df):
    """
    Converts a GeoDataFrame to a GeoJSON dictionary.
    """
    return json.loads(geo_df.to_json())

def inject_values_into_geojson(template, values_by_id):
    """
    Injects values into a GeoJSON template based on resolution_id.
    """
    updated_geojson = {"type": "FeatureCollection", "features": []}
    for feature in template["features"]:
        res_id = feature["properties"]["resolution_id"]
        value = values_by_id.get(res_id, 0)
        if value > 0:
            new_feature = deepcopy(feature)
            new_feature["properties"]["value"] = value
            updated_geojson["features"].append(new_feature)
    return updated_geojson

def generate_h3_map_data(df_to_map, gdf_polygons, precomputed_geojson_template):
    """
    From a DataFrame:
    - Groups by resolution_id and aggregates CO₂.
    - Merges with unique polygon geometries.
    - Injects values into the precomputed GeoJSON template.
    
    Returns:
        - df_grouped: GeoDataFrame with geometry and emissions
        - gdf_json: GeoJSON ready for plotting
    """
    df_grouped = df_to_map.groupby("resolution_id", as_index=False)["co2_equivalent_t"].sum()
    df_grouped = df_grouped.merge(gdf_polygons, on="resolution_id", how="left")

    values_by_id = df_grouped.set_index("resolution_id")["co2_equivalent_t"].to_dict()
    gdf_json = inject_values_into_geojson(precomputed_geojson_template, values_by_id)

    return gdf_json, df_grouped

unique_polygons_gdf = generate_unique_polygons(df_emissions)
geojson_template = create_geojson_template(unique_polygons_gdf)

#gdf_json, df_grouped = generate_h3_map_data(df_emissions, unique_polygons_gdf, geojson_template)


# ========================== 6️⃣ INITIAL CHARTS CREATION ==========================

line_chart_emissions_by_year_month = go.Figure()
bar_chart_emissions_by_type = go.Figure()
line_chart_emissions_by_type_year_month = go.Figure()
h3_map = go.Figure()

# ========================== KPI TEST ==========================

kpi_1 = charts.plot_kpi("", 0.0, "", "", 0.0)
kpi_2 = charts.plot_kpi("", 0.0, "", "", 0.0)

# ========================== 7️⃣ DASHBOARD LAYOUT ==========================

app.layout = layout.build_dashboard_layout(
    [kpi_1],
    {"id": "chart-1",
     "fig": line_chart_emissions_by_year_month, 
     "title": "Total Emissions", 
     "subtitle": "TONNES"},
    {"id": "chart-2",
     "fig": bar_chart_emissions_by_type, 
     "title": "Emissions by Type of Vessel", 
     "subtitle": "TONNES"},
    {"id": "chart-3",
     "fig": h3_map, "title": 
     "Emissions by Region", 
     "subtitle": "TONNES"},
    {"id": "chart-4",
     "fig": line_chart_emissions_by_type_year_month, 
     "title": "Emissions by Type of Vessel", 
     "subtitle": "TONNES"},
    min_index,
    max_index,
    unique_year_months,
    master_emissions_vessel_types
)


# ========================== 8️⃣ CALLBACKS ==========================

# @callback(
#     Output("filter-emissions-type", "value"),
#     Input("filter-emissions-type", "value")
# )
# def update_vessel_filter(selected_values):
#     """
#     If selected_values is empty or falsy (like None or []), 
#     return the full list master_emissions_vessel_types. 
#     Otherwise, return selected_values.
#     """
#     return list(master_emissions_vessel_types) if not selected_values else selected_values


@app.callback(
    Output("filter-emissions-type", "value"),
Input("btn-select-all", "n_clicks"),
Input("btn-clear-all", "n_clicks"),
    prevent_initial_call=True
)
def update_checklist(select_all_clicks, clear_all_clicks):
    """
    Updates the checklist based on button clicks.
    """

    triggered_id = ctx.triggered_id

    if triggered_id == "btn-select-all":
        return list(master_emissions_vessel_types)
    elif triggered_id == "btn-clear-all":
        return []

@callback(
    [
        Output("chart-1", "figure"),
        Output("chart-2", "figure"),
        Output("chart-3", "figure"),
        Output("chart-4", "figure"),
        Output("kpi-1", "children"),
        Output("no-data-modal", "is_open"),  
    ],
    Input("apply-filters-btn", "n_clicks"),
    [
        State("filter-emissions-type", "value"),
        State("filter-date-range", "value"),
    ]
)
def update_charts(n_clicks, selected_vessel_types, selected_date_range):
    """
    Updates the charts and KPI based on user-selected filters.
    """
    logger.info("🟢 Callback started")
    t = time.time()

    start_ym = index_to_year_month[selected_date_range[0]]
    end_ym = index_to_year_month[selected_date_range[1]]

    filtered_df = df_emissions[
        (df_emissions["year_month"] >= start_ym) &
        (df_emissions["year_month"] <= end_ym) &
        (df_emissions["StandardVesselType"].isin(selected_vessel_types))
    ]

    if filtered_df.empty:
        empty_fig = go.Figure()
        return (
            empty_fig, empty_fig, empty_fig, empty_fig,
            html.Div("No data available", style={"color": "#999"}),
            True  # modal open
        )
    t = log_step("Filtered DataFrame", t)


    # KPI Calculation
    sorted_ym = sorted(filtered_df["year_month"].unique())
    kpi_component = html.Div("Insufficient data", style={"color": "#999"})  # fallback default

    if len(sorted_ym) >= 2:
        latest_ym = sorted_ym[-1]
        previous_ym = sorted_ym[-2]

        latest_total = filtered_df[
            filtered_df["year_month"] == latest_ym]["co2_equivalent_t"].sum()
        previous_total = filtered_df[filtered_df["year_month"] == previous_ym]["co2_equivalent_t"].sum()
        change = latest_total - previous_total
        pct_change = (change / previous_total * 100) if previous_total != 0 else 0

        comparison_label = "Last Month"
        kpi_component = charts.plot_kpi(
            name="Total Emissions",
            value=latest_total,
            date=f"{str(latest_ym)}",
            comparison_label=comparison_label,
            comparison_value=previous_total
        )


    df_year_month = filtered_df.groupby(['year', 'month'])['co2_equivalent_t'].sum().reset_index()
    df_type = filtered_df.groupby('StandardVesselType')['co2_equivalent_t'].sum().sort_values(ascending=False).head(6)
    df_type_ym = filtered_df.groupby(['StandardVesselType', 'year_month'])['co2_equivalent_t'].sum().reset_index()

    gdf_json, df_h3 = generate_h3_map_data(filtered_df, unique_polygons_gdf, geojson_template)

    size_kb = len(json.dumps(gdf_json).encode("utf-8")) / 1024
    logger.info("📦 GeoJSON payload size: %.2f KB", size_kb)
    t = log_step("Injected values into GeoJSON", t)
    logger.info("🟣 Callback finished. Total time: %.2f s", time.time() - t)

    return (
        charts.plot_line_chart_emissions_by_year_month(df_year_month),
        charts.plot_bar_chart_emissions_by_type(df_type),
        charts.plot_emissions_map(gdf_json, df_h3),
        charts.plot_line_chart_emissions_by_type_year_month(df_type_ym),
        kpi_component,
        False 
    )

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
