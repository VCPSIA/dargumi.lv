"""Pievieno izmirušās valstis katalogu."""
import asyncio
from sqlalchemy import select, delete
from app.database import init_db, AsyncSessionLocal
from app.models.catalog import Continent, Country, Period, SectionType

# Izmirušās valstis ar to periodiem
# Formāts: (angļu_nosaukums, latviešu_nosaukums, kods, [(perioda_nosaukums, gads_no, gads_līdz)])
EXTINCT = [

    # ── Eiropa ────────────────────────────────────────────────────
    ("Soviet Union (USSR)", "Padomju Savienība (PSRS)", "USSR", [
        ("Russian SFSR Transition", 1917, 1922),
        ("Early Soviet Union", 1922, 1941),
        ("WWII Soviet Union", 1941, 1945),
        ("Post-war USSR", 1945, 1961),
        ("Late Soviet Union", 1961, 1991),
    ]),
    ("Yugoslavia", "Dienvidslāvija", "YUG", [
        ("Kingdom of Yugoslavia", 1918, 1941),
        ("WWII Yugoslavia", 1941, 1945),
        ("SFR Yugoslavia", 1945, 1991),
        ("FRY (Serbia & Montenegro)", 1992, 2006),
    ]),
    ("Czechoslovakia", "Čehoslovākija", "CSK", [
        ("First Republic", 1918, 1939),
        ("WWII Protectorate", 1939, 1945),
        ("Third Republic", 1945, 1948),
        ("Czechoslovak SSR", 1948, 1993),
    ]),
    ("East Germany (GDR)", "Austrumvācija (VDR)", "DDR", [
        ("German Democratic Republic", 1949, 1990),
    ]),
    ("Prussia", "Prūsija", "PRU", [
        ("Duchy of Prussia", 1525, 1618),
        ("Brandenburg-Prussia", 1618, 1701),
        ("Kingdom of Prussia", 1701, 1871),
        ("Province of Prussia", 1871, 1947),
    ]),
    ("Holy Roman Empire", "Svētā Romas impērija", "HRE", [
        ("Early HRE", 962, 1250),
        ("Late Medieval HRE", 1250, 1500),
        ("Early Modern HRE", 1500, 1648),
        ("Late HRE", 1648, 1806),
    ]),
    ("Austro-Hungarian Empire", "Austrijas-Ungārijas impērija", "AHE", [
        ("Austro-Hungarian Empire", 1867, 1918),
    ]),
    ("Ottoman Empire (Europe)", "Osmaņu impērija (Eiropa)", "OTE", [
        ("Ottoman Expansion in Europe", 1354, 1566),
        ("Ottoman Rule in Europe", 1566, 1800),
        ("Ottoman Decline in Europe", 1800, 1923),
    ]),
    ("Polish-Lithuanian Commonwealth", "Polijas-Lietuvas savienība", "PLC", [
        ("Union of Lublin", 1569, 1648),
        ("Deluge & Recovery", 1648, 1717),
        ("Decline & Partitions", 1717, 1795),
    ]),
    ("Republic of Venice", "Venēcijas republika", "VEN", [
        ("Early Venice", 697, 1204),
        ("Maritime Republic", 1204, 1453),
        ("Late Republic", 1453, 1797),
    ]),
    ("Papal States", "Pāvesta valsts", "PAP", [
        ("Medieval Papal States", 756, 1417),
        ("Renaissance Papal States", 1417, 1648),
        ("Late Papal States", 1648, 1870),
    ]),
    ("Kingdom of the Two Sicilies", "Divu Sicīliju karaliste", "TAS", [
        ("Kingdom of Naples & Sicily", 1130, 1816),
        ("Kingdom of the Two Sicilies", 1816, 1861),
    ]),
    ("Kingdom of Sardinia", "Sardīnijas karaliste", "SAR", [
        ("Kingdom of Sardinia", 1720, 1861),
    ]),
    ("Kingdom of Bavaria", "Bavārijas karaliste", "BAV", [
        ("Duchy / Electorate of Bavaria", 1180, 1806),
        ("Kingdom of Bavaria", 1806, 1918),
    ]),
    ("Kingdom of Württemberg", "Virtembergas karaliste", "WTB", [
        ("Duchy of Württemberg", 1495, 1806),
        ("Kingdom of Württemberg", 1806, 1918),
    ]),
    ("Kingdom of Saxony", "Saksijas karaliste", "SAX", [
        ("Electorate of Saxony", 1356, 1806),
        ("Kingdom of Saxony", 1806, 1918),
    ]),
    ("Grand Duchy of Lithuania", "Lietuvas lielkņaziste", "GDL", [
        ("Early Grand Duchy", 1251, 1385),
        ("Jagiellonian Period", 1385, 1569),
        ("Commonwealth Period", 1569, 1795),
    ]),
    ("Republic of Novgorod", "Novgorodas republika", "NOV", [
        ("Novgorod Republic", 1136, 1478),
    ]),
    ("Duchy of Courland and Semigallia", "Kurzemes un Zemgales hercogiste", "CRL", [
        ("Duchy of Courland", 1562, 1795),
    ]),
    ("Livonian Order", "Livonijas ordenis", "LVO", [
        ("Livonian Confederation", 1228, 1562),
    ]),
    ("Kingdom of Bohemia", "Bohēmijas karaliste", "BOH", [
        ("Přemyslid Bohemia", 870, 1306),
        ("Luxembourg Bohemia", 1310, 1437),
        ("Habsburg Bohemia", 1526, 1804),
    ]),
    ("Duchy of Warsaw", "Varšavas hercogiste", "WAR", [
        ("Duchy of Warsaw", 1807, 1815),
    ]),
    ("Weimar Republic", "Veimāras republika", "WRG", [
        ("Weimar Republic", 1919, 1933),
    ]),
    ("Third Reich (Nazi Germany)", "Trešais Reihs", "TRI", [
        ("Third Reich", 1933, 1945),
    ]),
    ("French First Empire", "Francijas Pirmā impērija", "FRE", [
        ("Napoleonic Empire", 1804, 1815),
    ]),
    ("Kingdom of Greece (Royal)", "Grieķijas karaliste", "GRK", [
        ("Kingdom of Greece", 1832, 1974),
    ]),
    ("Kingdom of Yugoslavia", "Dienvidslāvijas karaliste", "KYG", [
        ("Kingdom of Serbs, Croats and Slovenes", 1918, 1929),
        ("Kingdom of Yugoslavia", 1929, 1941),
    ]),
    ("Republic of Ragusa (Dubrovnik)", "Dubrovnikas republika", "RAG", [
        ("Republic of Ragusa", 1358, 1808),
    ]),
    ("Principality of Transylvania", "Transilvānijas firstiste", "TRN", [
        ("Principality of Transylvania", 1570, 1711),
    ]),
    ("Montenegro (Kingdom)", "Melnkalnes karaliste", "MNK", [
        ("Principality of Montenegro", 1852, 1910),
        ("Kingdom of Montenegro", 1910, 1918),
    ]),

    # ── Āzija ─────────────────────────────────────────────────────
    ("Mughal Empire", "Mogolu impērija", "MGL", [
        ("Early Mughal", 1526, 1605),
        ("Classical Mughal", 1605, 1707),
        ("Declining Mughal", 1707, 1857),
    ]),
    ("British India", "Britu Indija", "BRI", [
        ("East India Company", 1757, 1858),
        ("British Raj", 1858, 1947),
    ]),
    ("Qing Dynasty (Imperial China)", "Cjinu dinastija", "QNG", [
        ("Early Qing", 1644, 1735),
        ("High Qing", 1735, 1839),
        ("Late Qing", 1839, 1912),
    ]),
    ("Republic of China (mainland)", "Ķīnas republika (kontinentālā)", "ROC", [
        ("Beiyang Government", 1912, 1928),
        ("Nationalist China", 1928, 1949),
    ]),
    ("Manchukuo", "Mandžūkuo", "MAN", [
        ("State / Empire of Manchukuo", 1932, 1945),
    ]),
    ("Korean Empire", "Korejas impērija", "KEM", [
        ("Korean Empire", 1897, 1910),
    ]),
    ("Japanese Korea (Joseon)", "Japānas Koreja", "JKO", [
        ("Japanese Rule in Korea", 1910, 1945),
    ]),
    ("French Indochina", "Franču Indoķīna", "FIC", [
        ("French Indochina", 1887, 1954),
    ]),
    ("Netherlands East Indies", "Nīderlandes Austrumindija", "NEI", [
        ("VOC Period", 1602, 1800),
        ("Dutch East Indies", 1800, 1949),
    ]),
    ("Ottoman Empire (Asia)", "Osmaņu impērija (Āzija)", "OTA", [
        ("Early Ottoman", 1299, 1453),
        ("Classical Ottoman", 1453, 1700),
        ("Decline & Tanzimat", 1700, 1839),
        ("Late Ottoman", 1839, 1923),
    ]),
    ("Safavid Persia", "Safavīdu Persija", "SAF", [
        ("Safavid Dynasty", 1501, 1736),
    ]),
    ("Qajar Persia", "Kadžāru Persija", "QAJ", [
        ("Qajar Dynasty", 1789, 1925),
    ]),
    ("Afsharid / Zand Persia", "Afsharīdu / Zandu Persija", "AFZ", [
        ("Afsharid & Zand Dynasties", 1736, 1796),
    ]),
    ("Ryukyu Kingdom", "Rjūkjū karaliste", "RYU", [
        ("Ryukyu Kingdom", 1429, 1879),
    ]),
    ("Tibet (Independent)", "Neatkarīgā Tibeta", "TIB", [
        ("Tibetan Empire", 618, 842),
        ("Ganden Phodrang", 1642, 1951),
    ]),
    ("Kingdom of Iraq (Hashemite)", "Irākas karaliste (Hašimītu)", "IRK", [
        ("Hashemite Kingdom of Iraq", 1921, 1958),
    ]),
    ("Trucial States", "Pamiervalstis", "TRU", [
        ("Trucial States", 1820, 1971),
    ]),
    ("Muscat and Oman", "Maskata un Omāna", "MSO", [
        ("Sultanate of Muscat and Oman", 1749, 1970),
    ]),

    # ── Āfrika ────────────────────────────────────────────────────
    ("Rhodesia / Zimbabwe Rhodesia", "Rodēzija", "RHO", [
        ("Southern Rhodesia", 1923, 1965),
        ("Rhodesia (UDI)", 1965, 1979),
        ("Zimbabwe Rhodesia", 1979, 1980),
    ]),
    ("German East Africa", "Vācijas Austrumāfrika", "GEA", [
        ("German East Africa", 1885, 1919),
    ]),
    ("German Southwest Africa", "Vācijas Dienvidrietumāfrika", "GSA", [
        ("German Southwest Africa", 1884, 1915),
    ]),
    ("Belgian Congo", "Beļģijas Kongo", "BCG", [
        ("Congo Free State", 1885, 1908),
        ("Belgian Congo", 1908, 1960),
    ]),
    ("Biafra", "Bjafra", "BIA", [
        ("Republic of Biafra", 1967, 1970),
    ]),
    ("United Arab Republic", "Arābu Apvienotā republika", "UAR", [
        ("United Arab Republic", 1958, 1971),
    ]),
    ("Kingdom of Libya", "Lībijas karaliste", "LBK", [
        ("Kingdom of Libya", 1951, 1969),
    ]),
    ("Empire of Ethiopia", "Etiopijas impērija", "ETH", [
        ("Solomonid Empire", 1270, 1936),
        ("Restored Empire", 1941, 1974),
    ]),
    ("French West Africa", "Franču Rietumāfrika", "FWA", [
        ("French West Africa", 1895, 1960),
    ]),
    ("British West Africa", "Britu Rietumāfrika", "BWA", [
        ("British West Africa", 1821, 1957),
    ]),

    # ── Amerikas ─────────────────────────────────────────────────
    ("Confederate States of America", "Konfederācija (CSA)", "CSA", [
        ("Confederate States of America", 1861, 1865),
    ]),
    ("Republic of Texas", "Teksasas republika", "TEX", [
        ("Republic of Texas", 1836, 1846),
    ]),
    ("Gran Colombia", "Lielkolumbija", "GRC2", [
        ("Gran Colombia", 1819, 1831),
    ]),
    ("Empire of Brazil", "Brazīlijas impērija", "BRE", [
        ("Empire of Brazil", 1822, 1889),
    ]),
    ("First Mexican Empire", "Meksikas pirmā impērija", "MXE", [
        ("First Mexican Empire", 1821, 1824),
        ("Second Mexican Empire", 1864, 1867),
    ]),
    ("United Provinces of Central America", "Centrālamerikas savienotās provinces", "UPC", [
        ("United Provinces of Central America", 1823, 1841),
    ]),
    ("New Granada (Colombia)", "Jaunā Granada", "NGR", [
        ("Viceroyalty / New Granada", 1717, 1831),
        ("Republic of New Granada", 1831, 1858),
        ("Granadine Confederation", 1858, 1863),
        ("United States of Colombia", 1863, 1886),
    ]),

    # ── Senie ─────────────────────────────────────────────────────
    ("Ancient Egypt", "Senā Ēģipte", "AEG", [
        ("Old Kingdom", 2686, 2181),
        ("Middle Kingdom", 2055, 1650),
        ("New Kingdom", 1550, 1070),
        ("Late Period & Ptolemaic", 664, 30),
    ]),
    ("Carthage", "Kartāga", "CAR", [
        ("Carthaginian Republic", 814, 146),
    ]),
    ("Persian Achaemenid Empire", "Ahemenīdu Persija", "ACH", [
        ("Achaemenid Empire", 550, 330),
    ]),
    ("Macedonian / Seleucid Empire", "Maķedonijas / Seleikīdu impērija", "MAC", [
        ("Macedonian Empire (Alexander)", 336, 323),
        ("Successor Kingdoms (Diadochi)", 323, 63),
    ]),
    ("Kingdom of Bosporus", "Bosporas karaliste", "BOS", [
        ("Kingdom of Bosporus", 438, 370),
    ]),
    ("Parthian Empire", "Parfijas impērija", "PAR", [
        ("Parthian Empire", 247, 224),
    ]),
    ("Sassanid Empire", "Sasānīdu impērija", "SAS", [
        ("Sassanid / Neo-Persian Empire", 224, 651),
    ]),
    ("Umayyad Caliphate", "Omajadu kalifāts", "UMA", [
        ("Umayyad Caliphate", 661, 750),
    ]),
    ("Abbasid Caliphate", "Abasīdu kalifāts", "ABB", [
        ("Abbasid Caliphate", 750, 1258),
    ]),
    ("Mongol Empire", "Mongoļu impērija", "MON", [
        ("Mongol Empire", 1206, 1294),
        ("Successor Khanates", 1294, 1500),
    ]),
    ("Byzantine Empire", "Bizantijas impērija", "BYZ2", [
        ("Early Byzantine", 330, 641),
        ("Middle Byzantine", 641, 1204),
        ("Late Byzantine", 1204, 1453),
    ]),
    ("Ancient Rome", "Senā Roma", "ROM2", [
        ("Roman Republic", 509, 27),
        ("Early Roman Empire", 27, 180),
        ("Crisis of the 3rd Century", 180, 284),
        ("Late Roman Empire", 284, 476),
        ("Eastern Roman (Byzantine)", 476, 1453),
    ]),
    ("Ancient Greece", "Senā Grieķija", "GR2", [
        ("Archaic Period", 800, 480),
        ("Classical Period", 480, 323),
        ("Hellenistic Period", 323, 31),
    ]),
    ("Celtic Tribes", "Ķeltu ciltis", "CEL2", [
        ("Celtic Iron Age", 800, 50),
        ("Gallo-Roman transition", 50, 400),
    ]),
]

async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Atrodam vai izveido "Izmirušās valstis" kontinentu
        result = await db.execute(
            select(Continent).where(Continent.code == "EX")
        )
        cont = result.scalar_one_or_none()
        if not cont:
            cont = Continent(name="Extinct Countries", name_lv="Izmirušās valstis", code="EX")
            db.add(cont)
            await db.flush()
            print(f"Izveidots kontinents: Izmirušās valstis")
        else:
            print(f"Kontinents jau eksistē: {cont.name_lv}")

        added_countries = 0
        added_periods = 0

        for name, name_lv, code, periods in EXTINCT:
            # Pārbauda vai valsts jau eksistē
            result = await db.execute(
                select(Country).where(Country.code == code)
            )
            country = result.scalar_one_or_none()
            if not country:
                country = Country(name=name, name_lv=name_lv, code=code, continent_id=cont.id)
                db.add(country)
                await db.flush()
                added_countries += 1

            # Dzēš vecos periodus un pievieno jaunus
            await db.execute(delete(Period).where(Period.country_id == country.id))
            for pname, ystart, yend in periods:
                for section in [SectionType.coins, SectionType.medals, SectionType.stamps]:
                    db.add(Period(
                        name=pname,
                        year_start=ystart,
                        year_end=yend,
                        country_id=country.id,
                        section=section,
                    ))
                    added_periods += 1

        await db.commit()
        print(f"Pievienotas {added_countries} izmirušās valstis")
        print(f"Pievienoti {added_periods} periodi")

asyncio.run(main())
