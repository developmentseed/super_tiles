# !/usr/bin/env bash


# ST_CONTAINER="docker run --network=host -v ${PWD}:/mnt devseed/super-tiles:v1"

$ST_CONTAINER python super_tiles.py \
    data/mauritania_training_data.geojson \
    --zoom=18 \
    --url_map_service=$TMS_URL \
    --url_map_service_type="tms" \
    --tiles_folder=data/tiles \
    --st_tiles_folder=data/super_tiles \
    --geojson_output=data/mauritania_tiles.geojson

