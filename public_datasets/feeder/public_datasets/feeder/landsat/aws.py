"""Create Items for AWS Landsat PDS."""

import json
import math
from copy import deepcopy

import click
from datetime import datetime, timezone
from rasterio.features import bounds as feature_bounds

from suncalc import get_position


def create_assets(prefix: str):
    """Create assets object."""
    return {
        "ANG": {
            "href": f"{prefix}_ANG.txt",
            "title": "ANG Metadata",
            "type": "text/plain",
            "roles": [
                "metadata"
            ],
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
            "roles": [
                "quality"
            ],
        },
        "MTL": {
            "href": f"{prefix}_MTL.txt",
            "title": "MTL Metadata",
            "type": "text/plain",
            "roles": [
                "metadata"
            ],
        },
        "thumbnail": {
            "href": f"{prefix}_thumb_large.jpg",
            "title": "Thumbnail",
            "type": "image/jpeg",
            "roles": [
                "thumbnail"
            ],
        },
    }


def create_stac_items(scenes, grid):
    """Create STAC Items from scene_list and WRS2 grid."""
    # Read WRS2 Grid
    with open(grid, "r") as f:
        wrs_grid = [json.loads(line) for line in f.readlines()]
        pr = [x["properties"]["PR"] for x in wrs_grid]
        wrs_grid = dict(zip(pr, wrs_grid))

    # Open Scene list and use generator to limit memory usage
    with open(scenes, "r") as f:
        list_line = (s.rstrip().split(",") for s in f)

        # Retrieve the first line
        cols = next(list_line)

        for line in list_line:
            # Create a dict using the column names extracted earlier
            value = dict(zip(cols, line))

            # LC08_L1GT_070235_20180607_20180608_01_RT
            product_id = value["productId"]
            productid_info = product_id.split("_")
            path_row = productid_info[2]
            collection_number = productid_info[-2]
            collection_category = productid_info[-1]
            sat_number = int(productid_info[0][2:4])
            sensor = productid_info[0][1]

            # L1GT
            level = int(value["processingLevel"][1])

            # landsat-8-c1l1
            collection = f"landsat-{sat_number}-c{int(collection_number)}l{level}"

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
                date_info = datetime.strptime(value["acquisitionDate"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                date_info = datetime.strptime(value["acquisitionDate"], "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)

            center_lat = (float(value["min_lat"]) + float(value["max_lat"])) / 2
            center_lon = (float(value["min_lon"]) + float(value["max_lon"])) / 2

            pos = get_position(date_info, center_lon, center_lat)
            sun_azimuth = math.degrees(pos["azimuth"] + math.pi) % 360
            sun_elevation = math.degrees(pos["altitude"])

            stac_item = {
                "type": "Feature",
                "stac_version": "1.0.0-beta.2",
                "stac_extensions": ["eo", "landsat", "view"],
                "id": product_id,
                "collection": collection,
                "bbox": feature_bounds(geom),
                "geometry": geom,
                "properties": {
                    "datetime": date_info.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    "platform": f"LANDSAT_{sat_number}",
                    "instruments": instruments,
                    "gsd": 30,
                    "view:sun_azimuth":  sun_azimuth,
                    "view:sun_elevation": sun_elevation,
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
                        "href": "https://registry.opendata.aws/landsat-8"
                    }
                ],
            }

            prefix = f"https://landsat-pds.s3.us-west-2.amazonaws.com/c{int(collection_number)}/L{sat_number}/{path:03}/{row:03}/{product_id}/{product_id}"
            stac_item["assets"] = create_assets(prefix)
            yield stac_item


@click.command()
@click.argument("scene_list", type=str)
@click.argument("wrs2_grid", type=str)
def main(scene_list, wrs2_grid):
    """Create Landsat STAC Items."""
    for item in create_stac_items(scene_list, wrs2_grid):
        # to something here
        pass


if __name__ == "__main__":
    main()
