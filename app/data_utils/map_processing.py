"""Functions to process and visualize H3 map data."""

import json
from copy import deepcopy

import geopandas as gpd
from shapely.geometry import Polygon
from h3.api.basic_int import cell_to_boundary


def h3_to_polygon(h3_index):
    """Convert an H3 index to a Shapely ``Polygon``.

    Parameters
    ----------
    h3_index : int | str
        H3 index as integer or hexadecimal string.

    Returns
    -------
    Polygon
        Polygon representing the H3 cell.
    """
    if isinstance(h3_index, str):
        h3_index = int(h3_index, 16)
    boundary = cell_to_boundary(h3_index)
    return Polygon([(lng, lat) for lat, lng in boundary])

def generate_unique_polygons(df_with_resolution_id):
    """Create a GeoDataFrame of unique ``resolution_id`` polygons.

    Parameters
    ----------
    df_with_resolution_id : pandas.DataFrame
        DataFrame containing a ``resolution_id`` column.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with one row per unique ``resolution_id`` and geometry.
    """
    unique_ids = df_with_resolution_id[["resolution_id"]].drop_duplicates().copy()
    unique_ids["geometry"] = unique_ids["resolution_id"].apply(h3_to_polygon)
    return gpd.GeoDataFrame(unique_ids, geometry="geometry", crs="EPSG:4326")

def create_geojson_template(geo_df):
    """Convert a GeoDataFrame to a GeoJSON dictionary.

    Parameters
    ----------
    geo_df : geopandas.GeoDataFrame
        GeoDataFrame to convert.

    Returns
    -------
    dict
        GeoJSON representation of the input GeoDataFrame.
    """
    return json.loads(geo_df.to_json())

def inject_values_into_geojson(template, values_by_id):
    """Inject values into a GeoJSON template.

    Parameters
    ----------
    template : dict
        Base GeoJSON template containing features with ``resolution_id``.
    values_by_id : dict
        Mapping of ``resolution_id`` to numeric values.

    Returns
    -------
    dict
        GeoJSON with only features that have a positive value.
    """
    updated_geojson = {"type": "FeatureCollection", "features": []}
    for feature in template["features"]:
        res_id = feature["properties"]["resolution_id"]
        value = values_by_id.get(res_id, 0)
        if value > 0:
            new_feature = deepcopy(feature)
            new_feature["properties"]["value"] = value
            updated_geojson["features"].append(new_feature)
    return updated_geojson

def generate_h3_map_data(df_to_map, gdf_polygons, precomputed_geojson_template):
    """Prepare map data for H3-based emissions visualisation.

    Parameters
    ----------
    df_to_map : pandas.DataFrame
        DataFrame with ``resolution_id`` and ``co2_equivalent_t`` columns.
    gdf_polygons : geopandas.GeoDataFrame
        GeoDataFrame containing polygon geometries for each ``resolution_id``.
    precomputed_geojson_template : dict
        GeoJSON template produced by :func:`create_geojson_template`.

    Returns
    -------
    tuple[dict, geopandas.GeoDataFrame]
        GeoJSON ready for plotting and grouped GeoDataFrame with geometry.
    """
    # OPTIMIZATION: More efficient groupby and merge
    # Use as_index=False to avoid reset_index() call
    df_grouped = df_to_map.groupby("resolution_id", as_index=False)["co2_equivalent_t"].sum()
    
    # OPTIMIZATION: Use merge with only necessary columns
    df_grouped = df_grouped.merge(
        gdf_polygons[["resolution_id", "geometry"]], 
        on="resolution_id", 
        how="left"
    )

    # OPTIMIZATION: More efficient dictionary creation
    values_by_id = dict(zip(df_grouped["resolution_id"], df_grouped["co2_equivalent_t"]))
    gdf_json = inject_values_into_geojson(precomputed_geojson_template, values_by_id)

    return gdf_json, df_grouped

