from dash import html, dcc
import dash_bootstrap_components as dbc


def build_message_box():
    """
    Build a message box to inform the user that no data is available
    """
    return dbc.Modal(
            [
                dbc.ModalHeader("No Data Available"),
                dbc.ModalBody("Please select at least one option from each category to view the energy data."),
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
    ])

def build_date_range_display():
    """Build the date range display with title outside the accordion."""
    return html.Div([
        html.H6("Selected Week Range", className="mb-2", style={"fontWeight": "bold", "color": "#333"}),
        html.Div(id="energy--range-label", className="text-center p-1", 
                style={"backgroundColor": "#f8f9fa", "borderRadius": "4px", "border": "1px solid #dee2e6"})
    ], className="mb-3")

def build_country_before_checklist(country_before):
    """Build the origin-country checklist.

    Parameters
    ----------
    country_before : list[str]
        Origin countries to display.

    Returns
    -------
    html.Div
        Checklist component wrapped in a div.
    """
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
            placeholder="Search origin country",
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
    """Build the destination-country checklist.

    Parameters
    ----------
    country_after : list[str]
        Destination countries to display.

    Returns
    -------
    html.Div
        Checklist component wrapped in a div.
    """
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
            placeholder="Search destination country",
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

def build_country_role_dropdown(dropdown_id):
    """Dropdown to choose country role for energy charts."""
    options = [
        {"label": "Origin", "value": "country_before"},
        {"label": "Destination", "value": "country_after"},
    ]
    return dcc.Dropdown(
        id=dropdown_id,
        options=options,
        value="country_before",
        clearable=False,
        style={"width": "8rem"},
    )
