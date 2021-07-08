"""
Script for super-tiles creation
Author: @developmentseed
"""

import json
import os
from joblib import Parallel, delayed
from tqdm import tqdm
from geojson import FeatureCollection as fc
from shapely.geometry import shape, box, mapping
import click
import logging
from smart_open import open

from super_tiles.utils_transform import generate_buffer, get_tiles_bounds, tile_centroid
from super_tiles.utils_tiles import download_tiles
from super_tiles.utils_img import stitcher_tiles

logger = logging.getLogger(__name__)

zoom_distances = {
    "1": 10000000,
    "2": 5000000,
    "3": 2500000,
    "4": 1200000,
    "5": 600000,
    "6": 300000,
    "7": 150000,
    "8": 75000,
    "9": 42000,
    "10": 20000,
    "11": 10000,
    "12": 5000,
    "13": 2500,
    "14": 1250,
    "15": 700,
    "16": 400,
    "17": 200,
    "18": 100,
    "19": 50,
    "20": 20,
    "21": 10,
}


def super_tile(
    feature, tiles_folder, st_tiles_folder, url_map_service, url_map_service_type
):
    """Build super tile for map feature
    Returns:
        [dict]: map feature
    """

    try:
        tiles_list = feature["properties"]["tiles_list"]
        # download tiles
        if url_map_service_type == "tms":
            tiles_list_paths = download_tiles(tiles_list, tiles_folder, url_map_service)
            if "_" in tiles_list_paths:
                feature["properties"]["stile"] = "no_found"
            else:
                # build supertiles
                stile_file_name = f"{st_tiles_folder}/{tiles_list[0]}-st.png"
                stitcher_tiles(tiles_list_paths, stile_file_name)
                feature["properties"]["stile"] = os.path.basename(stile_file_name)

    except Exception as error:
        logger.error(error.__str__())
    return feature


def build_super_tiles(
    features, tiles_folder, st_tiles_folder, url_map_service, url_map_service_type, zoom
):
    """Create the supertiles

    Args:
        features (dict): map features
        tiles_folder (str): path to folder to download the tiles
        st_tiles_folder (str): path to folder where to create the supertiles
        url_map_service (str): map url service
        url_map_service_type (str): type of map service

    Returns:
        dict: map features
    """
    # create super tiles in parallel
    os.makedirs(st_tiles_folder, exist_ok=True)
    _features = Parallel(n_jobs=-1)(
        delayed(super_tile)(
            feature,
            tiles_folder,
            st_tiles_folder,
            url_map_service,
            url_map_service_type,
        )
        for feature in tqdm(
            features, desc=f"Building super tiles at zoom={zoom}", total=len(features)
        )
    )

    return _features


def get_tiles_coverage(features, zoom):
    """Get list of tiles thet cover the feature

    Args:
        feature (dict): map features
        zoom (int): Zoom to get the tiles
    Returns:
        dict: map feature
    """

    def get_tile_coverage(feature, zoom):
        geom = shape(feature["geometry"])
        centroid = geom.centroid
        # Get the centroid of the child  tile
        centroid_fixed = tile_centroid(centroid, zoom + 1)
        bbox = generate_buffer(centroid_fixed, zoom_distances[str(zoom)])
        objs_tile = get_tiles_bounds(bbox, zoom)
        props = feature["properties"]
        props["tiles_list"] = objs_tile["tiles_list"]
        props["tiles_bbox"] = objs_tile["tiles_bbox"]
        return feature

    new_features = Parallel(n_jobs=-1)(
        delayed(get_tile_coverage)(feature, zoom)
        for feature in tqdm(features, desc=f"Setting up tile coverage at zoom={zoom}")
    )

    return new_features


def clip_geometry_supertile(features):
    """Calculate Difference geometry of feature and supertile box

    Args:
        features (dict): map features
    Returns:
        dict: map features
    """
    has_clip = 0
    for feature in features:
        prop = feature.get("properties")
        geom = shape(feature.get("geometry"))
        geom_stile = shape(mapping(box(*prop["tiles_bbox"])))
        if not geom_stile.contains(geom):
            has_clip += 1
            prop["has_clip"] = True
            geom_intersection = geom_stile.intersection(geom)
            feature["geometry"] = mapping(geom_intersection)
    if has_clip:
        logger.info(f"{has_clip} clip geometries")
    return features


def set_tile_boox(feature):
    """Set tile bbox for a feature

    Args:
        feature (dict):

    Returns:
        [dict]: Feature with geometry updated
    """
    props = feature["properties"]
    geom_poly = box(*props["tiles_bbox"])
    feature["geometry"] = mapping(geom_poly)
    return feature


def supertiles(
    geojson_file,
    zoom,
    url_map_service,
    url_map_service_type,
    tiles_folder,
    st_tiles_folder,
    geojson_output,
    geojson_output_coverage,
    testing,
):
    """Main function to start building the supertiles

    Args:
        geojson_file (str): geojson file
        zoom (int):zoom
        url_map_service (str): url for the service
        url_map_service_type (str): type of service
        tiles_folder (str): Path for geojson output file
        st_tiles_folder (str): Output foder for supertiles
        geojson_output (str): Path for geojson output file
    """

    tiles_folder = tiles_folder.rstrip("/")
    st_tiles_folder = st_tiles_folder.rstrip("/")

    with open(geojson_file, encoding="utf8") as gfile:
        features = json.load(gfile)["features"]

    ############################################
    # Calculate super tiles cover
    ############################################
    new_features = get_tiles_coverage(features, zoom)
    # ############################################
    # # Clip geometry- supertiles
    # ############################################
    clip_features = clip_geometry_supertile(new_features)
    # ############################################
    # # Build super tiles
    # ############################################
    features = build_super_tiles(
        clip_features,
        tiles_folder,
        st_tiles_folder,
        url_map_service,
        url_map_service_type,
        zoom,
    )
    # save output
    with open(geojson_output, "w") as out_geo:
        out_geo.write(
            json.dumps(fc(features), ensure_ascii=False).encode("utf8").decode()
        )

    # save output of tile coverage
    features_tiles = [set_tile_boox(feature) for feature in features]
    with open(geojson_output_coverage, "w") as out_geo:
        out_geo.write(
            json.dumps(fc(features_tiles), ensure_ascii=False).encode("utf8").decode()
        )

    # Return features for testing
    if testing:
        return features


@click.command(short_help="Script to cretae super tiles")
@click.option(
    "--geojson_file",
    help="Geojson file",
    required=True,
    type=str,
)
@click.option(
    "--zoom",
    help="Zoom to get the supertiles",
    required=True,
    type=int,
    default=18,
)
@click.option(
    "--url_map_service",
    help="Tile map service url",
    required=True,
    type=str,
    default="http://tile.openstreetmap.org/{z}/{x}/{y}.png",
)
@click.option(
    "--url_map_service_type",
    help="Tile map service url type",
    required=True,
    type=str,
    default="tms",
)
@click.option(
    "--tiles_folder",
    help="Folder to dowload the tiles",
    type=str,
    default="data/tiles",
)
@click.option(
    "--st_tiles_folder",
    help="Folder to save the super tiles",
    type=str,
    default="data/supertiles",
)
@click.option(
    "--geojson_output",
    help="Original geojson with the attributes: stile, tiles_list, tiles_bbox",
    type=str,
    default="data/supertiles.geojson",
)
@click.option(
    "--geojson_output_coverage",
    help="Geojson file of the tile coverage including stile, tiles_list, tiles_bbox",
    type=str,
    required=False,
)
@click.option(
    "--testing",
    help="Value for testing",
    type=bool,
    required=False,
    default=False,
)
def main(
    geojson_file,
    zoom,
    url_map_service,
    url_map_service_type,
    tiles_folder,
    st_tiles_folder,
    geojson_output,
    geojson_output_coverage,
    testing,
):
    supertiles(
        geojson_file,
        zoom,
        url_map_service,
        url_map_service_type,
        tiles_folder,
        st_tiles_folder,
        geojson_output,
        geojson_output_coverage,
        testing,
    )


if __name__ == "__main__":
    main()
