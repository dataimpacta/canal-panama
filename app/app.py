import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
from h3.api.basic_str import cell_to_boundary
from shapely.geometry import Polygon
import geopandas as gpd
import json
import os
import boto3
from io import StringIO
from dash.dependencies import Input, Output
import datetime


# My libraries
import charts

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# Establish connection to the database

# Set up AWS S3 client
s3_client = boto3.client('s3')

def read_csv_from_s3(bucket, file):
    obj = s3_client.get_object(Bucket=bucket, Key=file)
    data = obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(data))

# Read the data
bucket_name = 'buckect-canalpanama'
file_name_emissions = 'Generated_Emission_Data_Monthly.csv'
# file_name_waiting = 'Waiting_Time_Data.csv'
# file_name_energy = 'Energy_Consumption_Data.csv'

# Read the data
df_emissions = read_csv_from_s3(bucket_name, file_name_emissions)
df_emissions['year_month'] =  df_emissions['year'].astype(str) + '-' + df_emissions['month'].astype(str)
# Convert year and month into a numerical format YYYYMM for filtering
df_emissions["year_month"] = (
    df_emissions["year"].astype(str) + df_emissions["month"].astype(str).str.zfill(2)
).astype(int)

# df_waiting = read_csv_from_s3(bucket_name, file_name_waiting)
# df_energy = read_csv_from_s3(bucket_name, file_name_energy)


# ➡️ Master Data
master_emissions_years = sorted(df_emissions['year'].unique())
master_emissions_vessel_types = df_emissions['StandardVesselType'].unique()
master_emission_types = df_emissions['emission_type'].unique()

# Define min and max values for the slider
#min_year_month = df_emissions["year_month_numeric"].min()
#max_year_month = df_emissions["year_month_numeric"].max()

# Create a sorted list of unique YYYYMM values
unique_year_months = sorted(df_emissions["year_month"].unique())

# Create a mapping from YYYYMM to a linear index (0, 1, 2, ...)
year_month_map = {ym: i for i, ym in enumerate(unique_year_months)}
index_to_year_month = {i: ym for ym, i in year_month_map.items()}  # Reverse mapping

# Get min/max values
min_index = min(year_month_map.values())  # 0
max_index = max(year_month_map.values())  # Last index



# Data Processing
# ➡️ Group by Year and Month
df_emissions_by_year_month = df_emissions.groupby(['year', 'month'])['emission_value'].sum().reset_index()

# Group by 'StandardVesselType' and sum 'emission_value'
df_emission_by_type = df_emissions.groupby('StandardVesselType')['emission_value'].sum().sort_values(ascending=False).head(6)

# Group by StandardVesselType and year_month
df_emissions_by_type_year_month = df_emissions.groupby(['StandardVesselType', 'year_month'])['emission_value'].sum().reset_index()


# ➡️ Convert H3 to Polygon
def h3_to_polygon(h3_index):
    boundary = cell_to_boundary(h3_index)  
    return Polygon([(lng, lat) for lat, lng in boundary])  # ✅ Swap (lat, lng) → (lng, lat)

# ➡️ Process H3 Data
def process_h3_data(df):
    if df.empty:
        raise ValueError("The DataFrame is empty. Check data input.")

    # ✅ Aggregate emissions by H3 resolution
    df_grouped = df.groupby("resolution_id", as_index=False).agg({"emission_value": "sum"})

    # ✅ Convert DataFrame to GeoDataFrame
    df_grouped["geometry"] = df_grouped["resolution_id"].apply(h3_to_polygon)
    gdf = gpd.GeoDataFrame(df_grouped, geometry="geometry")

    # ✅ Convert GeoDataFrame to GeoJSON
    gdf_json = json.loads(gdf.to_json())

    return gdf_json, gdf  

# Process H3 data
gdf_json, df_grouped = process_h3_data(df_emissions)

## Create the chart
line_chart_emissions_by_year_month = charts.create_line_chart_emissions_by_year_month(df_emissions_by_year_month)
bar_chart_emissions_by_type = charts.create_bar_chart_emissions_by_type(df_emission_by_type)
line_chart_emissions_by_type_year_month = charts.create_line_chart_emissions_by_type_year_month(df_emissions_by_type_year_month)


# Create the map figure
h3_map = charts.create_h3_map(gdf_json, df_grouped)



# Layout Structure
app.layout = dbc.Container([

    ## ➡️ Header
    dbc.Row([
        ## Title
        dbc.Col([
            dbc.Row(html.H1("Panama Maritime Statistics")),
            dbc.Row(html.H4("Efficiency and Sustaianability Indicators"))
        ], width=9,
        ),
        dbc.Col(html.Img(src="/assets/sample_image.png", width="100%"))
    ], className="dashboard-header"),

    ## ➡️ Tabs
    dbc.Row([
        dbc.Col(dcc.Tabs(id="chart-tabs", value="emissions", children=[
            dcc.Tab(label="Emissions", value="emissions"),
            dcc.Tab(label="Waiting Time", value="waiting"),
            dcc.Tab(label="Energy", value="energy"),
            dcc.Tab(label="Explorer", value="explorer")
        ]), width=6)
    ],  className="dashboard-navigation-bar"),
    
    ## ➡️ Buttons
    #dbc.Row([
    #    dbc.Col([dbc.Button("Emissions", color="primary", className="m-2"), 
    #             dbc.Button("Waiting Time", color="secondary", className="m-2"),
    #             dbc.Button("Energy", color="secondary", className="m-2"),
    #             dbc.Button("Explorer", color="secondary", className="m-2")])
    #], className="dashboard-navigation-bar"),
    
    ## ➡️ Main Components
    dbc.Row([

        ## ➡️ Sidebar
        dbc.Col([
            html.H3("ADD/REMOVE PARAMETERS", className="dashboard-sidebar-title") ,


            html.Br(),

            html.H3("Date Range", className="dashboard-sidebar-title"),
            dcc.RangeSlider(
                id="filter-date-range",
                min=min_index,  # ✅ Use linear index
                max=max_index,  # ✅ Use linear index
                step=1,  # ✅ Step by 1 (each step = 1 month)
                marks={
                    min_index: str(unique_year_months[0]),  # First YYYYMM
                    max_index: str(unique_year_months[-1])  # Last YYYYMM
                },
                value=[min_index, max_index],  # Default: full range
                allowCross=False
            ),

            html.Br(),

            html.H3("Vessel Type", className="dashboard-sidebar-title"),
            dcc.Dropdown(
                id="filter-emissions-type",
                options=[{"label": vessel_type, "value": vessel_type} for vessel_type in master_emissions_vessel_types],
                value=list(master_emissions_vessel_types),  # ✅ Start with all options selected
                multi=True,  # ✅ Enables multi-selection
                placeholder="Select Vessel Type(s)",
                clearable=False,
                style={"width": "100%"}
            ),

            html.Br(),


            html.H3("Emission Type", className="dashboard-sidebar-title"),
            dcc.Dropdown(
                id="filter-emissions-type-category",
                options=[{"label": emission, "value": emission} for emission in master_emission_types],
                value=list(master_emission_types),  # ✅ Start with all selected
                multi=True,
                placeholder="Select Emission Type(s)",
                clearable=False,
                style={"width": "100%"}
            ),
            
            html.Br(),



        ], width=2, className="dashboard-sidebar-container"),


        ## ➡️ Main Content
        dbc.Col([

            ## ➡️ Upper Row
            dbc.Row ([

                dbc.Col([
                    html.H3("Total Emissions", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    #dcc.Graph(figure=line_chart_emissions_by_year_month)  # 📌 Chart inserted here
                    dcc.Graph(id="line-chart-emissions-by-year-month", figure=line_chart_emissions_by_year_month),
                ], className="dashboard-chart-container"),
            
                dbc.Col([
                    html.H3("Emissions by Type of Vessel", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    #dcc.Graph(figure=bar_chart_emissions_by_type),
                    dcc.Graph(id="bar-chart-emissions-by-type", figure=bar_chart_emissions_by_type),
                ], className="dashboard-chart-container") 
            ]),

            ## ➡️ Lower Row            
            dbc.Row([
                dbc.Col([
                    html.H3("Emissions by Region", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    #dcc.Graph(figure=h3_map),  # 📌 Chart inserted here
                    dcc.Graph(id="map-chart-emissions-map", figure=h3_map),
                ], className="dashboard-chart-container"),
                dbc.Col([
                    html.H3("Emissions by Vessel type", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    #dcc.Graph(figure=line_chart_emissions_by_type_year_month),  # 📌 Chart inserted here
                    dcc.Graph(id="line-chart-emissions-by-type-year-month", figure=line_chart_emissions_by_type_year_month),

                ], className="dashboard-chart-container")

            ]),


        ], )



    ], className="dashboard-main-content")


], fluid=True)


from dash.dependencies import Input, Output

@callback(
    Output("filter-emissions-type-category", "value"),
    Input("filter-emissions-type-category", "value")
)
def update_emission_filter(selected_values):
    """Resets selection to all options when empty."""
    
    all_emission_types = list(master_emission_types)  

    # ✅ If nothing is selected, reset to all emission types
    if not selected_values:
        return all_emission_types

    return selected_values  # Otherwise, return the user's selection

@callback(
    Output("filter-emissions-type", "value"),  # Updates the dropdown selection
    Input("filter-emissions-type", "value")  # Gets selected values
)
def update_vessel_filter(selected_values):
    """Resets selection to all options when empty."""
    
    all_vessel_types = list(master_emissions_vessel_types)  # ✅ Convert to a list

    # ✅ If nothing is selected, reset to all vessel types
    if not selected_values:
        return all_vessel_types

    return selected_values  # Otherwise, return the user’s selection

@callback(
    [
        Output("line-chart-emissions-by-year-month", "figure"),
        Output("bar-chart-emissions-by-type", "figure"),
        Output("line-chart-emissions-by-type-year-month", "figure"),
        Output("map-chart-emissions-map", "figure"),
    ],
    [
        Input("filter-emissions-type", "value"),
        Input("filter-emissions-type-category", "value"),
        Input("filter-date-range", "value"),  # 🔥 New filter added
    ]
)
def update_charts(selected_vessel_types, selected_emission_types, selected_date_range):
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

    # ✅ Filter by emission type
    if selected_emission_types:
        filtered_df = filtered_df[filtered_df["emission_type"].isin(selected_emission_types)]

    # ✅ Recreate filtered data
    df_filtered_by_year_month = filtered_df.groupby(['year', 'month'])['emission_value'].sum().reset_index()
    df_filtered_by_type = filtered_df.groupby('StandardVesselType')['emission_value'].sum().sort_values(ascending=False).head(6)
    df_filtered_by_type_year_month = filtered_df.groupby(['StandardVesselType', 'year_month'])['emission_value'].sum().reset_index()

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