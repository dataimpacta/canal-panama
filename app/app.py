# 📌 Import Necessary Libraries
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
from h3.api.basic_str import cell_to_boundary
from h3.api.basic_int import cell_to_boundary 
from h3.api.basic_int import int_to_str
from shapely.geometry import Polygon
import geopandas as gpd
import json
import os
import io
import boto3
from io import StringIO
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv
import psutil
import time


# 📌 My custom module
import charts

# ========================== 1️⃣ APP INITIALIZATION ==========================

# ✅ Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

load_dotenv()

access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
#access_key = os.getenv("VICTOR_AWS_ACCESS_KEY_ID")
#secret_key = os.getenv("VICTOR_AWS_SECRET_ACCESS_KEY")

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

# ✅ Define file paths
#bucket_name = 'buckect-canalpanama'
#file_name_emissions = 'Generated_Emission_Data_Monthly.csv'

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


# ========================== 4️⃣ DATA PROCESSING ==========================

# ✅ Aggregate emissions by Year & Month
df_emissions_by_year_month = df_emissions.groupby(['year', 'month'])['co2_equivalent_t'].sum().reset_index()

# ✅ Aggregate emissions by Vessel Type
df_emission_by_type = df_emissions.groupby('StandardVesselType')['co2_equivalent_t'].sum().sort_values(ascending=False).head(6)

# ✅ Aggregate emissions by Vessel Type & Year-Month
df_emissions_by_type_year_month = df_emissions.groupby(['StandardVesselType', 'year_month'])['co2_equivalent_t'].sum().reset_index()


# ========================== 5️⃣ H3 MAP PROCESSING ==========================

def h3_to_polygon(h3_index):
    boundary = cell_to_boundary(h3_index)
    return Polygon([(lng, lat) for lat, lng in boundary])


def process_h3_data(df, unique_polygons):
    """Processes H3 spatial data for mapping using precomputed geometry"""
    if df.empty:
        raise ValueError("The DataFrame is empty. Check data input.")

    df_grouped = df.groupby(["resolution_id"], as_index=False).agg({
        "co2_equivalent_t": "sum"
    })

    df_grouped = df_grouped.merge(unique_polygons, on="resolution_id", how="left")

    gdf = gpd.GeoDataFrame(df_grouped, geometry="geometry", crs="EPSG:4326")
    gdf_json = json.loads(gdf.to_json())
    return gdf_json, gdf


# Pre-Process H3 data
# ✅ Create a unique DataFrame for H3 polygons
unique_polygons = df_emissions[["resolution_id"]].drop_duplicates().copy()
unique_polygons["geometry"] = unique_polygons["resolution_id"].apply(h3_to_polygon)


gdf_json, df_grouped = process_h3_data(df_emissions, unique_polygons)

# ========================== 6️⃣ INITIAL CHARTS CREATION ==========================


line_chart_emissions_by_year_month = charts.create_line_chart_emissions_by_year_month(df_emissions_by_year_month)
bar_chart_emissions_by_type = charts.create_bar_chart_emissions_by_type(df_emission_by_type)
line_chart_emissions_by_type_year_month = charts.create_line_chart_emissions_by_type_year_month(df_emissions_by_type_year_month)
h3_map = charts.create_h3_map(gdf_json, df_grouped)
#h3_map = go.Figure()

# ========================== 7️⃣ DASHBOARD LAYOUT ==========================

app.layout = dbc.Container([
    dcc.Store(id="store-gdf-json", data=gdf_json),  # ✅ Store GeoJSON
    dcc.Store(id="store-gdf", data=df_grouped.to_json()),  # ✅ Store filtered GeoDataFrame (as JSON)

    # ✅ Header Section
    dbc.Row([
        dbc.Col([
            dbc.Row(html.H1("Panama Maritime Statistics")),
            dbc.Row(html.H4("Efficiency and Sustainability Indicators"))
        ], width=9),
        dbc.Col(html.Img(src="/assets/sample_image.png", width="100%"))
    ], className="dashboard-header"),

    # ✅ Tabs Section
    dbc.Row([
        dbc.Col(dcc.Tabs(id="chart-tabs", value="emissions", children=[
            dcc.Tab(label="Emissions", value="emissions"),
            dcc.Tab(label="Waiting Time", value="waiting"),
            dcc.Tab(label="Energy", value="energy"),
            dcc.Tab(label="Explorer", value="explorer")
        ]), width=6)
    ], className="dashboard-navigation-bar"),

    # ✅ Sidebar (Filters)
    dbc.Row([
        dbc.Col([
            html.H3("Date Range", className="dashboard-sidebar-title"),
            dcc.RangeSlider(
                id="filter-date-range",
                min=min_index, max=max_index, step=1,
                marks={min_index: str(unique_year_months[0]), max_index: str(unique_year_months[-1])},
                value=[min_index, max_index], allowCross=False
            ),
            html.Br(),

            html.H3("Vessel Type", className="dashboard-sidebar-title"),
            dcc.Dropdown(
                id="filter-emissions-type",
                options=[{"label": v, "value": v} for v in master_emissions_vessel_types],
                value=list(master_emissions_vessel_types), multi=True, clearable=False
            ),
            html.Br(),

        ], width=2, className="dashboard-sidebar-container"),

        # ✅ Charts Section
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id="line-chart-emissions-by-year-month", figure=line_chart_emissions_by_year_month),
                        className="dashboard-chart-container"),
                dbc.Col(dcc.Graph(id="bar-chart-emissions-by-type", figure=bar_chart_emissions_by_type),
                        className="dashboard-chart-container")
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="map-chart-emissions-map", figure=h3_map),
                        className="dashboard-chart-container"),
                dbc.Col(dcc.Graph(id="line-chart-emissions-by-type-year-month", figure=line_chart_emissions_by_type_year_month),
                        className="dashboard-chart-container")
            ])
        ])
    ], className="dashboard-main-content")
], fluid=True)

# ========================== 8️⃣ CALLBACKS ==========================

@callback(
    Output("filter-emissions-type", "value"),
    Input("filter-emissions-type", "value")
)
def update_vessel_filter(selected_values):
    return list(master_emissions_vessel_types) if not selected_values else selected_values

import time
import psutil

@callback(
    [
        Output("line-chart-emissions-by-year-month", "figure"),
        Output("bar-chart-emissions-by-type", "figure"),
        Output("line-chart-emissions-by-type-year-month", "figure"),
        Output("map-chart-emissions-map", "figure"),
    ],
    [
        Input("filter-emissions-type", "value"),
        Input("filter-date-range", "value"),
    ],
    [
        State("store-gdf-json", "data"),
        State("store-gdf", "data"),
    ]
)
def update_charts(selected_vessel_types, selected_date_range, stored_geojson, stored_gdf_json):
    """Efficiently update charts using cached GeoJSON and filtered data"""

    process = psutil.Process()
    start_time = time.time()
    cpu_start = process.cpu_times()

    # ✅ Filter data
    t0 = time.time()
    start_ym = index_to_year_month[selected_date_range[0]]
    end_ym = index_to_year_month[selected_date_range[1]]
    filtered_df = df_emissions[
        (df_emissions["year_month"] >= start_ym) &
        (df_emissions["year_month"] <= end_ym) &
        (df_emissions["StandardVesselType"].isin(selected_vessel_types))
    ]
    print(f"🔹 Data filtered in {time.time() - t0:.2f}s")

    # ✅ Grouping operations
    t0 = time.time()
    df_year_month = filtered_df.groupby(['year', 'month'])['co2_equivalent_t'].sum().reset_index()
    df_type = filtered_df.groupby('StandardVesselType')['co2_equivalent_t'].sum().sort_values(ascending=False).head(6)
    df_type_ym = filtered_df.groupby(['StandardVesselType', 'year_month'])['co2_equivalent_t'].sum().reset_index()
    print(f"🔹 Grouping done in {time.time() - t0:.2f}s")

    # ✅ H3 aggregation and geo conversion
    t0 = time.time()
    df_h3 = filtered_df.groupby("resolution_id", as_index=False)['co2_equivalent_t'].sum()
    df_h3 = df_h3.merge(unique_polygons, on="resolution_id", how="left")
    gdf = gpd.GeoDataFrame(df_h3, geometry="geometry", crs="EPSG:4326")
    gdf_json = json.loads(gdf.to_json())
    print(f"🔹 H3 map processing in {time.time() - t0:.2f}s")

    # ✅ Chart creation
    t0 = time.time()
    line1 = charts.create_line_chart_emissions_by_year_month(df_year_month)
    bar = charts.create_bar_chart_emissions_by_type(df_type)
    line2 = charts.create_line_chart_emissions_by_type_year_month(df_type_ym)
    map_fig = charts.create_h3_map(gdf_json, df_h3)
    print(f"🔹 Charts created in {time.time() - t0:.2f}s")

    # ✅ Overall summary
    total_time = time.time() - start_time
    cpu_end = process.cpu_times()
    cpu_time = (cpu_end.user - cpu_start.user) + (cpu_end.system - cpu_start.system)
    print(f"✅ Total callback time: {total_time:.2f}s | CPU time: {cpu_time:.2f}s")

    return (line1, bar, line2, map_fig)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)