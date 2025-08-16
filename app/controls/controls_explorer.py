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
                    # Header section
                    html.Div([
                        html.P(
                            "Please provide your details to complete the download.",
                            className="text-muted mb-4",
                        ),
                    ]),
                    
                    # Download summary section
                    html.Div([
                        html.H6("Download Summary", className="mb-3", style={"color": "#495057", "fontWeight": "600"}),
                        html.Div([
                            html.Div([
                                html.Span("Data Type: ", style={"fontWeight": "600", "color": "#495057"}),
                                html.Span(id="download-summary-type", style={"color": "#0d6efd"}),
                            ], className="mb-2"),
                            html.Div([
                                html.Span("Date Range: ", style={"fontWeight": "600", "color": "#495057"}),
                                html.Span(id="download-summary-range", style={"color": "#0d6efd"}),
                            ], className="mb-2"),
                        ], className="p-3", style={"backgroundColor": "#f8f9fa", "borderRadius": "6px", "border": "1px solid #e9ecef"}),
                    ], className="mb-4"),
                    
                    # Required information section
                    html.Div([
                        html.H6("Your Information", className="mb-3", style={"color": "#495057", "fontWeight": "600"}),
                        html.Div([
                            html.Label("Country", className="form-label", style={"fontWeight": "500", "color": "#495057"}),
                            html.Span(" *", style={"color": "#dc3545", "fontWeight": "bold"}),
                        ], className="mb-2"),
                        dbc.Input(
                            id="explorer--field-country", 
                            placeholder="Your country", 
                            type="text", 
                            className="mb-3",
                            required=True
                        ),
                        html.Div([
                            html.Label("Purpose", className="form-label", style={"fontWeight": "500", "color": "#495057"}),
                            html.Span(" *", style={"color": "#dc3545", "fontWeight": "bold"}),
                        ], className="mb-2"),
                        dbc.Input(
                            id="explorer--field-purpose", 
                            placeholder="How will you use this data? (e.g., research, academic, business)", 
                            type="text", 
                            className="mb-3",
                            required=True
                        ),
                    ], className="mb-4"),
                    
                    # Email section (optional)
                    html.Div([
                        html.Div([
                            html.H6("Email", className="mb-3", style={"color": "#6c757d", "fontWeight": "600"}),
                            html.Span(
                                "ⓘ", 
                                className="ms-2",
                                style={"cursor": "help", "color": "#6c757d", "fontSize": "14px"},
                                title="We will not use your email for marketing. It is used only for analytics and is stored securely as a hash."
                            ),
                        ], className="d-flex align-items-center"),
                        dbc.Input(
                            id="explorer--field-email", 
                            placeholder="Email address", 
                            type="email", 
                            className="mb-3"
                        ),
                    ], className="mb-4"),
                    
                    # Citation example section
                    html.Div([
                        html.H6("Citation", className="mb-2", style={"color": "#495057", "fontWeight": "600"}),
                        html.Div([
                            html.Small(
                                "Fuentes, G., & Adland, R. (2023). Greenhouse gas mitigation at "
                                "maritime chokepoints: The case of the Panama Canal. Transportation "
                                "Research Part D: Transport and Environment, 118, 103694.",
                                className="text-muted",
                                style={"fontStyle": "italic"}
                            ),
                        ], className="p-3", style={"backgroundColor": "#f8f9fa", "borderRadius": "6px", "border": "1px solid #e9ecef"}),
                    ], className="mb-3"),
                ]
            ),
            dbc.ModalFooter(
                html.Div([
                    # Consent and privacy section
                    html.Div([
                        dbc.Switch(
                            id="explorer--field-consent",
                            label=[
                                "I consent to the use of my email for analytics purposes, as described in the ",
                                html.A(
                                    "Privacy Notice",
                                    href="/privacy",
                                    target="_blank",
                                    style={"color": "#0d6efd", "textDecoration": "underline"}
                                ),
                                "."
                            ],
                            value=False,
                            className="mb-3"
                        ),
                    ]),
                    
                    # Action buttons
                    html.Div([
                        dbc.Button(
                            "Cancel", 
                            id="explorer--download-cancel", 
                            className="me-2",
                            color="light"
                        ),
                        dbc.Button(
                            "Download Data", 
                            id="explorer--download-submit", 
                            color="primary"
                        ),
                    ], className="d-flex justify-content-end"),
                ])
            ),
        ],
        id="explorer--download-modal",
        is_open=False,
    )
