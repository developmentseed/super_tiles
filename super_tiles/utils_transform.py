"""
Utilities for getting bounds and areas
"""
from pyproj import Transformer
from shapely.geometry import Point, Polygon, LineString, shape, box, mapping
import pyproj
from geojson import Feature, FeatureCollection as fc
import mercantile
from rasterio.features import bounds as featureBounds
from rasterio.transform import from_bounds, rowcol
import os

transformer_4326_3857 = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
transformer_3857_4326 = Transformer.from_crs("epsg:3857", "epsg:4326", always_xy=True)


def generate_buffer(geom, distance):
    """Get buffer if geom"""
    centroid = geom.centroid
    x, y = transformer_4326_3857.transform(centroid.x, centroid.y)
    # print(x,y)
    point = Point(x, y)
    polygon_3857 = point.buffer(distance, cap_style=3)
    points = []
    for point in list(polygon_3857.exterior.coords):
        x = point[0]
        y = point[1]
        x, y = transformer_3857_4326.transform(x, y)
        points.append((x, y))
    polygon_4326 = Polygon(points)
    # polygon_4326.bounds
    return polygon_4326.bounds


def features_distance(feature1, feature2):
    """
    Calclate the distance of two features in meters
    """
    geom1 = shape(feature1["geometry"]).centroid
    geom2 = shape(feature2["geometry"]).centroid

    x1, y1 = transformer_4326_3857.transform(geom1.x, geom1.y)
    x2, y2 = transformer_4326_3857.transform(geom2.x, geom2.y)

    p1 = Point(x1, y1)
    p2 = Point(x2, y2)

    distance = p1.distance(p2)
    return distance


def tile_centroid(geom_centroid, zoom):
    tile = mercantile.tile(geom_centroid.x, geom_centroid.y, zoom)
    bounds = mercantile.bounds(*tile)
    poly = box(*bounds)
    return poly.centroid


def bbox_geometries(polygon_geoms):
    points = []
    for geom in polygon_geoms:
        for point in list(geom.exterior.coords):
            x = point[0]
            y = point[1]
            points.append((point[0], point[1]))
    return LineString(points).bounds


def get_tiles_bounds(geoBound, zoom):
    tiles = mercantile.tiles(
        geoBound[0], geoBound[1], geoBound[2], geoBound[3], [zoom], truncate=True
    )
    listTiles = []
    tx = []
    ty = []
    polygon_geoms = []

    for tile in tiles:
        tile_bounds = mercantile.bounds(tile[0], tile[1], tile[2])
        poly = box(*tile_bounds)
        polygon_geoms.append(poly)
        # print(polygon)
        tx.append(tile[0])
        ty.append(tile[1])
        t = f'{"-".join(str(n) for n in tile)}'
        listTiles.append(t)

    bounds_geoms = bbox_geometries(polygon_geoms)
    tile_width = len(list(set(tx))) * 256
    tile_height = len(list(set(ty))) * 256
    uniqTiles = []
    [uniqTiles.append(x) for x in listTiles if x not in uniqTiles]
    return {
        "tiles_list": uniqTiles,
        "width": tile_width,
        "height": tile_height,
        "tiles_bbox": bounds_geoms,
    }
