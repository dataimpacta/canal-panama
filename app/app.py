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
# df_waiting = read_csv_from_s3(bucket_name, file_name_waiting)
# df_energy = read_csv_from_s3(bucket_name, file_name_energy)


# ➡️ Master Data
master_emissions_years = sorted(df_emissions['year'].unique())


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







## Create the chart
line_chart_emissions_by_year_month = charts.create_line_chart_emissions_by_year_month(df_emissions_by_year_month)
bar_chart_emissions_by_type = charts.create_bar_chart_emissions_by_type(df_emission_by_type)
line_chart_emissions_by_type_year_month = charts.create_line_chart_emissions_by_type_year_month(df_emissions_by_type_year_month)


# Process H3 data
gdf_json, df_grouped = process_h3_data(df_emissions)

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

            dcc.Dropdown(
                id="year-filter",
                options=[{"label": str(year), "value": year} for year in master_emissions_years],
                value=2024,  # Default year selected
                clearable=False
                )


        ], width=2, className="dashboard-sidebar-container"),


        ## ➡️ Main Content
        dbc.Col([

            ## ➡️ Upper Row
            dbc.Row ([

                dbc.Col([
                    html.H3("Total Emissions", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    dcc.Graph(figure=line_chart_emissions_by_year_month)  # 📌 Chart inserted here
                ], className="dashboard-chart-container"),
            
                dbc.Col([
                    html.H3("Emissions by Type of Vessel", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    dcc.Graph(figure=bar_chart_emissions_by_type),
                ], className="dashboard-chart-container") 
            ]),

            ## ➡️ Lower Row            
            dbc.Row([
                dbc.Col([
                    html.H3("Emissions by Region", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    dcc.Graph(figure=h3_map),  # 📌 Chart inserted here
                ], className="dashboard-chart-container"),
                dbc.Col([
                    html.H3("Emissions by Vessel type", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    dcc.Graph(figure=line_chart_emissions_by_type_year_month),  # 📌 Chart inserted here
                ], className="dashboard-chart-container")

            ]),


        ], )



    ], className="dashboard-main-content")


], fluid=True)


## Callback to update chart
# @callback(
#     Output("emissions-chart", "figure"),
#     Input("year-filter", "value")
# )

# def update_chart(selected_year):
#     filtered_df = df_emissions_by_year_month[df_emissions_by_year_month["year"] == selected_year] 
#     return charts.create_line_chart_emissions_by_year_month(filtered_df)  # Pass only the filtered data




# #Callback to switch charts
# @callback(
#     Output("chart-output", "figure"),
#     Input("chart-tabs", "value")
# )
# def display_chart(selected_tab):
#     filtered_df = df_emissions_by_year_month[df_emissions_by_year_month["year"] == 2024]
#     filtered_df2 = df_emissions_by_year_month[df_emissions_by_year_month["year"] == 2023]
#     if selected_tab == "emissions":
#         return charts.create_line_chart_emissions_by_year_month(filtered_df)
#     elif selected_tab == "waiting":
#         return charts.create_line_chart_emissions_by_year_month(filtered_df2)
#     elif selected_tab == "energy":
#         return charts.create_line_chart_emissions_by_year_month(df_emissions)
#     elif selected_tab == "explorer":
#         return charts.create_line_chart_emissions_by_year_month(df_emissions)



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)