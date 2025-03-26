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
from dash.dependencies import Input, Output
from dotenv import load_dotenv


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
    """Convierte un índice H3 entero a un polígono"""
    boundary = cell_to_boundary(h3_index)  # Manténlo como int
    return Polygon([(lng, lat) for lat, lng in boundary])  # Swap (lat, lng)


def process_h3_data(df):
    """Procesa datos espaciales H3 para generar GeoJSON"""
    if df.empty:
        raise ValueError("El DataFrame está vacío. Revisa la fuente de datos.")

    df_grouped = df.groupby("resolution_id", as_index=False).agg({
        "co2_equivalent_t": "sum"
    })

    df_grouped["geometry"] = df_grouped["resolution_id"].apply(h3_to_polygon)
    gdf = gpd.GeoDataFrame(df_grouped, geometry="geometry")

    gdf_json = json.loads(gdf.to_json())
    return gdf_json, gdf


# ✅ Process H3 data
gdf_json, df_grouped = process_h3_data(df_emissions)

# ========================== 6️⃣ INITIAL CHARTS CREATION ==========================

line_chart_emissions_by_year_month = charts.create_line_chart_emissions_by_year_month(df_emissions_by_year_month)
bar_chart_emissions_by_type = charts.create_bar_chart_emissions_by_type(df_emission_by_type)
line_chart_emissions_by_type_year_month = charts.create_line_chart_emissions_by_type_year_month(df_emissions_by_type_year_month)
h3_map = charts.create_h3_map(gdf_json, df_grouped)


# ========================== 7️⃣ DASHBOARD LAYOUT ==========================

app.layout = dbc.Container([
    
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
            ], ),
            dbc.Row([
                dbc.Col(dcc.Graph(id="map-chart-emissions-map", figure=h3_map),
                        className="dashboard-chart-container"),
                dbc.Col(dcc.Graph(id="line-chart-emissions-by-type-year-month", figure=line_chart_emissions_by_type_year_month),
                        className="dashboard-chart-container")
            ])
        ])
    ], className="dashboard-main-content" )
], fluid=True)


# ========================== 8️⃣ CALLBACKS ==========================

@callback(
    Output("filter-emissions-type", "value"),
    Input("filter-emissions-type", "value")
)
def update_vessel_filter(selected_values):
    return list(master_emissions_vessel_types) if not selected_values else selected_values

@callback(
    [
        Output("line-chart-emissions-by-year-month", "figure"),
        Output("bar-chart-emissions-by-type", "figure"),
        Output("line-chart-emissions-by-type-year-month", "figure"),
        Output("map-chart-emissions-map", "figure"),
    ],
    [
        Input("filter-emissions-type", "value"),
        Input("filter-date-range", "value"),  # 🔥 New filter added
    ]
)
def update_charts(selected_vessel_types, selected_date_range):
    """Update charts based on selected vessel type, emission type, and date range."""

    filtered_df = df_emissions.copy()

    # ✅ Convert slider index to actual YYYYMM values
    start_ym = index_to_year_month[selected_date_range[0]]
    end_ym = index_to_year_month[selected_date_range[1]]

    # ✅ Filter by date range
    filtered_df = filtered_df[
        (filtered_df["year_month"].astype(int) >= start_ym) &
        (filtered_df["year_month"].astype(int) <= end_ym)
    ]

    # ✅ Filter by vessel type
    if selected_vessel_types:
        filtered_df = filtered_df[filtered_df["StandardVesselType"].isin(selected_vessel_types)]


    # ✅ Recreate filtered data
    df_filtered_by_year_month = filtered_df.groupby(['year', 'month'])['co2_equivalent_t'].sum().reset_index()
    df_filtered_by_type = filtered_df.groupby('StandardVesselType')['co2_equivalent_t'].sum().sort_values(ascending=False).head(6)
    df_filtered_by_type_year_month = filtered_df.groupby(['StandardVesselType', 'year_month'])['co2_equivalent_t'].sum().reset_index()

    # ✅ Process H3 data for the map
    gdf_json, df_grouped = process_h3_data(filtered_df)

    # ✅ Recreate charts with filtered data
    updated_chart_emissions_by_year_month = charts.create_line_chart_emissions_by_year_month(df_filtered_by_year_month)
    updated_chart_emissions_by_type = charts.create_bar_chart_emissions_by_type(df_filtered_by_type)
    updated_chart_emissions_by_type_year_month = charts.create_line_chart_emissions_by_type_year_month(df_filtered_by_type_year_month)
    updated_chart_map = charts.create_h3_map(gdf_json, df_grouped)

    return updated_chart_emissions_by_year_month, updated_chart_emissions_by_type, updated_chart_emissions_by_type_year_month, updated_chart_map


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)