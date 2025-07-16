"""
This module contains functions to create the charts related to emissions data.
"""

import plotly.graph_objects as go

from app.theme import PRIMARY_COLOR, SOFT_GRAY, DARK_GRAY

def plot_line_chart_waiting_time_by_year_month(df, value_column="waiting_time", top_padding_pct=0.1, bottom_padding_pct=0.1):
    """
    Function to create a line chart of waiting times by year and month.
    """
    fig = go.Figure()

    last_year = df['year'].max()
    y_max = df[value_column].max()
    y_min = df[value_column].min()

    line_general_color = SOFT_GRAY
    line_general_width = 2
    line_general_opacity = 0.2

    highlight_color = PRIMARY_COLOR
    highlight_opacity = 1
    highlight_width = 3

    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        is_latest = year == last_year
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data[value_column],
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
        dragmode="zoom",
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
            range=[y_min * (1 - bottom_padding_pct), y_max * (1 + top_padding_pct)],
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="#000000",
            zerolinewidth=1.5,
            side="left",
            anchor="free",
            tickfont_color=DARK_GRAY,
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


def plot_bar_chart_waiting_by_stop_area(df, value_column="waiting_time"):

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['stop_area'],
        x=df[value_column],
        orientation='h',
        marker=dict(
            color=PRIMARY_COLOR,
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
            range=[-df[value_column].max() * 0.05, df[value_column].max()]
        ),
        yaxis=dict(
            showgrid=False,
            automargin=True,
            categoryorder="total ascending",
            tickfont=dict(size=12, color=DARK_GRAY),
        ),

        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig


def plot_bar_chart_waiting_by_vessel_type(df_summary, value_column="waiting_time"):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_summary.index,
        x=df_summary.values,
        orientation="h",
        marker=dict(
            color=SOFT_GRAY,
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
            tickfont=dict(size=12, color=DARK_GRAY),
        ),

        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"
    )

    return fig


def plot_line_chart_waiting_by_type_week(df, value_column="waiting_time", top_padding_pct=0.2, bottom_padding_pct=0.1):
    fig = go.Figure()

    if df.empty or "StandardVesselType" not in df.columns:
        return fig  # Return empty figure if no data
    
    df["year_month_int"] = df["year_month"].astype(int)

    # Top 3 vessel types by average waiting time
    avg_waiting = df.groupby("StandardVesselType")[value_column].mean()
    top_3_types = avg_waiting.sort_values(ascending=False).head(3).index.tolist()

    # Assign highlight color for top types
    highlight_colors = {vt: PRIMARY_COLOR for vt in top_3_types}

    y_max = df[value_column].max()
    y_min = df[value_column].min()

    for vessel_type in df["StandardVesselType"].unique():
        vessel_data = df[df["StandardVesselType"] == vessel_type]
        if vessel_data.empty:
            continue

        is_top = vessel_type in top_3_types

        fig.add_trace(go.Scatter(
            x=vessel_data["year_month"],
            y=vessel_data[value_column],
            mode="lines",
            name=vessel_type,
            line=dict(
                color=highlight_colors.get(vessel_type, SOFT_GRAY),
                width=3 if is_top else 2
            ),
            opacity=1 if is_top else 0.5,
            showlegend=is_top,
            hovertemplate=f'{vessel_type}: ' + '%{y:.2s} hrs<br>Month: %{x}<extra></extra>'
        ))

        sorted_year_month = sorted(df["year_month"].unique(), key=lambda x: int(x))

        fig.update_layout(
            height=300,
            dragmode="zoom",
            xaxis=dict(
                type="category",
                categoryorder="array",
                categoryarray=sorted_year_month,
                tickangle=45,
                ticklabelstep=5,
                showgrid=False
            ),
            yaxis=dict(
                range=[y_min * (1 - bottom_padding_pct), y_max * (1 + top_padding_pct)],
                showgrid=True,
                gridcolor="#D4D4D4",
                gridwidth=1,
                zeroline=True,
                zerolinecolor="#000000",
                zerolinewidth=1.5,
                side="left",
                anchor="free",
                tickfont_color=DARK_GRAY,
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