from pydantic import BaseModel
from app.models.catalog import SectionType
from app.schemas.catalog import CatalogItemOut
import datetime

class CollectionItemCreate(BaseModel):
    catalog_item_id: int | None = None
    section: SectionType
    coin_category: str = "circulation"
    item_type: str = "collection"  # collection | trade | wishlist
    custom_name: str | None = None
    custom_year: str | None = None
    custom_description: str | None = None
    custom_country: str | None = None
    custom_denomination: str | None = None
    custom_material: str | None = None
    condition: str | None = None
    notes: str | None = None
    quantity: int = 1
    purchase_price: float | None = None

class CollectionItemUpdate(BaseModel):
    item_type: str | None = None
    condition: str | None = None
    notes: str | None = None
    quantity: int | None = None
    purchase_price: float | None = None
    custom_name: str | None = None
    custom_year: str | None = None
    custom_country: str | None = None
    custom_denomination: str | None = None
    custom_material: str | None = None

class PeriodInfo(BaseModel):
    id: int
    name: str
    year_start: int | None
    year_end: int | None
    model_config = {"from_attributes": True}

class CountryInfo(BaseModel):
    id: int
    name: str
    name_lv: str
    code: str
    model_config = {"from_attributes": True}

class ContinentInfo(BaseModel):
    id: int
    name: str
    name_lv: str
    model_config = {"from_attributes": True}

class CollectionItemOut(BaseModel):
    id: int
    section: SectionType
    catalog_item: CatalogItemOut | None
    custom_name: str | None
    custom_year: str | None
    custom_country: str | None
    custom_denomination: str | None
    custom_material: str | None
    custom_description: str | None
    user_image: str | None
    user_image_reverse: str | None
    coin_category: str = "circulation"
    item_type: str = "collection"
    condition: str | None
    notes: str | None
    quantity: int
    purchase_price: float | None = None
    added_at: datetime.datetime
    # Computed from catalog hierarchy
    period: PeriodInfo | None = None
    country: CountryInfo | None = None
    continent: ContinentInfo | None = None
    model_config = {"from_attributes": True}

class TreeNode(BaseModel):
    id: int
    name: str
    name_lv: str | None = None
    code: str | None = None
    count: int
    year_start: int | None = None
    year_end: int | None = None
    children: list["TreeNode"] = []

class CollectionTree(BaseModel):
    coins: list[TreeNode] = []
    medals: list[TreeNode] = []
    stamps: list[TreeNode] = []
    banknotes: list[TreeNode] = []
    continents: list[TreeNode] = []
    total: int = 0
