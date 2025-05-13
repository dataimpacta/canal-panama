# layout_test.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import layout

# Sample data for dummy charts
df = pd.DataFrame({
    "x": [1, 2, 3],
    "y": [4, 1, 2]
})

# Create dummy figures
fig1 = px.line(df, x="x", y="y", title="Chart 1")
fig2 = px.bar(df, x="x", y="y", title="Chart 2")
fig3 = px.scatter(df, x="x", y="y", title="Chart 3")
fig4 = px.area(df, x="x", y="y", title="Chart 4")

# === Dummy data ===
df_dummy = pd.DataFrame({
    "year": [2020, 2021, 2022],
    "month": [1, 2, 3],
    "co2_equivalent_t": [100, 200, 300],
    "StandardVesselType": ["Cargo", "Tanker", "Passenger"],
    "year_month": [202001, 202102, 202203],
    "resolution_id": [1, 2, 3]
})

unique_year_months = df_dummy["year_month"].unique()
min_index = 0
max_index = len(unique_year_months) - 1
master_emissions_vessel_types = df_dummy["StandardVesselType"].unique()

# === Dummy charts ===
def generate_dummy_fig(title):
    return go.Figure().update_layout(title=title, height=250)

line_chart_emissions_by_year_month = generate_dummy_fig("Line: Year-Month")
bar_chart_emissions_by_type = generate_dummy_fig("Bar: Vessel Type")
h3_map = generate_dummy_fig("Map: Emissions")
line_chart_emissions_by_type_year_month = generate_dummy_fig("Line: Type-Year-Month")



# === Launch app ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = layout.build_dashboard_layout(
    {"id": "chart-1", "fig": line_chart_emissions_by_year_month},
    {"id": "chart-2", "fig": bar_chart_emissions_by_type},
    {"id": "chart-3", "fig": h3_map},
    {"id": "chart-4", "fig": line_chart_emissions_by_type_year_month},
    min_index,
    max_index,
    unique_year_months,
    master_emissions_vessel_types
)

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True, port=8050)