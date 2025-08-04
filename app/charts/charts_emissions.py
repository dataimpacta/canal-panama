"""
This module contains functions to create various charts related to emissions data.
"""

from dash import html
import plotly.graph_objects as go
import theme

def plot_kpi(name, value, start_date, end_date, comparison_label="", comparison_value=0, delta=None, delta_percent=None):
    """
    Function to create a KPI card with title, value, and comparison range.
    """
    # Format dates from YYYYMM to YYYY-MM
    def format_date(yyyymm):
        return f"{str(yyyymm)[:4]}-{str(yyyymm)[4:]}"
    
    return html.Div([
        # Title
        html.Span(name, style={
            "fontWeight": "bold",
            "color": "#555",
            "fontSize": "1rem"
        }),

        # Main value + delta percent
        html.Div([
            html.Span([
                html.Span(f"{value:,.0f}", style={
                    "fontSize": "1.5rem",
                    "fontWeight": "bold",
                    "color": "#222"
                }),
                html.Span(" tonnes CO2-eq", style={
                    "fontSize": "1.0rem",
                    "fontWeight": "bold",
                    "color": "#666",
                    "marginLeft": "0.25rem"
                }),
            ]),
            html.Span(
                f" ↑ {delta_percent:.2%}" if delta_percent is not None else "",
                style={
                    "color": theme.PRIMARY_COLOR,
                    "fontSize": "0.9rem",
                    "marginLeft": "0.75rem",
                    "fontWeight": "normal"
                }
            )
        ], style={"marginTop": "0.25rem", "marginBottom": "0.25rem"}),

        # Date range
        html.Div(f"From {format_date(start_date)} to {format_date(end_date)}", style={
            "color": "#666",
            "fontSize": "0.8rem",
            "marginBottom": "0.2rem"
        }),

        # Comparison value (optional delta)

        # html.Div(
        #     f"{comparison_label}: {comparison_value:,.0f} tonnes CO2-eq"
        #     + (f" (+{delta:,.0f})" if delta is not None else ""),
        #     style={"color": "#999", "fontSize": "0.8rem"}
        # )
    ])

def plot_line_chart_emissions_by_year_month(df, top_padding_pct=0.1, bottom_padding_pct=0.1):
    """
    Function to create a line chart of emissions by year and month.
    """
    fig = go.Figure()

    if df.empty:
        return fig  # Return an empty figure

    # === Styling Setup ===
    last_year = df['year'].max()
    y_max = df['co2_equivalent_t'].max()
    y_min = df['co2_equivalent_t'].min()

    line_general_color = theme.DARK_GRAY
    line_general_width = 2
    line_general_opacity = 0.2

    highlight_color = theme.PRIMARY_COLOR
    highlight_opacity = 1
    highlight_width = 3

    # === Add traces per year ===
    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        is_latest = year == last_year
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['co2_equivalent_t'],
            mode='lines+markers',
            name=str(year),
            line=dict(
                color=highlight_color if is_latest else line_general_color,
                width=highlight_width if is_latest else line_general_width
            ),
            marker=dict(
                color=highlight_color if is_latest else line_general_color,
                size=6 if is_latest else 4,
                opacity=highlight_opacity if is_latest else line_general_opacity
            ),
            opacity=highlight_opacity if is_latest else line_general_opacity,
            showlegend=True,
            hovertemplate = '%{y:,.0f} tonnes CO₂<extra></extra>',
        ))

    # === Layout ===
    fig.update_layout(
        height=300,

        dragmode="zoom",

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
            range=[y_min * (1 - bottom_padding_pct), y_max * (1 + top_padding_pct)],
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="#000000",
            zerolinewidth=1.5,
            side="left",
            anchor="free",
            tickfont_color=theme.DARK_GRAY,
            shift=-10,
            tickformat=","
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
            color=theme.PRIMARY_COLOR,
            line=dict(color="black", width=0)  # Border for better visibility
        ),
        hovertemplate='%{x:,.0f} tonnes CO₂<extra></extra>'

    ))

    fig.update_layout(
        height=300,  # Keeps height fixed

        dragmode=False,

        xaxis=dict(
            showgrid=True, gridcolor="lightgray", gridwidth=0,
            zeroline=False,  # Removes the thick zero line
            range=[-df.values.max() * 0.02, df.values.max()],
            tickformat=","
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder="total ascending",  # Ensure correct sorting
            automargin=True,  # Allows automatic space adjustment for labels
            tickmode="array",
            tickfont=dict(size=12),  # Make labels more readable
            tickfont_color=theme.DARK_GRAY,

        ),

        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="white"

    )

    return fig

def plot_line_chart_emissions_by_type_year_month(df, top_padding_pct=0.1, bottom_padding_pct=0.1):
    """
    Function to create a line chart of emissions by vessel type and year/month.
    """
    fig = go.Figure()

    if df.empty or "StandardVesselType" not in df.columns:
        return fig  # Return empty figure if no data

    # Top 3 vessel types by average emissions
    avg_emissions = df.groupby("StandardVesselType")["co2_equivalent_t"].sum()
    top_3_types = avg_emissions.sort_values(ascending=False).head(3).index.tolist()

    # Assign highlight color for top types
    base_colors = [theme.PRIMARY_DARK, theme.PRIMARY_COLOR, theme.PRIMARY_LIGHT]
    highlight_colors = {vt: color for vt, color in zip(top_3_types, base_colors)}

    # Format year_month for display
    def format_year_month(ym):
        """Convert 202301 format to 2023-01 format"""
        ym_str = str(ym)
        if len(ym_str) == 6:
            return f"{ym_str[:4]}-{ym_str[4:]}"
        return ym_str

    for vessel_type in df["StandardVesselType"].unique():
        vessel_data = df[df["StandardVesselType"] == vessel_type]
        if vessel_data.empty:
            continue  # skip if no data

        is_top = vessel_type in top_3_types
        avg_value = avg_emissions[vessel_type]

        # Format the year_month values for hover display
        formatted_dates = [format_year_month(ym) for ym in vessel_data["year_month"]]

        fig.add_trace(go.Scatter(
            x=vessel_data["year_month"],
            y=vessel_data["co2_equivalent_t"],
            mode="lines",
            name=vessel_type,
            line=dict(
                color=highlight_colors.get(vessel_type, theme.SOFT_GRAY),
                width=3 if is_top else 2
            ),
            opacity=1 if is_top else 0.5,
            showlegend=is_top,
            hovertemplate=f'{vessel_type}: ' + '%{y:.2s} t CO₂<br>Month: %{text}<extra></extra>',
            text=formatted_dates  # Use formatted dates for hover
        ))


    y_max = df["co2_equivalent_t"].max()
    y_min = df["co2_equivalent_t"].min()

    # Get unique year_month values and format them for display
    unique_year_months = sorted(df["year_month"].unique())
    formatted_labels = [format_year_month(ym) for ym in unique_year_months]
    
    # Show only 5 evenly spaced labels
    n_labels = 5
    if len(unique_year_months) > n_labels:
        # Calculate step to get exactly 5 labels
        step = (len(unique_year_months) - 1) // (n_labels - 1)
        selected_indices = [0]  # Always include first
        for i in range(1, n_labels - 1):
            selected_indices.append(i * step)
        selected_indices.append(len(unique_year_months) - 1)  # Always include last
        
        selected_year_months = [unique_year_months[i] for i in selected_indices]
        selected_labels = [formatted_labels[i] for i in selected_indices]
    else:
        selected_year_months = unique_year_months
        selected_labels = formatted_labels

    fig.update_layout(
        height=300,
        dragmode="zoom",
        xaxis=dict(
            showgrid=False,
            type="category",
            categoryorder="array",
            categoryarray=unique_year_months,
            ticktext=selected_labels,
            tickvals=selected_year_months,
            tickangle=0
        ),
        yaxis=dict(
            range=[y_min * (1 - bottom_padding_pct), y_max * (1 + top_padding_pct)],
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            zeroline=True,
            zerolinewidth=1.5,
            side="left",
            anchor="free",
            tickfont_color=theme.DARK_GRAY,
            shift=-10,
            tickformat=","
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
        colorscale=[[0, 'rgb(238,238,238)'], [1, theme.PRIMARY_COLOR]],

        marker_opacity=0.7,
        marker_line_width=0.5,
        marker_line_color="lightgray",


        name="",  # Prevents "trace 0" in the tooltip
        hovertemplate='%{z:,.0f} tonnes CO₂<extra></extra>',

        showscale=False,

        colorbar_title="Emissions (tonnes CO₂)",

        colorbar=dict(
            orientation="h",
            thickness=10,
            tickfont=dict(size=9),
            title="Emissions (tonnes CO₂)"
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
