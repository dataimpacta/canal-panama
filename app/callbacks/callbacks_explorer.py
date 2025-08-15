# pylint: disable=import-error

"""Callbacks for the explorer tab."""

from dash import Input, Output, State, dcc, ctx
from charts import charts_explorer
from data_utils.form_saver import append_form_row, anonymize_ip
from flask import request


def setup_explorer_callbacks(app, df_emissions, df_waiting, df_energy, controls):
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
            if ctx.triggered_id  == "explorer--start-date":
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
        Output("explorer--start-week", "value"),
        Output("explorer--end-week", "value"),
        Input("explorer--start-week", "value"),
        Input("explorer--end-week", "value"),
    )
    def validate_weeks(start_idx, end_idx):
        if start_idx is None:
            start_idx = controls["week_range"]["min_index"]
        if end_idx is None:
            end_idx = controls["week_range"]["max_index"]
        if start_idx > end_idx:
            if ctx.triggered_id == "explorer--start-week":
                start_idx = end_idx
            else:
                end_idx = start_idx
        return start_idx, end_idx

    @app.callback(
        Output("explorer--week-range-label", "children"),
        Input("explorer--start-week", "value"),
        Input("explorer--end-week", "value"),
    )
    def update_week_label(start_idx, end_idx):
        index_map = controls["week_range"]["index_to_year_week"]
        start_yw = index_map[start_idx]
        end_yw = index_map[end_idx]

        def _fmt(yw):
            yw = str(yw)
            return f"{yw[:4]}-W{yw[4:]}"

        return f"{_fmt(start_yw)} to {_fmt(end_yw)}"

    @app.callback(
        Output("explorer--month-range", "style"),
        Output("explorer--week-range", "style"),
        Output("explorer--month-range-display", "style"),
        Output("explorer--week-range-display", "style"),
        Input("explorer--source", "value"),
    )
    def toggle_range_visibility(source):
        if source == "energy":
            # Hide month range, show week range
            return {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "block"}
        else:
            # Show month range, hide week range
            return {"display": "block"}, {"display": "none"}, {"display": "block"}, {"display": "none"}

    @app.callback(
        Output("explorer--chart", "figure"),
        Output("explorer--chart-fullscreen", "figure"),
        Output("explorer--table", "data"),
        Output("explorer--table", "columns"),
        Input("explorer--source", "value"),
        Input("explorer--start-date", "value"),
        Input("explorer--end-date", "value"),
        Input("explorer--start-week", "value"),
        Input("explorer--end-week", "value"),
    )
    def update_chart(source, start_month_idx, end_month_idx, start_week_idx, end_week_idx):
        start_ym = controls["date_range"]["index_to_year_month"].get(start_month_idx)
        end_ym = controls["date_range"]["index_to_year_month"].get(end_month_idx)
        start_yw = controls["week_range"]["index_to_year_week"].get(start_week_idx)
        end_yw = controls["week_range"]["index_to_year_week"].get(end_week_idx)

        if source == "emissions":
            df = df_emissions
            value_col = "co2_equivalent_t"
            filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]
            summary = filtered.groupby("year_month")[value_col].sum().reset_index()
            summary["date"] = summary["year_month"].astype(str).str.slice(0, 4) + "-" + summary["year_month"].astype(str).str.slice(4, 6)
        elif source == "waiting_time":
            df = df_waiting
            value_col = "waiting_time"
            filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]
            summary = filtered.groupby("year_month")[value_col].sum().reset_index()
            summary["date"] = summary["year_month"].astype(str).str.slice(0, 4) + "-" + summary["year_month"].astype(str).str.slice(4, 6)
        elif source == "service_time":
            df = df_waiting
            value_col = "service_time"
            filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]
            summary = filtered.groupby("year_month")[value_col].sum().reset_index()
            summary["date"] = summary["year_month"].astype(str).str.slice(0, 4) + "-" + summary["year_month"].astype(str).str.slice(4, 6)
        else:  # energy
            df = df_energy
            value_col = "sum_energy"
            filtered = df[(df["year_week"] >= start_yw) & (df["year_week"] <= end_yw)]
            summary = filtered.groupby("year_week")[value_col].sum().reset_index()
            summary["date"] = summary["year_week"].astype(str).str.slice(0, 4) + "-W" + summary["year_week"].astype(str).str.slice(4, None)
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
        State("explorer--start-week", "value"),
        State("explorer--end-week", "value"),
        State("explorer--field-country", "value"),
        State("explorer--field-purpose", "value"),
        prevent_initial_call=True,
    )
    def download_data(_, source, start_month_idx, end_month_idx, start_week_idx, end_week_idx, country, purpose):
        start_ym = controls["date_range"]["index_to_year_month"].get(start_month_idx)
        end_ym = controls["date_range"]["index_to_year_month"].get(end_month_idx)
        start_yw = controls["week_range"]["index_to_year_week"].get(start_week_idx)
        end_yw = controls["week_range"]["index_to_year_week"].get(end_week_idx)

        if source == "emissions":
            df = df_emissions
            filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]
        elif source == "waiting_time":
            df = df_waiting
            filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]
        elif source == "service_time":
            df = df_waiting
            filtered = df[(df["year_month"] >= start_ym) & (df["year_month"] <= end_ym)]
        else:
            df = df_energy
            filtered = df[(df["year_week"] >= start_yw) & (df["year_week"] <= end_yw)]

        # Save form information to S3 before returning the file
        if source == "energy":
            fmt_date = lambda yw: f"{str(yw)[:4]}-W{str(yw)[4:]}"
            start_val = fmt_date(start_yw)
            end_val = fmt_date(end_yw)
        else:
            fmt_date = lambda ym: f"{str(ym)[:4]}-{str(ym)[4:6]}-01"
            start_val = fmt_date(start_ym)
            end_val = fmt_date(end_ym)
        ip_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip_addr and "," in ip_addr:
            ip_addr = ip_addr.split(",")[0].strip()
        anonymized = anonymize_ip(ip_addr) if ip_addr else ""

        append_form_row(
            anonymized,
            country,
            purpose,
            source,
            start_val,
            end_val,
        )
        
        # Create filename with source information for better tracking
        filename = f"panama_canal_{source}_data.csv"
        return dcc.send_data_frame(filtered.to_csv, filename, index=False)
