#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed script: Banknote catalog.
Run from backend directory: python seed_banknotes.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import asyncio
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.catalog import Country, Period, CatalogItem, SectionType

DATABASE_URL = "sqlite+aiosqlite:///./kolekcija.db"
engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SECTION = SectionType.banknotes

# ── Latvia First Republic: Rubļi (1919–1922) ──────────────────────────────────
LV_RUBLI = [
    {"name": "5 Rubļi",   "year": "1919", "denom": "5 rubļi",   "km": "P-2",
     "mat": "Cotton paper",
     "obs": "Latvijas Valsts Kases Zīme. Value 5 in ornamental frame. Latvian coat of arms.",
     "rev": "Value 5 RUBĻI in floral border. Bilingua text in Latvian and Russian.",
     "mintage": "5000000", "printer": "Riga"},
    {"name": "10 Rubļi",  "year": "1919", "denom": "10 rubļi",  "km": "P-3",
     "mat": "Cotton paper",
     "obs": "Latvijas Valsts Kases Zīme. Value 10 in ornamental frame.",
     "rev": "Value 10 RUBĻI in floral border.",
     "mintage": "5000000", "printer": "Riga"},
    {"name": "25 Rubļi",  "year": "1919", "denom": "25 rubļi",  "km": "P-4",
     "mat": "Cotton paper",
     "obs": "Latvijas Valsts Kases Zīme. Value 25. Latvian coat of arms.",
     "rev": "Value 25 RUBĻI.",
     "mintage": "3000000", "printer": "Riga"},
    {"name": "50 Rubļi",  "year": "1919", "denom": "50 rubļi",  "km": "P-5",
     "mat": "Cotton paper",
     "obs": "Latvijas Valsts Kases Zīme. Value 50. Arms.",
     "rev": "Value 50 RUBĻI.",
     "mintage": "3000000", "printer": "Riga"},
    {"name": "100 Rubļi", "year": "1919", "denom": "100 rubļi", "km": "P-6",
     "mat": "Cotton paper",
     "obs": "Latvijas Valsts Kases Zīme. Value 100. Latvian arms.",
     "rev": "Value 100 RUBĻI in ornate border.",
     "mintage": "2000000", "printer": "Riga"},
    {"name": "500 Rubļi", "year": "1920", "denom": "500 rubļi", "km": "P-7",
     "mat": "Cotton paper",
     "obs": "Latvijas Valsts Kases Zīme. Value 500. Latvian coat of arms in circle.",
     "rev": "Value 500 RUBĻI.",
     "mintage": "1000000", "printer": "Riga"},
]

# ── Latvia First Republic: Lati (1922–1940) ────────────────────────────────────
LV_LATI = [
    {"name": "5 Lati (1928)",   "year": "1928", "denom": "5 lati",   "km": "P-23",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Latvian Maid (Latvijas Māriņa) with traditional headdress. LATVIJAS BANKA.",
     "rev": "Ornamental design with value 5 LATI, oak and linden branches.",
     "mintage": "2000000", "printer": "Giesecke & Devrient, Leipzig"},
    {"name": "10 Lati (1925)",  "year": "1925", "denom": "10 lati",  "km": "P-24",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Latvian Maid. Value 10. LATVIJAS BANKA.",
     "rev": "Ornamental design with value 10 LATI.",
     "mintage": "2000000", "printer": "Giesecke & Devrient, Leipzig"},
    {"name": "20 Lati (1935)",  "year": "1935", "denom": "20 lati",  "km": "P-29",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Latvian Maid wearing national costume. LATVIJAS BANKA. 20.",
     "rev": "Latvian national coat of arms. Value 20 LATI.",
     "mintage": "1500000", "printer": "Bradbury, Wilkinson & Co., London"},
    {"name": "25 Lati (1928)",  "year": "1928", "denom": "25 lati",  "km": "P-25",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Latvian Maid. LATVIJAS BANKA. 25.",
     "rev": "Value 25 LATI in ornamental design.",
     "mintage": "1200000", "printer": "Giesecke & Devrient, Leipzig"},
    {"name": "50 Lati (1934)",  "year": "1934", "denom": "50 lati",  "km": "P-28",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Latvian Maid. 50 LATI. LATVIJAS BANKA.",
     "rev": "Latvian coat of arms, ornamental border. Value 50 LATI.",
     "mintage": "800000",  "printer": "Bradbury, Wilkinson & Co., London"},
    {"name": "100 Lati (1939)", "year": "1939", "denom": "100 lati", "km": "P-31",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Latvian Maid in full national dress. LATVIJAS BANKA. 100.",
     "rev": "Latvian national coat of arms with sun, stars and oxen. Value 100 LATI.",
     "mintage": "500000",  "printer": "Bradbury, Wilkinson & Co., London"},
]

# ── Latvia Second Republic: Lati (1992–2013) ──────────────────────────────────
LV_REPUBLIC = [
    {"name": "1 Lats (1992)",    "year": "1992", "denom": "1 lats",    "km": "P-42",
     "mat": "Cotton paper",
     "obs": "Latvian coat of arms (rising sun, oxen, stars). LATVIJAS BANKA. 1.",
     "rev": "Oak tree silhouette. Value 1 LATS.",
     "mintage": "20000000", "printer": "De La Rue, London"},
    {"name": "2 Lati (1992)",    "year": "1992", "denom": "2 lati",    "km": "P-43",
     "mat": "Cotton paper",
     "obs": "Latvian coat of arms. LATVIJAS BANKA. 2.",
     "rev": "Value 2 LATI, oak wreath.",
     "mintage": "15000000", "printer": "De La Rue, London"},
    {"name": "5 Lati (1992)",    "year": "1992", "denom": "5 lati",    "km": "P-44",
     "mat": "Cotton paper",
     "obs": "Latvian coat of arms. LATVIJAS BANKA. 5. Krišjānis Barons portrait.",
     "rev": "Dainas (folk songs) motif. Value 5 LATI.",
     "mintage": "10000000", "printer": "De La Rue, London"},
    {"name": "10 Lati (1992)",   "year": "1992", "denom": "10 lati",   "km": "P-45",
     "mat": "Cotton paper",
     "obs": "Portrait of Latvian Maid. LATVIJAS BANKA. 10.",
     "rev": "Landscape with linden tree. Value 10 LATI.",
     "mintage": "8000000",  "printer": "De La Rue, London"},
    {"name": "20 Lati (2007)",   "year": "2007", "denom": "20 lati",   "km": "P-56",
     "mat": "Cotton paper",
     "obs": "Portrait of Latvian Maid. LATVIJAS BANKA. 20. Modern design.",
     "rev": "Landscape motif. Value 20 LATI.",
     "mintage": "5000000",  "printer": "Giesecke & Devrient, Munich"},
    {"name": "50 Lati (1992)",   "year": "1992", "denom": "50 lati",   "km": "P-46",
     "mat": "Cotton paper",
     "obs": "Portrait of Latvian Maid. LATVIJAS BANKA. 50.",
     "rev": "Ornamental design. Value 50 LATI.",
     "mintage": "3000000",  "printer": "De La Rue, London"},
    {"name": "100 Lati (1992)",  "year": "1992", "denom": "100 lati",  "km": "P-47",
     "mat": "Cotton paper",
     "obs": "Portrait of Latvian Maid. LATVIJAS BANKA. 100.",
     "rev": "Ornamental design. Value 100 LATI.",
     "mintage": "2000000",  "printer": "De La Rue, London"},
    {"name": "500 Lati (1998)",  "year": "1998", "denom": "500 lati",  "km": "P-53",
     "mat": "Cotton paper",
     "obs": "Portrait of Latvian Maid in full national costume. LATVIJAS BANKA. 500.",
     "rev": "Ornamental design with Latvian national symbols. Value 500 LATI.",
     "mintage": "500000",   "printer": "De La Rue, London"},
]

# ── USSR Banknotes (1961 reform) ───────────────────────────────────────────────
USSR_NOTES = [
    {"name": "1 Ruble (1961)",   "year": "1961", "denom": "1 ruble",   "km": "P-222",
     "mat": "Cotton paper",
     "obs": "Soviet state emblem (hammer and sickle on globe). ГОСУДАРСТВЕННЫЙ КАЗНАЧЕЙСКИЙ БИЛЕТ СССР. 1.",
     "rev": "Value 1 РУБЛЬ. Ornamental design with Soviet symbols.",
     "mintage": None, "printer": "Goznak (Государственный знак), Moscow"},
    {"name": "3 Rubļi (1961)",   "year": "1961", "denom": "3 rubļi",   "km": "P-223",
     "mat": "Cotton paper",
     "obs": "Lenin mausoleum, Moscow Kremlin. ГОСУДАРСТВЕННЫЙ КАЗНАЧЕЙСКИЙ БИЛЕТ СССР. 3.",
     "rev": "Value 3 РУБЛЯ. Ornamental design.",
     "mintage": None, "printer": "Goznak, Moscow"},
    {"name": "5 Rubles (1961)",  "year": "1961", "denom": "5 rubles",  "km": "P-224",
     "mat": "Cotton paper",
     "obs": "The Spassky Tower of the Moscow Kremlin. ГОСУДАРСТВЕННЫЙ БАНКОВСКИЙ БИЛЕТ СССР. 5.",
     "rev": "Value 5 РУБЛЕЙ. Ornamental design with Soviet emblems.",
     "mintage": None, "printer": "Goznak, Moscow"},
    {"name": "10 Rubles (1961)", "year": "1961", "denom": "10 rubles", "km": "P-233",
     "mat": "Cotton paper",
     "obs": "Soviet state emblem. БИЛЕТ ГОСУДАРСТВЕННОГО БАНКА СССР. 10.",
     "rev": "Value 10 РУБЛЕЙ. Ornamental pattern.",
     "mintage": None, "printer": "Goznak, Moscow"},
    {"name": "25 Rubles (1961)", "year": "1961", "denom": "25 rubles", "km": "P-234",
     "mat": "Cotton paper",
     "obs": "Soviet state emblem. БИЛЕТ ГОСУДАРСТВЕННОГО БАНКА СССР. 25.",
     "rev": "Value 25 РУБЛЕЙ. Ornamental guilloche pattern.",
     "mintage": None, "printer": "Goznak, Moscow"},
    {"name": "50 Rubles (1961)", "year": "1961", "denom": "50 rubles", "km": "P-235",
     "mat": "Cotton paper",
     "obs": "Soviet state emblem. БИЛЕТ ГОСУДАРСТВЕННОГО БАНКА СССР. 50.",
     "rev": "Value 50 РУБЛЕЙ. Ornamental guilloche.",
     "mintage": None, "printer": "Goznak, Moscow"},
    {"name": "100 Rubles (1961)","year": "1961", "denom": "100 rubles","km": "P-236",
     "mat": "Cotton paper",
     "obs": "Portrait of V.I. Lenin. БИЛЕТ ГОСУДАРСТВЕННОГО БАНКА СССР. 100.",
     "rev": "Value 100 РУБЛЕЙ. Ornamental design.",
     "mintage": None, "printer": "Goznak, Moscow"},
    {"name": "50 Rubles (1992)", "year": "1992", "denom": "50 rubles", "km": "P-247",
     "mat": "Cotton paper",
     "obs": "Moscow Kremlin, Spassky Tower. БАНК РОССИЙ. 50.",
     "rev": "Value 50 РУБЛЕЙ. Ornamental pattern.",
     "mintage": None, "printer": "Goznak, Moscow"},
    {"name": "100 Rubles (1993)","year": "1993", "denom": "100 rubles","km": "P-254",
     "mat": "Cotton paper",
     "obs": "Bolshoi Theatre, Moscow. БАНК РОССИЙ. 100.",
     "rev": "Value 100 РУБЛЕЙ. Rossiya (Russia) inscription.",
     "mintage": None, "printer": "Goznak, Moscow"},
]

# ── Germany Deutschmark Banknotes (1960–2001) ──────────────────────────────────
DE_NOTES = [
    {"name": "5 Deutsche Mark (1960)",   "year": "1960", "denom": "5 DM",   "km": "P-18",
     "mat": "Cotton paper",
     "obs": "Portrait of young Venetian woman (after Albrecht Dürer). DEUTSCHE BUNDESBANK. 5.",
     "rev": "Old sailing ship (Kogge). Value 5 DEUTSCHE MARK.",
     "mintage": None, "printer": "Bundesdruckerei, Berlin"},
    {"name": "10 Deutsche Mark (1960)",  "year": "1960", "denom": "10 DM",  "km": "P-19",
     "mat": "Cotton paper",
     "obs": "Portrait of Albrecht Dürer. DEUTSCHE BUNDESBANK. 10.",
     "rev": "Sailing ship (16th century). Value 10 DEUTSCHE MARK.",
     "mintage": None, "printer": "Bundesdruckerei, Berlin"},
    {"name": "20 Deutsche Mark (1960)",  "year": "1960", "denom": "20 DM",  "km": "P-20",
     "mat": "Cotton paper",
     "obs": "Portrait of Elsbeth Tucher (after Dürer). DEUTSCHE BUNDESBANK. 20.",
     "rev": "Violin and bow. Value 20 DEUTSCHE MARK.",
     "mintage": None, "printer": "Bundesdruckerei / Giesecke & Devrient"},
    {"name": "50 Deutsche Mark (1960)",  "year": "1960", "denom": "50 DM",  "km": "P-21",
     "mat": "Cotton paper",
     "obs": "Portrait of Hans Urmiller (after Barthel Bruyn). DEUTSCHE BUNDESBANK. 50.",
     "rev": "Holstein Gate (Holstentor), Lübeck. Value 50 DEUTSCHE MARK.",
     "mintage": None, "printer": "Giesecke & Devrient, Munich"},
    {"name": "100 Deutsche Mark (1960)", "year": "1960", "denom": "100 DM", "km": "P-22",
     "mat": "Cotton paper",
     "obs": "Portrait of Clara Schumann (musician). DEUTSCHE BUNDESBANK. 100.",
     "rev": "Eagle Gate (Adlertor), Rothenburg ob der Tauber. Value 100 DEUTSCHE MARK.",
     "mintage": None, "printer": "Giesecke & Devrient, Munich"},
    {"name": "200 Deutsche Mark (1996)", "year": "1996", "denom": "200 DM", "km": "P-49",
     "mat": "Cotton paper",
     "obs": "Portrait of Paul Ehrlich (Nobel laureate in medicine). DEUTSCHE BUNDESBANK. 200.",
     "rev": "Microscope. Value 200 DEUTSCHE MARK.",
     "mintage": None, "printer": "Giesecke & Devrient / Bundesdruckerei"},
    {"name": "500 Deutsche Mark (1991)", "year": "1991", "denom": "500 DM", "km": "P-43",
     "mat": "Cotton paper",
     "obs": "Portrait of Maria Sibylla Merian (naturalist). DEUTSCHE BUNDESBANK. 500.",
     "rev": "Dandelion and butterfly. Value 500 DEUTSCHE MARK.",
     "mintage": None, "printer": "Giesecke & Devrient, Munich"},
    {"name": "1000 Deutsche Mark (1991)","year": "1991", "denom": "1000 DM","km": "P-44",
     "mat": "Cotton paper",
     "obs": "Portrait of Wilhelm and Jacob Grimm (Brothers Grimm). DEUTSCHE BUNDESBANK. 1000.",
     "rev": "Deutschen Nationalbibliothek, Frankfurt. Value 1000 DEUTSCHE MARK.",
     "mintage": None, "printer": "Giesecke & Devrient, Munich"},
]

# ── United Kingdom Pound Sterling (Elizabeth II era) ──────────────────────────
UK_NOTES = [
    {"name": "£1 (1978)",  "year": "1978", "denom": "£1",  "km": "P-377",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Queen Elizabeth II facing right. ONE POUND. Bank of England. Chief Cashier signature.",
     "rev": "Isaac Newton portrait. Symbols of science: telescope, prism, book.",
     "mintage": None, "printer": "De La Rue, London"},
    {"name": "£5 (1990)",  "year": "1990", "denom": "£5",  "km": "P-382",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Queen Elizabeth II. FIVE POUNDS. Bank of England.",
     "rev": "George Stephenson portrait with locomotive Rocket.",
     "mintage": None, "printer": "De La Rue, London"},
    {"name": "£10 (1992)", "year": "1992", "denom": "£10", "km": "P-383",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Queen Elizabeth II. TEN POUNDS. Bank of England.",
     "rev": "Charles Dickens portrait with scene from The Pickwick Papers.",
     "mintage": None, "printer": "De La Rue, London"},
    {"name": "£20 (1991)", "year": "1991", "denom": "£20", "km": "P-384",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Queen Elizabeth II. TWENTY POUNDS. Bank of England.",
     "rev": "Michael Faraday portrait with electric motor.",
     "mintage": None, "printer": "De La Rue, London"},
    {"name": "£50 (1994)", "year": "1994", "denom": "£50", "km": "P-388",
     "mat": "Cotton-linen paper",
     "obs": "Portrait of Queen Elizabeth II. FIFTY POUNDS. Bank of England.",
     "rev": "Sir John Houblon (first Bank of England governor) portrait.",
     "mintage": None, "printer": "De La Rue, London"},
]

# ── United States Dollar (Federal Reserve Notes) ──────────────────────────────
US_NOTES = [
    {"name": "$1 Federal Reserve Note", "year": "1963", "denom": "$1",  "km": "P-443",
     "mat": "75% cotton / 25% linen",
     "obs": "Portrait of George Washington (1st President). THE UNITED STATES OF AMERICA. ONE DOLLAR. IN GOD WE TRUST.",
     "rev": "The Great Seal of the United States (bald eagle / pyramid with eye). ONE.",
     "mintage": None, "printer": "Bureau of Engraving and Printing, Washington D.C."},
    {"name": "$2 Federal Reserve Note", "year": "1976", "denom": "$2",  "km": "P-461",
     "mat": "75% cotton / 25% linen",
     "obs": "Portrait of Thomas Jefferson (3rd President). THE UNITED STATES OF AMERICA. TWO DOLLARS.",
     "rev": "Signing of the Declaration of Independence (after John Trumbull painting).",
     "mintage": None, "printer": "Bureau of Engraving and Printing, Washington D.C."},
    {"name": "$5 Federal Reserve Note", "year": "1969", "denom": "$5",  "km": "P-444",
     "mat": "75% cotton / 25% linen",
     "obs": "Portrait of Abraham Lincoln (16th President). THE UNITED STATES OF AMERICA. FIVE DOLLARS.",
     "rev": "Lincoln Memorial, Washington D.C. Value FIVE DOLLARS.",
     "mintage": None, "printer": "Bureau of Engraving and Printing, Washington D.C."},
    {"name": "$10 Federal Reserve Note","year": "1969", "denom": "$10", "km": "P-445",
     "mat": "75% cotton / 25% linen",
     "obs": "Portrait of Alexander Hamilton (1st Secretary of the Treasury). THE UNITED STATES OF AMERICA. TEN DOLLARS.",
     "rev": "United States Treasury Building, Washington D.C.",
     "mintage": None, "printer": "Bureau of Engraving and Printing, Washington D.C."},
    {"name": "$20 Federal Reserve Note","year": "1969", "denom": "$20", "km": "P-446",
     "mat": "75% cotton / 25% linen",
     "obs": "Portrait of Andrew Jackson (7th President). THE UNITED STATES OF AMERICA. TWENTY DOLLARS.",
     "rev": "The White House, Washington D.C.",
     "mintage": None, "printer": "Bureau of Engraving and Printing, Washington D.C."},
    {"name": "$50 Federal Reserve Note","year": "1969", "denom": "$50", "km": "P-447",
     "mat": "75% cotton / 25% linen",
     "obs": "Portrait of Ulysses S. Grant (18th President). THE UNITED STATES OF AMERICA. FIFTY DOLLARS.",
     "rev": "United States Capitol Building, Washington D.C.",
     "mintage": None, "printer": "Bureau of Engraving and Printing, Washington D.C."},
    {"name": "$100 Federal Reserve Note","year": "1969","denom": "$100","km": "P-448",
     "mat": "75% cotton / 25% linen",
     "obs": "Portrait of Benjamin Franklin (Founding Father). THE UNITED STATES OF AMERICA. ONE HUNDRED DOLLARS.",
     "rev": "Independence Hall, Philadelphia. Value ONE HUNDRED DOLLARS.",
     "mintage": None, "printer": "Bureau of Engraving and Printing, Washington D.C."},
]

# ── Euro Banknotes (European Union / ECB) ─────────────────────────────────────
EURO_NOTES = [
    {"name": "€5 Euro (2002)",   "year": "2002", "denom": "€5",   "km": "P-1",
     "mat": "Cotton fibre paper",
     "obs": "Classical/antique architecture (windows and arches). EUROPEAN CENTRAL BANK / BANQUE CENTRALE EUROPÉENNE / etc. Five Euros.",
     "rev": "Classical bridge motif. Stars of the EU. Value 5.",
     "mintage": None, "printer": "Various national printers under ECB authorization"},
    {"name": "€10 Euro (2002)",  "year": "2002", "denom": "€10",  "km": "P-2",
     "mat": "Cotton fibre paper",
     "obs": "Romanesque architecture (arches and windows). EUROPEAN CENTRAL BANK. Ten Euros.",
     "rev": "Romanesque bridge. EU stars. Value 10.",
     "mintage": None, "printer": "Various national printers under ECB authorization"},
    {"name": "€20 Euro (2002)",  "year": "2002", "denom": "€20",  "km": "P-3",
     "mat": "Cotton fibre paper",
     "obs": "Gothic architecture (windows and arches). EUROPEAN CENTRAL BANK. Twenty Euros.",
     "rev": "Gothic bridge. EU stars. Value 20.",
     "mintage": None, "printer": "Various national printers under ECB authorization"},
    {"name": "€50 Euro (2002)",  "year": "2002", "denom": "€50",  "km": "P-4",
     "mat": "Cotton fibre paper",
     "obs": "Renaissance architecture. EUROPEAN CENTRAL BANK. Fifty Euros.",
     "rev": "Renaissance bridge. EU stars. Value 50.",
     "mintage": None, "printer": "Various national printers under ECB authorization"},
    {"name": "€100 Euro (2002)", "year": "2002", "denom": "€100", "km": "P-5",
     "mat": "Cotton fibre paper",
     "obs": "Baroque/Rococo architecture. EUROPEAN CENTRAL BANK. One Hundred Euros.",
     "rev": "Baroque bridge. EU stars. Value 100.",
     "mintage": None, "printer": "Various national printers under ECB authorization"},
    {"name": "€200 Euro (2002)", "year": "2002", "denom": "€200", "km": "P-6",
     "mat": "Cotton fibre paper",
     "obs": "Iron and glass architecture (19th century). EUROPEAN CENTRAL BANK. Two Hundred Euros.",
     "rev": "Iron bridge. EU stars. Value 200.",
     "mintage": None, "printer": "Various national printers under ECB authorization"},
    {"name": "€500 Euro (2002)", "year": "2002", "denom": "€500", "km": "P-7",
     "mat": "Cotton fibre paper",
     "obs": "Modern 20th century architecture. EUROPEAN CENTRAL BANK. Five Hundred Euros.",
     "rev": "Modern bridge. EU stars. Value 500.",
     "mintage": None, "printer": "Various national printers under ECB authorization"},
]


async def ensure_period(db, country_name: str, period_name: str,
                        year_start: int, year_end: int | None) -> Period | None:
    """Find or create a banknotes period for the given country."""
    r = await db.execute(select(Country).where(Country.name.ilike(country_name)))
    country = r.scalars().first()
    if not country:
        r = await db.execute(select(Country).where(Country.name.ilike(f"%{country_name}%")))
        country = r.scalars().first()
    if not country:
        print(f"  [!] Valsts '{country_name}' nav atrasta DB — izlaizu")
        return None

    r = await db.execute(select(Period).where(
        Period.country_id == country.id,
        Period.section == SECTION,
        Period.name == period_name,
    ))
    period = r.scalars().first()
    if period:
        return period

    period = Period(
        name=period_name,
        year_start=year_start,
        year_end=year_end,
        country_id=country.id,
        section=SECTION,
        coin_category="circulation",
    )
    db.add(period)
    await db.flush()
    print(f"  [+] Izveidots periods: {country.name} — {period_name} ({year_start}–{year_end or '...'})")
    return period


async def note_exists(db, period_id: int, denomination: str) -> bool:
    r = await db.execute(select(CatalogItem).where(
        CatalogItem.period_id == period_id,
        CatalogItem.denomination == denomination,
        CatalogItem.section == SECTION,
    ))
    return r.scalars().first() is not None


async def add_note(db, period: Period, note: dict) -> bool:
    if await note_exists(db, period.id, note["denom"]):
        return False
    item = CatalogItem(
        section=SECTION,
        period_id=period.id,
        name=note["name"],
        year=note["year"],
        denomination=note["denom"],
        material=note.get("mat"),
        mint=note.get("printer"),
        mintage=note.get("mintage"),
        catalog_number=note.get("km"),
        obverse_description=note.get("obs"),
        reverse_description=note.get("rev"),
        coin_category="circulation",
    )
    db.add(item)
    return True


async def seed():
    added = 0
    skipped = 0

    async with Session() as db:

        # ── 1. Latvia: Rubļi (1919–1922) ─────────────────────────────────────
        print("\n[LV] Latvija — Rubļi (1919–1922)...")
        p = await ensure_period(db, "Latvia", "Rubļu periods (1919–1922)", 1919, 1922)
        if p:
            for n in LV_RUBLI:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_RUBLI)} banknotes")

        # ── 2. Latvia: Lati — Pirmā republika (1922–1940) ─────────────────────
        print("\n[LV] Latvija — Lati, Pirmā republika (1922–1940)...")
        p = await ensure_period(db, "Latvia", "Latu periods — Pirmā republika (1922–1940)", 1922, 1940)
        if p:
            for n in LV_LATI:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_LATI)} banknotes")

        # ── 3. Latvia: Lati — Otrā republika (1992–2013) ──────────────────────
        print("\n[LV] Latvija — Lati, Otrā republika (1992–2013)...")
        p = await ensure_period(db, "Latvia", "Latu periods — Otrā republika (1992–2013)", 1992, 2013)
        if p:
            for n in LV_REPUBLIC:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_REPUBLIC)} banknotes")

        # ── 4. USSR Rubles (1961–1991) ────────────────────────────────────────
        print("\n[USSR] PSRS — Rubļi (1961–1991)...")
        p = await ensure_period(db, "Soviet Union", "PSRS rubļi (1961–1991)", 1961, 1991)
        if not p:
            p = await ensure_period(db, "Russia", "PSRS rubļi (1961–1991)", 1961, 1991)
        if p:
            for n in USSR_NOTES:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(USSR_NOTES)} banknotes")

        # ── 5. Germany: Deutschmark (1948–2001) ───────────────────────────────
        print("\n[DE] Vācija — Deutschmark (1960–2001)...")
        p = await ensure_period(db, "Germany", "Deutschmark (1948–2001)", 1948, 2001)
        if p:
            for n in DE_NOTES:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(DE_NOTES)} banknotes")

        # ── 6. United Kingdom: Pound Sterling ────────────────────────────────
        print("\n[UK] Lielbritānija — Pound Sterling...")
        p = await ensure_period(db, "United Kingdom", "Pound Sterling (Elizabeth II)", 1952, 2022)
        if not p:
            p = await ensure_period(db, "Great Britain", "Pound Sterling (Elizabeth II)", 1952, 2022)
        if p:
            for n in UK_NOTES:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(UK_NOTES)} banknotes")

        # ── 7. United States: Dollar ──────────────────────────────────────────
        print("\n[US] ASV — Dollar...")
        p = await ensure_period(db, "United States", "US Dollar (Federal Reserve)", 1913, None)
        if not p:
            p = await ensure_period(db, "USA", "US Dollar (Federal Reserve)", 1913, None)
        if p:
            for n in US_NOTES:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(US_NOTES)} banknotes")

        # ── 8. Euro Banknotes (European Union) ───────────────────────────────
        print("\n[EU] Eiropas Savienība — Euro banknotes (2002–)...")
        p = await ensure_period(db, "European Union", "Euro banknotes (2002–)", 2002, None)
        if not p:
            # Try Germany as fallback (ECB is in Frankfurt)
            p = await ensure_period(db, "Germany", "Euro banknotes — ECB (2002–)", 2002, None)
        if p:
            for n in EURO_NOTES:
                ok = await add_note(db, p, n)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(EURO_NOTES)} banknotes")

    print(f"\n{'='*50}")
    print(f"PABEIGTS! Pievienots: {added}, izlaists (jau eksistē): {skipped}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(seed())
