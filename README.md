<h1 align="center">Super tiles</h1>

Script to generate centralized super tiles for trainee data process, The supertiles are 512X512 size, it can be customized top for bigger tiles.

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
    --geojson_file=data/schools.geojson \
    --zoom=18 \
    --url_map_service="https://tile.openstreetmap.org/{z}/{x}/{y}.png" \
    --url_map_service_type="tms" \
    --tiles_folder=data/tiles \
    --st_tiles_folder=data/super_tiles \
    --geojson_output=data/schools_supertiles.geojson
```

## Run tests

```sh
python -m unittest
```
