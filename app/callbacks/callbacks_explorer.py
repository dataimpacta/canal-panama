"""Callbacks for the explorer tab."""

from dash import Input, Output, State, dcc, ctx
from charts import charts_explorer
from data_utils.form_saver import append_form_row


def setup_explorer_callbacks(app, df_emissions, df_waiting, controls):
    """Register callbacks for the explorer tab."""

    @app.callback(
        Output("explorer--start-date", "value"),
        Output("explorer--end-date", "value"),
        Input("explorer--start-date", "value"),
        Input("explorer--end-date", "value"),
    )
    def validate_dates(start_idx, end_idx):
        if start_idx is None:
            start_idx = controls["date_range"]["min_index"]
        if end_idx is None:
            end_idx = controls["date_range"]["max_index"]
        if start_idx > end_idx:
            if dcc.callback_context.triggered_id == "explorer--start-date":
                start_idx = end_idx
            else:
                end_idx = start_idx
        return start_idx, end_idx

    @app.callback(
        Output("explorer--range-label", "children"),
        Input("explorer--start-date", "value"),
        Input("explorer--end-date", "value"),
    )
    def update_label(start_idx, end_idx):
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        def _fmt(ym):
            ym = str(ym)
            return f"{ym[:4]}-{ym[4:]}"

        return f"{_fmt(start_ym)} to {_fmt(end_ym)}"

    @app.callback(
        Output("explorer--chart", "figure"),
        Output("explorer--chart-fullscreen", "figure"),
        Output("explorer--table", "data"),
        Output("explorer--table", "columns"),
        Input("explorer--source", "value"),
        Input("explorer--start-date", "value"),
        Input("explorer--end-date", "value"),
    )
    def update_chart(source, start_idx, end_idx):
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        if source == "emissions":
            df = df_emissions
            value_col = "co2_equivalent_t"
        elif source == "waiting_time":
            df = df_waiting
            value_col = "waiting_time"
        else:
            df = df_waiting
            value_col = "service_time"

        filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]
        summary = filtered.groupby("year_month")[value_col].sum().reset_index()
        summary["date"] = summary["year_month"].astype(str).str.slice(0, 4) + "-" + summary["year_month"].astype(str).str.slice(4, 6)
        fig = charts_explorer.plot_line_chart(summary, value_col)
        table = filtered.head(6)
        columns = [{"name": c.replace("_", " ").title(), "id": c} for c in table.columns]
        return fig, fig, table.to_dict("records"), columns

    @app.callback(
        Output("explorer--download-modal", "is_open"),
        Input("explorer--download-btn", "n_clicks"),
        Input("explorer--download-cancel", "n_clicks"),
        Input("explorer--download-submit", "n_clicks"),
        State("explorer--download-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_modal(btn, cancel, submit, is_open):
        trigger = ctx.triggered_id
        if trigger == "explorer--download-btn":
            return True
        if trigger in {"explorer--download-cancel", "explorer--download-submit"}:
            return False
        return is_open

    @app.callback(
        Output("explorer--download", "data"),
        Input("explorer--download-submit", "n_clicks"),
        State("explorer--source", "value"),
        State("explorer--start-date", "value"),
        State("explorer--end-date", "value"),
        State("explorer--field-name", "value"),
        State("explorer--field-country", "value"),
        State("explorer--field-purpose", "value"),
        State("explorer--field-email", "value"),
        prevent_initial_call=True,
    )
    def download_data(_, source, start_idx, end_idx, _name, _country, _purpose, _email):
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        if source == "emissions":
            df = df_emissions
            value_col = "co2_equivalent_t"
        elif source == "waiting_time":
            df = df_waiting
            value_col = "waiting_time"
        else:
            df = df_waiting
            value_col = "service_time"

        filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]

        # Save form information to S3 before returning the file
        append_form_row(_name, _country, _purpose, _email)

        return dcc.send_data_frame(filtered.to_csv, "explorer_data.csv", index=False)
