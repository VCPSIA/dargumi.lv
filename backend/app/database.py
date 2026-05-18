from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        from app.models import user, catalog, collection  # noqa
        await conn.run_sync(Base.metadata.create_all)
    # Ensure default AppSettings row exists
    from app.models.catalog import AppSettings
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        r = await session.execute(select(AppSettings).where(AppSettings.id == 1))
        if not r.scalar_one_or_none():
            session.add(AppSettings(id=1))
            await session.commit()
        from sqlalchemy import text
        for col, typedef in [
            ("reset_token", "VARCHAR(100)"),
            ("reset_token_expiry", "DATETIME"),
            ("google_id", "VARCHAR(100)"),
            ("facebook_id", "VARCHAR(100)"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {typedef}"))
            except Exception:
                pass
        for col, typedef in [
            ("designer", "TEXT"),
            ("engraver", "TEXT"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE catalog_items ADD COLUMN {col} {typedef}"))
            except Exception:
                pass
