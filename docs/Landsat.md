
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
```

4. Create a collection

see: https://github.com/stac-utils/pgstac#bulk-data-loading

```json
// content of aws-landsat-c1l1_collection.json
{
    "id": "aws-landsat-c1l1",
    "description": "Landsat Data Collection 1, Level1 stored on AWS PDS.",
    "stac_version": "1.0.0",
    "license": "public-domain",
    "links": [],
    "extent": {
        "spatial": {
            "bbox": [
                [
                    -180.0,
                    -90.0,
                    180.0,
                    90.0
                ]
            ]
        },
        "temporal": {
            "interval": [
                [
                    "2013-03-18T00:00:00Z",
                    "null"
                ]
            ]
        }
    }
}
```

```
$ pypgstac load collections aws-landsat-c1l1_collection.json --dsn postgresql://username:password@localhost:5439/postgis
```

5. Load the items

```
$ pypgstac load items aws-landsat-c1l1.json --dsn postgresql://username:password@localhost:5439/postgis
```


### Google Cloud


### Azure
