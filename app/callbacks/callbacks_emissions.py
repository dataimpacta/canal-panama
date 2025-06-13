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
        Output("emissions--checklist--vessel", "options"),
        Output("emissions--checklist--vessel", "value"),
        Input("emissions--btn--vessel-select", "n_clicks"),
        Input("emissions--btn--vessel-clear", "n_clicks"),
        Input("emissions--input--vessel-search", "value"),
        State("emissions--checklist--vessel", "value"),
        prevent_initial_call=True,
    )
    def update_vessel_checklist(_select_all_clicks, _clear_all_clicks,
                                search_value, selected_values):
        """Update vessel checklist options and selected values."""
        vessel_types = controls_emissions["vessel_types"]

        if search_value:
            search_value = search_value.lower()
            filtered = [v for v in vessel_types if search_value in v.lower()]
        else:
            filtered = vessel_types

        options = [{"label": v, "value": v} for v in filtered]

        triggered_id = ctx.triggered_id
        if triggered_id == "emissions--btn--vessel-select":
            new_selected = list(filtered)
        elif triggered_id == "emissions--btn--vessel-clear":
            new_selected = []
        else:
            new_selected = [v for v in selected_values if v in filtered]

        return options, new_selected

    @app.callback(
        Output("emissions--start-date", "value"),
        Output("emissions--end-date", "value"),
        Input("emissions--start-date", "value"),
        Input("emissions--end-date", "value"),
        prevent_initial_call=True,
    )
    def validate_date_range(start_idx, end_idx):
        """Ensure the start date is not after the end date."""
        if start_idx is None:
            start_idx = controls_emissions["date_range"]["min_index"]
        if end_idx is None:
            end_idx = controls_emissions["date_range"]["max_index"]
        if start_idx > end_idx:
            if ctx.triggered_id == "emissions--start-date":
                start_idx = end_idx
            else:
                end_idx = start_idx
        return start_idx, end_idx

    @app.callback(
        Output("emissions--range-label", "children"),
        Input("emissions--start-date", "value"),
        Input("emissions--end-date", "value"),
    )
    def update_date_label(start_idx, end_idx):
        """Show the selected year-month range below the dropdowns."""
        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]

        def _fmt(ym: int) -> str:
            ym = str(ym)
            return f"{ym[:4]}-{ym[4:]}"

        return f"{_fmt(start_ym)} to {_fmt(end_ym)}"


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
            State("emissions--start-date", "value"),
            State("emissions--end-date", "value"),
        ]
    )
    def update_charts(_n_clicks, selected_vessel_types, start_idx, end_idx):
        """
        Updates the charts and KPI based on user-selected filters.
        """
        #logger.info("🟢 Callback started")
        #t = time.time()

        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]

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
