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
import fire
from smart_open import open

from super_tiles.utils_transform import generate_buffer, get_tiles_bounds, tile_centroid
from super_tiles.utils_tiles import download_tiles
from super_tiles.stitcher import stitcher_tiles

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
        # build supertiles
        stile_file_name = f"{st_tiles_folder}/{tiles_list[0]}-st.png"
        stitcher_tiles(tiles_list_paths, tiles_folder, stile_file_name)
        feature["properties"]["stile"] = stile_file_name
    except Exception as error:
        print(error)
    return feature


def build_super_tiles(
    features,
    tiles_folder,
    st_tiles_folder,
    url_map_service,
    url_map_service_type,
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
            features, desc="Building super tiles...", total=len(features)
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
        geom_poly = box(*objs_tile["tiles_bbox"])
        feature["geometry"] = mapping(geom_poly)
        return feature

    new_features = Parallel(n_jobs=-1)(
        delayed(get_tile_coverage)(feature, zoom)
        for feature in tqdm(features, desc="Setting up tile coverage...")
    )

    return new_features


def main(
    geojson_file="https://gist.githubusercontent.com/Rub21/da3bb75805d5b3dd61fb41fbb997337b/raw/2a777c025fe7f89a463fa24a33b272a68359fdc9/data.json",
    zoom=18,
    url_map_service="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    url_map_service_type="tms",
    tiles_folder="data/tiles",
    st_tiles_folder="data/supertiles",
    geojson_output="data/supertiles.geojson",
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
    # # Build super tiles
    # ############################################
    features = build_super_tiles(
        new_features,
        tiles_folder,
        st_tiles_folder,
        url_map_service,
        url_map_service_type,
    )
    # save output
    with open(geojson_output, "w") as out_geo:
        out_geo.write(
            json.dumps(fc(features), ensure_ascii=False).encode("utf8").decode()
        )

    # Return features for testing
    return features


if __name__ == "__main__":
    fire.Fire(main)
