# pylint: disable=import-error

import dash_bootstrap_components as dbc
from dash import html, dcc

from charts import charts_emissions
from controls import controls_explorer
from controls import controls_emissions
from controls import controls_time


# FIXED VALUES

def build_header():
    return html.Div([
        # Logo only visible on small screens (above the title)
        html.Div([
            html.Img(
                src="/assets/Financing_Logo.png",
                alt="SENACYT Logo",
                style={
                    "height": "60px",
                    "margin": "0 auto",
                    "display": "block",
                    "alignItems": "left",
                }
            )
        ], className="d-flex d-md-none mb-3"),  # Show on xs-md only

        dbc.Row([
            # Title column
            dbc.Col([
                html.Div([
                    html.H1("Panama Maritime Statistics", style={"margin": 0}),
                    html.H4("Efficiency and Sustainability Indicators", style={"margin": 0, "fontWeight": "normal"})
                ])
            ], xs=12, md=10, lg=10),

            # Logo column (only visible on lg and up)
            dbc.Col([
                html.Div([
                    html.Img(
                        src="/assets/Financing_Logo.png",
                        alt="SENACYT Logo",
                        style={
                            "height": "70px",
                            "marginLeft": "auto"
                        }
                    )
                ],
                className="d-none d-md-flex",
                style={
                    "justifyContent": "flex-end",
                    "alignItems": "center",
                    "height": "100%"
                })
            ], md=2)
        ], className="dashboard-header pb-4")
    ])


def build_footer():
    return dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Small(
                "This dashboard was developed as part of the project \"Green Shipping Corridors in the Panama Canal under Climate Risk risk\", partly sponsored by SENACYT under project number 060/2024.",
                className="text-muted",
            ),
        ])
    ], className="dashboard-footer mt-4 mb-2")


def build_about_us():
    return dbc.Container([
        html.Br(),



        html.P(
            "This dashboard is inspired by the study "
            "'Greenhouse Gas Mitigation at Maritime Chokepoints: The Case of the Panama Canal', "
            "led by Gabriel Fuentes. The goal is to visualize maritime emissions and performance indicators "
            "to support sustainable shipping practices and informed decision-making."
        ),


        html.Br(),

        dbc.Row([
            dbc.Col([
                html.Img(
                    src="/assets/gabriel_moises_fuentes.jpg",
                    alt="Gabriel Fuentes",
                    style={"width": "100%", "maxWidth": "150px", "borderRadius": "8px"}
                )
            ], xs=12, md=12, lg=3, width=3),

            dbc.Col([
                html.H5("Gabriel Fuentes"),
                html.P(
                    "Assistant Professor at the Norwegian School of Economics (NHH), Gabriel Fuentes specializes in maritime analytics and operations research. "
                    "He co-authored the study that serves as the foundation for this dashboard. "
                    "His research focuses on improving operational efficiency to reduce emissions in maritime transport."
                ),
                html.P([
                    "Read the full study: ",
                    html.A(
                        "Greenhouse Gas Mitigation at Maritime Chokepoints",
                        href="https://doi.org/10.1016/j.trd.2023.103694",
                        target="_blank",
                        style={"textDecoration": "underline"}
                    )
                ])
            ], xs=12, md=12, lg=9, width=9)
        ], className="mb-4 g-4"),

        html.Br(),

        dbc.Row([
            dbc.Col([
                html.Img(
                    src="/assets/logo_senacyt.jpg",
                    alt="SENACYT",
                    style={"width": "100%", "maxWidth": "200px"}
                )
            ], xs=12, md=12, lg=3, width=3),
            dbc.Col([
                html.H5("SENACYT"),
                html.P(
                    "The National Secretariat of Science, Technology and Innovation (SENACYT) of Panama supports scientific research and technological development. "
                    "SENACYT has been instrumental in providing resources and support for projects aimed at sustainable development, including initiatives in maritime emissions reduction."
                )
            ], xs=12, md=12, lg=9, width=9)
        ], className="mb-4 g-4"),

        html.Br()
    ], className="")


def build_navigation_bar(active_tab="emissions"):
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Emissions", href="#", id="tab-emissions", active=(active_tab == "emissions"))),
            dbc.NavItem(dbc.NavLink("Waiting Time", href="#", id="tab-waiting", active=(active_tab == "waiting"))),
            dbc.NavItem(dbc.NavLink("Service Time", href="#", id="tab-service", active=(active_tab == "service"))),
            dbc.NavItem(dbc.NavLink("Energy", href="#", id="tab-energy", active=(active_tab == "energy"))),
            dbc.NavItem(dbc.NavLink("Explorer", href="#", id="tab-explorer", active=(active_tab == "explorer"))),
            dbc.NavItem(dbc.NavLink("About Us", href="#", id="tab-about", active=(active_tab == "about"))),
        ],
        pills=True,
        vertical=False,
        className="mb-2"
    )

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
                xs=12, sm=12, md=6, lg=int(12/items_per_row))
            for card in kpi_cards[i:i+items_per_row]
        ], class_name="g-2 mt-0 me-2 ms-2")
        rows.append(row)
    return html.Div(rows)



def create_standard_chart_container(chart):
    """
    Create the standard HTML DIV for the charts with a title, subtitle, and tooltip on the title.
    """
    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Span(
                        chart["title"] + " ",
                        style={
                            "fontWeight": "bold",
                            "color": "#333",
                            "fontSize": "1.1rem"
                        },
                    ),
                    html.I(
                        className="bi bi-info-circle-fill info-icon",
                        id=f"title-tooltip-{chart['id']}"
                    ),
                    dbc.Tooltip(
                        chart.get("description", "No description available."),
                        target=f"title-tooltip-{chart['id']}",
                        placement="right",
                        style={"maxWidth": "300px"}
                    )
                ], width="auto")
            ], className="align-items-center g-1"),

            html.P(chart["subtitle"], className="mb-2", style={"fontSize": "0.85rem", "color": "#666"})
        ]),

        dcc.Loading(
            id=f"loading-{chart['id']}",
            type="circle",
            children=dcc.Graph(id=chart["id"])
        )
    ], className="border rounded p-4 m-0 g-0")

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
        controls_emissions.build_button_refresh_charts()
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
                "id": "emissions--kpi--1",
                "title": "Total Emissions in the Panama Canal",
                "subtitle": "TONNES"
            },
        ]),
        build_chart_grid([
            {
                "id": "emissions--chart--1",
                "title": "Total Emissions", 
                "subtitle": "TONNES CO2-eq",
                "description": "This is the description for total emissions."
            },
            {
                "id": "emissions--chart--2",
                "title": "Emissions by Type of Vessel", 
                "subtitle": "TONNES CO2-eq"},
            {
                "id": "emissions--chart--3",
                "title": "Emissions by Region", 
                "subtitle": "TONNES CO2-eq"},
            {
                "id": "emissions--chart--4",
                "title": "Emissions by Type of Vessel", 
                "subtitle": "TONNES CO2-eq"},
        ])
        ], className="p-0", xs=12, md=12, lg=10, width=10)


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
        controls_time.build_message_box(),
        dbc.Accordion([
            dbc.AccordionItem(
                [controls_time.build_date_range_slider(controls["date_range"])],
                title="Date Range"
            ),
            dbc.AccordionItem(
                [controls_time.build_vessel_type_checklist(controls["vessel_types"])],
                title="Vessel Type"
            ),
            dbc.AccordionItem(
                [controls_time.build_stop_area_checklist(controls["stop_area"])],
                title="Stop Area"
            )
        ]),
        html.Br(),
        controls_emissions.build_button_refresh_charts()

    ], className="border rounded p-3", xs=12, md=12, lg=2, width=2)


def build_main_container_waiting_times():
    """
    Here we only have statick content, with the tags
    - KPI grid
    - Chart grid
    """
    return dbc.Col([

        build_chart_grid([
            {
                "id": "time--chart--1",
                "title": "Overall Waiting Time", 
                "subtitle": "HOURS"
            },
            {
                "id": "time--chart--2",
                "title": "AVG Waiting Time by Stop Area", 
                "subtitle": "HOURS"},
            {
                "id": "time--chart--3",
                "title": "Waiting Time by Vessel  ", 
                "subtitle": "HOURS"},
            {
                "id": "time--chart--4",
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
                "id": "time--chart--1",
                "title": "Overall Service Time", 
                "subtitle": "HOURS"
            },
            {
                "id": "time--chart--2",
                "title": "AVG Service Time by Stop Area", 
                "subtitle": "HOURS"},
            {
                "id": "time--chart--3",
                "title": "Service Time by Vessel  ", 
                "subtitle": "HOURS"},
            {
                "id": "time--chart--4",
                "title": "AVG Service Time by Vessel Type", 
                "subtitle": "HOURS"},
        ])
        ], xs=12, md=12, lg=10, width=10)


def build_sidebar_explorer(controls):
    """Sidebar for the explorer tab."""
    return dbc.Col([
        dbc.Accordion([
            dbc.AccordionItem(
                [controls_explorer.build_source_dropdown(controls["sources"])],
                title="Source"
            ),
            dbc.AccordionItem(
                [controls_explorer.build_date_range_slider(controls["date_range"])],
                title="Date Range"
            )
        ]),
        html.Br(),
        controls_explorer.build_download_button(),
        dcc.Download(id="explorer--download")
    ], className="border rounded p-3", xs=12, md=12, lg=2, width=2)


def build_main_container_explorer():
    """Main container for the explorer tab."""
    return dbc.Col([
        build_chart_grid([
            {
                "id": "explorer--chart",
                "title": "Value Over Time",
                "subtitle": ""
            }
        ])
    ], className="p-0", xs=12, md=12, lg=10, width=10)



# ============================




def build_main_layout():
    return dbc.Container([
        dcc.Store(id="chart-tabs-store", data="emissions"),
        build_header(),
        #build_navigation_bar(),  # This has id="chart-tabs"
        html.Div(id="tab-content"),  # ✅ Dynamic container for tab-specific layout
        build_footer()
    ], className="g-0 p-4", fluid=True)