"""
Utilities for getting bounds and areas
"""
from pyproj import Transformer
from shapely.geometry import Point, Polygon, LineString, shape, box
import mercantile

transformer_4326_3857 = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
transformer_3857_4326 = Transformer.from_crs("epsg:3857", "epsg:4326", always_xy=True)


def generate_buffer(geom, distance):
    """Get buffer if geom"""
    centroid = geom.centroid
    x, y = transformer_4326_3857.transform(centroid.x, centroid.y)
    point = Point(x, y)
    polygon_3857 = point.buffer(distance, cap_style=3)
    points = []
    for point in list(polygon_3857.exterior.coords):
        x = point[0]
        y = point[1]
        x, y = transformer_3857_4326.transform(x, y)
        points.append((x, y))
    polygon_4326 = Polygon(points)
    return polygon_4326.bounds


def tile_centroid(geom_centroid, zoom):
    """Get centroid of te tile"""
    tile = mercantile.tile(geom_centroid.x, geom_centroid.y, zoom)
    bounds = mercantile.bounds(*tile)
    poly = box(*bounds)
    return poly.centroid


def bbox_geometries(polygon_geoms):
    """Get bbox of geometries"""
    points = []
    for geom in polygon_geoms:
        for point in list(geom.exterior.coords):
            x = point[0]
            y = point[1]
            points.append((point[0], point[1]))
    return LineString(points).bounds


def get_tiles_bounds(geo_bound, zoom):
    tiles = mercantile.tiles(
        geo_bound[0], geo_bound[1], geo_bound[2], geo_bound[3], [zoom], truncate=True
    )
    listTiles = []
    tx = []
    ty = []
    polygon_geoms = []

    for tile in tiles:
        tile_bounds = mercantile.bounds(tile[0], tile[1], tile[2])
        poly = box(*tile_bounds)
        polygon_geoms.append(poly)
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
