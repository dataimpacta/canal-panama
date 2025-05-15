import dash_bootstrap_components as dbc
from dash import html, dcc


def build_header():
    return dbc.Row([
        dbc.Col([
            html.H1("Panama Maritime Statistics"),
            html.H4("Efficiency and Sustainability Indicators")
        ])
    ], className="dashboard-header pb-4")

def build_sidebar(unique_year_months, min_index, max_index, vessel_types):
    return dbc.Col([
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
                    dbc.Label("Select Vessel Types"),
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
        dbc.Button("Apply Filters", id="apply-filters-btn", n_clicks=0, color="primary")
    ], className="border p-3", xs=12, md=12, lg=2, width=2)

def build_kpi():
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
    ], className="dashboard-navigation-bar")

def create_chart_container(graph_id, figure, config=None):
    return html.Div(
        dcc.Loading(
            id=f"loading-{graph_id}",
            type="circle",
            children=dcc.Graph(
                id=graph_id,
                figure=figure,
                config=config or {}
            )
        ),
        className="border bg-light p-2"
    )

def build_chart_grid(chart_items):
    rows = []
    for i in range(0, len(chart_items), 2):
        row = dbc.Row([
            dbc.Col(
                create_chart_container(item["id"], item["fig"], item.get("config")),
                className="", 
                xs=12, sm=12, md=6, lg=6, xl=6)
            for item in chart_items[i:i+2]
        ], class_name="border bg-light g-1 p-0 m-0")
        rows.append(row)

    return dbc.Col(rows, className="container g-0", xs=12, md=12, lg=10, width=10)

def build_dashboard_layout(
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
            
            build_chart_grid([
                chart_1,
                chart_2,
                chart_3,
                chart_4,
            ])

        ], className="g-0",),

    ],className="g-0 p-4", fluid=True)