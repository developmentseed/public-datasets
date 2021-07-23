"""Public-dataset utils."""

from typing import Dict


def _reduce_precision(geom: Dict) -> Dict:
    if geom["type"] == "Polygon":
        geom["coordinates"][0] = [
            [round(x, 6), round(y, 6)] for (x, y) in geom["coordinates"][0]
        ]
    elif geom["type"] == "MultiPolygon":
        for ii in range(len(geom["coordinates"])):
            geom["coordinates"][ii][0] = [
                [round(x, 6), round(y, 6)] for (x, y) in geom["coordinates"][ii][0]
            ]
    return geom
