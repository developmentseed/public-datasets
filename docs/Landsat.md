
# Landsat

### Amazon Web Services - Collection 1

1. Get List of scenes on AWS

```bash
$ aws s3 cp s3://landsat-pds/c1/L8/scene_list.gz - | gunzip > scene_list.csv
```

2. Get Path/Row file geometry file

```bash
# Day time
$ wget https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip
$ fio cat WRS2_descending_0/WRS2_descending.shp | jq -c '.properties={"PR": .properties.PR, "PATH": .properties.PATH, "ROW": .properties.ROW, "PERIOD": "DAY"}' > WRS2_descending.geojson

# Night time
$ wget https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_ascending_0.zip
$ fio cat WRS2_ascending_0/WRS2_acsending.shp | jq -c '.properties={"PR": .properties.PR, "PATH": .properties.PATH, "ROW": .properties.ROW, "PERIOD": "NIGHT"}' > WRS2_ascending.geojson

# Merge both
$ cat WRS2_ascending.geojson WRS2_descending.geojson > WRS2_daynight.geojson
```


3. Create items

```
# Install dependencies
$ pip install public_datasets/extensions public_datasets/feeder

# Create NewLine delimited JSON (ndjson)
$ python -m public_datasets.stac.aws.landsat_pds_collection1 data/landsat/scene_list.csv data/landsat/WRS2_daynight.geojson --collection 1 --level 1 > aws-landsat-c1l1.json

# Load items in the database
see: https://github.com/stac-utils/pgstac#bulk-data-loading
```

### Google Cloud


### Azure
