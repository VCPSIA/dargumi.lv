from pydantic import BaseModel, field_validator
from app.models.catalog import SectionType

class RecognitionResult(BaseModel):
    recognized: bool
    section: SectionType | None = None
    name: str | None = None
    year: str | None = None
    country: str | None = None
    denomination: str | None = None
    material: str | None = None
    diameter_mm: str | None = None
    weight_g: str | None = None
    mint: str | None = None
    mintage: str | None = None
    description: str | None = None
    obverse_description: str | None = None
    reverse_description: str | None = None
    coin_category: str | None = None
    catalog_item_id: int | None = None
    confidence: float | None = None
    notes: str | None = None
    perforation: str | None = None
    color: str | None = None
    catalog_number: str | None = None

    @field_validator(
        "year", "diameter_mm", "weight_g", "mintage",
        "denomination", "perforation", mode="before"
    )
    @classmethod
    def coerce_to_str(cls, v):
        if v is None:
            return None
        return str(v)
