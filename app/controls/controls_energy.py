from dash import html, dcc
import dash_bootstrap_components as dbc


def build_message_box():
    """
    Build a message box to inform the user that no data is available
    """
    return dbc.Modal(
            [
                dbc.ModalHeader("No Data Available"),
                dbc.ModalBody("Please select at least one vessel type to view the emissions data."),
            ],
            id="energy--modal--no-data",
            is_open=False,
        )

def build_date_range_slider(date_range):
    """Build dropdowns to select a start and end week."""
    def _fmt(yw):
        yw = str(yw)
        return f"{yw[:4]}-W{yw[4:]}"

    options = [
        {"label": _fmt(yw), "value": idx}
        for idx, yw in enumerate(date_range["unique_year_week"])
    ]

    start_dropdown = dcc.Dropdown(
        id="energy--start-date",
        options=options,
        value=date_range["min_index"],
        clearable=False,
        className="mb-2",
    )

    end_dropdown = dcc.Dropdown(
        id="energy--end-date",
        options=options,
        value=date_range["max_index"],
        clearable=False,
    )

    return html.Div([
        start_dropdown,
        end_dropdown,
        html.Div(id="energy--range-label", className="text-center mt-2"),
    ])

def build_country_before_checklist(country_before):
    return html.Div([
        html.Div([
            html.Span(
                "Select All",
                id="energy--btn--country-before-select",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer", "marginRight": "0.24em"}
            ),
            html.Span("•", style={"color": "#999", "fontSize": "0.8rem", "marginRight": "0.2rem"}),
            html.Span(
                "Clear",
                id="energy--btn--country-before-clear",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer"}
            )
        ], style={"marginBottom": "0.5rem"}),

        dcc.Input(
            id="energy--input--country-before-search",
            type="text",
            placeholder="Search country before",
            debounce=False,
            className="form-control mb-2"
        ),

        html.Div(
            dbc.Checklist(
                id="energy--checklist--country-before",
                options=[{"label": v, "value": v} for v in country_before],
                value=list(country_before),
                inline=False,
                switch=False
            ),
            style={
                "maxHeight": "200px",
                "overflowY": "scroll",
                "overflowX": "hidden",
                "border": "1px solid #dee2e6",
                "padding": "0.5rem",
                "borderRadius": "4px",
                "backgroundColor": "#f9f9f9"
            }
        )
    ])

def build_country_after_checklist(country_after):
    return html.Div([
        html.Div([
            html.Span(
                "Select All",
                id="energy--btn--country-after-select",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer", "marginRight": "0.24em"}
            ),
            html.Span("•", style={"color": "#999", "fontSize": "0.8rem", "marginRight": "0.2rem"}),
            html.Span(
                "Clear",
                id="energy--btn--country-after-clear",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer"}
            )
        ], style={"marginBottom": "0.5rem"}),

        dcc.Input(
            id="energy--input--country-after-search",
            type="text",
            placeholder="Search country after",
            debounce=False,
            className="form-control mb-2"
        ),

        html.Div(
            dbc.Checklist(
                id="energy--checklist--country-after",
                options=[{"label": v, "value": v} for v in country_after],
                value=list(country_after),
                inline=False,
                switch=False
            ),
            style={
                "maxHeight": "200px",
                "overflowY": "scroll",
                "overflowX": "hidden",
                "border": "1px solid #dee2e6",
                "padding": "0.5rem",
                "borderRadius": "4px",
                "backgroundColor": "#f9f9f9"
            }
        )
    ])
