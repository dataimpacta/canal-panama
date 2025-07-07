import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import pycountry



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


def plot_bar_chart_energy_by_country(df, value_column="country_before"):

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df[value_column],
        x=df['sum_energy'],
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
            range=[-df['sum_energy'].max() * 0.05, df['sum_energy'].max()]
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


def plot_sankey_before_after(df, origin_col="country_before", dest_col="country_after", top_n=10,):
    """
    Generate a Sankey diagram showing the top N energy flows between countries.

    Parameters:
    - df (pd.DataFrame): Input dataframe with columns ['country_before', 'country_after', 'sum_energy']
    - top_n (int): Number of top flows to include
    - title (str): Title of the Sankey diagram

    Returns:
    - fig (plotly.graph_objects.Figure): Sankey diagram figure
    """
    # Step 1: Group by origin and destination
    sankey_data = (
        df.groupby([origin_col, dest_col])['sum_energy']
        .sum()
        .reset_index()
    )

    # Step 2: Get top N flows
    sankey_data = sankey_data.sort_values(by='sum_energy', ascending=False).head(top_n)

    # Step 3: Distinguish labels
    sankey_data['origin_label'] = sankey_data[origin_col]
    sankey_data['dest_label'] = sankey_data[dest_col] + " (dest)"

    # Step 4: Unique labels
    all_labels = pd.concat([sankey_data['origin_label'], sankey_data['dest_label']]).unique()
    label_to_index = {label: i for i, label in enumerate(all_labels)}

    # Simple color palette
    node_color = "#4273EE"  # blue
    link_color = "#D9D9D9"  # gray
    node_colors = [node_color] * len(all_labels)
    link_colors = [link_color] * len(sankey_data)

    # Step 5: Create Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            label=all_labels,
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            color=node_colors,
        ),
        link=dict(
            source=sankey_data['origin_label'].map(label_to_index),
            target=sankey_data['dest_label'].map(label_to_index),
            value=sankey_data['sum_energy'],
            color=link_colors,
        )
    )])
    fig.update_layout(
        height=300,  # Increased height for better visibility
        margin=dict(l=5, r=5, t=5, b=5)
    )
    return fig



def get_iso3(code2):
    """Convert 2-letter to 3-letter ISO code (for Plotly's map)"""
    try:
        return pycountry.countries.get(alpha_2=code2).alpha_3
    except:
        return None


def get_country_name(code2):
    """Return full country name from ISO-2 code."""
    try:
        return pycountry.countries.get(alpha_2=code2).name
    except:
        return code2

def generate_energy_bubble_map(df, country_role='country_before', title="Energy by Country"):
    """
    Creates a bubble map using Plotly, where bubble size = sum_energy for each country.

    Parameters:
    - df: pandas DataFrame with ['country_before', 'country_after', 'country_code_before', 'country_code_after', 'sum_energy']
    - country_role: 'country_before' or 'country_after'
    - title: Chart title

    Returns:
    - fig: Plotly figure
    """

    # Step 1: Choose role and corresponding ISO code
    #country_col = country_role
    #iso_code_col = 'country_code_before' if country_role == 'country_before' else 'country_code_after'

    # Step 2: Group by country
    grouped = df.groupby([country_role])['sum_energy'].sum().reset_index()
    grouped.columns = ['iso2', 'sum_energy']

    # Step 3: Convert ISO-2 to ISO-3 (for Plotly)
    grouped['iso3'] = grouped['iso2'].apply(get_iso3)
    grouped = grouped.dropna(subset=['iso3'])  # drop rows without a valid ISO3

    # Step 4: Plot
    fig = px.scatter_geo(
        grouped,
        locations="iso3",
        size="sum_energy",
        projection="natural earth",
    )

    fig.update_layout(geo=dict(showland=True, landcolor="LightGrey"))
    return fig