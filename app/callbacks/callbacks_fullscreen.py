"""Callbacks to manage fullscreen chart modals."""

from dash import Input, Output, State, callback, ctx
import dash


def setup_fullscreen_callbacks(app, chart_ids):
    """Register callbacks for fullscreen modals for each chart id."""
    for cid in chart_ids:
        _open_id = f"{cid}-open-fullscreen"
        _close_id = f"{cid}-close-fullscreen"
        _modal_id = f"{cid}-fullscreen-modal"
        _graph_id = cid
        _fs_graph_id = f"{cid}-fullscreen"

        @app.callback(
            Output(_modal_id, "is_open"),
            Output(_fs_graph_id, "figure"),
            Input(_open_id, "n_clicks"),
            Input(_close_id, "n_clicks"),
            State(_modal_id, "is_open"),
            State(_graph_id, "figure"),
            prevent_initial_call=True,
        )
        def toggle_modal(n_open, n_close, is_open, fig, _cid=cid):  # pylint: disable=unused-argument
            triggered = ctx.triggered_id
            if triggered == _open_id:
                return True, fig
            if triggered == _close_id:
                return False, fig
            return is_open, fig


def setup_waiting_times_fullscreen(app, chart_ids):
    """Display waiting time charts in a dedicated fullscreen container."""
    open_ids = [f"{cid}-open-fullscreen" for cid in chart_ids]

    @app.callback(
        Output("waiting-fullscreen-container", "className"),
        Output("waiting-fullscreen-graph", "figure"),
        [Input(oid, "n_clicks") for oid in open_ids]
        + [Input("waiting-fullscreen-close", "n_clicks")],
        [State(cid, "figure") for cid in chart_ids]
        + [State("waiting-fullscreen-container", "className")],
        prevent_initial_call=True,
    )
    def toggle_container(*args):  # pylint: disable=unused-variable
        triggered = ctx.triggered_id
        current_class = args[-1]
        figs = args[len(open_ids) + 1 : len(open_ids) + 1 + len(open_ids)]

        if triggered == "waiting-fullscreen-close":
            return "mb-4 d-none", dash.no_update

        for i, oid in enumerate(open_ids):
            if triggered == oid:
                return "mb-4", figs[i]

        return current_class, dash.no_update

