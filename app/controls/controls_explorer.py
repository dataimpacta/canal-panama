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
