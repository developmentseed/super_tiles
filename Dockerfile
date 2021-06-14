FROM lambgeo/lambda-gdal:3.2-python3.8
RUN pip install mercantile
RUN pip install requests
RUN pip install mercantile
RUN pip install shapely
RUN pip install joblib
RUN pip install tqdm
RUN pip install owslib
RUN pip install geojson
RUN pip install Pillow
RUN pip install rasterio
WORKDIR /mnt
