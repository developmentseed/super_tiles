<h1 align="center">Super tiles</h1>

Script to generate centralized super tiles for training data process, The supertiles are 512X512 size, it can be customized top for bigger tiles.

### 🏠 [Homepage](https://github.com/developmentseed/super_tiles)

## Install

- Local

```sh
git clone clone https://github.com/developmentseed/super_tiles
cd super_tiles/
python setup.py install
```

- Docker container

```sh
git clone clone https://github.com/developmentseed/super_tiles
cd super_tiles/
docker-compose build
```

Note: `docker-compose build` will execute the testing when it is building the container!

## Usage

```sh
    super_tiles \
        --geojson_file=s3://ds-data-projects/data_test/schools.geojson \
        --zoom=18 \
        --url_map_service="https://tile.openstreetmap.org/{z}/{x}/{y}.png" \
        --url_map_service_type="tms" \
        --tiles_folder=s3://ds-data-projects/data_test/tiles \
        --st_tiles_folder=s3://ds-data-projects/data_test/super_tiles \
        --geojson_output=s3://ds-data-projects/data_test/schools_training.geojson \
        --geojson_output_coverage=s3://ds-data-projects/schools_training_coverage.geojson
```

## Run tests

```sh
python -m unittest
```
