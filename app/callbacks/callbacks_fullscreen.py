from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate


def setup_fullscreen_callbacks(app):
    """Register callbacks for fullscreen chart modal."""

    @app.callback(
        Output("fullscreen-modal", "is_open"),
        Output("fullscreen-modal-graph", "figure"),
        Input("emissions--chart--1-expand", "n_clicks"),
        Input("emissions--chart--2-expand", "n_clicks"),
        Input("emissions--chart--3-expand", "n_clicks"),
        Input("emissions--chart--4-expand", "n_clicks"),
        Input("time--chart--1-expand", "n_clicks"),
        Input("time--chart--2-expand", "n_clicks"),
        Input("time--chart--3-expand", "n_clicks"),
        Input("time--chart--4-expand", "n_clicks"),
        Input("close-fullscreen", "n_clicks"),
        State("emissions--chart--1", "figure"),
        State("emissions--chart--2", "figure"),
        State("emissions--chart--3", "figure"),
        State("emissions--chart--4", "figure"),
        State("time--chart--1", "figure"),
        State("time--chart--2", "figure"),
        State("time--chart--3", "figure"),
        State("time--chart--4", "figure"),
        prevent_initial_call=True,
    )
    def toggle_fullscreen(*args):
        triggered = ctx.triggered_id
        if not triggered:
            raise PreventUpdate

        figures = args[9:]

        if triggered == "close-fullscreen":
            return False, no_update

        btn_to_fig = {
            "emissions--chart--1-expand": figures[0],
            "emissions--chart--2-expand": figures[1],
            "emissions--chart--3-expand": figures[2],
            "emissions--chart--4-expand": figures[3],
            "time--chart--1-expand": figures[4],
            "time--chart--2-expand": figures[5],
            "time--chart--3-expand": figures[6],
            "time--chart--4-expand": figures[7],
        }
        if triggered in btn_to_fig:
            return True, btn_to_fig[triggered]

        return no_update, no_update
