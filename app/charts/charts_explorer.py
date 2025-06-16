"""Charts for the explorer tab."""

import plotly.graph_objects as go


def plot_line_chart(df, value_column):
    """Create a simple line chart."""
    fig = go.Figure()

    if df.empty:
        return fig

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df[value_column],
        mode="lines",
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_title="Date",
        yaxis_title=value_column.replace("_", " ").title(),
        plot_bgcolor="white",
    )
    return fig
