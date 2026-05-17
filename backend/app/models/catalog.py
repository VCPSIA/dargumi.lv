from sqlalchemy import String, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum

class SectionType(str, enum.Enum):
    coins = "coins"
    medals = "medals"
    stamps = "stamps"
    banknotes = "banknotes"

class Continent(Base):
    __tablename__ = "continents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    name_lv: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(10), unique=True)
    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)

    countries: Mapped[list["Country"]] = relationship(back_populates="continent")

class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    name_lv: Mapped[str] = mapped_column(String(150))
    code: Mapped[str] = mapped_column(String(5), index=True)
    continent_id: Mapped[int] = mapped_column(ForeignKey("continents.id"))
    is_extinct: Mapped[bool] = mapped_column(default=False)

    continent: Mapped["Continent"] = relationship(back_populates="countries")
    periods: Mapped[list["Period"]] = relationship(back_populates="country")

class Period(Base):
    __tablename__ = "periods"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    year_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    section: Mapped[SectionType] = mapped_column(Enum(SectionType))
    coin_category: Mapped[str] = mapped_column(String(20), default="circulation")

    country: Mapped["Country"] = relationship(back_populates="periods")
    items: Mapped[list["CatalogItem"]] = relationship(back_populates="period")

class CatalogItem(Base):
    __tablename__ = "catalog_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    section: Mapped[SectionType] = mapped_column(Enum(SectionType))
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"))

    # Common fields
    name: Mapped[str] = mapped_column(String(300))
    year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Coin/Medal specific
    denomination: Mapped[str | None] = mapped_column(String(100), nullable=True)
    material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    diameter_mm: Mapped[str | None] = mapped_column(String(20), nullable=True)
    weight_g: Mapped[str | None] = mapped_column(String(20), nullable=True)
    mint: Mapped[str | None] = mapped_column(String(150), nullable=True)
    mintage: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Stamp specific
    perforation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    catalog_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    coin_category: Mapped[str] = mapped_column(String(20), default="circulation")
    obverse_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reverse_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reference
    image_url_reverse: Mapped[str | None] = mapped_column(String(500), nullable=True)
    admin_edited: Mapped[bool] = mapped_column(default=False)

    ucoin_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    numista_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_approved: Mapped[bool] = mapped_column(default=False)

    period: Mapped["Period"] = relationship(back_populates="items")
    collection_items: Mapped[list["CollectionItem"]] = relationship(back_populates="catalog_item")  # noqa
