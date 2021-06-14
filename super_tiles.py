"""
Script for super-tiles creation
Author: @developmentseed
Run:
    python3 super_tiles.py input.geojson \
    --buffer_distance=100 \
    --zoom=18 \
    --tiles_folder=data/tiles_from_UNICEF_training/img_chad \
    --geojson_outpute=data/validated_data/chad_tile_bounds.geojson \
    --st_tiles_folder=data/tiles_from_UNICEF_training/img_chad_st

"""

import json
import os
from joblib import Parallel, delayed
from tqdm import tqdm
from geojson import FeatureCollection as fc
from shapely.geometry import shape, box, mapping
import fire

from utils_transform import generate_buffer, get_tiles_bounds, tile_centroid
from utils_tiles import download_tiles
from stitcher import stitcher_tiles

zoom_distances = {
    "1": 20037508,
    "2": 10018754,
    "3": 5009377,
    "4": 2504689,
    "5": 1252344,
    "6": 626172,
    "7": 313086,
    "8": 156543,
    "9": 78272,
    "10": 39136,
    "11": 19568,
    "12": 9784,
    "13": 4892,
    "14": 2446,
    "15": 1223,
    "16": 611,
    "17": 306,
    "18": 100,
    "19": 76,
    "20": 38,
    "21": 19,
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
    geojson_file,
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
        features = json.load(gfile)["features"][0:3]

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


#   f = open(output_tiles_bounds_file, "w")
#     f.write(json.dumps(fc(updated_features),
#                        ensure_ascii=False).encode('utf8').decode())
#     f.close()

if __name__ == "__main__":
    fire.Fire(main)
