import dash_bootstrap_components as dbc
from dash import html, dcc


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
            dcc.Tab(label="Energy", value="energy"),
            dcc.Tab(label="Explorer", value="explorer")
        ]), width=12)
    ], className="")


def build_sidebar(unique_year_months, min_index, max_index, vessel_types):
    return dbc.Col([
        dbc.Modal(
            [
                dbc.ModalHeader("No Data Available"),
                dbc.ModalBody("Please select at least one vessel type to view the emissions data."),
            ],
            id="no-data-modal",
            is_open=False,
        ),
        dbc.Accordion([
            dbc.AccordionItem(
                [
                    dcc.RangeSlider(
                        id="filter-date-range",
                        min=min_index, max=max_index,
                        value=[min_index, max_index],
                        marks={min_index: str(unique_year_months[0]), max_index: str(unique_year_months[-1])},
                        step=1, allowCross=False
                    )
                ],
                title="Date Range"
            ),
            dbc.AccordionItem(
                [
                    html.Div([
                        html.Span(
                            "Select All",
                            id="btn-select-all",
                            n_clicks=0,
                            style={"color": "#007bff", "cursor": "pointer", "marginRight": "0.24em"}
                        ),
                        html.Span(
                            "•",
                            style={"color": "#999", "fontSize": "0.8rem", "marginRight": "0.2rem"}
                        ),
                        html.Span(
                            "Clear",
                            id="btn-clear-all",
                            n_clicks=0,
                            style={"color": "#007bff", "cursor": "pointer"}
                        )
                    ], style={"marginBottom": "0.5rem"}),

                    dbc.Checklist(
                        id="filter-emissions-type",
                        options=[{"label": v, "value": v} for v in vessel_types],
                        value=list(vessel_types),
                        inline=True
                    )
                ],
                title="Vessel Type"
            )
        ]),
        html.Br(),
        dbc.Button("Refresh Charts", id="apply-filters-btn", n_clicks=0, color="primary")
    ], className="border rounded p-3", xs=12, md=12, lg=2, width=2)


def build_kpi_grid(kpi_cards, items_per_row=2):
    rows = []
    for i in range(0, len(kpi_cards), items_per_row):
        row = dbc.Row([
            dcc.Loading(type="circle", children=dbc.Col(card, xs=12, sm=6, md=6, lg=int(12/items_per_row), id="kpi-1"))
            for card in kpi_cards[i:i+items_per_row]
        ], class_name="g-2 mt-2 me-2 ms-2")
        rows.append(row)
    return html.Div(rows)


def create_chart_container(graph_id, figure, config=None, title="Total Emissions", subtitle="Tonnes"):
    return html.Div([
        html.Div([
            html.H5(title, className="mb-1", style={"fontWeight": "bold", "color": "#333"}),
            html.P(subtitle, className="mb-2", style={"fontSize": "0.85rem", "color": "#666"})
        ]),
        dcc.Loading(
            id=f"loading-{graph_id}",
            type="circle",
            children=dcc.Graph(
                id=graph_id,
                figure=figure,
                config=config or {}
            )
        )
    ],
    className="border rounded p-3 m-0 g-0")


def build_chart_grid(chart_items):
    rows = []
    for i in range(0, len(chart_items), 2):
        row = html.Div(dbc.Row([
            dbc.Col(
                create_chart_container(item["id"], item["fig"], item.get("config"), title=item.get("title"), subtitle=item.get("subtitle")),
                className="", # gaps between columns
                xs=12, sm=12, md=6, lg=6, xl=6)
            for item in chart_items[i:i+2]
        ], class_name="g-2 mt-0 me-2 ms-2"))
        rows.append(row)

    return html.Div(rows)


def build_dashboard_layout(
    kpi_cards,
    chart_1,
    chart_2,
    chart_3,
    chart_4,
    min_index,
    max_index,
    unique_year_months,
    master_emissions_vessel_types
):
    

    return dbc.Container([

        # Header
        build_header(),  
        build_navigation_bar(),  
        
        # Main Content
        dbc.Row([

            # =============== Sidebar ===============
            build_sidebar(unique_year_months, min_index, max_index, master_emissions_vessel_types),

            # =============== CHART ZONE ===============
            dbc.Col([
                build_kpi_grid(kpi_cards),  # ✅ Add KPI grid here
                build_chart_grid([
                    chart_1,
                    chart_2,
                    chart_3,
                    chart_4,
                ])
            ], xs=12, md=12, lg=10, width=10)
        ], className="g-0"),

    ],className="g-0 p-4", fluid=True)