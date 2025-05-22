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
            id="no-data-modal",
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
    return dcc.RangeSlider(
        id="filter-date-range",
        min=date_range["min_index"],
        max=date_range["max_index"],
        value=[date_range["min_index"], date_range["max_index"]],
        marks={
            date_range["min_index"]: str(date_range["unique_year_months"][0]),
            date_range["max_index"]: str(date_range["unique_year_months"][-1])
        },
        step=1,
        allowCross=False
    )

def build_vessel_type_checklist(vessel_types):
    return html.Div([
        html.Div([
            html.Span(
                "Select All",
                id="btn-select-all",
                n_clicks=0,
                style={"color": "#007bff", "cursor": "pointer", "marginRight": "0.24em"}
            ),
            html.Span("•", style={"color": "#999", "fontSize": "0.8rem", "marginRight": "0.2rem"}),
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
    ])
