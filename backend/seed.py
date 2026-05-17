"""Seed initial continents, countries, and sample periods."""
import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models.catalog import Continent, Country, Period, SectionType

CONTINENTS = [
    ("Europe", "Eiropa", "EU"),
    ("Asia", "Āzija", "AS"),
    ("Americas", "Amerikas", "AM"),
    ("Africa", "Āfrika", "AF"),
    ("Oceania", "Okeānija", "OC"),
    ("Ancient / World", "Senie / Pasaule", "AW"),
]

COUNTRIES = {
    "EU": [
        ("Latvia", "Latvija", "LV"),
        ("Germany", "Vācija", "DE"),
        ("France", "Francija", "FR"),
        ("Russia", "Krievija", "RU"),
        ("United Kingdom", "Lielbritānija", "GB"),
        ("Austria", "Austrija", "AT"),
        ("Sweden", "Zviedrija", "SE"),
        ("Poland", "Polija", "PL"),
        ("Lithuania", "Lietuva", "LT"),
        ("Estonia", "Igaunija", "EE"),
    ],
    "AS": [
        ("China", "Ķīna", "CN"),
        ("Japan", "Japāna", "JP"),
        ("India", "Indija", "IN"),
        ("Israel", "Izraēla", "IL"),
    ],
    "AM": [
        ("United States", "ASV", "US"),
        ("Canada", "Kanāda", "CA"),
        ("Mexico", "Meksika", "MX"),
        ("Brazil", "Brazīlija", "BR"),
    ],
    "AF": [
        ("South Africa", "Dienvidāfrika", "ZA"),
        ("Egypt", "Ēģipte", "EG"),
    ],
    "OC": [
        ("Australia", "Austrālija", "AU"),
        ("New Zealand", "Jaunzēlande", "NZ"),
    ],
    "AW": [
        ("Ancient Rome", "Senā Roma", "ROM"),
        ("Ancient Greece", "Senā Grieķija", "GRC"),
        ("Byzantine Empire", "Bizantija", "BYZ"),
    ],
}

# Sample periods for Latvia (all sections)
LATVIA_PERIODS = [
    ("Russian Empire", 1721, 1917, "coins"),
    ("First Republic", 1918, 1940, "coins"),
    ("Soviet Period", 1940, 1991, "coins"),
    ("Modern Latvia", 1991, 2025, "coins"),
    ("First Republic", 1918, 1940, "stamps"),
    ("Soviet Period", 1940, 1991, "stamps"),
    ("Modern Latvia", 1991, 2025, "stamps"),
    ("First Republic", 1918, 1940, "medals"),
    ("Modern Latvia", 1991, 2025, "medals"),
]

async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select
        result = await db.execute(select(Continent))
        if result.scalars().first():
            print("Already seeded.")
            return

        cont_map = {}
        for name, name_lv, code in CONTINENTS:
            c = Continent(name=name, name_lv=name_lv, code=code)
            db.add(c)
            await db.flush()
            cont_map[code] = c.id

        country_map = {}
        for cont_code, countries in COUNTRIES.items():
            for name, name_lv, code in countries:
                c = Country(name=name, name_lv=name_lv, code=code, continent_id=cont_map[cont_code])
                db.add(c)
                await db.flush()
                country_map[code] = c.id

        # Add periods for Latvia
        lv_id = country_map["LV"]
        for name, y_start, y_end, section in LATVIA_PERIODS:
            p = Period(name=name, year_start=y_start, year_end=y_end, country_id=lv_id, section=SectionType(section))
            db.add(p)

        await db.commit()
        print(f"Seeded {len(CONTINENTS)} continents, {sum(len(v) for v in COUNTRIES.values())} countries, {len(LATVIA_PERIODS)} Latvia periods.")

asyncio.run(seed())
