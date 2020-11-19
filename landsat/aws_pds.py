"""Create Items for AWS Landsat PDS."""

import json

import click
from rasterio.features import bounds as feature_bounds

landsat_assets = {
    "ANG": {
        "href": "{prefix}_ANG.txt",
        "title": "Angle coefficients file",
        "type": "text/plain",
    },
    "B1": {
        "href": "{prefix}_B1.TIF",
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
        "href": "{prefix}_B2.TIF",
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
        "href": "{prefix}_B3.TIF",
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
        "href": "{prefix}_B4.TIF",
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
        "href": "{prefix}_B5.TIF",
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
        "href": "{prefix}_B6.TIF",
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
        "href": "{prefix}_B7.TIF",
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
        "href": "{prefix}_B8.TIF",
        "type": "image/tiff; application=geotiff",
        "eo:bands": [
            {
                "name": "B8",
                "common_name": "pan",
                "center_wavelength": 0.59,
                "full_width_half_max": 0.18,
            }
        ],
        "title": "Band 8 (pan)",
    },
    "B9": {
        "href": "{prefix}_B9.TIF",
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
        "href": "{prefix}_B10.TIF",
        "type": "image/tiff; application=geotiff",
        "eo:bands": [
            {
                "name": "B10",
                "common_name": "lwir11",
                "center_wavelength": 10.9,
                "full_width_half_max": 0.8,
            }
        ],
        "title": "Band 10 (lwir)",
    },
    "B11": {
        "href": "{prefix}_B11.TIF",
        "type": "image/tiff; application=geotiff",
        "eo:bands": [
            {
                "name": "B11",
                "common_name": "lwir12",
                "center_wavelength": 12,
                "full_width_half_max": 1,
            }
        ],
        "title": "Band 11 (lwir)",
    },
    "BQA": {
        "href": "{prefix}_BQA.TIF",
        "title": "Band quality data",
        "type": "image/tiff; application=geotiff",
    },
    "MTL": {
        "href": "{prefix}_MTL.txt",
        "title": "original metadata file",
        "type": "text/plain",
    },
    "thumbnail": {
        "href": "{prefix}_thumb_large.jpg",
        "title": "Thumbnail image",
        "type": "image/jpeg",
    },
}


@click.command()
@click.argument("scene_list", type=str)
@click.argument("wrs2_grid", type=str)
def main(scene_list, wrs2_grid):
    """Create Landsat STAC Items."""
    # Read WRS2 Grid
    with open(wrs2_grid, "r") as f:
        wrs_grid = [json.loads(line) for line in f.readlines()]
        pr = [x["properties"]["PR"] for x in wrs_grid]
        wrs_grid = dict(zip(pr, wrs_grid))

    # Open Scene list and use generator to limit memory usage
    with open(scene_list, "r") as f:
        lines = (line for line in f)
        list_line = (s.rstrip().split(",") for s in lines)
        cols = next(list_line)

        for line in list_line:
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

            stac_item = {
                "type": "Feature",
                "stac_version": "1.0.0-beta.2",
                "stac_extensions": ["eo", "landsat", "view"],
                "id": product_id,
                "collection": collection,
                "bbox": feature_bounds(geom),
                "geometry": geom,
                "properties": {
                    "datetime": value["acquisitionDate"],
                    "platform": f"landsat-{sat_number}",
                    "instruments": instruments,
                    "gsd": 30,
                    "view:off_nadir": 0,
                    # https://forum.developer.parrot.com/t/suns-elevation-and-azimuth-calculation/5573
                    #     "view:sun_azimuth":  # can we calculate this ?
                    #     "view:sun_elevation": # can we calculate this ?
                    "landsat:row": row,
                    "landsat:path": path,
                    "landsat:sceneid": value["entityId"],
                    "landsat:day_or_night": scene_time.lower(),
                    "landsat:processing_level": value["processingLevel"],
                    "landsat:processing_category": collection_category,
                    "landsat:collection_number": collection_number,
                    "eo:cloud_cover": float(value["cloudCover"]),
                },
                "links": [],
            }

            prefix = f"https://landsat-pds.s3.amazonaws.com/c{int(collection_number)}/L{sat_number}/{path}/{row}/{product_id}/{product_id}"

            assets = {}
            for asset, info in landsat_assets.copy().items():
                info["href"] = info["href"].format(prefix=prefix)
                assets[asset] = info

            stac_item["assets"] = assets

            # Validation ?
            # item = Item(**stac_item)  # noqa

            # Next ?


if __name__ == "__main__":
    main()
