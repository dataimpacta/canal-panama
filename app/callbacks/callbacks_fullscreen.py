"""Callbacks to manage fullscreen chart modals."""

from dash import Input, Output, State, callback, ctx


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

