# pylint: disable=import-error
"""App to monitor the emissions in the Panama Canal."""

# ========== Standard Libraries ==========
import os
import io
import json
import time
import logging
from io import StringIO
from pathlib import Path
import datetime

PRIORITY_VESSEL_TYPES = [
    "Bulk Carrier",
    "Container",
    "Oil tanker",
    "Chemical tanker",
    "Liquified gas tanker",
]

PRIORITY_STOP_AREAS = [
    "PPC Balboa",
    "MIT",
    "Panama Canal South Transit",
    "Panama Canal North Transit",
]


def reorder_with_priority(options, priority):
    """Return ``options`` with ``priority`` values at the front."""
    options = list(options)
    priority_items = [p for p in priority if p in options]
    remaining = [o for o in options if o not in priority_items]
    return priority_items + remaining

# ========== Third-Party Libraries ==========
import dash
import dash_bootstrap_components as dbc

from dash import Input, Output, State, ctx, html, MATCH

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
from callbacks import callbacks_energy
from callbacks import callbacks_explorer
from layout import build_footer
from charts.charts_energy import get_country_name

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
file_name_energy = os.getenv("file_name_energy")

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
    vessel_types = reorder_with_priority(
        df['StandardVesselType'].unique(), PRIORITY_VESSEL_TYPES
    )

    # Date slider values
    unique_year_months = sorted(df["year_month"].unique())
    year_month_map = {ym: i for i, ym in enumerate(unique_year_months)}
    index_to_year_month = {i: ym for ym, i in year_month_map.items()}
    min_index = min(year_month_map.values())
    max_index = max(year_month_map.values())
    
    # Set default start date to 2022-01 instead of minimum value
    default_start_ym = 202301  # 2022-01
    if default_start_ym in year_month_map:
        default_start_index = year_month_map[default_start_ym]
    else:
        # If 2022-01 doesn't exist, find the closest date after it
        available_dates = [ym for ym in unique_year_months if ym >= default_start_ym]
        if available_dates:
            default_start_index = year_month_map[min(available_dates)]
        else:
            # Fallback to minimum if no dates after 2022-01
            default_start_index = min_index

    return {
        "vessel_types": vessel_types,
        "date_range": {
            "min_index": min_index,
            "max_index": max_index,
            "default_start_index": default_start_index,  # New field for default start
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
    vessel_types = reorder_with_priority(
        df['StandardVesselType'].unique(), PRIORITY_VESSEL_TYPES
    )
    stop_area = reorder_with_priority(
        df['stop_area'].unique(), PRIORITY_STOP_AREAS
    )

    # Date slider values
    unique_year_months = sorted(df["year_month"].unique())
    year_month_map = {ym: i for i, ym in enumerate(unique_year_months)}
    index_to_year_month = {i: ym for ym, i in year_month_map.items()}
    min_index = min(year_month_map.values())
    max_index = max(year_month_map.values())
    
    # Set default start date to 2022-01 instead of minimum value
    default_start_ym = 202301  # 2022-01
    if default_start_ym in year_month_map:
        default_start_index = year_month_map[default_start_ym]
    else:
        # If 2022-01 doesn't exist, find the closest date after it
        available_dates = [ym for ym in unique_year_months if ym >= default_start_ym]
        if available_dates:
            default_start_index = year_month_map[min(available_dates)]
        else:
            # Fallback to minimum if no dates after 2022-01
            default_start_index = min_index

    return {
        "vessel_types": vessel_types,
        "stop_area": stop_area,
        "date_range": {
            "min_index": min_index,
            "max_index": max_index,
            "default_start_index": default_start_index,  # New field for default start
            "unique_year_months": unique_year_months,
            "index_to_year_month": index_to_year_month,
        }
    }

def prepare_energy_controls(df):
    """
    Given a DataFrame with energy demand data, returns a dictionary
    with control values for origin (country_before), destination (country_after), and date ranges.
    """
    
    # Unique origin and destination countries (use full names for controls)
    country_before = sorted(df['country_before_name'].unique())
    country_after = sorted(df['country_after_name'].unique())

    # Maps from country name to ISO-2 code for filtering
    country_before_map = dict(
        df[['country_before_name', 'country_before']].drop_duplicates().values
    )
    country_after_map = dict(
        df[['country_after_name', 'country_after']].drop_duplicates().values
    )

    # Date slider values for year_week
    unique_year_weeks = sorted(df["year_week"].unique())
    year_week_map = {yw: i for i, yw in enumerate(unique_year_weeks)}
    index_to_year_week = {i: yw for yw, i in year_week_map.items()}
    min_index = min(year_week_map.values())
    max_index = max(year_week_map.values())

    return {
        "country_before": country_before,
        "country_after": country_after,
        "country_before_map": country_before_map,
        "country_after_map": country_after_map,
        "date_range": {
            "min_index": min_index,
            "max_index": max_index,
            "unique_year_week": unique_year_weeks,
            "index_to_year_week": index_to_year_week,
        }
    }

def _yw_to_month(yw: int) -> int:
    """Convert YYYYWW to YYYYMM for month based sliders."""
    year = int(str(yw)[:4])
    week = int(str(yw)[4:])
    date_val = datetime.date.fromisocalendar(year, week, 1)
    return int(date_val.strftime("%Y%m"))


def prepare_explorer_controls(df_emissions, df_waiting, df_energy):
    """Prepare controls for the explorer tab."""
    energy_months = [_yw_to_month(yw) for yw in df_energy["year_week"]]
    all_months = sorted(
        set(df_emissions["year_month"]).union(df_waiting["year_month"]).union(energy_months)
    )
    year_month_map = {ym: i for i, ym in enumerate(all_months)}
    index_to_year_month = {i: ym for ym, i in year_month_map.items()}

    unique_year_weeks = sorted(df_energy["year_week"].unique())
    year_week_map = {yw: i for i, yw in enumerate(unique_year_weeks)}
    index_to_year_week = {i: yw for yw, i in year_week_map.items()}

    return {
        "sources": ["emissions", "waiting_time", "service_time", "energy"],
        "date_range": {
            "min_index": min(year_month_map.values()),
            "max_index": max(year_month_map.values()),
            "unique_year_months": all_months,
            "index_to_year_month": index_to_year_month,
        },
        "week_range": {
            "min_index": min(year_week_map.values()) if year_week_map else 0,
            "max_index": max(year_week_map.values()) if year_week_map else 0,
            "unique_year_week": unique_year_weeks,
            "index_to_year_week": index_to_year_week,
        },
    }

# ========================== 3️⃣ READ & PREPROCESS DATA ==========================

# ✅ Read the data
df_emissions = read_parquet_from_s3(bucket_name, file_name_emissions)
df_emissions["year_month"] = (
    df_emissions["year"].astype(str) + df_emissions["month"].astype(str).str.zfill(2)
).astype(int)

# Pre-sort the DataFrame by year_month for better performance in callbacks
df_emissions = df_emissions.sort_values("year_month").reset_index(drop=True)

# Optimize data types for better memory usage and performance
df_emissions = df_emissions.astype({
    "year": "int16",
    "month": "int8", 
    "year_month": "int32",
    "co2_equivalent_t": "float32"
})

controls_emissions = prepare_emissions_controls(df_emissions)


# Read Waiting Time Data
df_waiting_times = read_parquet_from_s3(bucket_name, file_name_waiting)
df_waiting_times["year_month"] = (
    df_waiting_times["year"].astype(str) + df_waiting_times["month"].astype(str).str.zfill(2)
).astype(int)

controls_waiting_times = prepare_waiting_time_controls(df_waiting_times)

# Read Energy Demand Data
df_energy_demand = read_parquet_from_s3(bucket_name, file_name_energy)
df_energy_demand["year_week"] = (
    df_energy_demand["year"].astype(str) + df_energy_demand["week"].astype(str).str.zfill(2)
).astype(int)
df_energy_demand["year_month"] = df_energy_demand.apply(
    lambda row: int(
        datetime.date.fromisocalendar(int(row["year"]), int(row["week"]), 1).strftime("%Y%m")
    ),
    axis=1,
)

df_energy_demand["country_before_name"] = df_energy_demand["country_before"].apply(get_country_name)
df_energy_demand["country_after_name"] = df_energy_demand["country_after"].apply(get_country_name)

controls_energy = prepare_energy_controls(df_energy_demand)
controls_explorer = prepare_explorer_controls(
    df_emissions,
    df_waiting_times,
    df_energy_demand,
)

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

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Panama Canal Analytics"  # This sets the browser tab title
)
server = app.server

# Respect headers set by a reverse proxy like nginx
# This ensures correct URLs when the app is served behind a proxy
from werkzeug.middleware.proxy_fix import ProxyFix
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)

# Inline the local stylesheet and preload external CSS to minimise
# render-blocking resources.
local_css_path = Path(__file__).resolve().parent / "assets" / "styles.css"
try:
    local_css = local_css_path.read_text()
except FileNotFoundError:
    local_css = ""

bootstrap_css = dbc.themes.BOOTSTRAP
bootstrap_icons = dbc.icons.BOOTSTRAP

app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        <link rel=\"preload\" href=\"{bootstrap_icons}\" as=\"style\" onload=\"this.onload=null;this.rel='stylesheet'\">
        <link rel=\"preload\" href=\"{bootstrap_css}\" as=\"style\" onload=\"this.onload=null;this.rel='stylesheet'\">
        <link rel=\"preload\" href=\"/assets/Financing_Logo.png\" as=\"image\">
        <noscript>
            <link rel=\"stylesheet\" href=\"{bootstrap_icons}\">
            <link rel=\"stylesheet\" href=\"{bootstrap_css}\">
        </noscript>
        <style>{local_css}</style>
        {{%css%}}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            <script src=\"/_dash-component-suites/dash/deps/polyfill@7.v2_18_2m174...12.1.min.js\" defer></script>
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

app.layout = html.Div([
    layout.build_header(),  # <-- Not in dbc.Container
    layout.build_main_layout_content()  # <-- Refactor everything else into a new function
])

# ========================== 8️⃣ CALLBACKS ==========================

callbacks_emissions.setup_emissions_callbacks(
    app,
    df_emissions,
    controls_emissions,
    geojson_template,
    unique_polygons_gdf)

callbacks_waiting.setup_waiting_times_callbacks(
    app,
    df_waiting_times,
    controls_waiting_times
)

callbacks_energy.setup_energy_callbacks(
    app,
    df_energy_demand,
    controls_energy
)

@app.callback(
    Output("chart-tabs-store", "data"),
    [
        Input("tab-emissions", "n_clicks"),
        Input("tab-waiting", "n_clicks"),
        Input("tab-service", "n_clicks"),
        Input("tab-energy", "n_clicks"),
        Input("tab-explorer", "n_clicks"),
        Input("tab-about", "n_clicks"),
    ],
    prevent_initial_call=True
)

def update_tab(*args):
    """Update name of the tab"""
    triggered_id = ctx.triggered_id
    return triggered_id.replace("tab-", "") if triggered_id else "emissions"



@app.callback(
    Output("main-content", "children"),
    Input("initial-delay", "n_intervals")
)
def show_main_content(n_intervals):
    """Show the main content after initial delay"""
    if n_intervals is None or n_intervals == 0:
        return html.Div([
            html.H4("Loading main content...", className="text-center text-muted"),
            html.Div(className="text-center", children=[
                dbc.Spinner(size="lg", color="primary")
            ])
        ])
    return ""  # Let the tab-content callback handle the actual content


@app.callback(
    Output("tab-content", "children"),
    Input("chart-tabs-store", "data"),
    Input("initial-delay", "n_intervals")
)

def update_tab_content(selected_tab, n_intervals):
    """Update the dashboard depending on the different tabs."""
    # Don't show content until initial delay is complete
    if n_intervals is None or n_intervals == 0:
        return ""
    
    nav_bar = layout.build_navigation_bar(active_tab=selected_tab)
    """
    Update the dashboard depending on the differnt tabs. 
    """
    nav_bar = layout.build_navigation_bar(active_tab=selected_tab)

    if selected_tab == "emissions":
        return html.Div([
            nav_bar,
            dbc.Row([
                layout.build_sidebar_emissions(controls_emissions),
                layout.build_main_container_emissions()
            ], className="g-0")
        ])
    
    elif selected_tab == "waiting":
        return html.Div([
            nav_bar,
            dbc.Row([
            layout.build_sidebar_waiting_times(controls_waiting_times),  # Your existing sidebar
            layout.build_main_container_waiting_times()
        ], className="g-0")
        ])
    elif selected_tab == "service":
        return html.Div([
            nav_bar,
            dbc.Row([
            layout.build_sidebar_waiting_times(controls_waiting_times),  # Your existing sidebar
            layout.build_main_container_service_times()
        ], className="g-0")
        ])
    elif selected_tab == "energy":
        return html.Div([
            nav_bar,
            dbc.Row([
            layout.build_sidebar_energy(controls_energy), 
            layout.build_main_container_energy()
        ], className="g-0")
        ])
    elif selected_tab == "explorer":
        return html.Div([
            nav_bar,
            dbc.Row([
                layout.build_sidebar_explorer(controls_explorer),
                layout.build_main_container_explorer()
            ], className="g-0")
        ])
    elif selected_tab == "about":
        return html.Div([
            nav_bar,
            dbc.Container([
            layout.build_about_us()
        ], fluid=True)
        ])


@app.callback(
    Output("modal-welcome", "is_open"),
    Output("popover-filters", "is_open"),
    Input("tutorial-store", "data")
)
def display_tutorial(step):
    if step is None:
        return True, False
    return False, step == "filters"


@app.callback(
    Output("tutorial-store", "data"),
    Input("btn-tutorial-start", "n_clicks"),
    Input("btn-tutorial-next-filters", "n_clicks"),
    State("tutorial-store", "data"),
    prevent_initial_call=True
)
def update_tutorial(start_click, next_click, current):
    triggered = ctx.triggered_id
    if triggered == "btn-tutorial-start":
        return "filters"
    if triggered == "btn-tutorial-next-filters":
        return "done"
    return current


@app.callback(
    Output({"type": "chart-modal", "id": MATCH}, "is_open"),
    Input({"type": "open-fullscreen", "id": MATCH}, "n_clicks"),
    Input({"type": "close-fullscreen", "id": MATCH}, "n_clicks"),
    State({"type": "chart-modal", "id": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_chart_modal(open_clicks, close_clicks, is_open):
    trigger = ctx.triggered_id
    if trigger and trigger.get("type") == "open-fullscreen":
        return True
    if trigger and trigger.get("type") == "close-fullscreen":
        return False
    return is_open


callbacks_explorer.setup_explorer_callbacks(
    app,
    df_emissions,
    df_waiting_times,
    df_energy_demand,
    controls_explorer,
)

# Run the app
if __name__ == '__main__':
    
    app.run_server(debug=False, host='0.0.0.0', port=8050)
