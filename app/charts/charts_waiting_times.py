"""
This module contains functions to create the charts related to emissions data.
"""

import plotly.graph_objects as go

def plot_line_chart_waiting_time_by_year_month(df):
    """
    Function to create a line chart of waiting times by year and month.
    """
    fig = go.Figure()

    last_year = df['year'].max()
    #y_max = df['waiting_time'].max()

    line_general_color = "#757575"
    line_general_width = 2
    line_general_opacity = 0.2

    highlight_color = "#02ACA3"
    highlight_opacity = 1
    highlight_width = 3

    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        is_latest = year == last_year
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['waiting_time'],
            mode='lines',
            name=str(year),
            line=dict(
                color=highlight_color if is_latest else line_general_color,
                width=highlight_width if is_latest else line_general_width
            ),
            opacity=highlight_opacity if is_latest else line_general_opacity,
            hovertemplate='%{y:.2f} hours',
            showlegend=True
        ))

    fig.update_layout(
        height=300,
        dragmode=False,
        hovermode="x unified",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar',
                      'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep',
                      'Oct', 'Nov', 'Dec'],
            showgrid=True
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
            x=-0.09, y=1.1,
            xanchor="left", yanchor="top",
            orientation="h"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig
