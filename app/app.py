# pylint: disable=import-error
"""App to monitor the emissions in the Panama Canal."""

# ========== 🔧 Standard Libraries ==========
import os
import io
import json
import time
import logging
from io import StringIO

# ========== 📦 Third-Party Libraries ==========
import dash
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
from charts import charts_emissions
from callbacks import callbacks_emissions

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

unique_polygons_gdf = generate_unique_polygons(df_emissions)
geojson_template = create_geojson_template(unique_polygons_gdf)

#gdf_json, df_grouped = generate_h3_map_data(df_emissions, unique_polygons_gdf, geojson_template)


# ========================== 6️⃣ INITIAL CHARTS CREATION ==========================

line_chart_emissions_by_year_month = go.Figure()
bar_chart_emissions_by_type = go.Figure()
line_chart_emissions_by_type_year_month = go.Figure()
h3_map = go.Figure()

# ========================== KPI TEST ==========================

kpi_1 = charts_emissions.plot_kpi("", 0.0, "", "", 0.0)
kpi_2 = charts_emissions.plot_kpi("", 0.0, "", "", 0.0)

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

callbacks_emissions.setup_emissions_callbacks(
    app,
    df_emissions,
    index_to_year_month,
    master_emissions_vessel_types,
    geojson_template,
    unique_polygons_gdf)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
