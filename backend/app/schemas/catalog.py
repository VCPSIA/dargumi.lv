from pydantic import BaseModel, field_validator
from app.models.catalog import SectionType

class ContinentOut(BaseModel):
    id: int
    name: str
    name_lv: str
    code: str
    icon: str | None = None
    model_config = {"from_attributes": True}

class CountryOut(BaseModel):
    id: int
    name: str
    name_lv: str
    code: str
    continent_id: int
    is_extinct: bool = False
    model_config = {"from_attributes": True}

class PeriodOut(BaseModel):
    id: int
    name: str
    year_start: int | None
    year_end: int | None
    country_id: int
    section: SectionType
    coin_category: str = "circulation"
    model_config = {"from_attributes": True}

class CatalogItemOut(BaseModel):
    id: int
    section: SectionType
    period_id: int
    name: str
    year: str | None
    description: str | None
    obverse_description: str | None = None
    reverse_description: str | None = None
    image_url: str | None
    image_url_reverse: str | None = None
    admin_edited: bool = False
    denomination: str | None
    material: str | None
    diameter_mm: str | None
    weight_g: str | None
    mint: str | None
    mintage: str | None
    designer: str | None = None
    engraver: str | None = None
    perforation: str | None
    color: str | None
    catalog_number: str | None
    coin_category: str = "circulation"
    is_approved: bool = False
    avg_price: float | None = None
    avg_price_count: int = 0
    model_config = {"from_attributes": True}

class RecognitionSave(BaseModel):
    section: SectionType
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
    perforation: str | None = None
    color: str | None = None
    catalog_number: str | None = None
    coin_category: str = "circulation"

    @field_validator("year", "diameter_mm", "weight_g", "mintage", "denomination", mode="before")
    @classmethod
    def coerce_to_str(cls, v):
        return None if v is None else str(v)
