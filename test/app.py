import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
import os
import boto3
from io import StringIO

# My libraries
from charts import create_emissions_chart 

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# Read the Data

# ➡️ Here is the connection with pandas to read the CSV file
# Get the absolute path to the root directory
# root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# csv_file_path = os.path.join(root_dir, "sample_data", "Generated_Emission_Data_Monthly.csv")

# ➡️ Here is the connection, we need to change this to the S3
# df = pd.read_csv(csv_file_path)

# Set up AWS S3 client
s3_client = boto3.client('s3')

# Bucket and file name
bucket_name = 'buckect-canalpanama'
file_name = 'Generated_Emission_Data_Monthly.csv'

# Function to read CSV from S3
def read_csv_from_s3(bucket, file):
    obj = s3_client.get_object(Bucket=bucket, Key=file)
    data = obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(data))

# Read the data from S3
df = read_csv_from_s3(bucket_name, file_name)


years = sorted(df['year'].unique())


# ➡️ Group by Year and Month
emissions_by_month = df.groupby(['year', 'month'])['emission_value'].sum().reset_index()

## Create the chart
emissions_chart = create_emissions_chart(emissions_by_month)


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
                options=[{"label": str(year), "value": year} for year in years],
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
                    dcc.Graph(figure=emissions_chart)  # 📌 Chart inserted here
                ], className="dashboard-chart-container"),
            
                dbc.Col([
                    html.H3("Emissions by Type of Vessel", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    dcc.Graph(id="emissions-chart")
                ], className="dashboard-chart-container") 
            ]),

            ## ➡️ Lower Row            
            dbc.Row([
                dbc.Col([
                    html.H3("Emissions by Region", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    dcc.Graph(id="chart-output"),  # 📌 Chart inserted here
                ], className="dashboard-chart-container"),
                dbc.Col([
                    html.H3("Emissions by Vessel type", className="dashboard-chart-title"),
                    html.P("TONNES", className="dashboard-chart-subtitle"),
                    dcc.Graph(figure=emissions_chart),  # 📌 Chart inserted here
                ], className="dashboard-chart-container")

            ]),


        ], )



    ], className="dashboard-main-content")


], fluid=True)


# Callback to update chart
@callback(
    Output("emissions-chart", "figure"),
    Input("year-filter", "value")
)

def update_chart(selected_year):
    filtered_df = emissions_by_month[emissions_by_month["year"] == selected_year]  # 🔥 Filter correctly!
    return create_emissions_chart(filtered_df)  # Pass only the filtered data




# Callback to switch charts
@callback(
    Output("chart-output", "figure"),
    Input("chart-tabs", "value")
)
def display_chart(selected_tab):
    filtered_df = emissions_by_month[emissions_by_month["year"] == 2024]
    filtered_df2 = emissions_by_month[emissions_by_month["year"] == 2023]
    if selected_tab == "emissions":
        return create_emissions_chart(filtered_df)
    elif selected_tab == "waiting":
        return create_emissions_chart(filtered_df2)
    elif selected_tab == "energy":
        return create_emissions_chart(df)
    elif selected_tab == "explorer":
        return create_emissions_chart(df)



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)