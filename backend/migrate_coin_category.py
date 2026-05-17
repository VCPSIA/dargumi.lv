import asyncio
from app.database import init_db, AsyncSessionLocal
from sqlalchemy import text

async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        try:
            sql = "ALTER TABLE periods ADD COLUMN coin_category VARCHAR(20) NOT NULL DEFAULT 'circulation'"
            await db.execute(text(sql))
            await db.commit()
            print("Kolonna coin_category pievienota")
        except Exception as e:
            print(f"Kļūda (iespējams jau eksistē): {e}")

asyncio.run(main())
