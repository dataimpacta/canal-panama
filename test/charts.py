import plotly.graph_objects as go
import pandas as pd


def create_emissions_chart(df):

    # ➡️ Create a Plotly Figure Instead of Matplotlib
    fig = go.Figure()

    color_map = {2024: "#F78671"}  # Define custom colors
    opacity_map = {2024: 1}  # Define custom opacities
    width_map = {2024: 3}  # Define custom line widths


    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['emission_value'],
            mode='lines',
            name=str(year),  # Name in the legend list
            line=dict(color=color_map.get(year, "#757575"), width=width_map.get(year, 2)),
            opacity=opacity_map.get(year, 0.2),
            # showlegend=True,
            showlegend = bool(year == 2024)
        ))

    fig.update_layout(
        hovermode="x unified",  # Show all values for the same month
        # autosize=True,  # Automatically takes the Bootstrap column width
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
