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

    return html.Div([
        start_dropdown,
        end_dropdown,
        html.Div(id="explorer--range-label", className="text-center mt-2"),
    ])


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
                        "Please provide the following details so we understand how the data will be used and can inform you of updates.",
                        className="small",
                    ),
                    dbc.Input(id="explorer--field-name", placeholder="Name and Last Name", type="text", className="mb-2"),
                    dbc.Input(id="explorer--field-country", placeholder="Country", type="text", className="mb-2"),
                    dbc.Input(id="explorer--field-purpose", placeholder="Purpose of the Download", type="text", className="mb-2"),
                    dbc.Input(id="explorer--field-email", placeholder="Email", type="email", className="mb-2"),
                    html.Div(
                        [
                            html.Hr(),
                            html.Small(
                                "Example citation: Fuentes, G. (2024). Panama Maritime Statistics Dashboard dataset. Norwegian School of Economics & SENACYT.",
                                className="text-muted",
                            ),
                        ],
                        className="mt-3",
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Cancel", id="explorer--download-cancel", className="me-2"),
                    dbc.Button("Download", id="explorer--download-submit", color="primary"),
                ]
            ),
        ],
        id="explorer--download-modal",
        is_open=False,
    )
