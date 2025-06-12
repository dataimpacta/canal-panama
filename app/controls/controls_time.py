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
    """
    Build a date range slider for the emissions dashboard.
    Args:
        date_range (dict): A dictionary containing the min and max indices
                           for the date range slider, and a list of unique
                           year-month strings.

    Returns:
        dcc.RangeSlider: A Dash RangeSlider component for selecting a date range.
    """
    def _fmt(ym):
        ym = str(ym)
        return f"{ym[:4]}-{ym[4:]}"

    marks = {i: "" for i in range(date_range["min_index"], date_range["max_index"] + 1)}
    marks[date_range["min_index"]] = _fmt(date_range["unique_year_months"][0])
    marks[date_range["max_index"]] = _fmt(date_range["unique_year_months"][-1])

    slider = dcc.RangeSlider(
        id="time--range--date",
        min=date_range["min_index"],
        max=date_range["max_index"],
        value=[date_range["min_index"], date_range["max_index"]],
        marks=marks,
        step=1,
        allowCross=False,
    )

    return html.Div([
        slider,
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