import asyncio
from app.database import init_db, AsyncSessionLocal
from sqlalchemy import text

async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        for col in ["obverse_description TEXT", "reverse_description TEXT"]:
            try:
                await db.execute(text(f"ALTER TABLE catalog_items ADD COLUMN {col}"))
                await db.commit()
                print(f"Pievienota: {col}")
            except Exception as e:
                print(f"Kļūda ({col}): {e}")

asyncio.run(main())
