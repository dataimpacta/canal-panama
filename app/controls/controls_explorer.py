"""Controls for the explorer tab."""

from dash import html, dcc
import dash_bootstrap_components as dbc


def build_source_dropdown(sources):
    """Dropdown to choose the data source."""
    options = [{"label": s.replace("_", " ").title(), "value": s} for s in sources]
    return dcc.Dropdown(id="explorer--source", options=options, value=sources[0], clearable=False)


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
        id="explorer--start-date",
        options=options,
        value=date_range["min_index"],
        clearable=False,
        className="mb-2",
    )

    end_dropdown = dcc.Dropdown(
        id="explorer--end-date",
        options=options,
        value=date_range["max_index"],
        clearable=False,
    )

    return html.Div(
        [
            start_dropdown,
            end_dropdown,
        ],
        id="explorer--month-range",
    )


def build_week_range_slider(week_range):
    """Dropdowns to select a start and end week."""
    def _fmt(yw):
        yw = str(yw)
        return f"{yw[:4]}-W{yw[4:]}"

    options = [
        {"label": _fmt(yw), "value": idx}
        for idx, yw in enumerate(week_range["unique_year_week"])
    ]

    start_dd = dcc.Dropdown(
        id="explorer--start-week",
        options=options,
        value=week_range["min_index"],
        clearable=False,
        className="mb-2",
    )

    end_dd = dcc.Dropdown(
        id="explorer--end-week",
        options=options,
        value=week_range["max_index"],
        clearable=False,
    )

    return html.Div(
        [
            start_dd,
            end_dd,
        ],
        id="explorer--week-range",
        style={"display": "none"},
    )


def build_date_range_display():
    """Build the date range display with title outside the accordion."""
    return html.Div([
        html.H6(
            "Selected Date Range", className="mb-2", 
            style={"fontWeight": "bold", "color": "#333"}
        ),
        html.Div(
            id="explorer--range-label", className="text-center p-2",
            style={"backgroundColor": "#f8f9fa", "borderRadius": "4px",
            "border": "1px solid #dee2e6"}
        )
    ], className="mb-3", id="explorer--month-range-display")

def build_week_range_display():
    """Build the week range display with title outside the accordion."""
    return html.Div([
        html.H6(
            "Selected Date Range", className="mb-2", 
            style={"fontWeight": "bold", "color": "#333"}
        ),
        html.Div(
            id="explorer--week-range-label", className="text-center p-1",
            style={"backgroundColor": "#f8f9fa", "borderRadius": "4px",
            "border": "1px solid #dee2e6"}
        )
    ], className="mb-3", id="explorer--week-range-display")


def build_download_button():
    return dbc.Button("Download Data", id="explorer--download-btn", color="primary")


def build_download_modal():
    """Form modal shown before downloading data."""
    return dbc.Modal(
        [
            dbc.ModalHeader("Download Data"),
            dbc.ModalBody(
                [
                    html.P(
                        "Please provide the following details so we understand how the data will be used.",
                        className="small",
                    ),
                    dbc.Input(id="explorer--field-country", placeholder="Country", type="text", className="mb-2"),
                    dbc.Input(id="explorer--field-purpose", placeholder="Purpose of the Download", type="text", className="mb-2"),
                    html.Div(
                        [
                            html.Hr(),
                            html.Small(
                                "Example citation: ",
                                style={"fontWeight": "bold"}
                            ),
                            html.Small(
                                "Fuentes, G., & Adland, R. (2023). Greenhouse gas mitigation at "
                                "maritime chokepoints: The case of the Panama Canal. Transportation "
                                "Research Part D: Transport and Environment, 118, 103694.",
                                className="text-muted",
                            ),
                        ],
                        className="mt-3",
                    ),
                ]
            ),
            dbc.ModalFooter(
                html.Div(
                    [
                        html.Small(
                            [
                                "We collect country and purpose to understand usage. Your IP address is processed for security and regional statistics. See our ",
                                html.A(
                                    "Privacy Notice",
                                    href="/privacy",
                                    target="_blank",
                                ),
                                ".",
                            ],
                            className="text-muted",
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                dbc.Button("Cancel", id="explorer--download-cancel", className="me-2"),
                                dbc.Button("Download", id="explorer--download-submit", color="primary"),
                            ],
                            className="mt-2",
                        ),
                    ]
                )
            ),
        ],
        id="explorer--download-modal",
        is_open=False,
    )
