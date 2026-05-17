#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed script: Medals catalog — Latvian First Republic, Soviet USSR, German, Latvian Republic.
Run from backend directory: python seed_medals.py
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


# ── Latvian First Republic medals & orders (1918–1940) ────────────────────────
LV_FIRST_REPUBLIC_MEDALS = [
    {
        "name": "Triju Zvaigžņu ordenis — I šķira",
        "year": "1924",
        "cat_no": "TZO-I",
        "mat": "Gold, silver, enamel",
        "dia": "60.00", "wt": "35.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 50",
        "obs": "Three golden stars in a triangle arrangement on a white enamel Maltese cross with golden rays. Latvian national ribbon: dark red with white stripes.",
        "rev": "LATVIJA and three stars engraved on the back.",
        "desc": "Order of the Three Stars, 1st class (Grand Cross). Highest Latvian state decoration, established 1924 by the Saeima. Awarded for outstanding civil and military merit to Latvia.",
    },
    {
        "name": "Triju Zvaigžņu ordenis — II šķira",
        "year": "1924",
        "cat_no": "TZO-II",
        "mat": "Silver, enamel",
        "dia": "52.00", "wt": "25.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 150",
        "obs": "Three silver stars on white enamel Maltese cross with silver rays. Neck decoration.",
        "rev": "LATVIJA and three stars on reverse.",
        "desc": "Order of the Three Stars, 2nd class. Neck decoration awarded for distinguished service to Latvia.",
    },
    {
        "name": "Triju Zvaigžņu ordenis — III šķira",
        "year": "1924",
        "cat_no": "TZO-III",
        "mat": "Silver, enamel",
        "dia": "48.00", "wt": "20.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 500",
        "obs": "Three silver stars on white enamel cross. Breast decoration with ribbon.",
        "rev": "LATVIJA on reverse.",
        "desc": "Order of the Three Stars, 3rd class. Breast star awarded for meritorious service to the Latvian state.",
    },
    {
        "name": "Triju Zvaigžņu ordenis — IV šķira",
        "year": "1924",
        "cat_no": "TZO-IV",
        "mat": "Silver, enamel",
        "dia": "42.00", "wt": "16.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 1500",
        "obs": "Three silver stars on white enamel cross, smaller format. Worn on ribbon.",
        "rev": "LATVIJA on reverse.",
        "desc": "Order of the Three Stars, 4th class. Most commonly awarded class; given for significant contributions to Latvia.",
    },
    {
        "name": "Triju Zvaigžņu ordenis — V šķira",
        "year": "1924",
        "cat_no": "TZO-V",
        "mat": "Silver, enamel",
        "dia": "38.00", "wt": "12.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 3000",
        "obs": "Three silver stars on white enamel cross, smallest format. Worn on ribbon.",
        "rev": "LATVIJA on reverse.",
        "desc": "Order of the Three Stars, 5th class. Entry-level class of the order, awarded for loyal service to Latvia.",
    },
    {
        "name": "Lāčplēša Kara ordenis — I šķira",
        "year": "1920",
        "cat_no": "LKO-I",
        "mat": "Gold, silver, enamel",
        "dia": "52.00", "wt": "28.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 20",
        "obs": "Bear head (Lāčplēsis symbol) on Maltese cross with red and white enamel. LATVIJA inscription. Worn on neck ribbon.",
        "rev": "Serial number and LATVIJA engraved.",
        "desc": "Military Order of Lāčplēsis, 1st class. Established 1919, Latvia's highest military award for bravery in the Liberation War (1918–1920). Named after the mythological hero Lāčplēsis (Bear-Slayer).",
    },
    {
        "name": "Lāčplēša Kara ordenis — II šķira",
        "year": "1920",
        "cat_no": "LKO-II",
        "mat": "Silver, enamel",
        "dia": "46.00", "wt": "22.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 300",
        "obs": "Bear head on Maltese cross with red/white enamel. Breast decoration with ribbon.",
        "rev": "Serial number engraved on reverse.",
        "desc": "Military Order of Lāčplēsis, 2nd class. Awarded for extraordinary bravery during the Latvian War of Independence.",
    },
    {
        "name": "Lāčplēša Kara ordenis — III šķira",
        "year": "1920",
        "cat_no": "LKO-III",
        "mat": "Bronze, enamel",
        "dia": "40.00", "wt": "15.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 2000",
        "obs": "Bear head on cross with red/white enamel. Smaller format with ribbon.",
        "rev": "Serial number engraved.",
        "desc": "Military Order of Lāčplēsis, 3rd class. Most numerous class, awarded to soldiers and officers for personal bravery in combat during the Liberation War.",
    },
    {
        "name": "Viestura ordenis — I šķira",
        "year": "1938",
        "cat_no": "VO-I",
        "mat": "Gold, silver, enamel",
        "dia": "65.00", "wt": "40.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 10",
        "obs": "Medieval Latvian warrior Viesturs on horseback, surrounded by oak leaves. Golden cross with white enamel.",
        "rev": "LATVIJA and serial number.",
        "desc": "Order of Viesturs, 1st class (Grand Cross). Established 1938 by President Ulmanis. Awarded to foreign heads of state and highest dignitaries. Named after 13th-century Latvian chieftain Viesturs.",
    },
    {
        "name": "Viestura ordenis — IV šķira",
        "year": "1938",
        "cat_no": "VO-IV",
        "mat": "Silver, enamel",
        "dia": "44.00", "wt": "18.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 800",
        "obs": "Medieval warrior motif on silver cross, white/blue enamel. Breast decoration.",
        "rev": "LATVIJA on reverse.",
        "desc": "Order of Viesturs, 4th class. Most commonly distributed class, awarded to foreign officials and domestic merit holders.",
    },
    {
        "name": "Atzinības krusts — I šķira",
        "year": "1925",
        "cat_no": "AK-I",
        "mat": "Gold, enamel",
        "dia": "58.00", "wt": "30.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 30",
        "obs": "Ornate gold cross with Latvian folk-art motifs and enamel in national colors (red/white). Ribbon decoration.",
        "rev": "LATVIJA and ATZINĪBA (recognition).",
        "desc": "Cross of Recognition, 1st class. Established 1925 to recognize cultural, scientific, and social contributions to Latvia. First Latvian civil award.",
    },
    {
        "name": "Atzinības krusts — IV šķira",
        "year": "1925",
        "cat_no": "AK-IV",
        "mat": "Bronze, enamel",
        "dia": "40.00", "wt": "14.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 4000",
        "obs": "Bronze cross with folk-art motifs and enamel. Worn on ribbon.",
        "rev": "LATVIJA and ATZINĪBA on reverse.",
        "desc": "Cross of Recognition, 4th class. Most common class; awarded to teachers, doctors, cultural workers, and public servants for service to Latvia.",
    },
    {
        "name": "Brīvības krusts",
        "year": "1928",
        "cat_no": "BK-1928",
        "mat": "Bronze",
        "dia": "38.00", "wt": "18.00",
        "mint": "State Mint of Latvia, Riga",
        "mintage": "approx. 50000",
        "obs": "Latvian coat of arms (rising sun, three stars, ox, griffin, lion) on a Greek cross. LATVIJA 1918–1928.",
        "rev": "Oak wreath and date 1918–1928.",
        "desc": "Freedom Cross (Brīvības krusts). Commemorative medal issued for the 10th anniversary of Latvian independence (1928). Awarded to all soldiers who served during the Liberation War (1918–1920).",
    },
    {
        "name": "Dzelzceļnieku krusts",
        "year": "1929",
        "cat_no": "DzK-1929",
        "mat": "Bronze, enamel",
        "dia": "36.00", "wt": "14.00",
        "mint": "W. F. Müller, Riga",
        "mintage": "approx. 3000",
        "obs": "Wheel and rail motif with Latvian national colors enamel. Cross shape.",
        "rev": "LATVIJAS DZELZCEĻI (Latvian Railways).",
        "desc": "Railway Cross. Awarded to Latvian railway workers for long service and merit. Established by the Latvian Railways administration.",
    },
    {
        "name": "Nopelnu krusts",
        "year": "1926",
        "cat_no": "NK-1926",
        "mat": "Bronze",
        "dia": "38.00", "wt": "15.00",
        "mint": "State Mint of Latvia, Riga",
        "mintage": "approx. 10000",
        "obs": "Latvian coat of arms on a simple cross. NOPELNU KRUSTS (Merit Cross).",
        "rev": "LATVIJA and date.",
        "desc": "Cross of Merit (Nopelnu krusts). General merit award for civilian service to Latvia. Lower in precedence than the Order of the Three Stars.",
    },
]

# ── Latvian Second Republic medals (1991–present) ─────────────────────────────
LV_REPUBLIC_MEDALS = [
    {
        "name": "Triju Zvaigžņu ordenis (restored) — III šķira",
        "year": "1994",
        "cat_no": "TZO-R-III",
        "mat": "Silver, enamel",
        "dia": "48.00", "wt": "20.00",
        "mint": "Jānis Strupulis workshop, Riga",
        "mintage": None,
        "obs": "Three silver stars on white enamel Maltese cross, restored design based on 1924 original. Breast decoration with carmine/white ribbon.",
        "rev": "LATVIJA on reverse.",
        "desc": "Order of the Three Stars, 3rd class (restored). Re-established 1994 by the restored Republic of Latvia. Highest national order, awarded to citizens and foreigners for distinguished service to Latvia.",
    },
    {
        "name": "Lāčplēša Kara ordenis (restored) — III šķira",
        "year": "1995",
        "cat_no": "LKO-R-III",
        "mat": "Bronze, enamel",
        "dia": "40.00", "wt": "15.00",
        "mint": "Jānis Strupulis workshop, Riga",
        "mintage": None,
        "obs": "Bear head on cross with red/white enamel, restored 1920 design. LATVIJA inscription.",
        "rev": "Serial number engraved.",
        "desc": "Military Order of Lāčplēsis, 3rd class (restored). Re-established 1995 for veterans of the National Partisans (Forest Brothers) who fought against Soviet occupation.",
    },
    {
        "name": "Atzinības krusts (restored) — IV šķira",
        "year": "1994",
        "cat_no": "AK-R-IV",
        "mat": "Bronze, enamel",
        "dia": "40.00", "wt": "14.00",
        "mint": "Jānis Strupulis workshop, Riga",
        "mintage": None,
        "obs": "Bronze cross with folk-art motifs, restored design. LATVIJA inscription.",
        "rev": "ATZINĪBA on reverse.",
        "desc": "Cross of Recognition, 4th class (restored). Re-established 1994 for cultural and social merit to Latvia.",
    },
    {
        "name": "Viestura ordenis (restored) — IV šķira",
        "year": "2003",
        "cat_no": "VO-R-IV",
        "mat": "Silver, enamel",
        "dia": "44.00", "wt": "18.00",
        "mint": "Jānis Strupulis workshop, Riga",
        "mintage": None,
        "obs": "Viesturs warrior motif on silver cross. LATVIJA.",
        "rev": "LATVIJA on reverse.",
        "desc": "Order of Viesturs, 4th class (restored). Re-established 2003. Awarded to foreigners and Latvians for diplomatic and cultural contributions.",
    },
    {
        "name": "Latvijas Republikas Aizsardzības ministrijas Atzinības raksts",
        "year": "2000",
        "cat_no": "AM-AZ-2000",
        "mat": "Bronze",
        "dia": "35.00", "wt": "12.00",
        "mint": "State Mint of Latvia",
        "mintage": None,
        "obs": "Latvian national coat of arms with military symbols. AIZSARDZĪBAS MINISTRIJA.",
        "rev": "LATVIJA and date.",
        "desc": "Ministry of Defence Commendation Medal. Awarded to Latvian military personnel and civilians for service to national defense.",
    },
    {
        "name": "NATO dalībvalsts piemiņas medaļa",
        "year": "2004",
        "cat_no": "NATO-LV-2004",
        "mat": "Brass, enamel",
        "dia": "32.00", "wt": "10.00",
        "mint": "State Mint of Latvia",
        "mintage": None,
        "obs": "NATO compass rose symbol alongside Latvian coat of arms. NATO and LATVIJA inscriptions.",
        "rev": "2004 and Baltic NATO accession inscription.",
        "desc": "NATO Membership Commemorative Medal. Issued to mark Latvia's accession to NATO on 29 March 2004.",
    },
]

# ── USSR / Soviet medals ───────────────────────────────────────────────────────
USSR_MEDALS = [
    {
        "name": "Medaļa 'Par drosmi' (За отвагу)",
        "year": "1938",
        "cat_no": "SU-ZA-OTVAGU",
        "mat": "Silver",
        "dia": "37.00", "wt": "25.00",
        "mint": "Leningrad / Moscow Mint",
        "mintage": "approx. 4500000",
        "obs": "T-35 tank and aircraft in relief. ЗА ОТВАГУ (For Valor) inscription. USSR inscription at bottom.",
        "rev": "Smooth reverse with serial number stamped.",
        "desc": "Medal for Valor (За отвагу). Established 1938. One of the most respected Soviet military medals, awarded exclusively for personal courage and bravery in combat. Approximately 4.5 million awarded.",
    },
    {
        "name": "Medaļa 'Par kaujas nopelniem' (За боевые заслуги)",
        "year": "1938",
        "cat_no": "SU-ZA-BOJ-ZAS",
        "mat": "Silver",
        "dia": "32.00", "wt": "15.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 5200000",
        "obs": "ЗА БОЕВЫЕ ЗАСЛУГИ (For Combat Service) inscription. Red banner motif.",
        "rev": "Serial number stamped on smooth reverse.",
        "desc": "Medal for Combat Service (За боевые заслуги). Established 1938. Awarded for skilled and courageous actions in combat that significantly aided the success of operations. Over 5 million awarded.",
    },
    {
        "name": "Sarkanās Zvaigznes ordenis (Орден Красной Звезды)",
        "year": "1930",
        "cat_no": "SU-OKZ",
        "mat": "Silver, enamel",
        "dia": "47.00", "wt": "33.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 3876740",
        "obs": "Red five-pointed star with soldier in uniform at center. Red enamel star with silver border. ПРОЛЕТАРИИ ВСЕХ СТРАН СОЕДИНЯЙТЕСЬ (Workers of the world, unite!).",
        "rev": "Screwback mounting with serial number.",
        "desc": "Order of the Red Star (Орден Красной Звезды). Established 1930. Military order awarded for distinguished service in defense of USSR in peacetime or wartime. Nearly 4 million awarded — one of the most common Soviet orders.",
    },
    {
        "name": "Slavas ordenis — III šķira (Орден Славы III степени)",
        "year": "1943",
        "cat_no": "SU-OS-III",
        "mat": "Silver",
        "dia": "46.00", "wt": "30.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 980000",
        "obs": "Kremlin Spasskaya Tower in relief on five-pointed star. СЛАВА (Glory) at top. Red enamel center.",
        "rev": "Serial number stamped.",
        "desc": "Order of Glory, 3rd class (Орден Славы). Established November 1943. Awarded only to enlisted soldiers and junior sergeants for personal bravery. Modelled after Imperial Russia's St. George Cross. About 980,000 3rd class awards made.",
    },
    {
        "name": "Slavas ordenis — II šķira (Орден Славы II степени)",
        "year": "1943",
        "cat_no": "SU-OS-II",
        "mat": "Silver, gold plating",
        "dia": "46.00", "wt": "32.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 46473",
        "obs": "Kremlin Spasskaya Tower on star. СЛАВА inscription. Partially gold-plated.",
        "rev": "Serial number stamped.",
        "desc": "Order of Glory, 2nd class. Gold-plated version awarded for second act of exceptional personal bravery. About 46,000 awarded.",
    },
    {
        "name": "Slavas ordenis — I šķira (Орден Славы I степени)",
        "year": "1943",
        "cat_no": "SU-OS-I",
        "mat": "Gold",
        "dia": "46.00", "wt": "30.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 2631",
        "obs": "Full gold Kremlin tower on star. СЛАВА inscription. Worn on ribbon above all other medals.",
        "rev": "Serial number engraved.",
        "desc": "Order of Glory, 1st class. The full gold award given for a third act of exceptional bravery. Only 2,631 awarded. Full Cavaliers of all 3 classes received rights equivalent to Heroes of the Soviet Union.",
    },
    {
        "name": "Tēvijas kara ordenis — I šķira (Орден Отечественной войны I степени)",
        "year": "1942",
        "cat_no": "SU-OOW-I",
        "mat": "Gold, silver, enamel",
        "dia": "45.00", "wt": "32.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 344000",
        "obs": "Red star with golden rays. Crossed rifle and saber at center. ОТЕЧЕСТВЕННАЯ ВОЙНА (Patriotic War). Red and gold enamel.",
        "rev": "Serial number. Screwback mount.",
        "desc": "Order of the Patriotic War, 1st class (Орден Отечественной войны). Established May 1942. First Soviet order awarded posthumously and to foreign allies. 1st class in gold-tinted silver for officers; awarded for destroying enemy equipment or leading troops to victory.",
    },
    {
        "name": "Tēvijas kara ordenis — II šķira (Орден Отечественной войны II степени)",
        "year": "1942",
        "cat_no": "SU-OOW-II",
        "mat": "Silver, enamel",
        "dia": "45.00", "wt": "28.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 1028000",
        "obs": "Red star with silver rays. Crossed rifle and saber. ОТЕЧЕСТВЕННАЯ ВОЙНА in red enamel.",
        "rev": "Serial number. Screwback mount.",
        "desc": "Order of the Patriotic War, 2nd class. Silver version awarded for contributing to victory in combat. Over 1 million awarded during WWII; mass re-issued to all veterans in 1985 for the 40th anniversary.",
    },
    {
        "name": "Medaļa 'Par Ļeņingradas aizstāvēšanu'",
        "year": "1942",
        "cat_no": "SU-LENINGRAD",
        "mat": "Brass",
        "dia": "32.00", "wt": "12.00",
        "mint": "Leningrad Mint",
        "mintage": "approx. 1470000",
        "obs": "Soviet soldiers, sailors, and workers standing before Leningrad skyline. Admiralty building visible. Hammer and sickle at top.",
        "rev": "ЗА НАШУ СОВЕТСКУЮ РОДИНУ (For our Soviet Motherland) on reverse.",
        "desc": "Medal for the Defense of Leningrad (Медаль «За оборону Ленинграда»). Established December 1942. Awarded to military and civilian defenders of the 872-day Siege of Leningrad (1941–1944). About 1.47 million awarded.",
    },
    {
        "name": "Medaļa 'Par Staļingradas aizstāvēšanu'",
        "year": "1942",
        "cat_no": "SU-STALINGRAD",
        "mat": "Brass",
        "dia": "32.00", "wt": "12.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 760000",
        "obs": "Tank and aircraft battle scene above Stalingrad cityscape. Hammer and sickle at top.",
        "rev": "ЗА НАШУ СОВЕТСКУЮ РОДИНУ on reverse.",
        "desc": "Medal for the Defense of Stalingrad (Медаль «За оборону Сталинграда»). Established December 1942. Awarded for defending the city during the Battle of Stalingrad (Aug 1942 – Feb 1943). About 760,000 awarded.",
    },
    {
        "name": "Medaļa 'Par uzvaru pār Vāciju' (За победу над Германией)",
        "year": "1945",
        "cat_no": "SU-VICTORY-DE",
        "mat": "Brass",
        "dia": "32.00", "wt": "12.00",
        "mint": "Moscow / Leningrad Mint",
        "mintage": "approx. 14900000",
        "obs": "Portrait of Stalin in profile facing right. НАШЕ ДЕЛО ПРАВОЕ МЫ ПОБЕДИЛИ (Our cause was just, we have won).",
        "rev": "ЗА ПОБЕДУ НАД ГЕРМАНИЕЙ В ВЕЛИКОЙ ОТЕЧЕСТВЕННОЙ ВОЙНЕ 1941–1945 ГГ.",
        "desc": "Medal for Victory over Germany in the Great Patriotic War 1941–1945. Established May 1945. Awarded to all Soviet military personnel who participated in WWII on any front. Nearly 15 million awarded — the most widely distributed Soviet WWII medal.",
    },
    {
        "name": "Medaļa 'Par uzvaru pār Japānu' (За победу над Японией)",
        "year": "1945",
        "cat_no": "SU-VICTORY-JP",
        "mat": "Brass",
        "dia": "32.00", "wt": "12.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 1831000",
        "obs": "Soviet soldiers in battle, Rising Sun imagery. Hammer and sickle at top.",
        "rev": "ЗА ПОБЕДУ НАД ЯПОНИЕЙ on reverse.",
        "desc": "Medal for Victory over Japan (Медаль «За победу над Японией»). Established September 1945. Awarded for participation in the Soviet-Japanese War (August–September 1945). About 1.83 million awarded.",
    },
    {
        "name": "Ļeņina ordenis (Орден Ленина)",
        "year": "1930",
        "cat_no": "SU-OL",
        "mat": "Gold, platinum, enamel",
        "dia": "38.00", "wt": "35.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 431418",
        "obs": "Portrait medallion of Lenin facing left in center. Hammer and sickle and wheat sheaves surrounding. Gold with red enamel banner.",
        "rev": "Serial number. Originally pin, later screwback.",
        "desc": "Order of Lenin (Орден Ленина). Established 1930. The highest civilian honor of the USSR, equivalent to the Hero of Soviet Union in prestige. Awarded for extraordinary service to the Communist Party and Soviet state. About 431,000 awarded.",
    },
    {
        "name": "PSRS Varoņa zelta zvaigzne (Золотая Звезда Героя)",
        "year": "1939",
        "cat_no": "SU-HERO-GOLD",
        "mat": "Gold",
        "dia": "32.00", "wt": "21.50",
        "mint": "Moscow Mint",
        "mintage": "approx. 12772",
        "obs": "Five-pointed star in gold. ГЕРОЙ СССР (Hero of the USSR) on reverse ribbon.",
        "rev": "ГЕРОЙ СОВЕТСКОГО СОЮЗА and serial number engraved.",
        "desc": "Hero of the Soviet Union Gold Star Medal. Established 1939. The supreme distinction of the USSR awarded for heroic feats in service to the Soviet state and society. Only 12,772 awarded across the entire Soviet era.",
    },
    {
        "name": "Jubliejas medaļa '30 gadi PSRS uzvarā' (30 лет Победы)",
        "year": "1975",
        "cat_no": "SU-30-VICTORY",
        "mat": "Brass",
        "dia": "32.00", "wt": "12.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 14000000",
        "obs": "Soviet soldier silhouette with Order of the Patriotic War star. 30 ЛЕТ ПОБЕДЫ.",
        "rev": "ЗА НАШУ СОВЕТСКУЮ РОДИНУ on reverse.",
        "desc": "Jubilee Medal '30 Years of Victory in the Great Patriotic War 1941–1945'. Issued 1975 for the 30th anniversary of WWII victory. Awarded to all living WWII veterans.",
    },
    {
        "name": "Jubliejas medaļa '40 gadi PSRS uzvarā' (40 лет Победы)",
        "year": "1985",
        "cat_no": "SU-40-VICTORY",
        "mat": "Brass, enamel",
        "dia": "32.00", "wt": "12.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 9000000",
        "obs": "Order of the Patriotic War, 1st class motif. 40 ЛЕТ ПОБЕДЫ in red enamel arc.",
        "rev": "ЗА НАШУ СОВЕТСКУЮ РОДИНУ.",
        "desc": "Jubilee Medal '40 Years of Victory'. Issued 1985 for the 40th anniversary. Awarded to WWII veterans still alive; also accompanied by mass re-issue of the Order of the Patriotic War.",
    },
    {
        "name": "Darba veterāna medaļa (Ветеран труда)",
        "year": "1974",
        "cat_no": "SU-VET-TRUD",
        "mat": "Brass, enamel",
        "dia": "32.00", "wt": "12.00",
        "mint": "Moscow Mint",
        "mintage": "approx. 40000000",
        "obs": "Hammer and sickle with cogwheel and wheat sheaves. Red enamel banner: ВЕТЕРАН ТРУДА.",
        "rev": "ЗА ДОЛГОЛЕТНИЙ ДОБРОСОВЕСТНЫЙ ТРУД (For long and dedicated work).",
        "desc": "Veteran of Labour Medal (Медаль «Ветеран труда»). Established 1974. Awarded to workers and employees with at least 25–35 years of service. One of the most common Soviet medals — approximately 40 million awarded.",
    },
]

# ── German medals (Imperial & WWII era) ───────────────────────────────────────
DE_MEDALS = [
    {
        "name": "Dzelzs krusts I šķira (Eisernes Kreuz 1. Klasse)",
        "year": "1939",
        "cat_no": "DE-EK-I-1939",
        "mat": "Iron, silver frame",
        "dia": "44.00", "wt": "26.00",
        "mint": "Multiple German manufacturers",
        "mintage": "approx. 450000",
        "obs": "Black iron Maltese cross with silver border. WWII version has swastika at center and date 1939 at bottom arm.",
        "rev": "1813 at top arm (original institution date). Pin fastening. No ribbon — worn directly on uniform.",
        "desc": "Iron Cross, 1st Class (Eisernes Kreuz 1. Klasse), 1939 version. Re-established by Hitler at the start of WWII. Awarded for repeated acts of bravery or successful military leadership. About 450,000 awarded.",
    },
    {
        "name": "Dzelzs krusts II šķira (Eisernes Kreuz 2. Klasse)",
        "year": "1939",
        "cat_no": "DE-EK-II-1939",
        "mat": "Iron, silver frame",
        "dia": "44.00", "wt": "22.00",
        "mint": "Multiple German manufacturers",
        "mintage": "approx. 4500000",
        "obs": "Black iron Maltese cross with silver border. Swastika at center, 1939 at bottom.",
        "rev": "1813 at top arm. Black/white/red ribbon for wear; cross displayed without ribbon after initial award.",
        "desc": "Iron Cross, 2nd Class (Eisernes Kreuz 2. Klasse), 1939 version. Standard award for battlefield bravery, wound, or significant action. About 4.5 million awarded — the most common German WWII combat decoration.",
    },
    {
        "name": "Dzelzs krusts I šķira (WWI, 1914)",
        "year": "1914",
        "cat_no": "DE-EK-I-1914",
        "mat": "Iron, silver frame",
        "dia": "44.00", "wt": "24.00",
        "mint": "KPM Berlin and others",
        "mintage": "approx. 218000",
        "obs": "Black iron Maltese cross with silver frame. W (Kaiser Wilhelm) crowned at top, 1914 at bottom. No swastika.",
        "rev": "Plain iron. Pin fastening.",
        "desc": "Iron Cross, 1st Class (WWI, 1914 version). Re-established by Kaiser Wilhelm II in August 1914. Worn directly on the uniform without ribbon. About 218,000 awarded during WWI.",
    },
    {
        "name": "Rytumu frontes medaļa (Ostmedaille)",
        "year": "1942",
        "cat_no": "DE-OSTMEDAILLE",
        "mat": "Bronze",
        "dia": "36.00", "wt": "15.00",
        "mint": "Multiple German manufacturers",
        "mintage": "approx. 3000000",
        "obs": "German soldier's head in steel helmet against Eastern European landscape. Snowflakes above. WINTERSCHLACHT IM OSTEN 1941/42.",
        "rev": "Sword pointing downward with oak leaves. Black/white/red/black ribbon.",
        "desc": "Eastern Front Medal (Ostmedaille / Winterschlacht im Osten). Established August 1942. Awarded for participation in the brutal 1941–42 winter campaign on the Eastern Front (Operation Barbarossa). Nicknamed 'Gefrierfleischorden' (Frozen Meat Medal). About 3 million awarded.",
    },
    {
        "name": "Kara nopelnu krusts I šķira (Kriegsverdienstkreuz 1. Klasse)",
        "year": "1939",
        "cat_no": "DE-KVK-I",
        "mat": "Bronze, enamel",
        "dia": "44.00", "wt": "18.00",
        "mint": "Multiple German manufacturers",
        "mintage": "approx. 100000",
        "obs": "Maltese cross with eagle and swastika at center, swords at arms. Bronze with black enamel center.",
        "rev": "1939 date on reverse. Pin backing.",
        "desc": "War Merit Cross, 1st Class with Swords (Kriegsverdienstkreuz 1. Klasse mit Schwertern). Established 1939. Awarded for meritorious service in the war effort that did not qualify for the Iron Cross (non-combat roles under fire).",
    },
    {
        "name": "Vācu krusts zeltā (Deutsches Kreuz in Gold)",
        "year": "1941",
        "cat_no": "DE-DKG",
        "mat": "Gilt silver, enamel",
        "dia": "63.00", "wt": "90.00",
        "mint": "Multiple manufacturers (Deschler, Steinhauer & Lück, etc.)",
        "mintage": "approx. 26000",
        "obs": "Large eight-pointed star with Iron Cross at center. Golden eagle and swastika. Worn on right breast.",
        "rev": "Hinged pin-back construction. Hollow construction common.",
        "desc": "German Cross in Gold (Deutsches Kreuz in Gold). Established September 1941 as an intermediate award between the Iron Cross 1st Class and the Knight's Cross. Awarded for repeated acts of outstanding battlefield leadership or bravery. About 26,000 awarded.",
    },
    {
        "name": "Rīta zvaigzne (Infanterie-Sturmabzeichen)",
        "year": "1939",
        "cat_no": "DE-ISA",
        "mat": "Zinc (later), silver alloy (early)",
        "dia": "59.00", "wt": "20.00",
        "mint": "W. Deumer, C. Juncker, and others",
        "mintage": "approx. 1000000",
        "obs": "Oval wreath of oak leaves. Imperial eagle at top. Infantryman with rifle charging, grenade in right hand.",
        "rev": "Hollow flat reverse. Pin fastening.",
        "desc": "Infantry Assault Badge (Infanterie-Sturmabzeichen). Established September 1939. Awarded for infantry soldiers who participated in at least 3 separate infantry assault operations. One of the most common combat decorations of the German army.",
    },
]

# ── British medals (popular among collectors) ─────────────────────────────────
UK_MEDALS = [
    {
        "name": "Victoria Cross",
        "year": "1856",
        "cat_no": "UK-VC",
        "mat": "Gunmetal (Crimean cannon bronze)",
        "dia": "36.00", "wt": "27.00",
        "mint": "Hancocks & Co., London",
        "mintage": "approx. 1358 (since 1856)",
        "obs": "Lion passant guardant on the royal crown. FOR VALOUR inscription on crimson ribbon bar.",
        "rev": "Date of act of bravery engraved on reverse of bar. Recipient's name, rank and regiment on back of cross.",
        "desc": "Victoria Cross. The highest British and Commonwealth military decoration, awarded for valour 'in the face of the enemy'. Instituted 1856 by Queen Victoria for the Crimean War. Cast from the bronze of Russian cannons captured at Sevastopol. Only 1,358 awarded since inception.",
    },
    {
        "name": "Military Medal (George V)",
        "year": "1916",
        "cat_no": "UK-MM-GV",
        "mat": "Silver",
        "dia": "36.00", "wt": "18.00",
        "mint": "Royal Mint, London",
        "mintage": "approx. 115600 (WWI)",
        "obs": "Effigy of King George V facing left. GEORGIVS V BRITT. OMN: REX ET IND: IMP.",
        "rev": "FOR BRAVERY IN THE FIELD inscription. Blue/white/red/white/blue ribbon.",
        "desc": "Military Medal. Established March 1916 for NCOs and enlisted men who displayed bravery in the field (other ranks equivalent of the Military Cross for officers). About 115,600 awarded in WWI.",
    },
    {
        "name": "1939–45 Zvaigzne (1939–45 Star)",
        "year": "1945",
        "cat_no": "UK-1939-45-STAR",
        "mat": "Brass",
        "dia": "44.00", "wt": "15.00",
        "mint": "Royal Mint, London",
        "mintage": "approx. 8000000",
        "obs": "Royal cypher GRI VI (George VI) at top. Date 1939–45. Six-pointed star shape.",
        "rev": "THE 1939-45 STAR inscription on reverse. Dark blue/red/pale blue ribbon.",
        "desc": "1939–45 Star. British campaign star awarded for operational service during WWII (minimum 180 days). One of the most common British WWII medals; awarded to over 8 million service personnel.",
    },
    {
        "name": "Krimas medaļa (Crimea Medal)",
        "year": "1854",
        "cat_no": "UK-CRIMEA",
        "mat": "Silver",
        "dia": "36.00", "wt": "22.00",
        "mint": "Royal Mint, London",
        "mintage": "approx. 210000",
        "obs": "Effigy of Queen Victoria facing left. VICTORIA REGINA.",
        "rev": "Roman warrior standing, holding shield and laurel. Clasps for individual battles (Alma, Balaklava, Inkermann, Sebastopol). Crimson/grey ribbon.",
        "desc": "Crimea Medal. Awarded for service in the Crimean War (1854–1856) against Russia. Historically significant as it prompted creation of the Victoria Cross and systematic recording of war deaths (Florence Nightingale's reforms).",
    },
]

# ── French medals (popular internationally) ───────────────────────────────────
FR_MEDALS = [
    {
        "name": "Goda leģiona ordenis (Légion d'honneur) — Chevalier",
        "year": "1802",
        "cat_no": "FR-LH-CH",
        "mat": "Silver, enamel",
        "dia": "40.00", "wt": "20.00",
        "mint": "Paris Mint (Monnaie de Paris)",
        "mintage": "approx. 3000000 (all classes, all time)",
        "obs": "Five-pointed star with white enamel. Center: portrait of Napoleon Bonaparte surrounded by a wreath. Obverse: REPUBLIQUE FRANÇAISE. Red/white enamel arms of cross.",
        "rev": "Eagle atop crossed French tricolors. HONNEUR ET PATRIE (Honour and Fatherland). Red moiré ribbon.",
        "desc": "Legion of Honour, Chevalier (Knight) grade. France's highest state award, established by Napoleon Bonaparte in 1802. Awarded for distinguished military or civil service to France. One of the world's most prestigious decorations.",
    },
    {
        "name": "Militāra medaļa (Médaille Militaire)",
        "year": "1852",
        "cat_no": "FR-MM",
        "mat": "Silver, gilt",
        "dia": "32.00", "wt": "17.00",
        "mint": "Paris Mint",
        "mintage": "approx. 460000",
        "obs": "Portrait of Napoleon III. Yellow/green ribbon.",
        "rev": "VALEUR ET DISCIPLINE (Valor and Discipline) in wreath.",
        "desc": "Military Medal (Médaille Militaire). Established 1852. France's third-highest military decoration. Awarded to non-commissioned officers and enlisted men for distinguished service. Generals and marshals also receive it after winning the Grand Cross of the Legion of Honour.",
    },
    {
        "name": "Kara krusts (Croix de Guerre) 1914–1918",
        "year": "1915",
        "cat_no": "FR-CDG-WWI",
        "mat": "Bronze",
        "dia": "37.00", "wt": "16.00",
        "mint": "Paris Mint and private manufacturers",
        "mintage": "approx. 2000000",
        "obs": "Crossed swords with branch. REPUBLIQUE FRANÇAISE above, date 1914–1918 below.",
        "rev": "Gallic rooster (coq gaulois). Green/red striped ribbon with red stars indicating level of citation.",
        "desc": "Croix de Guerre 1914–1918. French military decoration established 1915 for individual acts of bravery involving combat with the enemy during WWI. Stars on ribbon indicate level of commendation (army, corps, division, regiment citation). About 2 million awarded.",
    },
]


async def find_period(db, country_name: str, section: str, year_hint: int | None = None) -> Period | None:
    r = await db.execute(select(Country).where(Country.name.ilike(country_name)))
    country = r.scalars().first()
    if not country:
        r = await db.execute(select(Country).where(Country.name.ilike(f"%{country_name}%")))
        country = r.scalars().first()
    if not country:
        return None

    q = select(Period).where(
        Period.country_id == country.id,
        Period.section == section,
    )
    r = await db.execute(q.order_by(Period.year_start.desc()))
    periods = r.scalars().all()
    if not periods:
        return None

    if year_hint:
        for p in periods:
            ys = p.year_start or 0
            ye = p.year_end or 9999
            if ys <= year_hint <= ye:
                return p

    return periods[0]


async def medal_exists(db, period_id: int, name: str) -> bool:
    r = await db.execute(
        select(CatalogItem).where(
            CatalogItem.period_id == period_id,
            CatalogItem.name == name,
            CatalogItem.section == SectionType.medals,
        )
    )
    return r.scalars().first() is not None


async def add_medal(db, period: Period, m: dict) -> bool:
    if await medal_exists(db, period.id, m["name"]):
        return False
    item = CatalogItem(
        section=SectionType.medals,
        period_id=period.id,
        name=m["name"],
        year=m.get("year"),
        description=m.get("desc"),
        material=m.get("mat"),
        diameter_mm=m.get("dia"),
        weight_g=m.get("wt"),
        mint=m.get("mint"),
        mintage=m.get("mintage"),
        catalog_number=m.get("cat_no"),
        obverse_description=m.get("obs"),
        reverse_description=m.get("rev"),
        coin_category="medal",
    )
    db.add(item)
    return True


async def seed():
    added = 0
    skipped = 0

    async with Session() as db:

        # ── 1. Latvian First Republic medals ──────────────────────────────────
        print("\n[LV-I] Pievienoju Latvijas Pirmās Republikas medaļas (1918–1940)...")
        period_lv1 = await find_period(db, "Latvia", "medals", 1930)
        if period_lv1:
            for m in LV_FIRST_REPUBLIC_MEDALS:
                ok = await add_medal(db, period_lv1, m)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_FIRST_REPUBLIC_MEDALS)} medaļas -> periods: {period_lv1.name}")
        else:
            print("  [!] Latvia medals periods nav atrasts")

        # ── 2. Latvian Second Republic medals ─────────────────────────────────
        print("\n[LV-II] Pievienoju Latvijas Otras Republikas medaļas (1991–)...")
        period_lv2 = await find_period(db, "Latvia", "medals", 2000)
        if period_lv2:
            for m in LV_REPUBLIC_MEDALS:
                ok = await add_medal(db, period_lv2, m)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_REPUBLIC_MEDALS)} medaļas -> periods: {period_lv2.name}")
        else:
            print("  [!] Latvia 1991+ medals periods nav atrasts")

        # ── 3. Soviet / USSR medals ────────────────────────────────────────────
        print("\n[USSR] Pievienoju PSRS medaļas...")
        period_ussr = await find_period(db, "Soviet Union", "medals", 1945)
        if not period_ussr:
            period_ussr = await find_period(db, "Russia", "medals", 1945)
        if period_ussr:
            for m in USSR_MEDALS:
                ok = await add_medal(db, period_ussr, m)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(USSR_MEDALS)} medaļas -> periods: {period_ussr.name}")
        else:
            print("  [!] USSR/Russia medals periods nav atrasts")

        # ── 4. German medals ───────────────────────────────────────────────────
        print("\n[DE] Pievienoju Vācijas medaļas...")
        period_de = await find_period(db, "Germany", "medals", 1942)
        if period_de:
            for m in DE_MEDALS:
                ok = await add_medal(db, period_de, m)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(DE_MEDALS)} medaļas -> periods: {period_de.name}")
        else:
            print("  [!] Germany medals periods nav atrasts")

        # ── 5. British medals ──────────────────────────────────────────────────
        print("\n[UK] Pievienoju Lielbritānijas medaļas...")
        period_uk = await find_period(db, "United Kingdom", "medals", 1940)
        if not period_uk:
            period_uk = await find_period(db, "Great Britain", "medals", 1940)
        if period_uk:
            for m in UK_MEDALS:
                ok = await add_medal(db, period_uk, m)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(UK_MEDALS)} medaļas -> periods: {period_uk.name}")
        else:
            print("  [!] United Kingdom medals periods nav atrasts")

        # ── 6. French medals ───────────────────────────────────────────────────
        print("\n[FR] Pievienoju Francijas medaļas...")
        period_fr = await find_period(db, "France", "medals", 1940)
        if period_fr:
            for m in FR_MEDALS:
                ok = await add_medal(db, period_fr, m)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(FR_MEDALS)} medaļas -> periods: {period_fr.name}")
        else:
            print("  [!] France medals periods nav atrasts")

    print(f"\n{'='*50}")
    print(f"PABEIGTS! Pievienots: {added}, izlaists (jau eksiste): {skipped}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(seed())
