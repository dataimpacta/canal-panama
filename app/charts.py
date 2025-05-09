import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import geopandas as gpd


# Emissions

def plot_line_chart_emissions_by_year_month(df):

    # ➡️ Create a Plotly Figure Instead of Matplotlib
    fig = go.Figure()

    color_map = {2024: "#F78671"}  # Define custom colors
    opacity_map = {2024: 1}  # Define custom opacities
    width_map = {2024: 3}  # Define custom line widths


    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['co2_equivalent_t'],
            mode='lines',
            name=str(year),  # Name in the legend list
            line=dict(color=color_map.get(year, "#757575"), width=width_map.get(year, 2)),
            opacity=opacity_map.get(year, 0.2),
            # showlegend=True,
            showlegend = bool(year == 2024)
        ))

    fig.update_layout(
        hovermode="x unified",  # Show all values for the same month
        #autosize=True,  # Automatically takes the Bootstrap column width
        width = 500,
        height=300,  # Keeps height fixed to avoid stretching
        dragmode=False,  # Disable all user interactions
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            tickangle=0, # La dirección del texto
            showgrid=False, gridcolor="lightgray", gridwidth=0.5,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="lightgray", gridwidth=1,
            side="left",  # Ensures Y-axis labels stay on the left
            position=0  # Moves Y-axis slightly left
        ),
        showlegend = True, ## Por ahora lo voy a dejar así mientras termino el resto
        legend=dict(
            x=-0.09,  # Moves legend to the left
            y=1.1,  # Moves legend above the chart
            xanchor="left",
            yanchor="top",
            orientation="h"  # Horizontal legend
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )


    return fig  

def plot_bar_chart_emissions_by_type(df):
    
    # ➡️ Create a Plotly Bar Chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df.index,  # Vessel types on Y-axis
        x=df.values,  # Emission values on X-axis
        orientation="h",  # Horizontal bars
        marker=dict(
            color="#D9D9D9",  # Custom color for bars
            line=dict(color="black", width=0)  # Border for better visibility
        ),
        text=df.values,  # Show values on bars
        textposition="inside"  # Place text inside the bars
    ))

    fig.update_layout(
        hovermode="y unified",  # Show all values for the same vessel type
        #autosize=True,
        width=500,
        height=300,  # Keeps height fixed
        dragmode=False,  # Disable user interactions
        xaxis=dict(
            showgrid=False, gridcolor="lightgray", gridwidth=0,
            zeroline=False,  # Removes the thick zero line
            range=[-df.values.max() * 0.02, df.values.max()] 
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder="total ascending",  # Ensure correct sorting
            #position=0
            automargin=True,  # Allows automatic space adjustment for labels
            tickmode="array",
            tickfont=dict(size=13),  # Make labels more readable
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig

def plot_line_chart_emissions_by_type_year_month(df):
    
    fig = go.Figure()

    # Generate a color palette for different vessel types
    unique_vessel_types = df["StandardVesselType"].unique()

    for vessel_type in unique_vessel_types:
        vessel_data = df[df["StandardVesselType"] == vessel_type]

        fig.add_trace(go.Scatter(
            x=vessel_data["year_month"],  # Time series
            y=vessel_data["co2_equivalent_t"],  # Emission values
            mode="lines",
            name=vessel_type,  # Name in the legend
            #line=dict(color=color_map[vessel_type], width=2),
            opacity=0.8
        ))

    fig.update_layout(
        hovermode="x unified",  # Show all vessel emissions for a given month
        width=500,
        #width=800,
        height=300,
        dragmode=False,
        xaxis=dict(
            showgrid=True, gridcolor="lightgray", gridwidth=0.5,
            tickangle=0,  # Rotate labels for better readability
            type="category",  # Ensure categorical formatting of dates
        ),
        yaxis=dict(
            showgrid=True, gridcolor="lightgray", gridwidth=1,
        ),
        legend=dict(
            x=0, y=1, xanchor="left", yanchor="top",
            orientation="h"  # Horizontal legend for better readability
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig


def plot_emissions_map(gdf_json, gdf):
    if gdf.empty:
        raise ValueError("The GeoDataFrame is empty. Check processed data.")

    values = gdf["co2_equivalent_t"]

    fig = go.Figure(go.Choroplethmap(
        geojson=gdf_json,
        locations=gdf["resolution_id"],
        z=values,
        featureidkey="properties.resolution_id",
        colorscale="OrRd",
        marker_opacity=0.5,
        marker_line_width=0,
        colorbar_title="Emissions (tons)"
    ))

    fig.update_layout(
        map=dict(
            center={"lat": 9.117975, "lon": -79.735890},
            zoom=7,
            style="light"  # or "white-bg", "stamen-terrain", etc.
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width=500,
        height=300
    )

    return fig