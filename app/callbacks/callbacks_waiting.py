# pylint: disable=import-error

"""Module for waiting times dashboard callbacks."""

from dash import Input, Output, State, callback
from dash import html, ctx
import plotly.graph_objects as go

from data_utils import map_processing
from charts import charts_waiting_times


def setup_waiting_times_callbacks(app, df, controls):
    """
    These are the callbacks for the waiting times dashboard.
    """
    @app.callback(
        Output("time--checklist--vessel", "options"),
        Output("time--checklist--vessel", "value"),
        Input("time--btn--vessel-select", "n_clicks"),
        Input("time--btn--vessel-clear", "n_clicks"),
        Input("time--input--vessel-search", "value"),
        State("time--checklist--vessel", "value"),
        prevent_initial_call=True,
    )
    def update_vessel_checklist(_select_all_clicks, _clear_all_clicks,
                                search_value, selected_values):
        """Update vessel checklist options and selected values."""
        vessel_types = controls["vessel_types"]

        if search_value:
            search_value = search_value.lower()
            filtered = [v for v in vessel_types if search_value in v.lower()]
        else:
            filtered = vessel_types

        options = [{"label": v, "value": v} for v in filtered]

        triggered_id = ctx.triggered_id
        if triggered_id == "time--btn--vessel-select":
            new_selected = list(filtered)
        elif triggered_id == "time--btn--vessel-clear":
            new_selected = []
        else:
            # Preserve existing selections even if not currently visible
            new_selected = selected_values

        return options, new_selected


    @app.callback(
        Output("time--checklist--stop-area", "options"),
        Output("time--checklist--stop-area", "value"),
        Input("time--btn--stop-area-select", "n_clicks"),
        Input("time--btn--stop-area-clear", "n_clicks"),
        Input("time--input--stop-area-search", "value"),
        State("time--checklist--stop-area", "value"),
        prevent_initial_call=True,
    )
    def update_checklist_stop_area(_select_all_clicks, _clear_all_clicks,
                                   search_value, selected_values):
        """Update stop area checklist options and values."""
        stop_areas = controls["stop_area"]

        if search_value:
            search_value = search_value.lower()
            filtered = [a for a in stop_areas if search_value in a.lower()]
        else:
            filtered = stop_areas

        options = [{"label": a, "value": a} for a in filtered]

        triggered_id = ctx.triggered_id
        if triggered_id == "time--btn--stop-area-select":
            new_selected = list(filtered)
        elif triggered_id == "time--btn--stop-area-clear":
            new_selected = []
        else:
            new_selected = selected_values

        return options, new_selected

    @app.callback(
        Output("time--start-date", "value"),
        Output("time--end-date", "value"),
        Input("time--start-date", "value"),
        Input("time--end-date", "value"),
        prevent_initial_call=True,
    )
    def validate_date_range(start_idx, end_idx):
        """Ensure the start date is not after the end date."""
        if start_idx is None:
            start_idx = controls["date_range"].get("default_start_index", controls["date_range"]["min_index"])
        if end_idx is None:
            end_idx = controls["date_range"]["max_index"]
        if start_idx > end_idx:
            if ctx.triggered_id == "time--start-date":
                start_idx = end_idx
            else:
                end_idx = start_idx
        return start_idx, end_idx

    # Split the large callback into smaller, individual callbacks
    @app.callback(
        [
            Output("time--chart--1", "figure"),
            Output("time--chart--1-fullscreen", "figure"),
        ],
        Input("time--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("time--start-date", "value"),
            State("time--end-date", "value"),
            State("time--checklist--vessel", "value"),
            State("time--checklist--stop-area", "value")
        ]
    )
    def update_chart_1(_n_clicks, current_tab, start_idx, end_idx, selected_vessels, selected_areas):
        """Updates chart 1 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        time_col = "waiting_time" if current_tab == "waiting" else "service_time"
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        filtered_df = df[
            (df["year_month"] >= start_ym) &
            (df["year_month"] <= end_ym) &
            (df["StandardVesselType"].isin(selected_vessels)) &
            (df["stop_area"].isin(selected_areas))
        ]

        # Sort by year_month
        filtered_df = filtered_df.sort_values("year_month")

        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 1: Line chart of waiting/service time by year and month
        df_waiting_time_avg = filtered_df.groupby(['year', 'month'])[time_col].mean().reset_index()
        fig = charts_waiting_times.plot_line_chart_waiting_time_by_year_month(df_waiting_time_avg, value_column=time_col)
        return fig, fig

    @app.callback(
        [
            Output("time--chart--2", "figure"),
            Output("time--chart--2-fullscreen", "figure"),
        ],
        Input("time--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("time--start-date", "value"),
            State("time--end-date", "value"),
            State("time--checklist--vessel", "value"),
            State("time--checklist--stop-area", "value")
        ]
    )
    def update_chart_2(_n_clicks, current_tab, start_idx, end_idx, selected_vessels, selected_areas):
        """Updates chart 2 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        time_col = "waiting_time" if current_tab == "waiting" else "service_time"
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        filtered_df = df[
            (df["year_month"] >= start_ym) &
            (df["year_month"] <= end_ym) &
            (df["StandardVesselType"].isin(selected_vessels)) &
            (df["stop_area"].isin(selected_areas))
        ]

        # Sort by year_month
        filtered_df = filtered_df.sort_values("year_month")

        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 2: Bar chart of waiting/service time by stop area
        avg_waiting_times = filtered_df.groupby('stop_area')[time_col].mean().reset_index()
        top_areas = avg_waiting_times.sort_values(time_col, ascending=False).head(6)
        fig = charts_waiting_times.plot_bar_chart_waiting_by_stop_area(top_areas, value_column=time_col)
        return fig, fig

    @app.callback(
        [
            Output("time--chart--3", "figure"),
            Output("time--chart--3-fullscreen", "figure"),
        ],
        Input("time--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("time--start-date", "value"),
            State("time--end-date", "value"),
            State("time--checklist--vessel", "value"),
            State("time--checklist--stop-area", "value")
        ]
    )
    def update_chart_3(_n_clicks, current_tab, start_idx, end_idx, selected_vessels, selected_areas):
        """Updates chart 3 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        time_col = "waiting_time" if current_tab == "waiting" else "service_time"
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        filtered_df = df[
            (df["year_month"] >= start_ym) &
            (df["year_month"] <= end_ym) &
            (df["StandardVesselType"].isin(selected_vessels)) &
            (df["stop_area"].isin(selected_areas))
        ]

        # Sort by year_month
        filtered_df = filtered_df.sort_values("year_month")

        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 3: Bar chart of waiting/service time by vessel type
        top_waiting_by_vessel = filtered_df.groupby('StandardVesselType')[time_col].mean().sort_values(ascending=False).head(6)
        fig = charts_waiting_times.plot_bar_chart_waiting_by_vessel_type(top_waiting_by_vessel, value_column=time_col)
        return fig, fig

    @app.callback(
        [
            Output("time--chart--4", "figure"),
            Output("time--chart--4-fullscreen", "figure"),
        ],
        Input("time--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("time--start-date", "value"),
            State("time--end-date", "value"),
            State("time--checklist--vessel", "value"),
            State("time--checklist--stop-area", "value")
        ]
    )
    def update_chart_4(_n_clicks, current_tab, start_idx, end_idx, selected_vessels, selected_areas):
        """Updates chart 4 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        time_col = "waiting_time" if current_tab == "waiting" else "service_time"
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        filtered_df = df[
            (df["year_month"] >= start_ym) &
            (df["year_month"] <= end_ym) &
            (df["StandardVesselType"].isin(selected_vessels)) &
            (df["stop_area"].isin(selected_areas))
        ]

        # Sort by year_month
        filtered_df = filtered_df.sort_values("year_month")

        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 4: Line chart of waiting/service time by vessel type and year/month
        df_type_week = filtered_df.groupby(["StandardVesselType", "year_month"])[time_col].mean().reset_index()
        fig = charts_waiting_times.plot_line_chart_waiting_by_type_week(df_type_week, value_column=time_col)
        return fig, fig

    @app.callback(
        Output("time--modal--no-data", "is_open"),
        Input("time--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("time--start-date", "value"),
            State("time--end-date", "value"),
            State("time--checklist--vessel", "value"),
            State("time--checklist--stop-area", "value")
        ]
    )
    def update_modal(_n_clicks, current_tab, start_idx, end_idx, selected_vessels, selected_areas):
        """Updates modal only."""
        # Don't update if we don't have a valid tab
        if current_tab is None:
            return False
        
        if start_idx is None or end_idx is None:
            return False
        
        time_col = "waiting_time" if current_tab == "waiting" else "service_time"
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        filtered_df = df[
            (df["year_month"] >= start_ym) &
            (df["year_month"] <= end_ym) &
            (df["StandardVesselType"].isin(selected_vessels)) &
            (df["stop_area"].isin(selected_areas))
        ]

        # Sort by year_month
        filtered_df = filtered_df.sort_values("year_month")
        
        # Check if data exists
        has_data = len(filtered_df) > 0
        return not has_data

    @app.callback(
        Output("time--range-label", "children"),
        Input("time--btn--refresh", "n_clicks"),
        [
            State("time--start-date", "value"),
            State("time--end-date", "value"),
        ]
    )
    def update_range_label(_n_clicks, start_idx, end_idx):
        """Updates range label only."""
        if start_idx is None or end_idx is None:
            return ""
        
        start_ym = controls["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls["date_range"]["index_to_year_month"][end_idx]

        # Format date range label
        def _fmt(ym: int) -> str:
            ym_str = str(ym)
            return f"{ym_str[:4]}-{ym_str[4:]}"
        date_range_label = f"{_fmt(start_ym)} to {_fmt(end_ym)}"
        
        return date_range_label
