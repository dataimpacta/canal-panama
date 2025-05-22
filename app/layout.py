# pylint: disable=import-error

import dash_bootstrap_components as dbc
from dash import html, dcc

from charts import charts_emissions
from controls import controls_emissions


# FIXED VALUES

def build_header():
    return dbc.Row([
        dbc.Col([
            html.H1("Panama Maritime Statistics"),
            html.H4("Efficiency and Sustainability Indicators")
        ])
    ], className="dashboard-header pb-4")


def build_navigation_bar():
    return dbc.Row([
        dbc.Col(dcc.Tabs(id="chart-tabs", value="emissions", children=[
            dcc.Tab(label="Emissions", value="emissions"),
            dcc.Tab(label="Waiting Time", value="waiting"),
            dcc.Tab(label="Service Time", value="service"),
            dcc.Tab(label="Energy", value="energy"),
            dcc.Tab(label="Explorer", value="explorer")
        ]), width=12)
    ], className="")


# ============================
# Funcitons for the charts and KPIs

def create_standard_kpi_container(kpi_id):
    return html.Div([
        dcc.Loading(
            id=f"loading-{kpi_id}",
            type="circle",
            children=dbc.Col(
                id=kpi_id,
            )
        )
    ],
    className="border rounded p-3 m-0 g-0")

def build_kpi_grid(kpi_cards, items_per_row=2):
    rows = []
    for i in range(0, len(kpi_cards), items_per_row):
        row = dbc.Row([
            dbc.Col(
                create_standard_kpi_container(kpi_id=card["id"]),
                xs=12, sm=6, md=6, lg=int(12/items_per_row))
            for card in kpi_cards[i:i+items_per_row]
        ], class_name="g-2 mt-2 me-2 ms-2")
        rows.append(row)
    return html.Div(rows)



def create_standard_chart_container(chart):
    """
    Create the standar html DIV for the charts.
    Args:
        Title
        Subtitle
        Id for updating the box
        Margins
    """
    return html.Div([
        html.Div([
            html.H5(chart["title"], className="mb-1", style={"fontWeight": "bold", "color": "#333"}),
            html.P(chart["subtitle"], className="mb-2", style={"fontSize": "0.85rem", "color": "#666"})
        ]),
        dcc.Loading(
            id=f"loading-{chart['id']}",
            type="circle",
            children=dcc.Graph(
                id=chart["id"]
            )
        )
    ],
    className="border rounded p-4 m-0 g-0")

def build_chart_grid(chart_items):
    """
    Build the chart grid with a list of chart items.
    - Separation between columns
    """
    rows = []
    for i in range(0, len(chart_items), 2):
        row = html.Div(
            dbc.Row([
                dbc.Col(
                    create_standard_chart_container(item),
                    xs=12, sm=12, md=6, lg=6, xl=6)
            for item in chart_items[i:i+2]
        ],
        class_name="g-2 mt-0 me-2 ms-2"))

        rows.append(row)

    return html.Div(rows)


# ===========================

# Emissions

def build_sidebar_emissions(controls):
    """
    Build the sidebar for the emissions dashboard.
    - Message box
    - Accordion with:
        - Date range slider
        - Vessel type checklist
    - Refresh button
    """
    return dbc.Col([
        controls_emissions.build_message_box(),
        dbc.Accordion([
            dbc.AccordionItem(
                [controls_emissions.build_date_range_slider(controls["date_range"])],
                title="Date Range"
            ),
            dbc.AccordionItem(
                [controls_emissions.build_vessel_type_checklist(controls["vessel_types"])],
                title="Vessel Type"
            )
        ]),
        html.Br(),
        dbc.Button("Refresh Charts", id="apply-filters-btn", n_clicks=0, color="primary")
    ], className="border rounded p-3", xs=12, md=12, lg=2, width=2)






def build_main_container_emissions():
    """
    Here we only have statick content, with the tags
    - KPI grid
    - Chart grid
    """
    return dbc.Col([
        build_kpi_grid([
            {
                "id": "kpi-1",
                "title": "Total Emissions",
                "subtitle": "TONNES"
            },
        ]),
        build_chart_grid([
            {
                "id": "chart-1",
                "title": "Total Emissions", 
                "subtitle": "TONNES CO2 EQUIVALENT"
            },
            {
                "id": "chart-2",
                "title": "Emissions by Type of Vessel", 
                "subtitle": "TONNES CO2 EQUIVALENT"},
            {
                "id": "chart-3",
                "title": "Emissions by Region", 
                "subtitle": "TONNES CO2 EQUIVALENT"},
            {
                "id": "chart-4",
                "title": "Emissions by Type of Vessel", 
                "subtitle": "TONNES CO2 EQUIVALENT"},
        ])
        ], xs=12, md=12, lg=10, width=10)


def build_sidebar_waiting_times(controls):
    """
    Build the sidebar for the emissions dashboard.
    - Message box
    - Accordion with:
        - Date range slider
        - Vessel type checklist
    - Refresh button
    """
    return dbc.Col([
        controls_emissions.build_message_box(),
        dbc.Accordion([
            dbc.AccordionItem(
                [controls_emissions.build_date_range_slider(controls["date_range"])],
                title="Date Range"
            ),
            dbc.AccordionItem(
                [controls_emissions.build_vessel_type_checklist(controls["vessel_types"])],
                title="Vessel Type"
            ),
            dbc.AccordionItem(
                [controls_emissions.build_vessel_type_checklist(controls["stop_area"])],
                title="Stop Area"
            )
        ]),
        html.Br(),
        dbc.Button("Refresh Charts", id="apply-filters-btn", n_clicks=0, color="primary")

    ], className="border rounded p-3", xs=12, md=12, lg=2, width=2)


def build_main_container_waiting_times():
    """
    Here we only have statick content, with the tags
    - KPI grid
    - Chart grid
    """
    return dbc.Col([
        # build_kpi_grid([
        #     {
        #         "id": "kpi-11",
        #         "title": "Total Emissions",
        #         "subtitle": "TONNES"
        #     },
        # ]),
        build_chart_grid([
            {
                "id": "chart-11",
                "title": "Overall Waiting Time", 
                "subtitle": "HOURS"
            },
            {
                "id": "chart-22",
                "title": "AVG Waiting Time by Stop Area", 
                "subtitle": "HOURS"},
            {
                "id": "chart-33",
                "title": "Waiting Time by Vessel  ", 
                "subtitle": "HOURS"},
            {
                "id": "chart-44",
                "title": "AVG Waiting Time by Vessel Type", 
                "subtitle": "HOURS"},
        ])
        ], xs=12, md=12, lg=10, width=10)


def build_main_container_service_times():
    """
    Here we only have statick content, with the tags
    - KPI grid
    - Chart grid
    """
    return dbc.Col([
        # build_kpi_grid([
        #     {
        #         "id": "kpi-11",
        #         "title": "Total Emissions",
        #         "subtitle": "TONNES"
        #     },
        # ]),
        build_chart_grid([
            {
                "id": "chart-11",
                "title": "Overall Service Time", 
                "subtitle": "HOURS"
            },
            {
                "id": "chart-22",
                "title": "AVG Service Time by Stop Area", 
                "subtitle": "HOURS"},
            {
                "id": "chart-33",
                "title": "Service Time by Vessel  ", 
                "subtitle": "HOURS"},
            {
                "id": "chart-44",
                "title": "AVG Service Time by Vessel Type", 
                "subtitle": "HOURS"},
        ])
        ], xs=12, md=12, lg=10, width=10)



# ============================




def build_main_layout():
    return dbc.Container([
        build_header(),
        build_navigation_bar(),  # This has id="chart-tabs"
        html.Div(id="tab-content")  # ✅ Dynamic container for tab-specific layout
    ], className="g-0 p-4", fluid=True)