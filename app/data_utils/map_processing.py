"""Functions to process and visualize H3 map data."""

import json
from copy import deepcopy

import geopandas as gpd
from shapely.geometry import Polygon
from h3.api.basic_int import cell_to_boundary


def h3_to_polygon(h3_index):
    """Converts an H3 index to a Shapely Polygon.

    Accepts either an integer H3 index or a hexadecimal string.
    """
    if isinstance(h3_index, str):
        h3_index = int(h3_index, 16)
    boundary = cell_to_boundary(h3_index)
    return Polygon([(lng, lat) for lat, lng in boundary])

def generate_unique_polygons(df_with_resolution_id):
    """
    Generates a GeoDataFrame with unique resolution_id polygons.
    Only needs to be run once at app startup.
    """
    unique_ids = df_with_resolution_id[["resolution_id"]].drop_duplicates().copy()
    unique_ids["geometry"] = unique_ids["resolution_id"].apply(h3_to_polygon)
    return gpd.GeoDataFrame(unique_ids, geometry="geometry", crs="EPSG:4326")

def create_geojson_template(geo_df):
    """
    Converts a GeoDataFrame to a GeoJSON dictionary.
    """
    return json.loads(geo_df.to_json())

def inject_values_into_geojson(template, values_by_id):
    """
    Injects values into a GeoJSON template based on resolution_id.
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
    """
    From a DataFrame:
    - Groups by resolution_id and aggregates CO₂.
    - Merges with unique polygon geometries.
    - Injects values into the precomputed GeoJSON template.
    
    Returns:
        - df_grouped: GeoDataFrame with geometry and emissions
        - gdf_json: GeoJSON ready for plotting
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
