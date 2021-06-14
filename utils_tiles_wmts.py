"""
utils to download  wmts tiles.

"""
import math
import os
import random
import time
from owslib.wmts import WebMapTileService
import math
from tqdm import tqdm
import click
import json
from joblib import Parallel, delayed


wmts = WebMapTileService(
    "https://evwhs.digitalglobe.com/earthservice/wmtsaccess?connectid=5f4b5f3d-47e0-402a-996a-ed37f05a871b",
    version="1.0.0",
    username=os.getenv("MAXAR_USERNAME", "admin"),
    password=os.getenv("MAXAR_PASSWORD", "admin"),
)


def fetch_tile(tile, download_folder):
    os.makedirs(download_folder, exists_ok=True)

    tile_status = None
    tilefilename = f"{download_folder}/{tile}.png"
    x, y, z = tile.split("-")
    if not os.path.isfile(tilefilename):
        try:
            tile_request = wmts.gettile(
                layer="DigitalGlobe:ImageryTileService",
                REQUEST="GetMap",
                tilematrixset="EPSG:3857",
                tilematrix="EPSG:3857:18",
                row=y,
                column=x,
                style="",
                featureProfile="Most_Aesthetic_Mosaic_Profile",
                COVERAGE_CQL_FILTER="",
                format="image/png",
            )
            with open(tilefilename, "wb") as png:
                png.write(tile_request.read())
        except Exception as e:
            print(e)
            tile_status = tile
    return tile_status


def download_tiles_wmts(tiles, download_folder):
    failed_download_list = Parallel(n_jobs=-1)(
        delayed(fetch_tile)(tile, download_folder)
        for tile in tqdm(
            tiles, desc=f"Downloading tiles on {download_folder}...", total=len(tiles)
        )
    )
    failed_download_list = [t for t in failed_download_list if t is not None]
    return failed_download_list
