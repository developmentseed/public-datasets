"""test landsat"""

import json
import math
import os

from stac_pydantic import Item

from public_datasets.stac.aws import landsat_pds_collection1

data = os.path.join(os.path.dirname(__file__), "fixtures")

grid = os.path.join(data, "wrs_grid.geojson")
scenes = os.path.join(data, "landsat_scenes.csv")

with open(os.path.join(data, "landsat8_item.json"), "r") as f:
    e84_landsat_stac_item = json.load(f)


def test_item_creation():
    """test Item creation."""
    items = {}
    for stac_item in landsat_pds_collection1.create_stac_items(
        scenes, grid, collection=1, level=1
    ):
        assert Item(**stac_item)

        items[stac_item["id"]] = stac_item

    product_id = e84_landsat_stac_item["id"]
    ds_landsat_stac_item = items[product_id]

    # Note:
    # e84 type for the GeoTIFF is set to `image/tiff; application=geotiff; profile=cloud-optimized` in the original file, which is not true
    # we set it to `image/tiff; application=geotiff`
    # e84 item is also missing Title
    for asset in [
        "ANG",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B9",
        "B10",
        "B11",
        "BQA",
        "MTL",
        "thumbnail",
    ]:
        assert (
            e84_landsat_stac_item["assets"][asset]
            == ds_landsat_stac_item["assets"][asset]
        )

    for i in range(4):
        assert math.floor(e84_landsat_stac_item["bbox"][i]) == math.floor(
            ds_landsat_stac_item["bbox"][i]
        )

    e84_props = e84_landsat_stac_item["properties"]
    ds_props = ds_landsat_stac_item["properties"]
    assert round(e84_props["eo:cloud_cover"]) == round(ds_props["eo:cloud_cover"])
    assert round(e84_props["view:sun_azimuth"]) == round(ds_props["view:sun_azimuth"])
    assert round(e84_props["view:sun_elevation"]) == round(
        ds_props["view:sun_elevation"]
    )

    assert e84_props["landsat:scene_id"] == ds_props["landsat:scene_id"]
    assert e84_props["landsat:processing_level"] == ds_props["landsat:processing_level"]
    assert (
        e84_props["landsat:collection_number"] == ds_props["landsat:collection_number"]
    )
    assert (
        e84_props["landsat:collection_category"]
        == ds_props["landsat:collection_category"]
    )
    assert e84_props["datetime"] == ds_props["datetime"]

    assert ds_props["platform"] == "LANDSAT_8"
    assert ds_props["gsd"] == 30
    assert ds_props["instruments"] == ["oli", "tirs"]
