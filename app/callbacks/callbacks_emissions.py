# pylint: disable=import-error

"""Module for emissions dashboard callbacks."""

from dash import Input, Output, State, callback
from dash import html, ctx
import plotly.graph_objects as go

from data_utils import map_processing
from charts import charts_emissions


def setup_emissions_callbacks(app, df_emissions, controls_emissions, geojson_template, unique_polygons_gdf):
    """
    These are the callbacks for the emissions dashboard.
    """
    @app.callback(
        Output("emissions--checklist--vessel", "value"),
        Input("emissions--btn--vessel-select", "n_clicks"),
        Input("emissions--btn--vessel-clear", "n_clicks"),
        prevent_initial_call=True
    )
    def update_checklist(_select_all_clicks, _clear_all_clicks):
        """
        Updates the checklist based on button clicks.
        """
        triggered_id = ctx.triggered_id

        if triggered_id == "emissions--btn--vessel-select":
            return list(controls_emissions["vessel_types"])
        elif triggered_id == "emissions--btn--vessel-clear":
            return []


    @app.callback(
        [
            Output("emissions--chart--1", "figure"),
            Output("emissions--chart--2", "figure"),
            Output("emissions--chart--3", "figure"),
            Output("emissions--chart--4", "figure"),
            Output("emissions--kpi--1", "children"),
            Output("modal-no-data", "is_open"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("emissions--checklist--vessel", "value"),
            State("emissions--range--date", "value"),
        ]
    )
    def update_charts(_n_clicks, selected_vessel_types, selected_date_range):
        """
        Updates the charts and KPI based on user-selected filters.
        """
        #logger.info("🟢 Callback started")
        #t = time.time()

        start_ym = controls_emissions["date_range"]["index_to_year_month"][selected_date_range[0]]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][selected_date_range[1]]

        filtered_df = df_emissions[
            (df_emissions["year_month"] >= start_ym) &
            (df_emissions["year_month"] <= end_ym) &
            (df_emissions["StandardVesselType"].isin(selected_vessel_types))
        ]

        if filtered_df.empty:
            empty_fig = go.Figure()
            return (
                empty_fig, empty_fig, empty_fig, empty_fig,
                html.Div("No data available", style={"color": "#999"}),
                True  # modal open
            )

        # KPI Calculation
        sorted_ym = sorted(filtered_df["year_month"].unique())
        kpi_component = html.Div("Insufficient data", style={"color": "#999"})  # fallback default

        if len(sorted_ym) >= 2:
            latest_ym = sorted_ym[-1]
            previous_ym = sorted_ym[-2]

            latest_total = filtered_df[
                filtered_df["year_month"] == latest_ym]["co2_equivalent_t"].sum()
            previous_total = filtered_df[filtered_df["year_month"] == previous_ym]["co2_equivalent_t"].sum()
            #change = latest_total - previous_total
            #pct_change = (change / previous_total * 100) if previous_total != 0 else 0

            comparison_label = "Last Month"
            kpi_component = charts_emissions.plot_kpi(
                name="Total Emissions in the Panama Canal",
                value=latest_total,
                start_date=f"{str(start_ym)}",
                end_date=f"{str(latest_ym)}",
                comparison_label=comparison_label,
                comparison_value=previous_total
            )


        df_year_month = filtered_df.groupby(['year', 'month'])['co2_equivalent_t'].sum().reset_index()
        df_type = filtered_df.groupby('StandardVesselType')['co2_equivalent_t'].sum().sort_values(ascending=False).head(6)
        df_type_ym = filtered_df.groupby(['StandardVesselType', 'year_month'])['co2_equivalent_t'].sum().reset_index()

        gdf_json, df_h3 = map_processing.generate_h3_map_data(filtered_df, unique_polygons_gdf, geojson_template)

        return (
            charts_emissions.plot_line_chart_emissions_by_year_month(df_year_month),
            charts_emissions.plot_bar_chart_emissions_by_type(df_type),
            charts_emissions.plot_emissions_map(gdf_json, df_h3),
            charts_emissions.plot_line_chart_emissions_by_type_year_month(df_type_ym),
            kpi_component,
            False
        )
