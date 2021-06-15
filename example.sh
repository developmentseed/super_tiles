# !/usr/bin/env bash

SUPER_TILES_CONTAINER="docker run -v ${PWD}:/mnt devseed/super-tiles:v1 "

$SUPER_TILES_CONTAINER \
    super_tiles \
    --geojson_file=https://gist.githubusercontent.com/Rub21/c56e1d036b4aa76421e220cafe212210/raw/e08d4dccb4b38475dd1a50dcb47e5381480a6844/schools.geojson \
    --zoom=18 \
    --url_map_service="https://tile.openstreetmap.org/{z}/{x}/{y}.png" \
    --url_map_service_type="tms" \
    --tiles_folder=data/tiles \
    --st_tiles_folder=data/super_tiles \
    --geojson_output=data/schools_supertiles.geojson
