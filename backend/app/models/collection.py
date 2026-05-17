from sqlalchemy import String, Text, Integer, Float, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.catalog import SectionType
import datetime

class CollectionItem(Base):
    __tablename__ = "collection_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    catalog_item_id: Mapped[int | None] = mapped_column(ForeignKey("catalog_items.id"), nullable=True)
    section: Mapped[SectionType] = mapped_column(Enum(SectionType))

    # If catalog_item_id is None, user entered data manually
    custom_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    custom_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    custom_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_country: Mapped[str | None] = mapped_column(String(150), nullable=True)
    custom_denomination: Mapped[str | None] = mapped_column(String(100), nullable=True)
    custom_material: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # User's own photos (obverse + reverse)
    user_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_image_reverse: Mapped[str | None] = mapped_column(String(500), nullable=True)

    coin_category: Mapped[str] = mapped_column(String(20), default="circulation")

    # Condition & notes
    item_type: Mapped[str] = mapped_column(String(20), default="collection")  # collection | trade | wishlist
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)  # UNC, XF, VF, F, VG, G
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    purchase_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    catalog_dismissed: Mapped[int] = mapped_column(Integer, default=0)

    added_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="collection_items")  # noqa
    catalog_item: Mapped["CatalogItem"] = relationship(back_populates="collection_items")  # noqa
