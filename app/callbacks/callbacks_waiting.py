# pylint: disable=import-error

"""Module for waiting times dashboard callbacks."""

from dash import Input, Output, State, callback
from dash import html, ctx
import plotly.graph_objects as go

from data_utils import map_processing
from charts import charts_waiting_times


def setup_waiting_times_callbacks(app, df):


    @app.callback(
        [
            Output("chart-11", "figure"),
            Output("chart-22", "figure"),
            Output("chart-33", "figure"),
            Output("chart-44", "figure"),
        ],
        Input("apply-filters-btn", "n_clicks"),
        State("chart-tabs", "value"),
    )
    def update_charts(_n_clicks, current_tab):
        """
        Updates the charts and KPI based on user-selected filters.
        """
        time_col = "waiting_time" if current_tab == "waiting" else "service_time"
        

        df_waiting_time_avg = df.groupby(['year', 'month'])[time_col].mean().reset_index()
        line_chart_waiting_times_by_year_month = charts_waiting_times.plot_line_chart_waiting_time_by_year_month(df_waiting_time_avg, value_column=time_col)

        avg_waiting_times = df.groupby('stop_area')[time_col].mean().reset_index()
        top_areas = avg_waiting_times.sort_values(time_col, ascending=False).head(6)
        bar_chart = charts_waiting_times.plot_bar_chart_waiting_by_stop_area(top_areas, value_column=time_col)

        top_waiting_by_vessel = (
            df.groupby('StandardVesselType')[time_col]
            .mean()
            .sort_values(ascending=False)
            .head(6)
        )
        bar_chart_2 = charts_waiting_times.plot_bar_chart_waiting_by_vessel_type(top_waiting_by_vessel, value_column=time_col)

        df["year_month"] = (
            df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
        )
        df_type_week = (
            df.groupby(["StandardVesselType", "year_month"])[time_col]
            .mean()
            .reset_index()
        )
        line_chart = charts_waiting_times.plot_line_chart_waiting_by_type_week(df_type_week, value_column=time_col)

        return (
            line_chart_waiting_times_by_year_month,
            bar_chart,
            line_chart,
            bar_chart_2,
        )
