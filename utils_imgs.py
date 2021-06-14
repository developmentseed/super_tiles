"""
Utilities for merge tiles in one, and verify the tile image.
"""
import sys
import json
import requests
import os
from joblib import Parallel, delayed
from tqdm import tqdm
import click
from PIL import Image, ImageDraw
from io import BytesIO


def get_concat_h(im1, im2):
    dst = Image.new("RGB", (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new("RGB", (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def merge_array_tiles(x_tiles, tiles_files, outPutImg, position):
    image_merged = Image.open(tiles_files[x_tiles[0]])
    image_merged.save(outPutImg)
    i = 1
    while i < len(x_tiles):
        img_t1 = image_merged
        img_t2 = Image.open(tiles_files[x_tiles[i]])
        if position == "vertical":
            get_concat_v(img_t1, img_t2).save(outPutImg)
        elif position == "horizontal":
            get_concat_h(img_t1, img_t2).save(outPutImg)
        image_merged = Image.open(outPutImg)
        i += 1
    return outPutImg


def verify_image(img_fname):
    if os.path.isfile(img_fname):
        try:
            img = Image.open(img_fname)
            img.verify()
        except (OSError, IOError, SyntaxError) as e:
            print("Bad file...", img_fname)
            print("Remove corrupted tile...", img_fname)
            os.remove(img_fname)
        size = os.path.getsize(img_fname)
        # Remove empty images
        if size < 2000:
            print("Remove empty tile...", img_fname)
            os.remove(img_fname)
    return img_fname


def verify_tile_images(tiles, download_folder, tile_image_extencion):
    _tiles = set(tiles)
    img_fname_tiles = []
    for tile in _tiles:
        img_fname = f"{download_folder}/{tile}.{tile_image_extencion}"
        img_fname_tiles.append(img_fname)

    Parallel(n_jobs=-1)(
        delayed(verify_image)(img_fname)
        for img_fname in tqdm(
            img_fname_tiles, desc="Verify tile images...", total=len(_tiles)
        )
    )


def verify_super_tile_images(tiles, download_folder):
    _tiles = set(tiles)
    img_fname_tiles = []
    for tile in _tiles:
        img_fname = f"{download_folder}/{tile}"
        img_fname_tiles.append(img_fname)

    Parallel(n_jobs=-1)(
        delayed(verify_image)(img_fname)
        for img_fname in tqdm(
            img_fname_tiles, desc="Verify super tile images...", total=len(_tiles)
        )
    )
