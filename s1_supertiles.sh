#!/bin/bash +x
SUPER_TILES="docker run --platform linux/amd64 -v ${PWD}:/mnt devseed/super-tiles:v1"
GEOKIT_NODE="docker run --platform linux/amd64 --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest"

SCENE_ID=S1A_IW_GRDH_1SDV_20211013T064329_20211013T064354_040097_04BF7D_66FF
SCENE_ID_BBOX=$(curl https://nfwqxd6ia0.execute-api.eu-central-1.amazonaws.com/scenes/sentinel1/$SCENE_ID/info | jq -r '.bounds | join(",")')

FOLDER=data/$SCENE_ID
TILES_FILE=${FOLDER}_tiles.geojson
mkdir -p $FOLDER

################################################################
######## Create supertiles for the boundary
################################################################
$GEOKIT_NODE geokit bbox2fc --bbox=$SCENE_ID_BBOX > data/output.geojson
$GEOKIT_NODE geokit tilecover data/output.geojson --zoom=6 >data/tiles.geojson

$SUPER_TILES \
    super_tiles \
    --geojson_file=data/tiles.geojson\
    --zoom=11 \
    --bounds_multiplier=30 \
    --url_map_service="https://nfwqxd6ia0.execute-api.eu-central-1.amazonaws.com/scenes/sentinel1/$SCENE_ID/tiles/WebMercatorQuad/{z}/{x}/{y}.png?expression=log(vv)&rescale=0,10" \
    --url_map_service_type="tms" \
    --tiles_folder=${FOLDER}/tiles \
    --st_tiles_folder=${FOLDER}/super_tiles \
    --geojson_output=${FOLDER}/test.geojson \
    --geojson_output_coverage=${FOLDER}/test_supertiles_coverage.geojson
    
