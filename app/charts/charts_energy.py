import plotly.graph_objects as go

def plot_line_chart_energy_demand_by_year_week(df, top_padding_pct=0.1, bottom_padding_pct=0.1):
    """
    Function to create a line chart of emissions by year and month.
    """
    fig = go.Figure()

    if df.empty:
        return fig  # Return an empty figure

    # === Styling Setup ===
    last_year = df['year'].max()
    y_max = df['sum_energy'].max()
    y_min = df['sum_energy'].min()

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
            x=year_data['week'],
            y=year_data['sum_energy'],
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

        dragmode="zoom",

        hovermode="x unified",


        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 53)),
            ticktext=list(range(1, 52)),
            tickangle=0,
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