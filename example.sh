# !/usr/bin/env bash
export AWS_PROFILE=devseed


outputDir=data
mkdir -p $outputDir

# ST_CONTAINER="docker run --network=host -v ${PWD}:/mnt devseed/super-tiles:v1"

$ST_CONTAINER python super_tiles.py \
    data/mauritania_training_data.geojson \
    --buffer_distance=100 \
    --tile_zoom=18 \
    --url_map_service=$TMS_URL \
    --url_map_service_type="tms" \
    --tiles_folder=data/tiles \
    --st_tiles_folder=data/super_tiles \
    --output_tiles_bounds_file=data/mauritania_tiles.geojson

