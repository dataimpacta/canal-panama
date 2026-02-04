# pylint: disable=import-error
"""
Layout of the dashboard.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

from controls import controls_explorer
from controls import controls_emissions
from controls import controls_time
from controls import controls_energy


def build_header():
    """
    Build the header of the dashboard.
    """
    return html.Div([
        # Logo only visible on small screens (above the title)
        html.Div([
            html.Img(
                src="/assets/Financing_Logo.webp",
                alt="SENACYT Logo",
                width="275px",
                height="60px",
            )
        ], className="d-flex d-md-none mb-3"),  # Show on xs–md only

        # Main title + large-screen logo
        dbc.Row([
            # Title column
            dbc.Col([
                html.Div([
                    html.H1(
                        "SEAnalytics",
                        style={
                            "margin": 0,
                            "fontSize": "2.75rem",
                            "fontWeight": 700,
                            "fontFamily": "Arial, Helvetica, sans-serif",
                        }
                    ),
                    html.H4(
                        "Shipping Energy Analytics",
                        style={
                            "margin": 0,
                            "fontWeight": 500,
                            "fontSize": "1.5rem",
                            "fontFamily": "Arial, Helvetica, sans-serif",
                        }
                    ),
                ])
            ], xs=12, md=10, lg=10),

            # Logo column (only visible on md and up)
            dbc.Col([
                html.Div([
                    html.Img(
                        src="/assets/Financing_Logo.webp",
                        alt="SENACYT Logo",
                        width="320px",
                        height="70px",
                    )
                ],
                    className="d-none d-md-flex",
                    style={
                        "justifyContent": "flex-end",
                        "alignItems": "center",
                        "height": "100%",
                    }
                )
            ], md=2),
        ], className="dashboard-header pb-4"),
        # Country row
        dbc.Row([
            dbc.Col([
                html.Div(
                    "Country: Panama",
                    style={
                        "fontSize": "1rem",
                        "fontWeight": 500,
                        "fontFamily": "Arial, Helvetica, sans-serif",
                        "paddingLeft": "4px",
                    },
                )
            ], width="auto"),
        ], className="pb-4"),
    ], className="ps-4 pe-4 pt-4")

    
def build_footer():
    """
    Build the footer of the dashboard.
    """
    return dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Small([
                "This dashboard was developed as part of the project ",
                html.Span(
                    "\"Green Shipping Corridors in the Panama Canal under Climate Risk\"",
                    style={"fontWeight": "bold"}
                ),
                ", partly sponsored by SENACYT under project number 060/2024 "
                "and with AIS data provided by the ",
                html.A(
                    "UN Global Platform",
                    href="https://unstats.un.org/bigdata/un-global-platform.cshtml",
                    target="_blank",
                    style={"textDecoration": "underline"}
                ),
                ".",
                html.Br(),
                html.Br(),
                "This project is a spin-off and also kindly supported by the ",
                html.A(
                    "SFI Climate Futures of Norway.",
                    href="https://www.climatefutures.no/en/home/",
                    target="_blank",
                    style={"textDecoration": "underline"}
                ),
                html.Br(),
                html.Br(),
                "The results and information presented herein are provided for informational "
                "purposes only and shall not be construed as assigning, implying, or establishing "
                "any liability, responsibility, or obligation on the part of any participant "
                "(individual or institutional). No warranties, express or implied, are made "
                "regarding the completeness or accuracy of this information, and it shall not be "
                "used as the basis for any legal, regulatory, or disciplinary action."
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
    """
    Build the about us section of the dashboard.
    """
    return dbc.Container([
        html.Br(),
        html.P(
            "This dashboard feeds from the methods of the study "
            html.A(
                "Greenhouse Gas Mitigation at Maritime Chokepoints",
                href="https://doi.org/10.1016/j.trd.2023.103694",
                target="_blank",
                style={"textDecoration": "underline"}
                    )
                ])
        ),
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
                    "The National Secretariat of Science, Technology and Innovation (SENACYT) "
                    "of Panama supports scientific research and technological development. "
                    "SENACYT has been instrumental in providing resources and support for "
                    "projects aimed at sustainable development, including initiatives in maritime "
                    "emissions reduction."
                )
            ], xs=12, md=12, lg=9, width=9)
        ], className="mb-4 g-4"),

        html.Br(),

                dbc.Row([
            dbc.Col([
                html.Img(
                    src="/assets/climate_futures.png",
                    alt="SENACYT",
                    style={"width": "100%", "maxWidth": "200px"}
                )
            ], xs=12, md=12, lg=3, width=3),
            dbc.Col([
                html.H5("SFI Climate Futures"),
                html.P(
                    "Climate Futures is a Centre for Research-based Innovation (abbreviated SFI in Norwegian)," 
                    "funded by the Research Council of Norway, and launched on October 1, 2020. Their goal is to"
                    "generate long-term cooperation between companies, public organizations and research groups"
                    "across sectors and disciplines to tackle one of the most urgent challenges of our time."
                    "The Green Corridors project works in close integration and within the goals of the Smart Shipping"
                    "node at the Climate Futures project."
                )
            ], xs=12, md=12, lg=9, width=9)
        ], className="mb-4 g-4"),

        html.Br(),

        dbc.Row([
            dbc.Col([
                html.Img(
                    src="/assets/MTCC-logo.png",
                    alt="MTCC Latin America",
                    style={"width": "100%", "maxWidth": "200px"}
                )
            ], xs=12, md=12, lg=3, width=3),
            dbc.Col([
                html.H5("MTCC Latin America"),
                html.P(
                    "The Maritime Technology Cooperation Centre for Latin America (MTCC Latin America) "
                    "is one of five Cooperation centres coordinated by the International Maritime Organization (IMO)"
                    "and operates within the Universidad Marítima Internacional de Panama (UMIP). "
                    " Strategically located near the Port of Balboa in Panama City, and the"
                    "Gulf of Panama entrance of the Panama Canal, MTCC Latin America focuses on all"
                    "aspects of the maritime sector including shipping, maritime"
                    "infrastructure, services, and environmental protection. The center plays a "
                    "crucial role in promoting sustainable maritime practices and technological "
                    "cooperation across the Latin American region."
                )
            ], xs=12, md=12, lg=9, width=9)
        ], className="mb-4 g-4"),

        html.Br(),

        dbc.Row([
            dbc.Col([
                html.Img(
                    src="/assets/data_impacta_logo.jpg",
                    alt="Data Impacta",
                    style={"width": "100%", "maxWidth": "200px"}
                )
            ], xs=12, md=12, lg=3, width=3),
            dbc.Col([
                html.H5("Data Impacta"),
                html.P(
                    "Data Impacta is a data-driven solutions company that develops tools to help "
                    "organizations measure and monitor problems for better decision making. "
                    "They create solutions that contribute to generating positive impact in areas "
                    "such as health, economy, environment, energy, equity, and innovation. "
                    "This platform was developed by their team to visualize maritime emissions "
                    "and performance indicators, supporting sustainable shipping practices and "
                    "informed decision-making."
                ),
                html.P([
                    "Visit their website: ",
                    html.A(
                        "dataimpacta.com",
                        href="https://dataimpacta.com/en/",
                        target="_blank",
                        style={"textDecoration": "underline"}
                    )
                ])
            ], xs=12, md=12, lg=9, width=9)
        ], className="mb-4 g-4"),

        html.Br(),

        html.H4("Collaboration with", style={
            "fontWeight": "bold",
            "color": "#333",
            "marginTop": "2rem",
            "marginBottom": "1rem",
            "fontFamily": "Arial, Helvetica, sans-serif"
        }),

        html.P([
            "This platofrm was developed in collaboration with ",
            html.Strong("Norwegian School of Economics (NHH)"),
            ", ",
            html.Strong("Universidad Tecnológica de Panamá"),
            ", ",
            html.Strong("Universidad Marítima Internacional de Panamá"),
            ", ",
            html.Strong("Liverpool John Moores University"),
            ", ",
            html.Strong("Georgia Tech Panamá"),
            ", ",
            html.Strong("Autoridad del Canal de Panamá"),
            ", and ",
            html.Strong("UN Big Data Group"),
            ". We extend our gratitude to these institutions for their "
            "valuable contributions and support."
        ], style={
            "fontSize": "1rem",
            "lineHeight": "1.6",
            "fontFamily": "Arial, Helvetica, sans-serif"
        }),

        html.Br()
    ], className="")

def build_navigation_bar(active_tab="emissions"):
    """
    Build the navigation bar of the dashboard.
    """
    return dbc.Nav(
        [
            dbc.NavItem(
                dbc.NavLink(
                    "Emissions", href="#", id="tab-emissions", active=active_tab == "emissions"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    "Waiting Time", href="#", id="tab-waiting", active=active_tab == "waiting"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    "Service Time", href="#", id="tab-service", active=(active_tab == "service")
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    "Energy", href="#", id="tab-energy", active=active_tab == "energy"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    "Explorer", href="#", id="tab-explorer", active=active_tab == "explorer"
                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    "About Us", href="#", id="tab-about", active=active_tab == "about"
                )
            ),
        ],
        pills=True,
        vertical=False,
        className="mb-3"
    )

def build_tutorial_components():
    """
    Build the tutorial components of the dashboard.
    """
    return html.Div([
        dcc.Store(id="tutorial-store", storage_type="local"),
        dbc.Modal([
            dbc.ModalHeader("Welcome to SEAnalytics"),
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
                    dbc.Button("Done", id="btn-tutorial-next-filters",
                        size="sm", color="primary", className="mt-2"),
                ],
                style={"backgroundColor": "#f8f9fa"},
            ),
        ], id="popover-filters", target="tutorial-filters-target",
        placement="right", is_open=False),
    ])

# ============================
# Funcitons for the charts and KPIs

def create_standard_kpi_container(kpi_id):
    """
    Create the standard HTML DIV for the KPIs with a title, subtitle, 
    and tooltip on the title.
    """
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
    """
    Build the KPI grid with a list of KPI cards.
    """
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
    Create the standard HTML DIV for the charts with a title, subtitle, 
    and tooltip on the title.
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

            dcc.Markdown(
                chart["subtitle"], className="mb-2",
                style={"fontSize": "0.85rem", "color": "#666"},
                dangerously_allow_html=True
            )
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
                            dcc.Markdown(
                                chart["subtitle"],
                                style={
                                    "fontSize": "0.85rem",
                                    "color": "#666"
                                },
                                dangerously_allow_html=True
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
                    style={
                        "display": "flex", "justifyContent": "space-between", 
                        "alignItems": "center", "width": "100%"
                    }),
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
        ),
        # Data Dictionary Download Link
        html.Div([
            html.Hr(style={"margin": "20px 0 15px 0"}),
            html.Div([
                html.I(className="bi bi-file-text me-2", style={"color": "#666"}),
                html.A(
                    "Download Data Dictionary",
                    href="/download-data-dictionary",
                    target="_blank",
                    style={
                        "color": "#007bff",
                        "textDecoration": "none",
                        "fontSize": "0.9rem",
                        "fontFamily": "system-ui, sans-serif"
                    }
                ),
                html.I(className="bi bi-box-arrow-up-right ms-1",
                style={"fontSize": "0.8rem", "color": "#666"})
            ], style={"display": "flex", "alignItems": "center"})
        ], style={"marginTop": "10px"})
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
                "title": "Total Emissions in Panama’s Territorial Sea",
                "subtitle": "TONNES"
            },
        ]),
        build_chart_grid([
            {
                "id": "emissions--chart--1",
                "title": "Monthly Vessel Emissions",
                "subtitle": "TONNES CO<sub>2</sub><sub>-eq</sub>",
                "description": (
                    "Monthly total emissions (in tonnes of CO2-equivalent) from all vessels "
                    "within the country of reference territorial waters. This chart helps in "
                    "comparing year-over-year changes and signals major shifts in environmental "
                    "impact."
                )
            },
            {
                "id": "emissions--chart--2",
                "title": "Total Emissions by Vessel Type", 
                "subtitle": "TONNES CO<sub>2</sub><sub>-eq</sub>",
                "description": "Total emissions per vessel type over the selected period.",
            },
            {
                "id": "emissions--chart--3",
                "title": "Emissions by Region", 
                "subtitle": "TONNES CO<sub>2</sub><sub>-eq</sub>",
                "description": (
                    "Map showing the geographical distribution of emissions across Panama "
                    "territorial waters. Darker areas indicate hot spots emissions."
                )
            },
            {
                "id": "emissions--chart--4",
                "title": "Emissions by Type of Vessel", 
                "subtitle": "TONNES CO<sub>2</sub><sub>-eq</sub>",
                "description": (
                    "Monthly emissions by vessel type. Useful for spotting seasonal "
                    "changes or long-term patterns for specific vessel categories."
                )
            },
        ])
        ], className="p-0", xs=12, md=12, lg=10, width=10)


# ===========================
# Waiting Times

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
        controls_time.build_button_refresh_charts()

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
                "description": (
                    "Average waiting time (in hours) per month before a vessel enters an "
                    "operations area (i.e. ports or the Panama Canal) (estimated from the "
                    "difference of vessels´ timestamp for anchoring in and anchoring out "
                    "before a call). This helps assess delays before service begins."
                )
            },
            {
                "id": "time--chart--2",
                "title": "Waiting Time by Stop Area", 
                "subtitle": "HOURS",
                "description": "Average number of hours vessels wait before a port call.",
            },
            {
                "id": "time--chart--3",
                "title": "Waiting Time by Vessel Type", 
                "subtitle": "HOURS",
                "description": (
                    "Average waiting time by vessel type. Some vessel types, "
                    "like bulk carriers, tend to wait longer before a port call."
                )
            },
            {
                "id": "time--chart--4",
                "title": "Waiting Time Series by Vessel Type", 
                "subtitle": "HOURS",
                "description": (
                    "Monthly waiting time series by vessel type. Helpful for "
                    "tracking operational efficiency over time."
                )
            },
        ])
        ], xs=12, md=12, lg=10, width=10)

def build_main_container_service_times():
    """
    Here we only have statick content, with the tags
    - KPI grid
    - Chart grid
    """
    return dbc.Col([
        build_chart_grid([
            {
                "id": "time--chart--1",
                "title": "Average Monthly Service Time", 
                "subtitle": "HOURS",
                "description": (
                    "Average time (in hours) that vessels spend being served at "
                    "ports. This is estimated from the difference between the "
                    "timestamps of a vessel entering and leaving a port polygon. "
                    "It provides an indicator for tracking operational efficiency "
                    "over time."
                )
            },
            {
                "id": "time--chart--2",
                "title": "Service Time by Stop Area", 
                "subtitle": "HOURS",
                "description": (
                    "Average time (in hours) vessels spend being served at ports. "
                    "The graph is segmented by ports, highlighting areas with longer "
                    "or shorter operation times."
                )
            },
            {
                "id": "time--chart--3",
                "title": "Service Time by Vessel Typel", 
                "subtitle": "HOURS",
                "description": (
                    "Average service time per vessel type. Shows how long different "
                    "types of vessels typically remain in service zones."
                )
            },
            {
                "id": "time--chart--4",
                "title": "Service Time Series by Vessel Type", 
                "subtitle": "HOURS",
                "description": (
                    "Monthly time series of service time by vessel type. Useful to "
                    "detect shifts in operational behavior or service efficiency."
                )
            },
        ])
        ], xs=12, md=12, lg=10, width=10)

# ===========================
# Energy

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
                title="Origin Country"
            ),
            dbc.AccordionItem(
                [controls_energy.build_country_after_checklist(controls["country_after"])],
                title="Destination Country"
            )
        ]),
        html.Br(),
        controls_emissions.build_button_refresh_charts()
    ], className="border p-3", xs=12, md=12, lg=2, width=2)

def build_main_container_energy():
    """
    Here we only have statick content, with the tags
    - KPI grid
    - Chart grid
    """
    return dbc.Col([
        build_chart_grid([
            {
                "id": "energy--chart--1",
                "title": "Total Weekly Energy Demand",
                "subtitle": "kWh",
                "description": (
                    "Total amount of energy (in kWh) demand of vessels along all routes that "
                    "are connected with and by a country of reference. For instance, "
                    "if Panama is the country of reference, then the energy consumed by "
                    "vessels calling to a from Panama are summarized in here. Highlights "
                    "weekly variation in energy volumes."
                )
                },
            {
                "id": "energy--chart--2",
                "title": "Energy Demand of Vessels via Panama",
                "subtitle": "kWh",
                "controls": controls_energy.build_country_role_dropdown("energy--dropdown-chart2"),
                "description": (
                    "Energy demand of vessels by country that connects with the country of reference. "
                    "Shows which routes are major energy consumers and touches upon the country "
                    "of reference. This information signals candidates for Green Maritime "
                    "Corridors."
                )
            },
            {
                "id": "energy--chart--3",
                "title": "Energy Demand by Vessels via Panama",
                "subtitle": "kWh",
                "controls": controls_energy.build_country_role_dropdown("energy--dropdown-chart3"),
                "description": (
                    "World map showing the origin and destination countries of routes connected "
                    "by the country of reference, along with the associated energy demand. "
                    "Circles represent energy volumes, with larger circles indicating higher "
                    "amounts exported (origins) or imported (destinations)."
                )
            },
            {
                "id": "energy--chart--4",
                "title": "Energy Interchange Between Countries via Panama", 
                "subtitle": "kWh",
                "description": (
                    "Flow diagram showing energy exchanges between countries of origin and "
                    "destination. Useful for identifying key trading partners in the energy "
                    "demand network."
                )
            },
        ])
        ], className="p-0", xs=12, md=12, lg=10, width=10)


# ===========================
# Explorer

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
                    "description": (
                        "Interactive chart showing the selected metric over time. Choose different "
                        "sources (emissions, waiting time, service time, or energy) to explore "
                        "various aspects of maritime data. The chart displays aggregated values "
                        "based on your selected date range and source."
                    )
                }),
                xs=12, sm=12, md=6, lg=6, xl=6,
            ),
            dbc.Col(
                create_standard_table_container({
                    "id": "explorer--table",
                    "title": "Sample Data",
                    "subtitle": "First rows",
                    "description": (
                        "Sample data table showing the first rows of the filtered dataset. "
                        "This table displays all available fields for the selected source, "
                        "allowing you to explore the data structure and available columns. "
                        "Use the download button to export the complete filtered dataset."
                    )
                }),
                xs=12, sm=12, md=6, lg=6, xl=6,
            ),
        ], class_name="g-0 mt-0 me-0 ms-0"),
    ], className="p-0", xs=12, md=12, lg=10, width=10)


# ============================
# Main layout content

def build_main_layout_content():
    """
    Main layout of the dashboard.
    """
    return dbc.Container([
        dcc.Location(id='url', refresh=False),  # URL routing component
        dcc.Store(id="chart-tabs-store", data="emissions"),
        dcc.Store(id="energy--role-chart2", data="country_before"),
        dcc.Store(id="energy--role-chart3", data="country_before"),
        dcc.Interval(id='footer-delay', interval=3000, n_intervals=0),
        dcc.Interval(id="initial-delay", interval=3000, n_intervals=0, max_intervals=1),
        build_tutorial_components(),
        # Navigation bar - always available
        html.Div(id="navigation-bar", children=build_navigation_bar()),
        html.Div(id="main-content"),
        html.Div(id="tab-content"),
        build_footer(),
    ], className="g-0 ps-4 pe-4 pt-2 pb-4", fluid=True)
