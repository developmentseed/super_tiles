"""
Script for super-tiles creation
Author: @developmentseed
Run:
    python3 super_tiles.py input.geojson \
    --buffer_distance=100 \
    --tile_zoom=18 \
    --tiles_folder=data/tiles_from_UNICEF_training/img_chad \
    --output_tiles_bounds_file=data/validated_data/chad_tile_bounds.geojson \
    --st_tiles_folder=data/tiles_from_UNICEF_training/img_chad_st

"""

import sys
import json
import requests
import glob
import os
from joblib import Parallel, delayed
from tqdm import tqdm
import click
from io import BytesIO
from geojson import Feature, FeatureCollection as fc
from shapely.geometry import Point, Polygon, shape, box, mapping
import itertools

# from utils_imgs import merge_array_tiles, verify_tile_images, verify_super_tile_images
from utils_transform import generate_buffer, get_tiles_bounds, tile_centroid

from utils_tiles import download_tiles
from stitcher import stitcher_tiles

# from utils_tiles_wmts import download_tiles_wmts


def super_tile(
    feature,
    tiles_folder,
    st_tiles_folder,
    url_map_service,
    url_map_service_type,
    index,
):

    try:
        tiles_list = feature["properties"]["tiles_list"]
        # Download tiles
        if url_map_service_type == "tms":
            tiles_list_paths = download_tiles(tiles_list, tiles_folder, url_map_service)
        # if url_map_service_type == "wmts":
        #     download_tiles_wmts(tiles_list, tiles_folder, url_map_service)

        # build supertiles
        stile_file_name = f"{st_tiles_folder}/{tiles_list[0]}-st.png"
        stitcher_tiles(tiles_list_paths, tiles_folder, stile_file_name)

    except Exception as e:
        if hasattr(e, "message"):
            print(e.message)
        else:
            print(e)
        feature["properties"]["st_tile"] = None
    return feature


def build_super_tiles(
    features,
    tiles_folder,
    st_tiles_folder,
    url_map_service,
    url_map_service_type,
):
    # Create super tiles folder

    os.makedirs(st_tiles_folder, exist_ok=True)

    _features = Parallel(n_jobs=-1)(
        delayed(super_tile)(
            feature,
            tiles_folder,
            st_tiles_folder,
            url_map_service,
            url_map_service_type,
            index,
        )
        for index, feature in tqdm(
            enumerate(features), desc=f"Building super tiles ...", total=len(features)
        )
    )

    return _features


def get_tiles_coverage(feature, buffer_distance, tile_zoom):
    """[summary]

    Args:
        feature ([type]): [description]
        buffer_distance ([type]): [description]
        tile_zoom ([type]): [description]

    Returns:
        [type]: [description]
    """
    geom = shape(feature["geometry"])
    centroid = geom.centroid
    # Get the centroid of the child  tile
    centroid_fixed = tile_centroid(centroid, tile_zoom + 1)
    bbox = generate_buffer(centroid_fixed, buffer_distance)
    objs_tile = get_tiles_bounds(bbox, tile_zoom)
    props = feature["properties"]
    props["tiles_list"] = objs_tile["tiles_list"]
    props["tiles_bbox"] = objs_tile["tiles_bbox"]
    geom_poly = box(*objs_tile["tiles_bbox"])
    feature["geometry"] = mapping(geom_poly)
    return feature


@click.command(short_help="Script for supertiles creation")
@click.argument("geojson_file", nargs=1)
@click.option(
    "--buffer_distance",
    help="The distance of the buffer to coverage the tiles in meters",
    type=float,
)
@click.option(
    "--url_map_service",
    help="url_map_service",
    type=str,
    default="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
)
@click.option(
    "--url_map_service_type", help="url_map_service_type", type=str, default="tms"
)
@click.option("--tile_zoom", help="tile_zoom", type=int)
@click.option(
    "--tiles_folder",
    help="Path for geojson output file",
    type=str,
    default="data/tiles",
)
@click.option(
    "--st_tiles_folder",
    help="Output foder for supertiles",
    type=str,
    default="data/super_tiles",
)
@click.option("--output_tiles_bounds_file", help="Path for geojson output file")
def main(
    geojson_file,
    buffer_distance,
    tile_zoom,
    url_map_service,
    url_map_service_type,
    tiles_folder,
    output_tiles_bounds_file,
    st_tiles_folder,
):

    tiles_folder = tiles_folder.rstrip("/")
    st_tiles_folder = st_tiles_folder.rstrip("/")

    with open(geojson_file, encoding="utf8") as f:
        features = json.load(f)["features"]

    ############################################
    # Calculate super tiles cover
    ############################################
    new_features = Parallel(n_jobs=-1)(
        delayed(get_tiles_coverage)(feature, buffer_distance, tile_zoom)
        for feature in tqdm(features, desc=f"Setting up tile coverage...")
    )

    # ############################################
    # # Build super tiles
    # ############################################
    updated_features = build_super_tiles(
        new_features,
        tiles_folder,
        st_tiles_folder,
        url_map_service,
        url_map_service_type,
    )


if __name__ == "__main__":
    main()
