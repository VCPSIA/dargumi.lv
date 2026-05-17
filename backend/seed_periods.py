# Seed skripts — vēsturiskie periodi galvenajām kolekcionāru valstīm.
import asyncio
from sqlalchemy import select
from app.models.catalog import Country, Period, SectionType

# Vēsturiskie periodi: { valsts_kods: [(nosaukums, gads_no, gads_lidz), ...] }
PERIODS = {
    "LV": [
        ("Latvijas Republika", 1922, 1940),
        ("Latvijas PSR / PSRS", 1941, 1991),
        ("Latvijas Republika (euro)", 1991, None),
    ],
    "LT": [
        ("Lietuvas Republika", 1925, 1940),
        ("Lietuvas PSR / PSRS", 1940, 1991),
        ("Lietuvas Republika (euro)", 1991, None),
    ],
    "EE": [
        ("Igaunijas Republika", 1922, 1940),
        ("Igaunijas PSR / PSRS", 1940, 1991),
        ("Igaunijas Republika (euro)", 1991, None),
    ],
    "RU": [
        ("Krievijas impērija", 1700, 1917),
        ("PSRS", 1917, 1991),
        ("Krievijas Federācija", 1991, None),
    ],
    "DE": [
        ("Vācijas impērija", 1871, 1918),
        ("Veimāras republika", 1919, 1933),
        ("Trešais reihs", 1933, 1945),
        ("VFR (Rietumvācija)", 1949, 1990),
        ("VDR (Austrumvācija)", 1949, 1990),
        ("Vienotā Vācija", 1990, None),
    ],
    "AT": [
        ("Austrijas impērija / A-U", 1806, 1918),
        ("Austrijas Republika", 1918, 1938),
        ("Anšluss (III reihs)", 1938, 1945),
        ("Austrijas Republika (mūsdienas)", 1945, None),
    ],
    "FR": [
        ("Francijas Republika (III)", 1870, 1940),
        ("Višī Francija", 1940, 1944),
        ("Francijas Republika (IV-V)", 1944, None),
    ],
    "GB": [
        ("Lielbritānija (Viktorijas laikmets)", 1837, 1901),
        ("Lielbritānija (XX gs.)", 1901, 1971),
        ("Lielbritānija (decimālā sistēma)", 1971, None),
    ],
    "US": [
        ("ASV (klasiskā perioda)", 1792, 1964),
        ("ASV (mūsdienu)", 1964, None),
    ],
    "PL": [
        ("Polijas Republika (I)", 1918, 1939),
        ("Polijas Tautas Republika", 1944, 1989),
        ("Polijas Republika (III)", 1989, None),
    ],
    "HU": [
        ("Austro-Ungārija", 1867, 1918),
        ("Ungārijas Republika / Tautas republika", 1918, 1989),
        ("Ungārijas Republika (mūsdienu)", 1989, None),
    ],
    "CZ": [
        ("Čehoslovākija", 1918, 1993),
        ("Čehijas Republika", 1993, None),
    ],
    "SK": [
        ("Čehoslovākija", 1918, 1993),
        ("Slovākijas Republika", 1993, None),
    ],
    "IT": [
        ("Itālijas Karaliste", 1861, 1946),
        ("Itālijas Republika", 1946, None),
    ],
    "ES": [
        ("Spānija (Franco)", 1939, 1975),
        ("Spānija (mūsdienu)", 1975, None),
    ],
    "NL": [
        ("Nīderlande (karaliste)", 1815, None),
    ],
    "BE": [
        ("Beļģijas Karaliste", 1831, None),
    ],
    "CH": [
        ("Šveices Konfederācija", 1848, None),
    ],
    "SE": [
        ("Zviedrija", 1873, None),
    ],
    "NO": [
        ("Norvēģija", 1905, None),
    ],
    "DK": [
        ("Dānija", 1873, None),
    ],
    "FI": [
        ("Somija", 1917, None),
    ],
    "UA": [
        ("Ukrainas PSR / PSRS", 1920, 1991),
        ("Ukraina (neatkarīgā)", 1991, None),
    ],
    "BY": [
        ("Baltkrievijas PSR / PSRS", 1920, 1991),
        ("Baltkrievija (neatkarīgā)", 1991, None),
    ],
    "GR": [
        ("Grieķija (klasiskā)", 1828, 1944),
        ("Grieķija (mūsdienu)", 1944, None),
    ],
    "TR": [
        ("Osmaņu impērija", 1299, 1922),
        ("Turcijas Republika", 1923, None),
    ],
    "LU": [
        ("Luksemburga", 1854, None),
    ],
}

SECTIONS = [s.value for s in SectionType]


async def seed():
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        # Iegūt visas valstis
        result = await db.execute(select(Country))
        countries = {c.code: c for c in result.scalars().all()}

        added = 0
        skipped = 0

        for code, period_list in PERIODS.items():
            country = countries.get(code)
            if not country:
                print(f"  ⚠ Valsts '{code}' nav datubāzē — izlaižam")
                continue

            for (name, yr_start, yr_end) in period_list:
                for section in SECTIONS:
                    # Pārbaudīt vai jau eksistē
                    existing = await db.execute(
                        select(Period).where(
                            Period.country_id == country.id,
                            Period.name == name,
                            Period.section == section,
                        )
                    )
                    if existing.scalar_one_or_none():
                        skipped += 1
                        continue

                    p = Period(
                        name=name,
                        year_start=yr_start,
                        year_end=yr_end,
                        country_id=country.id,
                        section=section,
                        coin_category="circulation",
                    )
                    db.add(p)
                    added += 1

        await db.commit()
        print(f"\nPievienoti: {added} periodi, izlaisti (jau eksiste): {skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
