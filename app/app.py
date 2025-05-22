# pylint: disable=import-error
"""App to monitor the emissions in the Panama Canal."""

# ========== Standard Libraries ==========
import os
import io
import json
import time
import logging
from io import StringIO

# ========== Third-Party Libraries ==========
import dash
import dash_bootstrap_components as dbc

import pandas as pd
import geopandas as gpd
import boto3
import psutil
from dotenv import load_dotenv

from shapely.geometry import Polygon
from h3.api.basic_int import cell_to_boundary

# ========== Custom Modules ==========

from callbacks import callbacks_emissions
from callbacks import callbacks_waiting

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

load_dotenv()

access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
bucket_name = os.getenv("bucket_name")
file_name_emissions = os.getenv("file_name_emissions")
file_name_waiting = os.getenv("file_name_waiting")

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

def prepare_emissions_controls(df):
    """
    Given a DataFrame with emissions data, returns a dictionary
    with control values for vessel types and date ranges.
    """

    # Vessel types
    vessel_types = df['StandardVesselType'].unique()

    # Date slider values
    unique_year_months = sorted(df["year_month"].unique())
    year_month_map = {ym: i for i, ym in enumerate(unique_year_months)}
    index_to_year_month = {i: ym for ym, i in year_month_map.items()}
    min_index = min(year_month_map.values())
    max_index = max(year_month_map.values())

    return {
        "vessel_types": vessel_types,
        "date_range": {
            "min_index": min_index,
            "max_index": max_index,
            "unique_year_months": unique_year_months,
            "index_to_year_month": index_to_year_month,
        }
    }

def prepare_waiting_time_controls(df):
    """
    Given a DataFrame with waiting data, returns a dictionary
    with control values for vessel types and date ranges.
    """

    # Vessel types
    vessel_types = df['StandardVesselType'].unique()
    stop_area = df['stop_area'].unique()

    # Date slider values
    unique_year_months = sorted(df["year_month"].unique())
    year_month_map = {ym: i for i, ym in enumerate(unique_year_months)}
    index_to_year_month = {i: ym for ym, i in year_month_map.items()}
    min_index = min(year_month_map.values())
    max_index = max(year_month_map.values())

    return {
        "vessel_types": vessel_types,
        "stop_area": stop_area,
        "date_range": {
            "min_index": min_index,
            "max_index": max_index,
            "unique_year_months": unique_year_months,
            "index_to_year_month": index_to_year_month,
        }
    }

# ========================== 3️⃣ READ & PREPROCESS DATA ==========================

# ✅ Read the data
df_emissions = read_parquet_from_s3(bucket_name, file_name_emissions)
df_emissions["year_month"] = (
    df_emissions["year"].astype(str) + df_emissions["month"].astype(str).str.zfill(2)
).astype(int)

controls_emissions = prepare_emissions_controls(df_emissions)


# Read Waiting Time Data
df_waiting_times = read_parquet_from_s3(bucket_name, file_name_waiting)
df_waiting_times["year_month"] = (
    df_waiting_times["year"].astype(str) + df_waiting_times["month"].astype(str).str.zfill(2)
).astype(int)

controls_waiting_times = prepare_waiting_time_controls(df_waiting_times)

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


# ========================== 7️⃣ DASHBOARD LAYOUT ==========================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

app.layout = layout.build_main_layout()

# ========================== 8️⃣ CALLBACKS ==========================


from dash import Input, Output, callback
import layout

callbacks_emissions.setup_emissions_callbacks(
    app,
    df_emissions,
    controls_emissions,
    geojson_template,
    unique_polygons_gdf)

callbacks_waiting.setup_waiting_times_callbacks(
    app,
    df_waiting_times
)


@app.callback(
    Output("tab-content", "children"),
    Input("chart-tabs", "value")
)

def update_tab_content(selected_tab):

    if selected_tab == "emissions":

        return dbc.Row([
            layout.build_sidebar_emissions(controls_emissions),  # Your existing sidebar
            layout.build_main_container_emissions()
        ], className="g-0")
    
    elif selected_tab == "waiting":
        return dbc.Row([
            layout.build_sidebar_waiting_times(),  # Your existing sidebar
            layout.build_main_container_waiting_times()
        ], className="g-0")
                       

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
