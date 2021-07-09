"""
utils to download tiles.
"""
import os
import requests
from joblib import Parallel, delayed
import logging
from smart_open import open

logger = logging.getLogger(__name__)


def fetch_tile(tile, tiles_folder, url_map_service):
    """Fetch a tiles"""
    x, y, z = tile.split("-")
    url = url_map_service.format(x=x, z=z, y=y)
    create_folder(tiles_folder)
    tilefilename = f"{tiles_folder}/{tile}.png"
    if not os.path.isfile(tilefilename):
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            with open(tilefilename, "wb") as f:
                f.write(r.content)
        else:
            logger.error(f"No found image... {url}")
            tilefilename = "_"
    return tilefilename


def download_tiles(tiles_list, tiles_folder, url_map_service):
    """Fetch tiles in parallel"""
    tiles_list_paths = Parallel(n_jobs=-1)(
        delayed(fetch_tile)(tile, tiles_folder, url_map_service) for tile in tiles_list
    )
    tiles_list_paths = [t for t in tiles_list_paths if t is not None]
    return tiles_list_paths


def create_folder(tiles_folder):
    """ Create folder in local in case is needed"""
    if tiles_folder[:5] not in ["s3://", "gs://"]:
        os.makedirs(tiles_folder, exist_ok=True)
