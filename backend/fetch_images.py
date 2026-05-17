#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch coin images from Wikimedia Commons and store URLs in catalog.
Run: python fetch_images.py
Run only Euro coins: python fetch_images.py --euro
Run only historical: python fetch_images.py --historical
"""
import asyncio, os, sys, io, httpx, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select
from app.models.catalog import CatalogItem, Period, Country, SectionType

DATABASE_URL = "sqlite+aiosqlite:///./kolekcija.db"
engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

COMMONS = "https://commons.wikimedia.org/w/api.php"
UA = "dargumi.lv/1.0 catalog image bot (educational; vcpsia@gmail.com)"
DELAY = 1.2  # seconds between searches (be polite to Wikimedia)

# Per-denomination Euro search queries — most reliable searches
EURO_QUERIES: dict[str, dict[str, str]] = {
    "Germany": {
        "1 cent":  "1 euro cent coin Germany Brandenburg Gate",
        "2 cent":  "2 euro cent coin Germany Brandenburg Gate",
        "5 cent":  "5 euro cent coin Germany Brandenburg Gate",
        "10 cent": "10 euro cent coin Germany",
        "20 cent": "20 euro cent coin Germany",
        "50 cent": "50 euro cent coin Germany",
        "1 Euro":  "1 euro coin Germany Bundesadler eagle",
        "2 Euro":  "2 euro coin Germany eagle",
    },
    "France": {
        "1 cent":  "1 euro cent coin France Marianne",
        "2 cent":  "2 euro cent coin France Marianne",
        "5 cent":  "5 euro cent coin France Marianne",
        "10 cent": "10 euro cent coin France",
        "20 cent": "20 euro cent coin France",
        "50 cent": "50 euro cent coin France",
        "1 Euro":  "1 euro coin France tree",
        "2 Euro":  "2 euro coin France La Semeuse",
    },
    "Italy": {
        "1 cent":  "1 euro cent coin Italy Castel del Monte",
        "2 cent":  "2 euro cent coin Italy",
        "5 cent":  "5 euro cent coin Italy Colosseum",
        "10 cent": "10 euro cent coin Italy",
        "20 cent": "20 euro cent coin Italy",
        "50 cent": "50 euro cent coin Italy",
        "1 Euro":  "1 euro coin Italy Vitruvian Man Leonardo",
        "2 Euro":  "2 euro coin Italy Dante Alighieri",
    },
    "Spain": {
        "1 cent":  "1 euro cent coin Spain Cathedral Santiago",
        "2 cent":  "2 euro cent coin Spain",
        "5 cent":  "5 euro cent coin Spain",
        "10 cent": "10 euro cent coin Spain Cervantes",
        "20 cent": "20 euro cent coin Spain",
        "50 cent": "50 euro cent coin Spain",
        "1 Euro":  "1 euro coin Spain King Juan Carlos",
        "2 Euro":  "2 euro coin Spain King",
    },
    "Netherlands": {
        "1 cent":  "1 euro cent coin Netherlands Beatrix",
        "2 cent":  "2 euro cent coin Netherlands",
        "5 cent":  "5 euro cent coin Netherlands",
        "10 cent": "10 euro cent coin Netherlands",
        "20 cent": "20 euro cent coin Netherlands",
        "50 cent": "50 euro cent coin Netherlands",
        "1 Euro":  "1 euro coin Netherlands Queen Beatrix",
        "2 Euro":  "2 euro coin Netherlands",
    },
    "Belgium": {
        "1 cent":  "1 euro cent coin Belgium King Albert",
        "2 cent":  "2 euro cent coin Belgium",
        "5 cent":  "5 euro cent coin Belgium",
        "10 cent": "10 euro cent coin Belgium",
        "20 cent": "20 euro cent coin Belgium",
        "50 cent": "50 euro cent coin Belgium",
        "1 Euro":  "1 euro coin Belgium Albert II",
        "2 Euro":  "2 euro coin Belgium",
    },
    "Austria": {
        "1 cent":  "1 euro cent coin Austria gentian",
        "2 cent":  "2 euro cent coin Austria",
        "5 cent":  "5 euro cent coin Austria",
        "10 cent": "10 euro cent coin Austria Stephansdom",
        "20 cent": "20 euro cent coin Austria",
        "50 cent": "50 euro cent coin Austria",
        "1 Euro":  "1 euro coin Austria Mozart",
        "2 Euro":  "2 euro coin Austria Bertha von Suttner",
    },
    "Finland": {
        "1 cent":  "1 euro cent coin Finland",
        "2 cent":  "2 euro cent coin Finland",
        "5 cent":  "5 euro cent coin Finland",
        "10 cent": "10 euro cent coin Finland",
        "20 cent": "20 euro cent coin Finland",
        "50 cent": "50 euro cent coin Finland",
        "1 Euro":  "1 euro coin Finland flying swans",
        "2 Euro":  "2 euro coin Finland cloudberry",
    },
    "Portugal": {
        "1 cent":  "1 euro cent coin Portugal royal seal",
        "2 cent":  "2 euro cent coin Portugal",
        "5 cent":  "5 euro cent coin Portugal",
        "10 cent": "10 euro cent coin Portugal castle",
        "20 cent": "20 euro cent coin Portugal",
        "50 cent": "50 euro cent coin Portugal",
        "1 Euro":  "1 euro coin Portugal royal seal",
        "2 Euro":  "2 euro coin Portugal",
    },
    "Ireland": {
        "1 cent":  "1 euro cent coin Ireland Celtic harp",
        "2 cent":  "2 euro cent coin Ireland",
        "5 cent":  "5 euro cent coin Ireland",
        "10 cent": "10 euro cent coin Ireland harp",
        "20 cent": "20 euro cent coin Ireland",
        "50 cent": "50 euro cent coin Ireland",
        "1 Euro":  "1 euro coin Ireland Celtic harp",
        "2 Euro":  "2 euro coin Ireland",
    },
    "Luxembourg": {
        "1 cent":  "1 euro cent coin Luxembourg Grand Duke Henri",
        "2 cent":  "2 euro cent coin Luxembourg",
        "5 cent":  "5 euro cent coin Luxembourg",
        "10 cent": "10 euro cent coin Luxembourg",
        "20 cent": "20 euro cent coin Luxembourg",
        "50 cent": "50 euro cent coin Luxembourg",
        "1 Euro":  "1 euro coin Luxembourg Henri",
        "2 Euro":  "2 euro coin Luxembourg",
    },
    "Greece": {
        "1 cent":  "1 euro cent coin Greece trireme",
        "2 cent":  "2 euro cent coin Greece",
        "5 cent":  "5 euro cent coin Greece",
        "10 cent": "10 euro cent coin Greece ship",
        "20 cent": "20 euro cent coin Greece",
        "50 cent": "50 euro cent coin Greece",
        "1 Euro":  "1 euro coin Greece owl Athens",
        "2 Euro":  "2 euro coin Greece Europa bull",
    },
    "Slovenia": {
        "1 cent":  "1 euro cent coin Slovenia Triglav",
        "2 cent":  "2 euro cent coin Slovenia",
        "5 cent":  "5 euro cent coin Slovenia",
        "10 cent": "10 euro cent coin Slovenia",
        "20 cent": "20 euro cent coin Slovenia",
        "50 cent": "50 euro cent coin Slovenia",
        "1 Euro":  "1 euro coin Slovenia Primoz Trubar",
        "2 Euro":  "2 euro coin Slovenia",
    },
    "Cyprus": {
        "1 cent":  "1 euro cent coin Cyprus mouflon",
        "2 cent":  "2 euro cent coin Cyprus",
        "5 cent":  "5 euro cent coin Cyprus",
        "10 cent": "10 euro cent coin Cyprus Kyrenia ship",
        "20 cent": "20 euro cent coin Cyprus",
        "50 cent": "50 euro cent coin Cyprus",
        "1 Euro":  "1 euro coin Cyprus idol Pomos",
        "2 Euro":  "2 euro coin Cyprus",
    },
    "Malta": {
        "1 cent":  "1 euro cent coin Malta cross",
        "2 cent":  "2 euro cent coin Malta",
        "5 cent":  "5 euro cent coin Malta",
        "10 cent": "10 euro cent coin Malta Mnajdra",
        "20 cent": "20 euro cent coin Malta",
        "50 cent": "50 euro cent coin Malta",
        "1 Euro":  "1 euro coin Malta Maltese Cross",
        "2 Euro":  "2 euro coin Malta",
    },
    "Slovakia": {
        "1 cent":  "1 euro cent coin Slovakia Krivan mountain",
        "2 cent":  "2 euro cent coin Slovakia",
        "5 cent":  "5 euro cent coin Slovakia",
        "10 cent": "10 euro cent coin Slovakia Bratislava castle",
        "20 cent": "20 euro cent coin Slovakia",
        "50 cent": "50 euro cent coin Slovakia",
        "1 Euro":  "1 euro coin Slovakia cross hills",
        "2 Euro":  "2 euro coin Slovakia coat of arms",
    },
    "Estonia": {
        "1 cent":  "1 euro cent coin Estonia map",
        "2 cent":  "2 euro cent coin Estonia",
        "5 cent":  "5 euro cent coin Estonia",
        "10 cent": "10 euro cent coin Estonia",
        "20 cent": "20 euro cent coin Estonia",
        "50 cent": "50 euro cent coin Estonia",
        "1 Euro":  "1 euro coin Estonia map",
        "2 Euro":  "2 euro coin Estonia",
    },
    "Latvia": {
        "1 cent":  "1 euro cent coin Latvia Latvian maid",
        "2 cent":  "2 euro cent coin Latvia",
        "5 cent":  "5 euro cent coin Latvia",
        "10 cent": "10 euro cent coin Latvia",
        "20 cent": "20 euro cent coin Latvia",
        "50 cent": "50 euro cent coin Latvia",
        "1 Euro":  "1 euro coin Latvia Latvian maid",
        "2 Euro":  "2 euro coin Latvia",
    },
    "Lithuania": {
        "1 cent":  "1 euro cent coin Lithuania Vytis",
        "2 cent":  "2 euro cent coin Lithuania",
        "5 cent":  "5 euro cent coin Lithuania",
        "10 cent": "10 euro cent coin Lithuania",
        "20 cent": "20 euro cent coin Lithuania",
        "50 cent": "50 euro cent coin Lithuania",
        "1 Euro":  "1 euro coin Lithuania Vytis",
        "2 Euro":  "2 euro coin Lithuania",
    },
    "Croatia": {
        "1 cent":  "1 euro cent coin Croatia marten",
        "2 cent":  "2 euro cent coin Croatia",
        "5 cent":  "5 euro cent coin Croatia",
        "10 cent": "10 euro cent coin Croatia Tesla",
        "20 cent": "20 euro cent coin Croatia",
        "50 cent": "50 euro cent coin Croatia",
        "1 Euro":  "1 euro coin Croatia map",
        "2 Euro":  "2 euro coin Croatia",
    },
}

# Historical coin queries
HISTORICAL_QUERIES: dict[str, str] = {
    "1 Santīms":              "1 santims Latvia 1922 bronze coin",
    "2 Santīmi":              "2 santimi Latvia 1922 bronze coin",
    "5 Santīmi":              "5 santimi Latvia 1922 bronze coin",
    "10 Santīmu":             "10 santimu Latvia 1922 nickel coin",
    "20 Santīmu":             "20 santimu Latvia 1922 nickel coin",
    "50 Santīmu":             "50 santimu Latvia 1922 nickel coin",
    "1 Lats":                 "1 lats Latvia 1924 silver coin Latvian Maid",
    "2 Lati":                 "2 lati Latvia 1925 silver coin",
    "5 Lati":                 "5 lati Latvia 1929 silver coin",
    "1 Lats (Salmon)":        "1 lats Latvia 1938 salmon fish coin",
    "1 Lats (Archer)":        "1 lats Latvia 1929 archer coin",
    "1 Santīms (Republic)":   "1 santims Latvia 1992 coin",
    "2 Santīmi (Republic)":   "2 santimi Latvia 1992 coin",
    "5 Santīmi (Republic)":   "5 santimi Latvia 1992 coin",
    "10 Santīmu (Republic)":  "10 santimu Latvia 1992 coin",
    "20 Santīmu (Republic)":  "20 santimu Latvia 1992 coin",
    "50 Santīmu (Republic)":  "50 santimu Latvia 1992 coin",
    "1 Lats (Republic)":      "1 lats Latvia 1992 coin",
    "2 Lati (Republic)":      "2 lati Latvia 1992 bimetallic coin",
    "1 Lats (Pretzel)":       "1 lats Latvia 2007 pretzel klingeris",
    "1 Lats (Snowflake)":     "1 lats Latvia snowflake coin",
    "1 Lats (Wagtail)":       "1 lats Latvia 2002 wagtail bird",
    "1 Lats (Mushroom)":      "1 lats Latvia 2004 mushroom boletus",
    "1 Lats (Ant)":           "1 lats Latvia 2003 ant",
    "1 Kopek":                "1 kopek USSR Soviet coin 1961",
    "2 Kopeki":               "2 kopeks USSR Soviet coin",
    "3 Kopeki":               "3 kopeks USSR Soviet coin",
    "5 Kopeek":               "5 kopeks USSR Soviet coin",
    "10 Kopeek":              "10 kopeks USSR Soviet coin",
    "15 Kopeek":              "15 kopeks USSR Soviet coin",
    "20 Kopeek":              "20 kopeks USSR Soviet coin",
    "50 Kopeek":              "50 kopeks USSR Soviet coin",
    "1 Ruble":                "1 ruble USSR Soviet coin 1961",
    "1 Ruble (Lenin)":        "1 ruble USSR 1970 Lenin commemorative",
    "1 Ruble (Gagarin)":      "1 ruble USSR 1981 Gagarin space",
    "1 Ruble (Moscow Olympics)": "1 ruble USSR 1977 Moscow Olympics",
    "1 Pfennig":              "1 pfennig West Germany Federal Republic coin",
    "2 Pfennig":              "2 pfennig Germany Federal Republic coin",
    "5 Pfennig":              "5 pfennig Germany Federal Republic coin",
    "10 Pfennig":             "10 pfennig Germany Federal Republic coin",
    "50 Pfennig":             "50 pfennig Germany woman planting oak",
    "1 Deutsche Mark":        "1 Deutsche Mark Germany Bundesadler",
    "2 Deutsche Mark (Heuss)":"2 Deutsche Mark Theodor Heuss coin",
    "5 Deutsche Mark":        "5 Deutsche Mark Germany silver coin",
    "Lincoln Cent":           "Lincoln cent wheat penny 1909 coin",
    "Buffalo Nickel":         "Buffalo nickel 1913 Native American coin",
    "Mercury Dime":           "Mercury dime 1916 silver coin",
    "Morgan Silver Dollar":   "Morgan silver dollar 1878 coin",
    "Walking Liberty Half Dollar": "Walking Liberty half dollar 1916 coin",
    "Penny (Elizabeth II)":   "penny Elizabeth II 1971 bronze coin United Kingdom",
    "Fifty Pence (Decimal)":  "50 pence Britannia coin United Kingdom",
    "One Pound Coin":         "1 pound coin United Kingdom 1983",
    "Two Pounds (Industrial Revolution)": "2 pounds coin United Kingdom Industrial Revolution",
    "Crown (Winston Churchill)": "crown Churchill commemorative coin 1965",
}


async def search_commons(query: str, client: httpx.AsyncClient) -> str | None:
    """Search Wikimedia Commons and return a usable image URL."""
    try:
        r = await client.get(COMMONS, params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",
            "srlimit": "8",
            "format": "json",
        }, timeout=12)
        results = r.json().get("query", {}).get("search", [])

        for result in results:
            title = result["title"]
            lower = title.lower()
            # Skip non-photo files
            if lower.endswith(".svg") or lower.endswith(".tif") or lower.endswith(".tiff"):
                continue

            r2 = await client.get(COMMONS, params={
                "action": "query",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url|mime|size",
                "iiurlwidth": "400",
                "format": "json",
            }, timeout=12)
            pages = r2.json().get("query", {}).get("pages", {})
            for page in pages.values():
                info = page.get("imageinfo", [])
                if not info:
                    continue
                mime = info[0].get("mime", "")
                size = info[0].get("size", 0)
                if "svg" in mime or size < 5000:
                    continue
                url = info[0].get("thumburl") or info[0].get("url")
                if url:
                    return url
    except Exception as e:
        print(f"  [err] {e}")
    return None


async def run(mode: str):
    updated = 0
    failed  = 0

    async with httpx.AsyncClient(
        headers={"User-Agent": UA},
        verify=False,
        follow_redirects=True,
    ) as client:
        async with Session() as db:
            r = await db.execute(
                select(CatalogItem)
                .options(selectinload(CatalogItem.period).selectinload(Period.country))
                .where(CatalogItem.image_url.is_(None))
                .order_by(CatalogItem.id)
            )
            items = r.scalars().all()
            total = len(items)
            print(f"Atrasti {total} ieraksti bez foto\n")

            for idx, item in enumerate(items, 1):
                cname = (item.period.country.name
                         if item.period and item.period.country else "")
                denom = item.denomination or ""
                name  = item.name

                # Determine mode
                is_euro = cname in EURO_QUERIES and denom in EURO_QUERIES.get(cname, {})

                if mode == "euro" and not is_euro:
                    continue
                if mode == "historical" and is_euro:
                    continue

                if is_euro:
                    query = EURO_QUERIES[cname][denom]
                elif name in HISTORICAL_QUERIES:
                    query = HISTORICAL_QUERIES[name]
                else:
                    # Generic fallback
                    query = f"{name} coin numismatic"

                print(f"[{idx}/{total}] {name[:45]:<45} | {query[:50]}")
                url = await search_commons(query, client)
                await asyncio.sleep(DELAY)

                if url:
                    item.image_url = url
                    updated += 1
                    print(f"  -> OK")
                else:
                    failed += 1
                    print(f"  -> nav atrasts")

                if idx % 15 == 0:
                    await db.commit()
                    print(f"\n  [saglabats] {updated} foto lidz sim\n")

            await db.commit()

    print(f"\n{'='*55}")
    print(f"PABEIGTS: pievienoti {updated} foto, nav atrasts: {failed}")
    print(f"{'='*55}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--euro",       action="store_true")
    parser.add_argument("--historical", action="store_true")
    args = parser.parse_args()

    if args.euro:
        mode = "euro"
    elif args.historical:
        mode = "historical"
    else:
        mode = "all"

    print(f"Rezims: {mode}")
    asyncio.run(run(mode))
