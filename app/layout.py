# pylint: disable=import-error

import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

from charts import charts_emissions
from controls import controls_explorer
from controls import controls_emissions
from controls import controls_time
from controls import controls_energy


# FIXED VALUES

def build_header():
    return html.Div([
        # Logo only visible on small screens (above the title)
        html.Div([
            html.Img(
                src="/assets/Financing_Logo.webp",
                alt="SENACYT Logo",
                width = "275px",
                height = "60px",
                #style="margin-left: auto;"
            )
        ], className="d-flex d-md-none mb-3"),  # Show on xs-md only

        dbc.Row([
            # Title column
            dbc.Col([
                html.Div([
                    html.H1(
                        "Panama Maritime Statistics",
                        style={
                            "margin": 0,
                            "fontSize": "2.75rem",  # or 1.75rem
                            "fontWeight": 700,
                            "fontFamily": "Arial, Helvetica, sans-serif"  # system fonts = fast
                        }
                    ),
                    html.H4(
                        "Efficiency and Sustainability Indicators",
                        style={
                            "margin": 0,
                            "fontWeight": 500,
                            "fontSize": "1.5rem",
                            "fontFamily": "Arial, Helvetica, sans-serif"
                        }
                    )
                ])
            ], xs=12, md=10, lg=10),

            # Logo column (only visible on lg and up)
            dbc.Col([
                html.Div([
                    html.Img(
                        src="/assets/Financing_Logo.webp",
                        alt="SENACYT Logo",
                        width="320px",
                        height="70px",
                        #style="margin-left: auto;"
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
    ], className="ps-4 pe-4 pt-4")  # Add the same padding as the main container


def build_footer():
    return dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Small([
                "This dashboard was developed as part of the project ",
                html.Span(
                    "\"Green Shipping Corridors in the Panama Canal under Climate Risk\"",
                    style={"fontWeight": "bold"}
                ),
                ", partly sponsored by SENACYT under project number 060/2024."
            ],
            className="text-muted",
            style={
                "fontSize": "0.9rem",
                "fontFamily": "Arial, Helvetica, sans-serif",
                "lineHeight": "1.4",
                "display": "block",
                "textAlign": "left"
            })
        ], style={"minHeight": "40px"})
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
        className="mb-3"
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
    className="border p-4 m-0 g-0")

def build_kpi_grid(kpi_cards, items_per_row=2):
    rows = []
    for i in range(0, len(kpi_cards), items_per_row):
        row = dbc.Row([
            dbc.Col(
                create_standard_kpi_container(kpi_id=card["id"]),
                xs=12, sm=12, md=6, lg=int(12/items_per_row))
            for card in kpi_cards[i:i+items_per_row]
        ], class_name="g-0 mt-0 me-0 ms-0")
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
                        id=f"title-tooltip-{chart['id']}",
                        style={"cursor": "pointer", "color": "#666"}
                    ),
                    chart.get("controls"),
                    dbc.Tooltip(
                        chart.get("description", "No description available."),
                        target=f"title-tooltip-{chart['id']}",
                        placement="right",
                        style={"maxWidth": "300px"}
                    )
                ], width="auto", class_name="d-flex align-items-center gap-2"),
                dbc.Col(
                    dbc.Button(
                        html.I(className="bi bi-arrows-fullscreen"),
                        id={"type": "open-fullscreen", "id": chart["id"]},
                        color="link",
                        className="p-0",
                    ),
                    width="auto",
                    className="ms-auto"
                ),
            ], className="align-items-center g-0"),

            html.P(chart["subtitle"], className="mb-2", style={"fontSize": "0.85rem", "color": "#666"})
        ]),

        dcc.Loading(
            id=f"loading-{chart['id']}",
            type="circle",
            children=dcc.Graph(id=chart["id"], style={"height": "300px"})
        ),

        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.Div([
                        html.Div([
                            html.Span(
                                chart["title"],
                                style={
                                    "fontWeight": "bold",
                                    "color": "#333",
                                    "fontSize": "1.1rem",
                                    "marginRight": "0.75rem"
                                },
                            ),
                            html.Span(
                                chart["subtitle"],
                                style={
                                    "fontSize": "0.85rem",
                                    "color": "#666"
                                },
                            ),
                        ], style={"display": "flex", "alignItems": "center"}),

                        dbc.Button(
                            html.I(className="bi bi-x-lg"),
                            id={"type": "close-fullscreen", "id": chart["id"]},
                            color="link",
                            className="ms-auto",
                            style={"fontSize": "1.2rem"}
                        )
                    ],
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "width": "100%"}),
                    close_button=False
                ),
                dbc.ModalBody([
                    dcc.Graph(id=f"{chart['id']}-fullscreen", style={"height": "70vh"})
                ])
            ],
            id={"type": "chart-modal", "id": chart["id"]},
            is_open=False,
            size="xl",
            backdrop=False,
            scrollable=True,
        )
    ], className="border p-4 m-0 g-0", style={"minHeight": "420px"})


def create_standard_table_container(table):
    """Container for data tables with title, subtitle, and clean styling."""
    return html.Div([
        # Title + Tooltip
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Span(
                        table["title"] + " ",
                        style={
                            "fontWeight": "bold",
                            "color": "#333",
                            "fontSize": "1.1rem",
                            "fontFamily": "system-ui, sans-serif",
                        },
                    ),
                    html.I(
                        className="bi bi-info-circle-fill info-icon",
                        id=f"title-tooltip-{table['id']}",
                        style={"cursor": "pointer", "color": "#666"}
                    ),
                    dbc.Tooltip(
                        table.get("description", "No description available."),
                        target=f"title-tooltip-{table['id']}",
                        placement="right",
                        style={"maxWidth": "300px"},
                    ),
                ], width="auto")
            ], className="align-items-center g-1"),

            html.P(table["subtitle"], className="mb-2", style={
                "fontSize": "0.85rem",
                "color": "#666",
                "marginTop": "0.25rem",
                "fontFamily": "system-ui, sans-serif"
            }),
        ]),

        # Table with custom styling
        dcc.Loading(
            id=f"loading-{table['id']}",
            type="circle",
            children=html.Div(
                dash_table.DataTable(
                    id=table["id"],
                    style_cell={
                        "fontFamily": "system-ui, sans-serif",
                        "fontSize": "0.9rem",
                        "padding": "8px 12px",
                        "whiteSpace": "nowrap",
                        "textAlign": "left"
                    },
                    style_header={
                        "backgroundColor": "#f8f9fa",
                        "fontWeight": "bold",
                        "borderBottom": "1px solid #dee2e6"
                    },
                    style_table={
                        "overflowX": "auto"
                    },
                    style_data={
                        "borderBottom": "1px solid #eee"
                    }
                )
            )
        )
    ], className="border p-4 m-0 g-0")  

def build_chart_grid(chart_items):
    """
    Build the chart grid with a list of chart items.
    - Separation between columns
    """
    rows = []
    for i in range(0, len(chart_items), 2):
        row = dbc.Row([
            dbc.Col(
                create_standard_chart_container(item),
                xs=12, sm=12, md=6, lg=6, xl=6,
                style={"minHeight": "420px"})
            for item in chart_items[i:i+2]
        ], class_name="g-0 mt-0 me-0 ms-0")
        rows.append(row)

    return html.Div(rows, id="tutorial-charts-target")


# ===========================

# Emissions

def build_sidebar_emissions(controls):
    """
    Build the sidebar for the emissions dashboard.
    - Message box
    - Date range display (outside accordion)
    - Accordion with:
        - Date range slider
        - Vessel type checklist
    - Refresh button
    """
    accordion = dbc.Accordion([
        dbc.AccordionItem(
            [controls_emissions.build_date_range_slider(controls["date_range"])],
            title="Date Range",
        ),
        dbc.AccordionItem(
            [controls_emissions.build_vessel_type_checklist(controls["vessel_types"])],
            title="Vessel Type",
        ),
    ], id="tutorial-filters-target")
    return dbc.Col([
        controls_emissions.build_message_box(),
        controls_emissions.build_date_range_display(),
        accordion,
        html.Br(),
        controls_emissions.build_button_refresh_charts(),
    ], className="border p-3", xs=12, md=12, lg=2, width=2)


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
                "title": "Monthly Vessel Emissions",
                "subtitle": "TONNES CO2-eq",
                "description": "Monthly trend of total emissions (in tonnes of CO₂-equivalent) from all vessel types transiting the Panama Canal. This chart helps compare year-over-year changes and detect major shifts in environmental impact."
            },
            {
                "id": "emissions--chart--2",
                "title": "Total Emissions by Vessel Type", 
                "subtitle": "TONNES CO2-eq",
                "description": "Total emissions per vessel type over the selected period. See which vessel categories (like container ships or tankers) contribute the most to overall emissions.",
            },
            {
                "id": "emissions--chart--3",
                "title": "Emissions by Region", 
                "subtitle": "TONNES CO2-eq",
                "description": "Map showing the distribution of emissions across Panama. Darker areas indicate higher levels of recorded emissions in those regions."
            },
            {
                "id": "emissions--chart--4",
                "title": "Emissions by Type of Vessel", 
                "subtitle": "TONNES CO2-eq",
                "description": "Monthly emissions trends by vessel type. Useful for spotting seasonal changes or long-term patterns for specific vessel categories."
            },
        ])
        ], className="p-0", xs=12, md=12, lg=10, width=10)


def build_sidebar_waiting_times(controls):
    """
    Build the sidebar for the waiting times dashboard.
    - Message box
    - Date range display (outside accordion)
    - Accordion with:
        - Date range slider
        - Vessel type checklist
        - Stop area checklist
    - Refresh button
    """
    return dbc.Col([
        controls_time.build_message_box(),
        controls_time.build_date_range_display(),
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

    ], className="border p-3", xs=12, md=12, lg=2, width=2)


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
                "title": "Average Monthly Waiting Time", 
                "subtitle": "HOURS",
                "description": "Average waiting time per month before a vessel enters a stop area (calculated from anchoring out to anchoring in). This helps assess delays before service begins.",
            },
            {
                "id": "time--chart--2",
                "title": "Waiting Time by Stop Area", 
                "subtitle": "HOURS",
                "description": "Average number of hours vessels wait at each stop area. Identify locations with the longest delays before docking or service.",
            },
            {
                "id": "time--chart--3",
                "title": "Waiting Time by Vessel Type", 
                "subtitle": "HOURS",
                "description": "Average waiting time by vessel type. Some vessel types, like bulk carriers, tend to wait longer before receiving service.",
            
            },
            {
                "id": "time--chart--4",
                "title": "Waiting Time Trends by Vessel Type", 
                "subtitle": "HOURS",
                "description": "Monthly waiting time trends by vessel type. Helpful for tracking operational efficiency and identifying bottlenecks over time.",

            },
        ])
        ], xs=12, md=12, lg=10, width=10)


def build_sidebar_energy(controls):
    """
    Build the sidebar for the energy dashboard.
    - Message box
    - Date range display (outside accordion)
    - Accordion with:
        - Date range slider
        - Country before checklist
        - Country after checklist
    - Refresh button (reuse emissions refresh for now)
    """
    return dbc.Col([
        controls_energy.build_message_box(),
        controls_energy.build_date_range_display(),
        dbc.Accordion([
            dbc.AccordionItem(
                [controls_energy.build_date_range_slider(controls["date_range"])],
                title="Date Range"
            ),
            dbc.AccordionItem(
                [controls_energy.build_country_before_checklist(controls["country_before"])],
                title="Country Before"
            ),
            dbc.AccordionItem(
                [controls_energy.build_country_after_checklist(controls["country_after"])],
                title="Country After"
            )
        ]),
        html.Br(),
        controls_emissions.build_button_refresh_charts()
    ], className="border p-3", xs=12, md=12, lg=2, width=2)


def build_main_container_energy():
    return dbc.Col([
        build_chart_grid([
            {
                "id": "energy--chart--1",
                "title": "Total Weekly Energy Transported",
                "subtitle": "kWh",
                "description": "Total amount of energy (in kWh) transported along all routes. Highlights weekly variation in energy volumes."
            },
            {
                "id": "energy--chart--2",
                "title": "Energy by Country",
                "subtitle": "kWh",
                "controls": controls_energy.build_country_role_dropdown("energy--dropdown-chart2"),
                "description": "Energy transported by country. Shows which countries are major sources or destinations of energy."
            },
            {
                "id": "energy--chart--3",
                "title": "Global Energy Demand",
                "subtitle": "kWh",
                "controls": controls_energy.build_country_role_dropdown("energy--dropdown-chart3"),
                "description": "World map showing countries based on the energy they send out (origin) or receive (destination). Larger circles represent higher energy volumes."
            },
            {
                "id": "energy--chart--4",
                "title": "Energy Interchange Between Countries", 
                "subtitle": "kWh",
                "description": "Flow diagram showing energy exchanges between countries of origin and destination. Useful for identifying key trading partners in the energy network."
            },
        ])
        ], className="p-0", xs=12, md=12, lg=10, width=10)


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
                "title": "Average Monthly Service Time", 
                "subtitle": "HOURS",
                "description": "Average time vessels spend receiving services in stop areas (from stop time in to stop time out). Helps track operational efficiency over time.",
            },
            {
                "id": "time--chart--2",
                "title": "Service Time by Stop Area", 
                "subtitle": "HOURS",
                "description": "Average number of hours vessels spend receiving services in each stop area. Highlights areas with longer or shorter operation times.",
            },
            {
                "id": "time--chart--3",
                "title": "Service Time by Vessel Type", 
                "subtitle": "HOURS",
                "description": "Average service time per vessel type. Shows how long different types of vessels typically remain in service zones.",
            },
            {
                "id": "time--chart--4",
                "title": "Service Time Trends by Vessel Type", 
                "subtitle": "HOURS",
                "description": "Monthly trends of service time by vessel type. Useful to detect shifts in operational behavior or service efficiency.",
            },
        ])
        ], xs=12, md=12, lg=10, width=10)


def build_sidebar_explorer(controls):
    """Sidebar for the explorer tab."""
    return dbc.Col([
        controls_explorer.build_date_range_display(),
        controls_explorer.build_week_range_display(),
        dbc.Accordion([
            dbc.AccordionItem(
                [controls_explorer.build_source_dropdown(controls["sources"])],
                title="Source"
            ),
            dbc.AccordionItem(
                [
                    controls_explorer.build_date_range_slider(controls["date_range"]),
                    controls_explorer.build_week_range_slider(controls["week_range"]),
                ],
                title="Date Range"
            )
        ]),
        html.Br(),
        controls_explorer.build_download_button(),
        controls_explorer.build_download_modal(),
        dcc.Download(id="explorer--download")
    ], className="border p-3", xs=12, md=12, lg=2, width=2)


def build_main_container_explorer():
    """Main container for the explorer tab."""
    return dbc.Col([
        dbc.Row([
            dbc.Col(
                create_standard_chart_container({
                    "id": "explorer--chart",
                    "title": "Value Over Time",
                    "subtitle": "",
                }),
                xs=12, sm=12, md=6, lg=6, xl=6,
            ),
            dbc.Col(
                create_standard_table_container({
                    "id": "explorer--table",
                    "title": "Sample Data",
                    "subtitle": "First five rows",
                }),
                xs=12, sm=12, md=6, lg=6, xl=6,
            ),
        ], class_name="g-0 mt-0 me-0 ms-0"),
    ], className="p-0", xs=12, md=12, lg=10, width=10)



# ============================



def build_tutorial_components():
    return html.Div([
        dcc.Store(id="tutorial-store", storage_type="local"),
        dbc.Modal([
            dbc.ModalHeader("Welcome to the Dashboard"),
            dbc.ModalBody(
                "Use the filters and charts to explore the data.",
                style={"backgroundColor": "#f8f9fa"},
            ),
            dbc.ModalFooter(
                dbc.Button("Start", id="btn-tutorial-start", color="primary")
            ),
        ], id="modal-welcome", backdrop="static", is_open=False),
        dbc.Popover([
            dbc.PopoverHeader("Filters"),
            dbc.PopoverBody(
                [
                    html.P("You can move the filters to change the data."),
                    dbc.Button("Done", id="btn-tutorial-next-filters", size="sm", color="primary", className="mt-2"),
                ],
                style={"backgroundColor": "#f8f9fa"},
            ),
        ], id="popover-filters", target="tutorial-filters-target", placement="right", is_open=False),
    ])



def build_main_layout_content():
    return dbc.Container([
        dcc.Store(id="chart-tabs-store", data="emissions"),
        dcc.Store(id="energy--role-chart2", data="country_before"),
        dcc.Store(id="energy--role-chart3", data="country_before"),
        dcc.Interval(id='footer-delay', interval=2000, n_intervals=0),
        dcc.Interval(id="initial-delay", interval=500, n_intervals=0, max_intervals=1),
        build_tutorial_components(),
        html.Div(id="main-content"),
        html.Div(id="tab-content"),
        build_footer(),
    ], className="g-0 ps-4 pe-4 pt-2 pb-4", fluid=True)


def build_main_layout():
    return dbc.Container([
        build_header(),
        dcc.Store(id="chart-tabs-store", data="emissions"),
        dcc.Store(id="energy--role-chart2", data="country_before"),
        dcc.Store(id="energy--role-chart3", data="country_before"),
        dcc.Interval(id='footer-delay', interval=2000, n_intervals=0),
        build_tutorial_components(),
        html.Div(id="tab-content"),
        build_footer(),
    ], className="g-0 p-4", fluid=True)
