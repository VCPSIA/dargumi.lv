from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    reset_token: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    reset_token_expiry: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    google_id: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    facebook_id: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)

    collection_items: Mapped[list["CollectionItem"]] = relationship(back_populates="user")  # noqa
    subscriptions: Mapped[list["UserSubscription"]] = relationship(back_populates="user")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plan: Mapped[str] = mapped_column(String(20))  # "monthly" | "yearly" | "manual"
    start_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    end_date: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship(back_populates="subscriptions")
