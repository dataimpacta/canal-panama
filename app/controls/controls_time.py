"""Build the emissiosn controls panel for the dashboard."""

# controls/emissions.py
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
            id="time--modal--no-data",
            is_open=False,
        )

def build_date_range_slider(date_range):
    """Build dropdowns to select a start and end date."""

    def _fmt(ym):
        ym = str(ym)
        return f"{ym[:4]}-{ym[4:]}"

    options = [
        {"label": _fmt(ym), "value": idx}
        for idx, ym in enumerate(date_range["unique_year_months"])
    ]

    start_dropdown = dcc.Dropdown(
        id="time--start-date",
        options=options,
        value=date_range["min_index"],
        clearable=False,
        className="mb-2",
    )

    end_dropdown = dcc.Dropdown(
        id="time--end-date",
        options=options,
        value=date_range["max_index"],
        clearable=False,
    )

    return html.Div([
        start_dropdown,
        end_dropdown,
        html.Div(id="time--range-label", className="text-center mt-2"),
    ])


def build_vessel_type_checklist(vessel_types):
    return html.Div([
        html.Div([
            html.Span(
                "Select All",
                id="time--btn--vessel-select",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer", "marginRight": "0.24em"}
            ),
            html.Span("•", style={"color": "#999", "fontSize": "0.8rem", "marginRight": "0.2rem"}),
            html.Span(
                "Clear",
                id="time--btn--vessel-clear",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer"}
            )
        ], style={"marginBottom": "0.5rem"}),

        dcc.Input(
            id="time--input--vessel-search",
            type="text",
            placeholder="Search vessel type",
            debounce=True,
            className="form-control mb-2"
        ),

        html.Div(
            dbc.Checklist(
                id="time--checklist--vessel",
                options=[{"label": v, "value": v} for v in vessel_types],
                value=list(vessel_types),
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


def build_stop_area_checklist(vessel_types):
    return html.Div([
        html.Div([
            html.Span(
                "Select All",
                id="time--btn--stop-area-select",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer", "marginRight": "0.24em"}
            ),
            html.Span("•", style={"color": "#999", "fontSize": "0.8rem", "marginRight": "0.2rem"}),
            html.Span(
                "Clear",
                id="time--btn--stop-area-clear",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer"}
            )
        ], style={"marginBottom": "0.5rem"}),

        html.Div(
            dbc.Checklist(
                id="time--checklist--stop-area",
                options=[{"label": v, "value": v} for v in vessel_types],
                value=list(vessel_types),
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