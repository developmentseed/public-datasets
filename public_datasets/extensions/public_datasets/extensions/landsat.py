"""STAC Extension."""

from pydantic import BaseModel


class LandsatExtension(BaseModel):
    """Landsat STAC Extension."""

    row: int
    path: int
    scene_id: str
    collection_number: str
    collection_category: str
    day_or_night: str
    processing_level: str

    # Setup extension namespace in model config
    class Config:
        """landsat extension config."""

        allow_population_by_fieldname = True
        alias_generator = lambda field_name: f"landsat:{field_name}"  # noqa
