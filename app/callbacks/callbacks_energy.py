# pylint: disable=import-error

"""Module for energy dashboard callbacks."""

from dash import Input, Output, State, callback, ctx
from dash import html
import plotly.graph_objects as go

from charts import charts_energy 

def setup_energy_callbacks(app, df_energy, controls_energy):
    """
    Set up all callbacks for the energy dashboard.
    """

    @app.callback(
        Output("energy--start-date", "value"),
        Output("energy--end-date", "value"),
        Input("energy--start-date", "value"),
        Input("energy--end-date", "value"),
        prevent_initial_call=True,
    )
    def validate_date_range(start_idx, end_idx):
        if start_idx is None:
            start_idx = controls_energy["date_range"]["min_index"]
        if end_idx is None:
            end_idx = controls_energy["date_range"]["max_index"]
        if start_idx > end_idx:
            if ctx.triggered_id == "energy--start-date":
                start_idx = end_idx
            else:
                end_idx = start_idx
        return start_idx, end_idx

    @app.callback(
        Output("energy--checklist--country-before", "options"),
        Output("energy--checklist--country-before", "value"),
        Input("energy--btn--country-before-select", "n_clicks"),
        Input("energy--btn--country-before-clear", "n_clicks"),
        Input("energy--input--country-before-search", "value"),
        State("energy--checklist--country-before", "value"),
        prevent_initial_call=True,
    )
    def update_country_before_checklist(_select_all, _clear_all, search_value, selected_values):
        country_before = controls_energy["country_before"]
        if search_value:
            search_value = search_value.lower()
            filtered = [v for v in country_before if search_value in v.lower()]
        else:
            filtered = country_before
        options = [{"label": v, "value": v} for v in filtered]
        triggered_id = ctx.triggered_id
        if triggered_id == "energy--btn--country-before-select":
            new_selected = list(filtered)
        elif triggered_id == "energy--btn--country-before-clear":
            new_selected = []
        else:
            new_selected = selected_values
        return options, new_selected

    @app.callback(
        Output("energy--role-chart2", "data"),
        Input("energy--dropdown-chart2", "value"),
        prevent_initial_call=True,
    )
    def store_role_chart2(value):
        return value

    @app.callback(
        Output("energy--role-chart3", "data"),
        Input("energy--dropdown-chart3", "value"),
        prevent_initial_call=True,
    )
    def store_role_chart3(value):
        return value

    @app.callback(
        Output("energy--checklist--country-after", "options"),
        Output("energy--checklist--country-after", "value"),
        Input("energy--btn--country-after-select", "n_clicks"),
        Input("energy--btn--country-after-clear", "n_clicks"),
        Input("energy--input--country-after-search", "value"),
        State("energy--checklist--country-after", "value"),
        prevent_initial_call=True,
    )
    def update_country_after_checklist(_select_all, _clear_all, search_value, selected_values):
        country_after = controls_energy["country_after"]
        if search_value:
            search_value = search_value.lower()
            filtered = [v for v in country_after if search_value in v.lower()]
        else:
            filtered = country_after
        options = [{"label": v, "value": v} for v in filtered]
        triggered_id = ctx.triggered_id
        if triggered_id == "energy--btn--country-after-select":
            new_selected = list(filtered)
        elif triggered_id == "energy--btn--country-after-clear":
            new_selected = []
        else:
            new_selected = selected_values
        return options, new_selected

    # Split the large callback into smaller, individual callbacks
    @app.callback(
        [
            Output("energy--chart--1", "figure"),
            Output("energy--chart--1-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("energy--checklist--country-before", "value"),
            State("energy--checklist--country-after", "value"),
            State("energy--start-date", "value"),
            State("energy--end-date", "value"),
        ]
    )
    def update_chart_1(_n_clicks, selected_country_before, selected_country_after, start_idx, end_idx):
        """Updates chart 1 only."""
        if start_idx is None or end_idx is None:
            return {}, {}
        
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        
        before_map = controls_energy["country_before_map"]
        after_map = controls_energy["country_after_map"]
        selected_before_codes = [before_map.get(n, n) for n in selected_country_before]
        selected_after_codes = [after_map.get(n, n) for n in selected_country_after]

        filtered_df = df_energy[
            (df_energy["year_week"] >= start_yw) &
            (df_energy["year_week"] <= end_yw) &
            (df_energy["country_before"].isin(selected_before_codes)) &
            (df_energy["country_after"].isin(selected_after_codes))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 1: Line chart of energy demand by year and week
        df_year_week = filtered_df.groupby(['year','week'])['sum_energy'].sum().reset_index()
        fig = charts_energy.plot_line_chart_energy_demand_by_year_week(df_year_week)
        return fig, fig

    @app.callback(
        [
            Output("energy--chart--2", "figure"),
            Output("energy--chart--2-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        Input("energy--role-chart2", "data"),
        [
            State("energy--checklist--country-before", "value"),
            State("energy--checklist--country-after", "value"),
            State("energy--start-date", "value"),
            State("energy--end-date", "value"),
        ]
    )
    def update_chart_2(_n_clicks, role_chart2, selected_country_before, selected_country_after, start_idx, end_idx):
        """Updates chart 2 only."""
        if start_idx is None or end_idx is None:
            return {}, {}
        
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        
        before_map = controls_energy["country_before_map"]
        after_map = controls_energy["country_after_map"]
        selected_before_codes = [before_map.get(n, n) for n in selected_country_before]
        selected_after_codes = [after_map.get(n, n) for n in selected_country_after]

        filtered_df = df_energy[
            (df_energy["year_week"] >= start_yw) &
            (df_energy["year_week"] <= end_yw) &
            (df_energy["country_before"].isin(selected_before_codes)) &
            (df_energy["country_after"].isin(selected_after_codes))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 2: Bar chart of energy by country
        country_col = "country_before_name" if role_chart2 == "country_before" else "country_after_name"
        df_country = filtered_df.groupby(country_col)["sum_energy"].sum().reset_index()
        top_countries = df_country.sort_values("sum_energy", ascending=False).head(6)
        fig = charts_energy.plot_bar_chart_energy_by_country(top_countries, value_column=country_col)
        return fig, fig

    @app.callback(
        [
            Output("energy--chart--3", "figure"),
            Output("energy--chart--3-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        Input("energy--role-chart3", "data"),
        [
            State("energy--checklist--country-before", "value"),
            State("energy--checklist--country-after", "value"),
            State("energy--start-date", "value"),
            State("energy--end-date", "value"),
        ]
    )
    def update_chart_3(_n_clicks, role_chart3, selected_country_before, selected_country_after, start_idx, end_idx):
        """Updates chart 3 only."""
        if start_idx is None or end_idx is None:
            return {}, {}
        
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        
        before_map = controls_energy["country_before_map"]
        after_map = controls_energy["country_after_map"]
        selected_before_codes = [before_map.get(n, n) for n in selected_country_before]
        selected_after_codes = [after_map.get(n, n) for n in selected_country_after]

        filtered_df = df_energy[
            (df_energy["year_week"] >= start_yw) &
            (df_energy["year_week"] <= end_yw) &
            (df_energy["country_before"].isin(selected_before_codes)) &
            (df_energy["country_after"].isin(selected_after_codes))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 3: Bubble map
        fig = charts_energy.generate_energy_bubble_map(filtered_df, country_role=role_chart3)
        return fig, fig

    @app.callback(
        [
            Output("energy--chart--4", "figure"),
            Output("energy--chart--4-fullscreen", "figure"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("energy--checklist--country-before", "value"),
            State("energy--checklist--country-after", "value"),
            State("energy--start-date", "value"),
            State("energy--end-date", "value"),
        ]
    )
    def update_chart_4(_n_clicks, selected_country_before, selected_country_after, start_idx, end_idx):
        """Updates chart 4 only."""
        if start_idx is None or end_idx is None:
            return {}, {}
        
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        
        before_map = controls_energy["country_before_map"]
        after_map = controls_energy["country_after_map"]
        selected_before_codes = [before_map.get(n, n) for n in selected_country_before]
        selected_after_codes = [after_map.get(n, n) for n in selected_country_after]

        filtered_df = df_energy[
            (df_energy["year_week"] >= start_yw) &
            (df_energy["year_week"] <= end_yw) &
            (df_energy["country_before"].isin(selected_before_codes)) &
            (df_energy["country_after"].isin(selected_after_codes))
        ]
        
        if filtered_df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig
        
        # Chart 4: Sankey diagram
        fig = charts_energy.plot_sankey_before_after(filtered_df, origin_col="country_before_name", dest_col="country_after_name")
        return fig, fig

    @app.callback(
        Output("energy--modal--no-data", "is_open"),
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("energy--checklist--country-before", "value"),
            State("energy--checklist--country-after", "value"),
            State("energy--start-date", "value"),
            State("energy--end-date", "value"),
        ]
    )
    def update_modal(_n_clicks, selected_country_before, selected_country_after, start_idx, end_idx):
        """Updates modal only."""
        if start_idx is None or end_idx is None:
            return False
        
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        
        before_map = controls_energy["country_before_map"]
        after_map = controls_energy["country_after_map"]
        selected_before_codes = [before_map.get(n, n) for n in selected_country_before]
        selected_after_codes = [after_map.get(n, n) for n in selected_country_after]

        filtered_df = df_energy[
            (df_energy["year_week"] >= start_yw) &
            (df_energy["year_week"] <= end_yw) &
            (df_energy["country_before"].isin(selected_before_codes)) &
            (df_energy["country_after"].isin(selected_after_codes))
        ]
        
        # Check if data exists
        has_data = len(filtered_df) > 0
        return not has_data

    @app.callback(
        Output("energy--range-label", "children"),
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("energy--start-date", "value"),
            State("energy--end-date", "value"),
        ]
    )
    def update_range_label(_n_clicks, start_idx, end_idx):
        """Updates range label only."""
        if start_idx is None or end_idx is None:
            return ""
        
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        
        # Format date range label
        def _fmt(yw):
            yw = str(yw)
            return f"{yw[:4]}-W{yw[4:]}"
        date_range_label = f"{_fmt(start_yw)} to {_fmt(end_yw)}"
        
        return date_range_label
