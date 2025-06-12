import pandas as pd
from shapely.geometry import Polygon

from app.data_utils.map_processing import h3_to_polygon, generate_unique_polygons


def test_h3_to_polygon_returns_polygon():
    index = "8866124823fffff"
    poly = h3_to_polygon(index)
    assert isinstance(poly, Polygon)
    # H3 cells have 6 vertices, shapely closes the ring so we expect 7 points
    assert len(poly.exterior.coords) >= 6


def test_generate_unique_polygons_creates_polygons():
    df = pd.DataFrame({"resolution_id": ["8866124823fffff", "8866124825fffff", "8866124823fffff"]})
    gdf = generate_unique_polygons(df)
    assert len(gdf) == 2
    assert "geometry" in gdf.columns
    first_poly = h3_to_polygon("8866124823fffff")
    assert gdf.loc[gdf["resolution_id"] == "8866124823fffff", "geometry"].iloc[0].equals(first_poly)
