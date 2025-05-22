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


def plot_bar_chart_waiting_by_stop_area(df):

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['stop_area'],
        x=df['waiting_time'],
        orientation='h',
        marker=dict(
            color="#02ACA3",  # Custom blue-green color
            line=dict(color="black", width=0)
        ),
        hovertemplate='%{y}<br>%{x:.2f} hours<extra></extra>'
    ))

    fig.update_layout(
        height=300,
        dragmode=False,

        xaxis=dict(
            showgrid=True, gridcolor="lightgray", gridwidth=0,
            zeroline=False,
            range=[-df['waiting_time'].max() * 0.05, df['waiting_time'].max()]
        ),
        yaxis=dict(
            showgrid=False,
            automargin=True,
            categoryorder="total ascending",
            tickfont=dict(size=12, color="#757575"),
        ),

        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig


def plot_bar_chart_waiting_by_vessel_type(df_summary):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_summary.index,
        x=df_summary.values,
        orientation="h",
        marker=dict(
            color="#D9D9D9",  
            line=dict(color="black", width=0)
        ),
        hovertemplate='%{y}<br>%{x:.2f} hours<extra></extra>'
    ))

    fig.update_layout(
        height=300,
        dragmode=False,

        xaxis=dict(
            showgrid=True, gridcolor="lightgray", gridwidth=0,
            zeroline=False,
            range=[-0.5, df_summary.max()]
        ),
        yaxis=dict(
            showgrid=False,
            automargin=True,
            categoryorder="total ascending",
            tickfont=dict(size=12, color="#757575"),
        ),

        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig


def plot_line_chart_waiting_by_type_week(df):
    fig = go.Figure()

    if df.empty or "StandardVesselType" not in df.columns:
        return fig  # Return empty figure if no data

    # Top 3 vessel types by average waiting time
    avg_waiting = df.groupby("StandardVesselType")["waiting_time"].mean()
    top_3_types = avg_waiting.sort_values(ascending=False).head(3).index.tolist()

    # Assign highlight colors only for available top types
    base_colors = ["#F78671", "#02ACA3", "#4273EE"]
    highlight_colors = {vt: color for vt, color in zip(top_3_types, base_colors)}

    for vessel_type in df["StandardVesselType"].unique():
        vessel_data = df[df["StandardVesselType"] == vessel_type]
        if vessel_data.empty:
            continue

        is_top = vessel_type in top_3_types

        fig.add_trace(go.Scatter(
            x=vessel_data["year_month"],
            y=vessel_data["waiting_time"],
            mode="lines",
            name=vessel_type,
            line=dict(
                color=highlight_colors.get(vessel_type, "#757575"),
                width=3 if is_top else 2
            ),
            opacity=1 if is_top else 0.5,
            showlegend=is_top,
            hovertemplate=f'{vessel_type}: ' + '%{y:.2s} hrs<br>Month: %{x}<extra></extra>'
        ))

    fig.update_layout(
        height=300,
        dragmode=False,
        xaxis=dict(
            type="category",
            tickangle=45,
            ticklabelstep=5,
            showgrid=False
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
            x=0,
            y=1,
            xanchor="left",
            yanchor="top",
            orientation="h"
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig