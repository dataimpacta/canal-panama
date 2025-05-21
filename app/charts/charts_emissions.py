"""
This module contains functions to create various charts related to emissions data.
"""

from dash import html
import plotly.graph_objects as go


def plot_kpi(name, value, date, comparison_label, comparison_value, delta=None, delta_percent=None):
    """
    Function to create a KPI card with title, value, date, and comparison.
    """
    return html.Div([
        # Title and date on same line
        html.Span([
            name,
            html.Span(f" as of {date}",
                      style={"color": "#999",
                             "fontSize": "0.8rem",
                             "fontWeight": "normal"})
        ], style={"fontWeight": "bold", "color": "#555", "fontSize": "1rem"}),

        # Main value with optional delta % next to it
        html.Div([
            html.Span(f"{value:,.0f} tonnes",
                      style={"fontSize": "1.5rem",
                             "fontWeight": "bold",
                             "color": "#222"}),
            html.Span(f" ↑ {delta_percent:.2%}" if delta_percent is not None else "", style={
                "color": "#02ACA3", "fontSize": "1rem", "marginLeft": "1rem", "fontWeight": "bold"
            })
        ], style={"marginTop": "0.25rem", "marginBottom": "0.25rem"}),

        # Comparison below (e.g. Last Year: $82,655 (+$13,261))
        html.Div(f"{comparison_label}: {comparison_value:,.0f} tonnes"
                + (f" (+${delta:,.0f})" if delta is not None else ""),
            style={"color": "#999", "fontSize": "0.8rem"})
    ], className="border rounded p-3 bg-white")

def plot_line_chart_emissions_by_year_month(df):
    """
    Function to create a line chart of emissions by year and month.
    """
    fig = go.Figure()

    if df.empty:
        return fig  # Return an empty figure

    # === Styling Setup ===
    last_year = df['year'].max()
    #y_max = df['co2_equivalent_t'].max()

    line_general_color = "#757575"
    line_general_width = 2
    line_general_opacity = 0.2

    highlight_color = "#F78671"
    highlight_opacity = 1
    highlight_width = 3

    # === Add traces per year ===
    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        is_latest = year == last_year
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['co2_equivalent_t'],
            mode='lines',
            name=str(year),
            line=dict(
                color=highlight_color if is_latest else line_general_color,
                width=highlight_width if is_latest else line_general_width
            ),
            opacity=highlight_opacity if is_latest else line_general_opacity,
            showlegend=True,
            hovertemplate = '%{y:.2s}',
        ))

    # === Layout ===
    fig.update_layout(
        height=300,

        dragmode=False,

        hovermode="x unified",


        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=[
                'Jan', 'Feb', 'Mar', 
                'Apr', 'May', 'Jun', 
                'Jul', 'Aug', 'Sep', 
                'Oct', 'Nov', 'Dec'],
            tickangle=0,
            showgrid=True
        ),
        yaxis=dict(
            #range=[0, y_max * 1.05],  # Add small padding
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="#000000",
            zerolinewidth=1.5,
            side="left",
            anchor="free",
            tickfont_color="#757575",
            shift=-10
        ),

        showlegend=True,
        legend=dict(
            x=-0.09,
            y=1.1,
            xanchor="left",
            yanchor="top",
            orientation="h"
        ),

        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig

def plot_bar_chart_emissions_by_type(df):
    """
    Function to create a horizontal bar chart of emissions by vessel type.
    """
    fig = go.Figure()

    if df.empty:
        return fig

    # === Add traces ===
    fig.add_trace(go.Bar(
        y=df.index,  # Vessel types on Y-axis
        x=df.values,  # Emission values on X-axis
        orientation="h",
        marker=dict(
            color="#D9D9D9",  # Custom color for bars
            line=dict(color="black", width=0)  # Border for better visibility
        ),
        xhoverformat=".2s"

    ))

    fig.update_layout(
        height=300,  # Keeps height fixed

        dragmode=False,

        xaxis=dict(
            showgrid=True, gridcolor="lightgray", gridwidth=0,
            zeroline=False,  # Removes the thick zero line
            range=[-df.values.max() * 0.02, df.values.max()]
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder="total ascending",  # Ensure correct sorting
            automargin=True,  # Allows automatic space adjustment for labels
            tickmode="array",
            tickfont=dict(size=12),  # Make labels more readable
            tickfont_color="#757575",

        ),

        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"

    )

    return fig

def plot_line_chart_emissions_by_type_year_month(df):
    """
    Function to create a line chart of emissions by vessel type and year/month.
    """
    fig = go.Figure()

    if df.empty or "StandardVesselType" not in df.columns:
        return fig  # Return empty figure if no data

    # Top 3 vessel types by average emissions
    avg_emissions = df.groupby("StandardVesselType")["co2_equivalent_t"].mean()
    top_3_types = avg_emissions.sort_values(ascending=False).head(3).index.tolist()

    # Assign highlight colors only for available top types
    base_colors = ["#F78671", "#02ACA3", "#4273EE"]
    highlight_colors = {vt: color for vt, color in zip(top_3_types, base_colors)}

    for vessel_type in df["StandardVesselType"].unique():
        vessel_data = df[df["StandardVesselType"] == vessel_type]
        if vessel_data.empty:
            continue  # skip if no data

        is_top = vessel_type in top_3_types
        #avg_value = avg_emissions.get(vessel_type, 0)

        fig.add_trace(go.Scatter(
            x=vessel_data["year_month"],
            y=vessel_data["co2_equivalent_t"],
            mode="lines",
            name=vessel_type,
            line=dict(
                color=highlight_colors.get(vessel_type, "#757575"),
                width=3 if is_top else 2
            ),
            opacity=1 if is_top else 0.5,
            showlegend=is_top,
            hovertemplate=f'{vessel_type}: ' + '%{y:.2s}' + '<extra></extra>'
        ))


    fig.update_layout(
        height=300,
        dragmode=False,
        xaxis=dict(
            showgrid=False,
            type="category",
            tickangle=0,
            ticklabelstep=5
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="#000000",
            zerolinewidth=1.5,
            side="left",
            anchor="free",
            tickfont_color="#757575",
            shift=-10
        ),
        legend=dict(
            x=0, y=1,
            xanchor="left",
            yanchor="top",
            orientation="h"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig

def plot_emissions_map(gdf_json, gdf):
    """
    Function to create a map of emissions using Plotly.
    """

    if gdf.empty:
        raise ValueError("The GeoDataFrame is empty. Check processed data.")

    values = gdf["co2_equivalent_t"]

    fig = go.Figure(go.Choroplethmap(

        geojson=gdf_json,
        locations=gdf["resolution_id"],
        z=values,

        featureidkey="properties.resolution_id",
        colorscale=[[0, 'rgb(238,238,238)'], [1, 'rgb(247,134,113)']],

        marker_opacity=0.8,
        marker_line_width=0.5,
        marker_line_color="lightgray",


        name="",  # Prevents "trace 0" in the tooltip
        hovertemplate='%{z:.2s}',

        showscale=False,

        colorbar_title="Emissions (tons)",

        colorbar=dict(
            orientation="h",
            thickness=10,
            tickfont=dict(size=9),
            title="Emissions (tons)"
        )
    )
    )

    if gdf.empty:
        return fig  # Return an empty figure gracefully


    fig.update_layout(
        height=300,
        map=dict(
            center={"lat": 9.117975, "lon": -79.735890},
            zoom=7,
            style="light"  # or "white-bg", "stamen-terrain", etc.
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig
