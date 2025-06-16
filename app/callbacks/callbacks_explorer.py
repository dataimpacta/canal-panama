"""Callbacks for the explorer tab."""

from dash import Input, Output, State, dcc

from charts import charts_explorer


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
        return fig

    @app.callback(
        Output("explorer--download", "data"),
        Input("explorer--download-btn", "n_clicks"),
        State("explorer--source", "value"),
        State("explorer--start-date", "value"),
        State("explorer--end-date", "value"),
        prevent_initial_call=True,
    )
    def download_data(_, source, start_idx, end_idx):
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
        out = filtered.groupby("year_month")[value_col].sum().reset_index()
        out.columns = ["date", "value"]
        return dcc.send_data_frame(out.to_csv, "explorer_data.csv", index=False)
