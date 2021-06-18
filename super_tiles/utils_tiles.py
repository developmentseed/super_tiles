"""
utils to download tiles.
"""

import sys
import json
import requests
import os
from joblib import Parallel, delayed
from tqdm import tqdm
import click
from io import BytesIO


def fetch_tile(tile, tiles_folder, url_map_service):
    x, y, z = tile.split("-")
    url = url_map_service.format(x=x, z=z, y=y)
    os.makedirs(tiles_folder, exist_ok=True)
    tilefilename = f"{tiles_folder}/{tile}.png"
    if not os.path.isfile(tilefilename):
        r = requests.get(url,timeout=3.05)
        if r.status_code == 200:
            with open(tilefilename, "wb") as f:
                f.write(r.content)
    return tilefilename


def download_tiles(tiles_list, tiles_folder, url_map_service):
    tiles_list_paths = Parallel(n_jobs=-1)(
        delayed(fetch_tile)(tile, tiles_folder, url_map_service) for tile in tiles_list
    )
    tiles_list_paths = [t for t in tiles_list_paths if t is not None]
    return tiles_list_paths
    # raise SystemExit
