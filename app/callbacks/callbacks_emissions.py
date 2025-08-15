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
            # Preserve existing selections even if not currently visible
            new_selected = selected_values

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
            start_idx = controls_emissions["date_range"].get("default_start_index", controls_emissions["date_range"]["min_index"])
        if end_idx is None:
            end_idx = controls_emissions["date_range"]["max_index"]
        if start_idx > end_idx:
            if ctx.triggered_id == "emissions--start-date":
                start_idx = end_idx
            else:
                end_idx = start_idx
        return start_idx, end_idx

    # Split the large callback into smaller, individual callbacks
    @app.callback(
        [
            Output("emissions--chart--1", "figure"),
            Output("emissions--chart--1-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("emissions--checklist--vessel", "value"),
            State("emissions--start-date", "value"),
            State("emissions--end-date", "value"),
        ]
    )
    def update_chart_1(_n_clicks, current_tab, selected_vessel_types, start_idx, end_idx):
        """Updates chart 1 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]
        
        # Filter data for this specific chart
        filtered_df = df_emissions[
            (df_emissions["year_month"] >= start_ym) &
            (df_emissions["year_month"] <= end_ym) &
            (df_emissions["StandardVesselType"].isin(selected_vessel_types))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 1: Line chart of emissions by year and month
        df_year_month = filtered_df.groupby(['year', 'month'], as_index=False)['co2_equivalent_t'].sum()
        fig = charts_emissions.plot_line_chart_emissions_by_year_month(df_year_month)
        return fig, fig

    @app.callback(
        [
            Output("emissions--chart--2", "figure"),
            Output("emissions--chart--2-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("emissions--checklist--vessel", "value"),
            State("emissions--start-date", "value"),
            State("emissions--end-date", "value"),
        ]
    )
    def update_chart_2(_n_clicks, current_tab, selected_vessel_types, start_idx, end_idx):
        """Updates chart 2 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]
        
        filtered_df = df_emissions[
            (df_emissions["year_month"] >= start_ym) &
            (df_emissions["year_month"] <= end_ym) &
            (df_emissions["StandardVesselType"].isin(selected_vessel_types))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 2: Bar chart of emissions by vessel type
        vessel_emissions = filtered_df.groupby('StandardVesselType')['co2_equivalent_t'].sum()
        df_type = vessel_emissions.nlargest(6)
        fig = charts_emissions.plot_bar_chart_emissions_by_type(df_type)
        return fig, fig

    @app.callback(
        [
            Output("emissions--chart--3", "figure"),
            Output("emissions--chart--3-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("emissions--checklist--vessel", "value"),
            State("emissions--start-date", "value"),
            State("emissions--end-date", "value"),
        ]
    )
    def update_chart_3(_n_clicks, current_tab, selected_vessel_types, start_idx, end_idx):
        """Updates chart 3 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]
        
        filtered_df = df_emissions[
            (df_emissions["year_month"] >= start_ym) &
            (df_emissions["year_month"] <= end_ym) &
            (df_emissions["StandardVesselType"].isin(selected_vessel_types))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 3: Map of emissions
        gdf_json, df_h3 = map_processing.generate_h3_map_data(
            filtered_df, unique_polygons_gdf, geojson_template
        )
        fig = charts_emissions.plot_emissions_map(gdf_json, df_h3)
        return fig, fig

    @app.callback(
        [
            Output("emissions--chart--4", "figure"),
            Output("emissions--chart--4-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("emissions--checklist--vessel", "value"),
            State("emissions--start-date", "value"),
            State("emissions--end-date", "value"),
        ]
    )
    def update_chart_4(_n_clicks, current_tab, selected_vessel_types, start_idx, end_idx):
        """Updates chart 4 only."""
        # Don't update charts if we don't have a valid tab
        if current_tab is None:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        if start_idx is None or end_idx is None:
            return {}, {}
        
        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]
        
        filtered_df = df_emissions[
            (df_emissions["year_month"] >= start_ym) &
            (df_emissions["year_month"] <= end_ym) &
            (df_emissions["StandardVesselType"].isin(selected_vessel_types))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 4: Line chart of emissions by type and year/month
        df_type_ym = filtered_df.groupby(['StandardVesselType', 'year_month'], as_index=False)['co2_equivalent_t'].sum()
        fig = charts_emissions.plot_line_chart_emissions_by_type_year_month(df_type_ym)
        return fig, fig

    @app.callback(
        Output("emissions--kpi--1", "children"),
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("emissions--checklist--vessel", "value"),
            State("emissions--start-date", "value"),
            State("emissions--end-date", "value"),
        ]
    )
    def update_kpi(_n_clicks, current_tab, selected_vessel_types, start_idx, end_idx):
        """Updates KPI only."""
        # Don't update if we don't have a valid tab
        if current_tab is None:
            return ""
        
        if start_idx is None or end_idx is None:
            return ""
        
        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]
        
        filtered_df = df_emissions[
            (df_emissions["year_month"] >= start_ym) &
            (df_emissions["year_month"] <= end_ym) &
            (df_emissions["StandardVesselType"].isin(selected_vessel_types))
        ]
        
        # Calculate KPI
        total_emissions = filtered_df["co2_equivalent_t"].sum()
        
        # Use the proper plot_kpi function for consistent styling
        kpi_component = charts_emissions.plot_kpi(
            name="Total Emissions in Panama’s Territorial Sea",
            value=total_emissions,
            start_date=f"{str(start_ym)}",
            end_date=f"{str(end_ym)}",
            comparison_label="",  # Not used since comparison is disabled
            comparison_value=0    # Not used since comparison is disabled
        )
        
        return kpi_component

    @app.callback(
        [
            Output("modal-no-data", "is_open"),
            Output("emissions--range-label", "children"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("chart-tabs-store", "data"),
            State("emissions--checklist--vessel", "value"),
            State("emissions--start-date", "value"),
            State("emissions--end-date", "value"),
        ]
    )
    def update_ui_elements(_n_clicks, current_tab, selected_vessel_types, start_idx, end_idx):
        """Updates UI elements only."""
        # Don't update if we don't have a valid tab
        if current_tab is None:
            return False, ""
        
        if start_idx is None or end_idx is None:
            return False, ""
        
        start_ym = controls_emissions["date_range"]["index_to_year_month"][start_idx]
        end_ym = controls_emissions["date_range"]["index_to_year_month"][end_idx]
        
        filtered_df = df_emissions[
            (df_emissions["year_month"] >= start_ym) &
            (df_emissions["year_month"] <= end_ym) &
            (df_emissions["StandardVesselType"].isin(selected_vessel_types))
        ]
        
        # Check if data exists
        has_data = len(filtered_df) > 0
        
        # Format date range
        def _fmt(ym: int) -> str:
            year = ym // 100
            month = ym % 100
            return f"{year}-{month:02d}"
        
        date_range_text = f"{_fmt(start_ym)} to {_fmt(end_ym)}"
        
        return not has_data, date_range_text
