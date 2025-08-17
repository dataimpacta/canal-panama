# pylint: disable=import-error

"""Callbacks for the explorer tab."""

from dash import Input, Output, State, dcc, ctx
from dash.exceptions import PreventUpdate
from charts import charts_explorer
from data_utils.form_saver import append_form_row


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
        Output("download-summary-type", "children"),
        Output("download-summary-range", "children"),
        Input("explorer--source", "value"),
        Input("explorer--start-date", "value"),
        Input("explorer--end-date", "value"),
        Input("explorer--start-week", "value"),
        Input("explorer--end-week", "value"),
    )
    def update_download_summary(source, start_month_idx, end_month_idx, start_week_idx, end_week_idx):
        """Update the download summary with current selections."""
        if not source:
            return "Not selected", "Not selected"
        
        # Get data type display name
        data_type_map = {
            'emissions': 'Emissions Data',
            'waiting_time': 'Waiting Time Data', 
            'service_time': 'Service Time Data',
            'energy': 'Energy Data'
        }
        data_type = data_type_map.get(source, source.replace('_', ' ').title())
        
        # Get date range
        if source == "energy":
            if start_week_idx is not None and end_week_idx is not None:
                start_yw = controls["week_range"]["index_to_year_week"].get(start_week_idx)
                end_yw = controls["week_range"]["index_to_year_week"].get(end_week_idx)
                if start_yw and end_yw:
                    start_val = f"{str(start_yw)[:4]}-W{str(start_yw)[4:]}"
                    end_val = f"{str(end_yw)[:4]}-W{str(end_yw)[4:]}"
                    date_range = f"{start_val} to {end_val}"
                else:
                    date_range = "Not selected"
            else:
                date_range = "Not selected"
        else:
            if start_month_idx is not None and end_month_idx is not None:
                start_ym = controls["date_range"]["index_to_year_month"].get(start_month_idx)
                end_ym = controls["date_range"]["index_to_year_month"].get(end_month_idx)
                if start_ym and end_ym:
                    start_val = f"{str(start_ym)[:4]}-{str(start_ym)[4:6]}"
                    end_val = f"{str(end_ym)[:4]}-{str(end_ym)[4:6]}"
                    date_range = f"{start_val} to {end_val}"
                else:
                    date_range = "Not selected"
            else:
                date_range = "Not selected"
        
        return data_type, date_range

    @app.callback(
        Output("explorer--download-submit", "disabled"),
        Output("explorer--download-submit", "children"),
        Output("explorer--field-country", "valid"),
        Output("explorer--field-country", "invalid"),
        Output("explorer--field-purpose", "valid"),
        Output("explorer--field-purpose", "invalid"),
        Input("explorer--field-country", "value"),
        Input("explorer--field-purpose", "value"),
        Input("explorer--download-submit", "n_clicks"),
    )
    def validate_required_fields(country, purpose, submit_clicks):
        """Validate required fields and update download button state."""
        country_valid = bool(country and country.strip())
        purpose_valid = bool(purpose and purpose.strip())
        is_valid = country_valid and purpose_valid
        
        # Only show validation errors if user has tried to submit or has entered data
        show_validation = submit_clicks is not None or country is not None or purpose is not None
        
        if is_valid:
            return False, "Download Data", True, False, True, False  # Button enabled, fields valid
        else:
            if show_validation:
                return True, "Fill Required Fields", country_valid, not country_valid, purpose_valid, not purpose_valid  # Button disabled, show field validation
            else:
                return True, "Download Data", False, False, False, False  # Button disabled, no validation errors shown
    
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
        State("explorer--field-email", "value"),
        State("explorer--field-consent", "value"),
        prevent_initial_call=True,
    )
    def download_data(_, source, start_month_idx, end_month_idx, start_week_idx, end_week_idx, country, purpose, email, consent):
        """
        Download filtered data with enhanced filename generation and analytics tracking.
        
        The filename includes:
        - Data type (emissions, waiting_time, service_time, energy)
        - Date range (start to end)
        
        Example: panama_canal_emissions_data_2023-01_to_2023-12.csv
        """
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
            # Create descriptive filename for energy data
            filename = f"panama_canal_energy_data_{start_val}_to_{end_val}.csv"
        else:
            fmt_date = lambda ym: f"{str(ym)[:4]}-{str(ym)[4:6]}"
            start_val = fmt_date(start_ym)
            end_val = fmt_date(end_ym)
            # Create descriptive filename for other data types
            filename = f"panama_canal_{source}_data_{start_val}_to_{end_val}.csv"

        # Validate required fields
        if not country or not country.strip():
            raise PreventUpdate
        if not purpose or not purpose.strip():
            raise PreventUpdate

        append_form_row(
            email,
            country,
            purpose,
            source,
            start_val,
            end_val,
        )
        
        # Add metadata about the download for analytics
        download_metadata = {
            'source': source,
            'date_range': f"{start_val}_to_{end_val}",
            'country': country or '',
            'purpose': purpose or '',
            'record_count': len(filtered),
            'filename': filename
        }
        

        
        return dcc.send_data_frame(filtered.to_csv, filename, index=False)
