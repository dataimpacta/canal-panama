"""Climate & Watershed tab callbacks, reading only from pre-existing S3 Parquet."""

import logging

import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from charts import charts_climate
from data_utils import climate_s3

LOG = logging.getLogger(__name__)


def setup_climate_callbacks(app, s3_client):
    """Register chart updates; new tab failures cannot break other dashboard tabs."""

    @app.callback(
        Output("climate--chart--combined", "figure"),
        Output("climate--chart--combined-fullscreen", "figure"),
        Output("climate--chart--enso", "figure"),
        Output("climate--chart--enso-fullscreen", "figure"),
        Output("climate--chart--gatun", "figure"),
        Output("climate--chart--gatun-fullscreen", "figure"),
        Output("climate--load-status", "children"),
        Input("climate--btn--refresh", "n_clicks"),
        Input("climate--history-years", "value"),
        State("chart-tabs-store", "data"),
    )
    def update_climate_charts(_refresh, years, selected_tab):
        if selected_tab != "climate":
            raise PreventUpdate
        datasets, errors = climate_s3.load_all(s3_client)
        try:
            combined = charts_climate.combined(datasets, years or "5")
            enso = charts_climate.enso(datasets, years or "5")
            gatun = charts_climate.gatun(datasets, years or "5")
        except (KeyError, ValueError, TypeError) as exc:
            LOG.exception("Unable to render climate chart")
            raise PreventUpdate from exc

        if errors:
            details = [
                dbc.Alert(f"{name}: {message}", color="warning", className="mb-2")
                for name, message in errors.items()
            ]
        else:
            details = ""
        return combined, combined, enso, enso, gatun, gatun, details
