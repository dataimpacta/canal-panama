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
        Output("energy--range-label", "children"),
        Input("energy--start-date", "value"),
        Input("energy--end-date", "value"),
    )
    def update_date_label(start_idx, end_idx):
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        def _fmt(yw):
            yw = str(yw)
            return f"{yw[:4]}-W{yw[4:]}"
        return f"{_fmt(start_yw)} to {_fmt(end_yw)}"

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


    @app.callback(
        [
            Output("energy--chart--1", "figure"),
            Output("energy--chart--1-fullscreen", "figure"),
            Output("energy--chart--2", "figure"),
            Output("energy--chart--2-fullscreen", "figure"),
            Output("energy--chart--3", "figure"),
            Output("energy--chart--3-fullscreen", "figure"),
            Output("energy--chart--4", "figure"),
            Output("energy--chart--4-fullscreen", "figure"),
            Output("energy--modal--no-data", "is_open"),
        ],
        Input("emissions--btn--refresh", "n_clicks"),
        [
            State("energy--checklist--country-before", "value"),
            State("energy--checklist--country-after", "value"),
            State("energy--start-date", "value"),
            State("energy--end-date", "value"),
        ]
    )
    def update_charts(_n_clicks, selected_country_before, selected_country_after, start_idx, end_idx):
        index_to_year_week = controls_energy["date_range"]["index_to_year_week"]
        start_yw = index_to_year_week[start_idx]
        end_yw = index_to_year_week[end_idx]
        filtered_df = df_energy[
            (df_energy["year_week"] >= start_yw) &
            (df_energy["year_week"] <= end_yw) &
            (df_energy["country_before"].isin(selected_country_before)) &
            (df_energy["country_after"].isin(selected_country_after))
        ]
        if filtered_df.empty:
            empty_fig = go.Figure()
            return (
                empty_fig, empty_fig,
                empty_fig, empty_fig,
                empty_fig, empty_fig,
                empty_fig, empty_fig,
                True
            )


        # For now, use the same chart for all outputs
        df_year_week = filtered_df.groupby(['year','week'])['sum_energy'].sum().reset_index()
        fig = charts_energy.plot_line_chart_energy_demand_by_year_week(df_year_week)
        
        country_col = "country_before"

        df_country = filtered_df.groupby(country_col)["sum_energy"].sum().reset_index()
        top_countries = df_country.sort_values(country_col, ascending=False).head(6)
        fig2 = charts_energy.plot_bar_chart_energy_by_country(top_countries, value_column=country_col)
        
        fig3 = charts_energy.generate_energy_bubble_map(filtered_df, country_role=country_col)

        fig4 = charts_energy.plot_sankey_before_after(filtered_df)

        return fig, fig, fig2, fig2, fig3, fig3, fig4, fig4, False
