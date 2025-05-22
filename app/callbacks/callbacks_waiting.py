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
        
        return (
            line_chart_waiting_times_by_year_month,
            line_chart_waiting_times_by_year_month,
            line_chart_waiting_times_by_year_month,
            line_chart_waiting_times_by_year_month,
        )
