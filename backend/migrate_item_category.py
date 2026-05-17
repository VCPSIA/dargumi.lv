import asyncio
from app.database import init_db, AsyncSessionLocal
from sqlalchemy import text

async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        for table, col in [
            ("catalog_items", "coin_category"),
            ("collection_items", "coin_category"),
        ]:
            try:
                sql = f"ALTER TABLE {table} ADD COLUMN {col} VARCHAR(20) NOT NULL DEFAULT 'circulation'"
                await db.execute(text(sql))
                await db.commit()
                print(f"{table}.{col} pievienota")
            except Exception as e:
                print(f"{table}.{col} kļūda (iespējams jau eksistē): {e}")

asyncio.run(main())
