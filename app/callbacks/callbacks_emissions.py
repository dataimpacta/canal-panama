# pylint: disable=import-error

"""Module for emissions dashboard callbacks."""

from dash import Input, Output, State, callback
from dash import html, ctx
import plotly.graph_objects as go

from data_utils import map_processing
from charts import charts_emissions


def setup_emissions_callbacks(app, df_emissions, index_to_year_month, master_emissions_vessel_types, geojson_template, unique_polygons_gdf):
    """
    These are the callbacks for the emissions dashboard.
    """
    @app.callback(
        Output("filter-emissions-type", "value"),
        Input("btn-select-all", "n_clicks"),
        Input("btn-clear-all", "n_clicks"),
        prevent_initial_call=True
    )
    def update_checklist(_select_all_clicks, _clear_all_clicks):
        """
        Updates the checklist based on button clicks.
        """
        triggered_id = ctx.triggered_id

        if triggered_id == "btn-select-all":
            return list(master_emissions_vessel_types)
        elif triggered_id == "btn-clear-all":
            return []


    @callback(
        [
            Output("chart-1", "figure"),
            Output("chart-2", "figure"),
            Output("chart-3", "figure"),
            Output("chart-4", "figure"),
            Output("kpi-1", "children"),
            Output("no-data-modal", "is_open"),
        ],
        Input("apply-filters-btn", "n_clicks"),
        [
            State("filter-emissions-type", "value"),
            State("filter-date-range", "value"),
        ]
    )
    def update_charts(_n_clicks, selected_vessel_types, selected_date_range):
        """
        Updates the charts and KPI based on user-selected filters.
        """
        #logger.info("🟢 Callback started")
        #t = time.time()

        start_ym = index_to_year_month[selected_date_range[0]]
        end_ym = index_to_year_month[selected_date_range[1]]

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
        #t = log_step("Filtered DataFrame", t)


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
                name="Total Emissions",
                value=latest_total,
                date=f"{str(latest_ym)}",
                comparison_label=comparison_label,
                comparison_value=previous_total
            )


        df_year_month = filtered_df.groupby(['year', 'month'])['co2_equivalent_t'].sum().reset_index()
        df_type = filtered_df.groupby('StandardVesselType')['co2_equivalent_t'].sum().sort_values(ascending=False).head(6)
        df_type_ym = filtered_df.groupby(['StandardVesselType', 'year_month'])['co2_equivalent_t'].sum().reset_index()

        gdf_json, df_h3 = map_processing.generate_h3_map_data(filtered_df, unique_polygons_gdf, geojson_template)

        #size_kb = len(json.dumps(gdf_json).encode("utf-8")) / 1024
        #logger.info("📦 GeoJSON payload size: %.2f KB", size_kb)
        #t = log_step("Injected values into GeoJSON", t)
        #logger.info("🟣 Callback finished. Total time: %.2f s", time.time() - t)

        return (
            charts_emissions.plot_line_chart_emissions_by_year_month(df_year_month),
            charts_emissions.plot_bar_chart_emissions_by_type(df_type),
            charts_emissions.plot_emissions_map(gdf_json, df_h3),
            charts_emissions.plot_line_chart_emissions_by_type_year_month(df_type_ym),
            kpi_component,
            False
        )
