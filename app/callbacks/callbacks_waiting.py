# pylint: disable=import-error

"""Module for waiting times dashboard callbacks."""

from dash import Input, Output, State, callback
from dash import html, ctx
import plotly.graph_objects as go

from data_utils import map_processing
from charts import charts_waiting_times


def setup_waiting_times_callbacks(app, df, controls):
    """
    These are the callbacks for the emissions dashboard.
    """
    @app.callback(
        Output("time--checklist--vessel", "value"),
        Input("time--btn--vessel-select", "n_clicks"),
        Input("time--btn--vessel-clear", "n_clicks"),
        prevent_initial_call=True
    )
    def update_checklist_vessel(_select_all_clicks, _clear_all_clicks):
        """
        Updates the checklist based on button clicks.
        """
        triggered_id = ctx.triggered_id

        if triggered_id == "time--btn--vessel-select":
            return list(controls["vessel_types"])
        elif triggered_id == "time--btn--vessel-clear":
            return []

    @app.callback(
        Output("time--checklist--vessel", "options"),
        Input("time--search--vessel", "value"),
    )
    def filter_vessel_options(search_value):
        """Filter vessel type options based on search value."""
        vessels = controls["vessel_types"]
        if not search_value:
            filtered = vessels
        else:
            filtered = [v for v in vessels if search_value.lower() in v.lower()]
        return [{"label": v, "value": v} for v in filtered]


    @app.callback(
        Output("time--checklist--stop-area", "value"),
        Input("time--btn--stop-area-select", "n_clicks"),
        Input("time--btn--stop-area-clear", "n_clicks"),
        prevent_initial_call=True
    )
    def update_checklist_stop_area(_select_all_clicks, _clear_all_clicks):
        """
        Updates the checklist based on button clicks.
        """
        triggered_id = ctx.triggered_id

        if triggered_id == "time--btn--stop-area-select":
            return list(controls["stop_area"])
        elif triggered_id == "time--btn--stop-area-clear":
            return []


    @app.callback(
        [
            Output("time--chart--1", "figure"),
            Output("time--chart--2", "figure"),
            Output("time--chart--3", "figure"),
            Output("time--chart--4", "figure"),
            Output("time--modal--no-data", "is_open")
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "value"),
            State("time--range--date", "value"),
            State("time--checklist--vessel", "value"),
            State("time--checklist--stop-area", "value")
        ]
    )
    def update_charts(_n_clicks, current_tab, selected_date_range, selected_vessels, selected_areas):
        time_col = "waiting_time" if current_tab == "waiting" else "service_time"
        start_ym = controls["date_range"]["index_to_year_month"][selected_date_range[0]]
        end_ym = controls["date_range"]["index_to_year_month"][selected_date_range[1]]

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
            return (
                empty_fig, empty_fig, empty_fig, empty_fig,
                True
            )
        
        

        df_waiting_time_avg = filtered_df.groupby(['year', 'month'])[time_col].mean().reset_index()
        fig1 = charts_waiting_times.plot_line_chart_waiting_time_by_year_month(df_waiting_time_avg, value_column=time_col)

        avg_waiting_times = filtered_df.groupby('stop_area')[time_col].mean().reset_index()
        top_areas = avg_waiting_times.sort_values(time_col, ascending=False).head(6)
        fig2 = charts_waiting_times.plot_bar_chart_waiting_by_stop_area(top_areas, value_column=time_col)

        top_waiting_by_vessel = filtered_df.groupby('StandardVesselType')[time_col].mean().sort_values(ascending=False).head(6)
        fig3 = charts_waiting_times.plot_bar_chart_waiting_by_vessel_type(top_waiting_by_vessel, value_column=time_col)

        df_type_week = filtered_df.groupby(["StandardVesselType", "year_month"])[time_col].mean().reset_index()
        fig4 = charts_waiting_times.plot_line_chart_waiting_by_type_week(df_type_week, value_column=time_col)

        return (
            fig1, fig2, fig3, fig4, False
        )
