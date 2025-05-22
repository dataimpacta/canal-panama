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

    )
    def update_charts(_n_clicks):
        """
        Updates the charts and KPI based on user-selected filters.
        """

        df_waiting_time_avg = df.groupby(['year', 'month'])['waiting_time'].mean().reset_index()
        line_chart_waiting_times_by_year_month = charts_waiting_times.plot_line_chart_waiting_time_by_year_month(df_waiting_time_avg)


        avg_waiting_times = df.groupby('stop_area')['waiting_time'].mean().reset_index()
        top_areas = avg_waiting_times.sort_values('waiting_time', ascending=False).head(6)
        bar_chart = charts_waiting_times.plot_bar_chart_waiting_by_stop_area(top_areas)


        top_waiting_by_vessel = (
            df.groupby('StandardVesselType')['service_time']
            .mean()  
            .sort_values(ascending=False)
            .head(6)
        )
        bar_chart_2 = charts_waiting_times.plot_bar_chart_waiting_by_vessel_type(top_waiting_by_vessel)
        

        df["year_month"] = (
        df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2))   

        df_type_week = (
            df.groupby(["StandardVesselType", "year_month"])["waiting_time"]
            .mean()
            .reset_index()
        )
        line_chart = charts_waiting_times.plot_line_chart_waiting_by_type_week(df_type_week)



        return (
            line_chart_waiting_times_by_year_month,
            bar_chart,
            bar_chart_2,
            line_chart,
        )
