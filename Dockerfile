FROM lambgeo/lambda-gdal:3.2-python3.8

COPY requirements.txt .
RUN pip install --upgrade --ignore-installed --no-cache-dir -r requirements.txt

WORKDIR /mnt
