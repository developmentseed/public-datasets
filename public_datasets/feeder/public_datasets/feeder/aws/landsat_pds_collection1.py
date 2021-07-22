"""Create Items for AWS Landsat PDS."""

import csv
import json
import math
from datetime import datetime, timezone

import click
import requests
from rasterio.features import bounds as feature_bounds
from stac_pydantic import Extensions, Item
from suncalc import get_position

from public_datasets.extensions.landsat import LandsatExtension
from public_datasets.feeder.utils import _reduce_precision

Extensions.register("landsat", LandsatExtension)


def create_assets(prefix: str):
    """Create assets object."""
    return {
        "ANG": {
            "href": f"{prefix}_ANG.txt",
            "title": "ANG Metadata",
            "type": "text/plain",
            "roles": ["metadata"],
        },
        "B1": {
            "href": f"{prefix}_B1.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B1",
                    "common_name": "coastal",
                    "center_wavelength": 0.44,
                    "full_width_half_max": 0.02,
                }
            ],
            "title": "Band 1 (coastal)",
        },
        "B2": {
            "href": f"{prefix}_B2.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B2",
                    "common_name": "blue",
                    "center_wavelength": 0.48,
                    "full_width_half_max": 0.06,
                }
            ],
            "title": "Band 2 (blue)",
        },
        "B3": {
            "href": f"{prefix}_B3.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B3",
                    "common_name": "green",
                    "center_wavelength": 0.56,
                    "full_width_half_max": 0.06,
                }
            ],
            "title": "Band 3 (green)",
        },
        "B4": {
            "href": f"{prefix}_B4.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B4",
                    "common_name": "red",
                    "center_wavelength": 0.65,
                    "full_width_half_max": 0.04,
                }
            ],
            "title": "Band 4 (red)",
        },
        "B5": {
            "href": f"{prefix}_B5.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B5",
                    "common_name": "nir",
                    "center_wavelength": 0.86,
                    "full_width_half_max": 0.03,
                }
            ],
            "title": "Band 5 (nir)",
        },
        "B6": {
            "href": f"{prefix}_B6.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B6",
                    "common_name": "swir16",
                    "center_wavelength": 1.6,
                    "full_width_half_max": 0.08,
                }
            ],
            "title": "Band 6 (swir16)",
        },
        "B7": {
            "href": f"{prefix}_B7.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B7",
                    "common_name": "swir22",
                    "center_wavelength": 2.2,
                    "full_width_half_max": 0.2,
                }
            ],
            "title": "Band 7 (swir22)",
        },
        "B8": {
            "href": f"{prefix}_B8.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B8",
                    "common_name": "pan",
                    "center_wavelength": 0.59,
                    "full_width_half_max": 0.18,
                }
            ],
            "gsd": 15,
            "title": "Band 8 (pan)",
        },
        "B9": {
            "href": f"{prefix}_B9.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B9",
                    "common_name": "cirrus",
                    "center_wavelength": 1.37,
                    "full_width_half_max": 0.02,
                }
            ],
            "title": "Band 9 (cirrus)",
        },
        "B10": {
            "href": f"{prefix}_B10.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B10",
                    "common_name": "lwir11",
                    "center_wavelength": 10.9,
                    "full_width_half_max": 0.8,
                }
            ],
            "gsd": 100,
            "title": "Band 10 (lwir)",
        },
        "B11": {
            "href": f"{prefix}_B11.TIF",
            "type": "image/tiff; application=geotiff",
            "eo:bands": [
                {
                    "name": "B11",
                    "common_name": "lwir12",
                    "center_wavelength": 12,
                    "full_width_half_max": 1,
                }
            ],
            "gsd": 100,
            "title": "Band 11 (lwir)",
        },
        "BQA": {
            "href": f"{prefix}_BQA.TIF",
            "title": "Quality Band",
            "type": "image/tiff; application=geotiff",
            "roles": ["quality"],
        },
        "MTL": {
            "href": f"{prefix}_MTL.txt",
            "title": "MTL Metadata",
            "type": "text/plain",
            "roles": ["metadata"],
        },
        "thumbnail": {
            "href": f"{prefix}_thumb_large.jpg",
            "title": "Thumbnail",
            "type": "image/jpeg",
            "roles": ["thumbnail"],
        },
    }


def create_stac_items(
    scenes_list: str, grid_geom: str, collection: int = 1, level: int = 1
):
    """Create STAC Items from scene_list and WRS2 grid."""
    # Read WRS2 Grid geometries
    with open(grid_geom, "r") as f:
        wrs_grid_list = [json.loads(line) for line in f.readlines()]
        pr = [x["properties"]["PR"] for x in wrs_grid_list]

        wrs_grid = dict(zip(pr, wrs_grid_list))
        for pr in wrs_grid.keys():
            wrs_grid[pr]["geometry"] = _reduce_precision(wrs_grid[pr]["geometry"])

    # Open list of scenes
    with open(scenes_list, "r") as f:
        reader = csv.DictReader(f)
        for value in reader:
            # LC08_L1GT_070235_20180607_20180608_01_RT
            product_id = value["productId"]
            productid_info = product_id.split("_")
            path_row = productid_info[2]
            collection_number = productid_info[-2]
            collection_category = productid_info[-1]
            sat_number = int(productid_info[0][2:4])
            sensor = productid_info[0][1]

            _level = int(value["processingLevel"][1])
            if _level != level:
                continue

            if int(collection_number) != collection:
                continue

            grid_cell = wrs_grid[path_row]
            scene_time = grid_cell["properties"]["PERIOD"]
            geom = grid_cell["geometry"]

            if sensor == "C":
                instruments = ["oli", "tirs"]
            elif sensor == "O":
                instruments = ["oli"]
            elif sensor == "T" and sat_number >= 8:
                instruments = ["tirs"]
            elif sensor == "E":
                instruments = ["etm"]
            elif sensor == "T" and sat_number <= 8:
                instruments = ["tm"]
            elif sensor == "M":
                instruments = ["mss"]

            path = int(value["path"])
            row = int(value["row"])

            # we remove the milliseconds because it's missing for some entry
            d = value["acquisitionDate"].split(".")
            if len(d) == 1:
                date_info = datetime.strptime(
                    value["acquisitionDate"], "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
            else:
                date_info = datetime.strptime(
                    value["acquisitionDate"], "%Y-%m-%d %H:%M:%S.%f"
                ).replace(tzinfo=timezone.utc)

            center_lat = (float(value["min_lat"]) + float(value["max_lat"])) / 2
            center_lon = (float(value["min_lon"]) + float(value["max_lon"])) / 2

            pos = get_position(date_info, center_lon, center_lat)
            sun_azimuth = math.degrees(pos["azimuth"] + math.pi) % 360
            sun_elevation = math.degrees(pos["altitude"])

            collection_name = f"aws-landsat-c{collection}l{level}"

            stac_item = {
                "type": "Feature",
                "stac_extensions": ["eo", "landsat", "view"],
                "id": product_id,
                "collection": collection_name,
                "bbox": feature_bounds(geom),
                "geometry": geom,
                "properties": {
                    "datetime": date_info.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "platform": f"LANDSAT_{sat_number}",
                    "instruments": instruments,
                    "gsd": 30,
                    "view:sun_azimuth": round(sun_azimuth, 6),
                    "view:sun_elevation": round(sun_elevation, 6),
                    "landsat:row": row,
                    "landsat:path": path,
                    "landsat:scene_id": value["entityId"],
                    "landsat:day_or_night": scene_time.lower(),
                    "landsat:processing_level": value["processingLevel"],
                    "landsat:collection_category": collection_category,
                    "landsat:collection_number": collection_number,
                    "eo:cloud_cover": float(value["cloudCover"]),
                },
                "links": [
                    {
                        "title": "AWS Public Dataset page for Landsat-8",
                        "rel": "about",
                        "type": "text/html",
                        "href": "https://registry.opendata.aws/landsat-8",
                    }
                ],
            }

            prefix = f"https://landsat-pds.s3.us-west-2.amazonaws.com/c{int(collection_number)}/L{sat_number}/{path:03}/{row:03}/{product_id}/{product_id}"
            stac_item["assets"] = create_assets(prefix)
            yield stac_item


@click.command()
@click.argument("scene_list", type=str)
@click.argument("wrs2_grid", type=str)
@click.option("--collection", type=int, required=True)
@click.option("--level", type=int, required=True)
@click.option("--host", type=str, required=True)
def main(scene_list, wrs2_grid, collection, level, host):
    """Create Landsat STAC Items."""
    r = requests.get(f"{host}/collections")
    if r.status_code not in (200, 409):
        r.raise_for_status()
    db_collections = [col.get("id") for col in r.json()]

    collection_name = f"aws-landsat-c{collection}l{level}"

    # Create Collection
    if collection_name not in db_collections:
        collection_body = {
            "id": collection_name,
            "description": "AWS Landsat-pds collection.",
            "license": "public-domain",
            "links": [],
            "extent": {
                "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
                "temporal": {"interval": [["1975-01-01T00:00:00Z", "null"]]},
            },
        }
        r = requests.post(f"{host}/collections", json=collection_body)
        if r.status_code not in (200, 409):
            r.raise_for_status()

    # Create and POST items
    for item in create_stac_items(
        scene_list, wrs2_grid, collection=collection, level=level
    ):
        # do something here
        stac_item = Item(**item)
        r = requests.post(
            f"{host}/collections/{collection_name}/items",
            json=stac_item.dict(exclude_none=True),
        )
        if r.status_code not in (200, 409):
            r.raise_for_status()


if __name__ == "__main__":
    main()
