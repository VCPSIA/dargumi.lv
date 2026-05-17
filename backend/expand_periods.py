"""Papildina periodus visām galvenajām valstīm."""
import asyncio
from sqlalchemy import select, delete
from app.database import init_db, AsyncSessionLocal
from app.models.catalog import Country, Period, SectionType

# Vēsturiskie periodi pēc valsts koda
PERIODS = {
    # Baltijas valstis
    "LV": [("Russian Empire",1721,1917),("First Republic",1918,1940),("Soviet Period",1940,1991),("Second Republic",1992,2013),("EU / Euro Era",2014,None)],
    "LT": [("Grand Duchy",1251,1795),("Russian Empire",1795,1918),("First Republic",1918,1940),("Soviet Period",1940,1990),("Second Republic",1990,2013),("EU / Euro Era",2014,None)],
    "EE": [("Medieval / Swedish Rule",1219,1710),("Russian Empire",1710,1918),("First Republic",1918,1940),("Soviet Period",1940,1991),("Second Republic",1991,2013),("EU / Euro Era",2014,None)],

    # Rietumeiropa
    "DE": [("Holy Roman Empire",800,1806),("German States",1806,1871),("German Empire (Kaiserreich)",1871,1918),("Weimar Republic",1919,1933),("Third Reich",1933,1945),("West Germany (FRG)",1949,1990),("East Germany (GDR)",1949,1990),("Reunified Germany",1990,None)],
    "FR": [("Royal France",987,1792),("First Republic",1792,1804),("Napoleonic Era",1804,1815),("Restoration & July Monarchy",1815,1848),("Second Republic & Empire",1848,1870),("Third Republic",1870,1940),("WWII / Vichy",1940,1944),("Fourth Republic",1944,1958),("Fifth Republic",1958,None)],
    "GB": [("Medieval England",1066,1603),("Stuart & Commonwealth",1603,1714),("Georgian Era",1714,1830),("Victorian Era",1837,1901),("Edwardian & WWI",1901,1918),("Interwar & WWII",1918,1952),("Elizabeth II",1952,2022),("Charles III",2022,None)],
    "AT": [("Habsburg Empire",1282,1804),("Austrian Empire",1804,1867),("Austro-Hungarian Empire",1867,1918),("First Republic",1918,1938),("WWII / Anschluss",1938,1945),("Second Republic",1945,None)],
    "CH": [("Old Swiss Confederacy",1291,1798),("Helvetic Republic",1798,1803),("Mediation & Restoration",1803,1848),("Swiss Confederation",1848,None)],
    "IT": [("Italian States",700,1861),("Kingdom of Italy",1861,1946),("Italian Republic",1946,None)],
    "ES": [("Medieval Kingdoms",718,1479),("Habsburg Spain",1479,1700),("Bourbon Spain",1700,1808),("Napoleonic & Restoration",1808,1868),("First Republic & Restoration",1868,1931),("Second Republic & Civil War",1931,1939),("Franco Era",1939,1975),("Constitutional Monarchy",1975,None)],
    "NL": [("Dutch Republic",1581,1795),("Batavian Republic",1795,1806),("Kingdom of Holland / Napoleon",1806,1815),("Kingdom of Netherlands",1815,None)],
    "BE": [("Austrian Netherlands",1713,1795),("French Period",1795,1815),("Kingdom of Belgium",1830,None)],
    "SE": [("Medieval Sweden",970,1523),("Vasa Dynasty",1523,1654),("Swedish Empire",1654,1718),("Age of Liberty & Gustavian",1718,1809),("Modern Sweden",1809,None)],
    "NO": [("Medieval Norway",872,1536),("Danish Rule",1536,1814),("Union with Sweden",1814,1905),("Independent Norway",1905,None)],
    "DK": [("Medieval Denmark",958,1534),("Reformation Era",1534,1660),("Absolute Monarchy",1660,1849),("Constitutional Monarchy",1849,None)],
    "PL": [("Piast & Jagiellonian",966,1569),("Polish-Lithuanian Commonwealth",1569,1795),("Partitions Era",1795,1918),("Second Republic",1918,1939),("WWII & PPR",1939,1952),("PRL (Communist)",1952,1989),("Third Republic",1989,None)],
    "CZ": [("Bohemian Kingdom",870,1526),("Habsburg Bohemia",1526,1918),("Czechoslovakia",1918,1939),("WWII Protectorate",1939,1945),("Czechoslovak Republic",1945,1993),("Czech Republic",1993,None)],
    "HU": [("Kingdom of Hungary",1000,1526),("Ottoman & Habsburg Era",1526,1867),("Austria-Hungary",1867,1918),("Interwar Hungary",1918,1944),("People's Republic",1944,1989),("Modern Hungary",1989,None)],
    "RO": [("Danubian Principalities",1330,1859),("United Principalities",1859,1881),("Kingdom of Romania",1881,1947),("Communist Romania",1947,1989),("Modern Romania",1989,None)],
    "RU": [("Kievan Rus / Principalities",862,1547),("Tsardom of Russia",1547,1721),("Russian Empire",1721,1917),("RSFSR / Soviet Union",1917,1991),("Russian Federation",1991,None)],
    "UA": [("Kievan Rus",862,1240),("Cossack Hetmanate",1648,1764),("Russian Empire",1764,1917),("Ukrainian State",1917,1922),("Soviet Ukraine",1922,1991),("Independent Ukraine",1991,None)],
    "GR": [("Ancient Greece",600,146),("Roman & Byzantine",146,1453),("Ottoman Greece",1453,1821),("Kingdom of Greece",1821,1924),("Second Republic & Axis",1924,1944),("Post-WWII Greece",1944,1974),("Modern Greece",1974,None)],
    "TR": [("Byzantine Empire",330,1453),("Ottoman Empire",1299,1923),("Republic of Turkey",1923,None)],
    "PT": [("County of Portugal",868,1139),("Kingdom of Portugal",1139,1910),("First Republic",1910,1926),("Estado Novo",1926,1974),("Modern Portugal",1974,None)],
    "FI": [("Swedish Rule",1249,1809),("Russian Grand Duchy",1809,1917),("Republic of Finland",1917,None)],
    "IE": [("Medieval Ireland",795,1171),("English / British Rule",1171,1922),("Irish Free State / Republic",1922,None)],
    "SK": [("Great Moravia / Hungary",833,1918),("Czechoslovakia",1918,1939),("Slovak State (WWII)",1939,1945),("Czechoslovakia",1945,1993),("Slovak Republic",1993,None)],
    "HR": [("Medieval Croatia",925,1102),("Habsburg Croatia",1102,1918),("Kingdom of Yugoslavia",1918,1941),("WWII NDH",1941,1945),("SFR Yugoslavia",1945,1991),("Republic of Croatia",1991,None)],
    "RS": [("Medieval Serbia",768,1389),("Ottoman Serbia",1389,1815),("Principality / Kingdom",1815,1918),("Yugoslavia",1918,1941),("WWII Serbia",1941,1945),("SFR Yugoslavia",1945,1992),("Modern Serbia",1992,None)],
    "BG": [("First Bulgarian Empire",681,1018),("Second Bulgarian Empire",1185,1396),("Ottoman Bulgaria",1396,1878),("Principality / Kingdom",1878,1946),("People's Republic",1946,1990),("Modern Bulgaria",1990,None)],

    # Āzija
    "CN": [("Ancient China",221,907),("Song / Yuan Dynasty",960,1368),("Ming Dynasty",1368,1644),("Qing Dynasty",1644,1912),("Republic of China",1912,1949),("People's Republic",1949,None)],
    "JP": [("Nara / Heian",700,1185),("Feudal Japan",1185,1603),("Edo Period (Tokugawa)",1603,1868),("Meiji Era",1868,1912),("Taisho Era",1912,1926),("Showa Era",1926,1989),("Heisei / Reiwa",1989,None)],
    "IN": [("Maurya / Gupta Empire",321,550),("Medieval Sultanates",712,1526),("Mughal Empire",1526,1857),("British India",1857,1947),("Republic of India",1947,None)],
    "IR": [("Safavid Persia",1501,1736),("Afsharid / Zand",1736,1796),("Qajar Dynasty",1796,1925),("Pahlavi Dynasty",1925,1979),("Islamic Republic",1979,None)],
    "IL": [("Ancient Judea",586,640),("Ottoman Palestine",1517,1920),("British Mandate",1920,1948),("State of Israel",1948,None)],
    "SA": [("Early Islamic Period",622,1744),("First Saudi State",1744,1818),("Second Saudi State",1824,1891),("Kingdom of Saudi Arabia",1932,None)],
    "KR": [("Three Kingdoms / Goryeo",57,1392),("Joseon Dynasty",1392,1897),("Korean Empire",1897,1910),("Japanese Rule",1910,1945),("Republic of Korea",1945,None)],
    "KP": [("Joseon / Japanese Rule",1392,1945),("DPRK",1948,None)],
    "TH": [("Sukhothai / Ayutthaya",1238,1767),("Thonburi & Rattanakosin",1767,1932),("Constitutional Monarchy",1932,None)],
    "VN": [("Imperial Vietnam",939,1858),("French Indochina",1858,1945),("Republic & DRV",1945,1975),("Socialist Republic",1975,None)],

    # Amerikas
    "US": [("Colonial Era",1607,1776),("Early Federal",1776,1836),("Antebellum & Civil War",1836,1865),("Reconstruction & Gilded Age",1865,1900),("Progressive Era",1900,1933),("New Deal & WWII",1933,1945),("Postwar & Cold War",1945,1971),("Modern United States",1971,None)],
    "MX": [("Colonial New Spain",1535,1821),("First Empire",1821,1824),("Early Republic",1824,1864),("Second Empire",1864,1867),("Restored Republic / Porfiriato",1867,1910),("Revolutionary Mexico",1910,1929),("Modern Mexico",1929,None)],
    "BR": [("Colonial Brazil",1500,1822),("Empire of Brazil",1822,1889),("Old Republic",1889,1930),("Vargas Era",1930,1945),("Modern Brazil",1945,None)],
    "AR": [("Colonial Argentina",1536,1816),("Early Republic",1816,1862),("Argentine Republic",1862,1943),("Perón & Military Era",1943,1983),("Modern Argentina",1983,None)],
    "CA": [("Colonial Era",1534,1867),("Dominion of Canada",1867,1952),("Modern Canada",1952,None)],
    "CU": [("Spanish Cuba",1511,1898),("Republic of Cuba",1898,1959),("Socialist Cuba",1959,None)],
    "PE": [("Inca & Colonial",1438,1821),("Republic of Peru",1821,None)],
    "CL": [("Colonial Chile",1541,1818),("Republic of Chile",1818,None)],

    # Āfrika
    "ZA": [("Colonial Era",1652,1910),("Union of South Africa",1910,1961),("Republic of South Africa",1961,None)],
    "EG": [("Pharaonic Egypt",3100,332),("Ptolemaic Egypt",332,30),("Roman / Byzantine Egypt",30,642),("Islamic Egypt",642,1798),("Muhammad Ali Dynasty",1805,1952),("Republic of Egypt",1952,None)],
    "MA": [("Idrisid / Medieval",788,1554),("Saadian & Alaouite",1554,1912),("French Protectorate",1912,1956),("Kingdom of Morocco",1956,None)],
    "NG": [("Pre-colonial",1000,1851),("British Nigeria",1851,1960),("Republic of Nigeria",1960,None)],
    "GH": [("Gold Coast (British)",1821,1957),("Republic of Ghana",1957,None)],
    "KE": [("British East Africa",1895,1963),("Republic of Kenya",1963,None)],
    "ET": [("Aksumite Empire",100,940),("Medieval Ethiopia",940,1855),("Ethiopian Empire",1855,1974),("Derg & EPRDF",1974,None)],

    # Okeānija
    "AU": [("Colonial Era",1788,1901),("Commonwealth of Australia",1901,1966),("Decimal Era",1966,None)],
    "NZ": [("Colonial Era",1840,1907),("Dominion / Realm",1907,1967),("Decimal Era",1967,None)],

    # Senās / Pasaule
    "ROM": [("Roman Republic",509,27),("Roman Empire",27,476),("Late Roman Empire",284,476)],
    "GRC": [("Archaic Greece",700,480),("Classical Greece",480,323),("Hellenistic Period",323,31)],
    "BYZ": [("Early Byzantine",330,641),("Middle Byzantine",641,1204),("Late Byzantine",1204,1453)],
    "OTT": [("Early Ottoman",1299,1566),("Classical Ottoman",1566,1703),("Decline & Tanzimat",1703,1839),("Late Ottoman",1839,1923)],
}

DEFAULT = [
    ("Ancient / Medieval", None, 1800),
    ("19th Century", 1800, 1900),
    ("Early 20th Century", 1900, 1950),
    ("Late 20th Century", 1950, 2000),
    ("Modern", 2000, None),
]

async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Country))
        countries = result.scalars().all()

        updated = 0
        for country in countries:
            periods_data = PERIODS.get(country.code, DEFAULT)

            # Dzēšam vecos periodus
            await db.execute(delete(Period).where(Period.country_id == country.id))

            for name, y_start, y_end in periods_data:
                for section in [SectionType.coins, SectionType.medals, SectionType.stamps]:
                    db.add(Period(
                        name=name,
                        year_start=y_start,
                        year_end=y_end,
                        country_id=country.id,
                        section=section,
                    ))
            updated += 1

        await db.commit()
        print(f"Atjaunoti periodi {updated} valstīm")
        print(f"Valstis ar specifiskiem periodiem: {len(PERIODS)}")
        print(f"Valstis ar noklusējuma periodiem: {updated - len([c for c in countries if c.code in PERIODS])}")

asyncio.run(main())
