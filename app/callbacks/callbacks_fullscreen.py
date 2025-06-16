from dash import Input, Output, State, callback, ctx, no_update, ALL
import json
from dash.exceptions import PreventUpdate


def setup_fullscreen_callbacks(app):
    """Register callbacks for fullscreen chart modal."""

    @app.callback(
        Output("fullscreen-modal", "is_open"),
        Output("fullscreen-modal-graph", "figure"),
        Input({"type": "expand-btn", "id": ALL}, "n_clicks"),
        Input("close-fullscreen", "n_clicks"),
        State({"type": "chart", "id": ALL}, "figure"),
        prevent_initial_call=True,
    )
    def toggle_fullscreen(expand_clicks, close_click, figures):
        triggered = ctx.triggered_id
        if triggered == "close-fullscreen" or triggered is None:
            return False, no_update

        if isinstance(triggered, dict) and triggered.get("type") == "expand-btn":
            chart_id = triggered["id"]

            state_map = {
                json.loads(k.split(".")[0])["id"]: v
                for k, v in ctx.states.items()
            }

            if chart_id in state_map:
                return True, state_map[chart_id]

        raise PreventUpdate
