"""
Pievieno vēsturiskos periodus visām valstīm, kurām trūkst periodu.
Palaiž: cd backend; venv\Scripts\python.exe seed_periods.py
"""
import asyncio
from sqlalchemy import text
from app.database import engine

SECTIONS = ["coins", "medals", "stamps", "banknotes"]

# (period_name, year_start, year_end)
PERIODS = {
    # ── Vesturiskas valstis ──────────────────────────────────────────
    "BZ": [("Bizantijas imperija", 330, 1453)],
    "RM": [("Romas imperija", -27, 476)],
    "AH": [("Austro-Ungarija", 1867, 1918)],
    "OT": [("Osmanu imperija", 1299, 1922)],
    "PU": [("Prusija", 1525, 1871)],
    "CS": [("Cehoslovakija", 1918, 1993)],
    "DD": [("Austrumvacija (VDR)", 1949, 1990)],
    "SU": [("Padomju Savieniba (PSRS)", 1917, 1991)],
    "YU": [("Dienvidslvija", 1918, 1992)],

    # ── Eiropa ──────────────────────────────────────────────────────
    "AL": [
        ("Albanija (Osmanu / Neatkariga)", 1912, 1944),
        ("Albanija (komunistiska)", 1944, 1992),
        ("Albanijas Republika", 1992, None),
    ],
    "AD": [("Andoras Firstiste", 1278, None)],
    "BA": [
        ("Bosnija (Osmanu / A-U)", 1878, 1918),
        ("Dienvidslvija (Bosnija)", 1918, 1992),
        ("Bosnija un Hercegovina", 1992, None),
    ],
    "BG": [
        ("Bulgarijas Firstiste / Karaliste", 1878, 1946),
        ("Bulgarijas Tautas Republika", 1946, 1990),
        ("Bulgarijas Republika", 1990, None),
    ],
    "HR": [
        ("Horvtija (A-U / Dienvidslvija)", 1918, 1991),
        ("Horvtijas Republika", 1991, None),
    ],
    "CY": [
        ("Kipra (Britu kolonila)", 1878, 1960),
        ("Kipras Republika", 1960, None),
    ],
    "GI": [("Gibraltars (Britu teritorija)", 1713, None)],
    "IS": [
        ("Islande (Danijas dala)", 1918, 1944),
        ("Islandes Republika", 1944, None),
    ],
    "IE": [
        ("Irijas Brivvalsts", 1922, 1937),
        ("Irijas Republika", 1937, None),
    ],
    "IM": [("Menas sala (Britu kronkolonija)", 1765, None)],
    "XK": [
        ("Kosovo (Dienvidslvija / Serbija)", 1945, 2008),
        ("Kosovas Republika", 2008, None),
    ],
    "LI": [("Lihtensteinas Firstiste", 1806, None)],
    "MT": [
        ("Malta (Britu kolonila)", 1800, 1964),
        ("Maltas Republika", 1964, None),
    ],
    "MD": [
        ("Moldovas PSR / PSRS", 1940, 1991),
        ("Moldovas Republika", 1991, None),
    ],
    "MC": [("Monakas Firstiste", 1297, None)],
    "ME": [
        ("Melnkalne (karaliste / Dienvidslvija)", 1878, 2006),
        ("Melnkalnes Republika", 2006, None),
    ],
    "MK": [
        ("Makedonija (Dienvidslvija)", 1945, 1991),
        ("Ziemelmakedoniijas Republika", 1991, None),
    ],
    "PT": [
        ("Portugale (karaliste)", 1385, 1910),
        ("Portugales Republika (I)", 1910, 1926),
        ("Portugale (Estado Novo)", 1926, 1974),
        ("Portugales Republika (III)", 1974, None),
    ],
    "RO": [
        ("Rumanijas Karaliste", 1881, 1947),
        ("Rumanijas Socialistiska Republika", 1947, 1989),
        ("Rumanijas Republika", 1989, None),
    ],
    "SM": [
        ("Sanmarino Republika (klasiska)", 1864, 1940),
        ("Sanmarino Republika (musdienu)", 1940, None),
    ],
    "RS": [
        ("Serbija (karaliste / Dienvidslvija)", 1878, 2006),
        ("Serbijas Republika", 2006, None),
    ],
    "SI": [
        ("Slovenija (Dienvidslvija)", 1918, 1991),
        ("Slovenijas Republika", 1991, None),
    ],
    "VA": [
        ("Pavesta valsts", 756, 1870),
        ("Vatikans (Vatikana pilsetvasts)", 1929, None),
    ],

    # ── Azija ────────────────────────────────────────────────────────
    "AF": [
        ("Afganistana (emirats / karaliste)", 1823, 1973),
        ("Afganistana (republika)", 1973, 2021),
        ("Afganistana (talibani)", 2021, None),
    ],
    "AM": [
        ("Armenijas PSR / PSRS", 1920, 1991),
        ("Armenijas Republika", 1991, None),
    ],
    "AZ": [
        ("Azerbaidzanas PSR / PSRS", 1920, 1991),
        ("Azerbaidzanas Republika", 1991, None),
    ],
    "BH": [
        ("Bahreina (Britu protektorats)", 1820, 1971),
        ("Bahreinas Emirates / Karaliste", 1971, None),
    ],
    "BD": [
        ("Bangladesa (Britu Indija / Pakistani)", 1947, 1971),
        ("Bangladesas Republika", 1971, None),
    ],
    "BT": [("Butanas Karaliste", 1907, None)],
    "BN": [
        ("Bruneja (Britu protektorats)", 1888, 1984),
        ("Brunejas Sultanats", 1984, None),
    ],
    "KH": [
        ("Kambodza (Francu protektorats)", 1863, 1953),
        ("Kambodzas Karaliste (I)", 1953, 1975),
        ("Kambodza (Republika / Khmer Rouge)", 1975, 1993),
        ("Kambodzas Karaliste (II)", 1993, None),
    ],
    "CN": [
        ("Kinas imperija (Cinu / Minu / Cingu)", 1368, 1912),
        ("Kinas Republika", 1912, 1949),
        ("Kinas Tautas Republika", 1949, None),
    ],
    "GE": [
        ("Gruzijas PSR / PSRS", 1921, 1991),
        ("Gruzijas Republika", 1991, None),
    ],
    "IN": [
        ("Britu Indija", 1858, 1947),
        ("Indijas Republika", 1947, None),
    ],
    "ID": [
        ("Niederlandes Indija (kolonila)", 1800, 1945),
        ("Indonezijas Republika", 1945, None),
    ],
    "IR": [
        ("Irana (Kadzaru dinastija)", 1796, 1925),
        ("Irana (Pahlavi dinastija)", 1925, 1979),
        ("Iranas Islama Republika", 1979, None),
    ],
    "IQ": [
        ("Iraka (Britu mandats / Karaliste)", 1920, 1958),
        ("Irakas Republika", 1958, None),
    ],
    "IL": [("Izraela (Valsts)", 1948, None)],
    "JP": [
        ("Japana (Meiji / Taisho / Showa I)", 1868, 1945),
        ("Japana (musdienu)", 1945, None),
    ],
    "JO": [
        ("Jordanija (Britu mandats)", 1921, 1946),
        ("Jordanijas Hasimitu Karaliste", 1946, None),
    ],
    "KZ": [
        ("Kazahstanas PSR / PSRS", 1936, 1991),
        ("Kazahstanas Republika", 1991, None),
    ],
    "KP": [("Ziemelkoreja (KTDR)", 1948, None)],
    "KR": [("Dienvidkoreja (Republika)", 1948, None)],
    "KW": [
        ("Kuveita (Britu protektorats)", 1899, 1961),
        ("Kuveitas Emirates", 1961, None),
    ],
    "KG": [
        ("Kirgizstanas PSR / PSRS", 1936, 1991),
        ("Kirgizstanas Republika", 1991, None),
    ],
    "LA": [
        ("Laosa (Francu protektorats)", 1893, 1953),
        ("Laosas Karaliste", 1953, 1975),
        ("Laosas PDR", 1975, None),
    ],
    "LB": [
        ("Libana (Francu mandats)", 1920, 1943),
        ("Libanas Republika", 1943, None),
    ],
    "MY": [
        ("Malaizija (Britu kolonila)", 1874, 1957),
        ("Malaizijas Federacija", 1957, None),
    ],
    "MV": [
        ("Maldivi (Sultanats / Britu protektorats)", 1887, 1965),
        ("Maldivu Republika", 1965, None),
    ],
    "MN": [
        ("Mongolija (Tautas Republika)", 1924, 1992),
        ("Mongolija (demokratiska)", 1992, None),
    ],
    "MM": [
        ("Birma (Britu kolonila)", 1824, 1948),
        ("Birma / Mjamma (neatkariga)", 1948, None),
    ],
    "NP": [
        ("Nepalas Karaliste", 1768, 2008),
        ("Nepalas Federativa Republika", 2008, None),
    ],
    "OM": [
        ("Omanas Sultanats (agrinals)", 1744, 1970),
        ("Omanas Sultanats (musdienu)", 1970, None),
    ],
    "PK": [
        ("Pakistani (Dominions)", 1947, 1956),
        ("Pakistanas Islama Republika", 1956, None),
    ],
    "PS": [("Palestina (Palestinas Parvalde)", 1994, None)],
    "PH": [
        ("Filipinas (Spanis / ASV kolonila)", 1565, 1946),
        ("Filipinu Republika", 1946, None),
    ],
    "QA": [
        ("Katara (Britu protektorats)", 1916, 1971),
        ("Kataras Valsts", 1971, None),
    ],
    "SA": [
        ("Sauda Arabija (karaliste, aginala)", 1902, 1953),
        ("Sauda Arabijas Karaliste (musdienu)", 1953, None),
    ],
    "SG": [
        ("Singapura (Britu kolonila)", 1819, 1965),
        ("Singapuras Republika", 1965, None),
    ],
    "LK": [
        ("Ceilona (Britu kolonila)", 1815, 1948),
        ("Srilankas Republika", 1948, None),
    ],
    "SY": [
        ("Sirija (Francu mandats)", 1920, 1946),
        ("Sirijas Arabu Republika", 1946, None),
    ],
    "TW": [
        ("Taivana (Japanas kolonila)", 1895, 1945),
        ("Taivana (Kinas Republika)", 1945, None),
    ],
    "TJ": [
        ("Tadzikistanas PSR / PSRS", 1929, 1991),
        ("Tadzikistanas Republika", 1991, None),
    ],
    "TH": [
        ("Siama / Taizemes Karaliste (Cakri)", 1782, 1932),
        ("Taizemes Karaliste (musdienu)", 1932, None),
    ],
    "TM": [
        ("Turkmenistanas PSR / PSRS", 1924, 1991),
        ("Turkmenistanas Republika", 1991, None),
    ],
    "AE": [
        ("AAE (Britu protektorats)", 1820, 1971),
        ("Apvienotie Arabu Emirali", 1971, None),
    ],
    "UZ": [
        ("Uzbekistanas PSR / PSRS", 1924, 1991),
        ("Uzbekistanas Republika", 1991, None),
    ],
    "VN": [
        ("Vjetnama (Francu Indokina)", 1887, 1954),
        ("Dienvidvjetnama / Ziemeljivjetnama", 1954, 1975),
        ("Vjetnamas Socialistiska Republika", 1975, None),
    ],
    "YE": [
        ("Jemena (Ziemelu- un Dienvidjemena)", 1918, 1990),
        ("Jemenas Republika", 1990, None),
    ],

    # ── Afrika ───────────────────────────────────────────────────────
    "DZ": [
        ("Alzirija (Francu kolonila)", 1830, 1962),
        ("Alzirijas Republika", 1962, None),
    ],
    "AO": [
        ("Angola (Portugales kolonila)", 1575, 1975),
        ("Angolas Republika", 1975, None),
    ],
    "BW": [
        ("Bechuanaland (Britu protektorats)", 1885, 1966),
        ("Botsvanas Republika", 1966, None),
    ],
    "CM": [
        ("Kameruna (Francu / Vacu kolonila)", 1884, 1960),
        ("Kamerunas Republika", 1960, None),
    ],
    "CG": [
        ("Kongo (Francu kolonila)", 1880, 1960),
        ("Kongo Republika", 1960, None),
    ],
    "CD": [
        ("Belgijas Kongo (kolonila)", 1885, 1960),
        ("DR Kongo (Zaira / Republika)", 1960, None),
    ],
    "EG": [
        ("Egipte (Osmanu / Britu)", 1798, 1922),
        ("Egiptes Karaliste", 1922, 1953),
        ("Egiptes Republika", 1953, None),
    ],
    "ET": [
        ("Etiopijas imperija", 1270, 1974),
        ("Etiopijas Republika", 1974, None),
    ],
    "GH": [
        ("Zelta Krasts (Britu kolonila)", 1874, 1957),
        ("Ganas Republika", 1957, None),
    ],
    "GN": [
        ("Gvineja (Francu kolonila)", 1890, 1958),
        ("Gvinejas Republika", 1958, None),
    ],
    "CI": [
        ("Zilonkaula Krasts (Francu kolonila)", 1893, 1960),
        ("Kotdivuaras Republika", 1960, None),
    ],
    "KE": [
        ("Kenija (Britu kolonila)", 1895, 1963),
        ("Kenijas Republika", 1963, None),
    ],
    "LY": [
        ("Libija (Italijas / Britu kolonila)", 1911, 1951),
        ("Libijas Karaliste / Dzamahirija", 1951, 2011),
        ("Libijas Valsts", 2011, None),
    ],
    "MG": [
        ("Madagaskara (Francu kolonila)", 1896, 1960),
        ("Madagaskaras Republika", 1960, None),
    ],
    "ML": [
        ("Mali (Francu kolonila)", 1890, 1960),
        ("Mali Republika", 1960, None),
    ],
    "MA": [
        ("Maroka (Francu / Spanis protektorats)", 1912, 1956),
        ("Marokas Karaliste", 1956, None),
    ],
    "MZ": [
        ("Mozambika (Portugales kolonila)", 1498, 1975),
        ("Mozambikas Republika", 1975, None),
    ],
    "NA": [
        ("Dienvidrietumafrika (Vacu / Dienvidafrikai)", 1884, 1990),
        ("Namibijas Republika", 1990, None),
    ],
    "NG": [
        ("Nigerija (Britu kolonila)", 1861, 1960),
        ("Nigerijas Federativa Republika", 1960, None),
    ],
    "RW": [
        ("Ruanda (Belgijas kolonila)", 1916, 1962),
        ("Ruandas Republika", 1962, None),
    ],
    "SN": [
        ("Senegala (Francu kolonila)", 1854, 1960),
        ("Seneglas Republika", 1960, None),
    ],
    "SL": [
        ("Sjerraleone (Britu kolonila)", 1808, 1961),
        ("Sjerraleones Republika", 1961, None),
    ],
    "SO": [
        ("Somalija (Italu / Britu kolonila)", 1889, 1960),
        ("Somalijas Republika", 1960, None),
    ],
    "ZA": [
        ("Dienvidafrikai Savieniba (Britu)", 1910, 1961),
        ("Dienvidafrikai Republika", 1961, None),
    ],
    "SD": [
        ("Sudana (Egiptes-Britu kolonila)", 1899, 1956),
        ("Sudanas Republika", 1956, None),
    ],
    "TZ": [
        ("Tanzanija (Vacu / Britu kolonila)", 1885, 1961),
        ("Tanzanijas Apvienota Republika", 1961, None),
    ],
    "TN": [
        ("Tunisija (Francu protektorats)", 1881, 1956),
        ("Tunisijas Republika", 1956, None),
    ],
    "UG": [
        ("Uganda (Britu kolonila)", 1894, 1962),
        ("Ugandas Republika", 1962, None),
    ],
    "ZM": [
        ("Ziemelirodezija (Britu kolonila)", 1889, 1964),
        ("Zambijas Republika", 1964, None),
    ],
    "ZW": [
        ("Rodezija (Britu kolonila / neatkariga)", 1890, 1980),
        ("Zimbabves Republika", 1980, None),
    ],

    # ── Amerikas ─────────────────────────────────────────────────────
    "AR": [
        ("Argentina (spanis kolonila)", 1776, 1816),
        ("Argentinas Republika", 1816, None),
    ],
    "BS": [
        ("Bahamu salas (Britu kolonila)", 1718, 1973),
        ("Bahamu salu Sadraudziba", 1973, None),
    ],
    "BB": [
        ("Barbadosa (Britu kolonila)", 1627, 1966),
        ("Barbadosas Republika", 1966, None),
    ],
    "BO": [
        ("Bolivija (spanis kolonila)", 1776, 1825),
        ("Bolivijas Republika", 1825, None),
    ],
    "BR": [
        ("Brazilija (Portugales kolonila)", 1500, 1822),
        ("Brazilijas imperija", 1822, 1889),
        ("Brazilijas Republika", 1889, None),
    ],
    "CA": [
        ("Kanada (Britu kolonila)", 1763, 1867),
        ("Kanada (Dominions / Federacija)", 1867, None),
    ],
    "CL": [
        ("Cile (spanis kolonila)", 1541, 1818),
        ("Ciles Republika", 1818, None),
    ],
    "CO": [
        ("Kolumbija (spanis kolonila)", 1499, 1819),
        ("Kolumbijas Republika", 1819, None),
    ],
    "CR": [
        ("Kostarika (spanis kolonila)", 1502, 1821),
        ("Kostarkas Republika", 1821, None),
    ],
    "CU": [
        ("Kuba (spanis / ASV kolonila)", 1492, 1902),
        ("Kubas Republika (I)", 1902, 1959),
        ("Kubas Socialistiska Republika", 1959, None),
    ],
    "DO": [
        ("Dominikana (spanis kolonila)", 1496, 1844),
        ("Dominikaas Republika", 1844, None),
    ],
    "EC": [
        ("Ekvadora (spanis kolonila)", 1534, 1830),
        ("Ekvadoras Republika", 1830, None),
    ],
    "SV": [
        ("Salvadora (spanis kolonila)", 1525, 1821),
        ("Salvadoras Republika", 1821, None),
    ],
    "GT": [
        ("Gvatemala (spanis kolonila)", 1524, 1821),
        ("Gvatemalas Republika", 1821, None),
    ],
    "GY": [
        ("Gajana (Britu kolonila)", 1814, 1966),
        ("Gajanas Republika", 1966, None),
    ],
    "HT": [
        ("Haiti (Francu / Spanis kolonila)", 1492, 1804),
        ("Haiti Republika", 1804, None),
    ],
    "HN": [
        ("Hondurasa (spanis kolonila)", 1502, 1821),
        ("Hondurasas Republika", 1821, None),
    ],
    "JM": [
        ("Jamaika (Britu kolonila)", 1655, 1962),
        ("Jamaikas Neatkariga valsts", 1962, None),
    ],
    "MX": [
        ("Meksika (spanis kolonila)", 1519, 1821),
        ("Meksika (imperija / republika, XIX gs.)", 1821, 1867),
        ("Meksika (Federativa Republika)", 1867, None),
    ],
    "NI": [
        ("Nikaragva (spanis kolonila)", 1522, 1838),
        ("Nikaragvas Republika", 1838, None),
    ],
    "PA": [
        ("Panama (spanis kolonila / Kolumbija)", 1510, 1903),
        ("Panamas Republika", 1903, None),
    ],
    "PY": [
        ("Paragvaja (spanis kolonila)", 1537, 1811),
        ("Paragvajas Republika", 1811, None),
    ],
    "PE": [
        ("Peru (spanis kolonila)", 1532, 1821),
        ("Peru Republika", 1821, None),
    ],
    "TT": [
        ("Trinidada un Tobago (Britu kolonila)", 1797, 1962),
        ("Trinidadas un Tobago Republika", 1962, None),
    ],
    "UY": [
        ("Urugvaja (spanis kolonila)", 1726, 1828),
        ("Urugvajas Republika", 1828, None),
    ],
    "VE": [
        ("Venecuela (spanis kolonila)", 1498, 1830),
        ("Venecuelas Republika", 1830, None),
    ],

    # ── Okeanija ─────────────────────────────────────────────────────
    "AU": [
        ("Australija (Britu kolonila)", 1788, 1901),
        ("Australijas Sadraudziba", 1901, None),
    ],
    "FJ": [
        ("Fidzi (Britu kolonila)", 1874, 1970),
        ("Fidzi Republika", 1970, None),
    ],
    "KI": [
        ("Kiribati (Britu kolonila)", 1892, 1979),
        ("Kiribati Republika", 1979, None),
    ],
    "MH": [
        ("Marsala salas (Vacu / Japanas / ASV mandats)", 1885, 1986),
        ("Marsala salu Republika", 1986, None),
    ],
    "NR": [
        ("Nauru (Vacu / Australijas mandats)", 1888, 1968),
        ("Nauru Republika", 1968, None),
    ],
    "NZ": [
        ("Jaunzelande (Britu kolonila)", 1840, 1907),
        ("Jaunzelande (Dominions / Neatkariga)", 1907, None),
    ],
    "PW": [
        ("Palau (Vacu / Japanas / ASV mandats)", 1885, 1994),
        ("Palau Republika", 1994, None),
    ],
    "PG": [
        ("Papua Jaungineja (Vacu / Australijas mandats)", 1884, 1975),
        ("Papua Jaungineja Neatkariga valsts", 1975, None),
    ],
    "WS": [
        ("Samoa (Vacu / Jaunzelandes mandats)", 1900, 1962),
        ("Samoa Neatkariga valsts", 1962, None),
    ],
    "SB": [
        ("Zalamana salas (Britu kolonila)", 1893, 1978),
        ("Zalamana salu Neatkariga valsts", 1978, None),
    ],
    "TO": [
        ("Tongas Karaliste (Britu protektorats)", 1875, 1970),
        ("Tongas Karaliste (neatkariga)", 1970, None),
    ],
    "TV": [
        ("Tuvalu (Britu kolonila)", 1892, 1978),
        ("Tuvalu Neatkariga valsts", 1978, None),
    ],
    "VU": [
        ("Jaunas Hebridas (Francu / Britu kondominijs)", 1906, 1980),
        ("Vanuatu Republika", 1980, None),
    ],
}


async def main():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id, code FROM countries"))
        country_map = {row[1]: row[0] for row in result.fetchall()}

        added = 0
        skipped = 0

        for code, periods in PERIODS.items():
            country_id = country_map.get(code)
            if not country_id:
                print(f"WARNING: '{code}' nav DB — izlaizham")
                continue

            for section in SECTIONS:
                r = await conn.execute(
                    text("SELECT COUNT(*) FROM periods WHERE country_id=:cid AND section=:sec"),
                    {"cid": country_id, "sec": section}
                )
                count = r.scalar()
                if count > 0:
                    skipped += 1
                    continue

                for name, year_start, year_end in periods:
                    await conn.execute(
                        text("""
                            INSERT INTO periods (name, year_start, year_end, country_id, section, coin_category)
                            VALUES (:name, :ys, :ye, :cid, :sec, 'circulation')
                        """),
                        {"name": name, "ys": year_start, "ye": year_end,
                         "cid": country_id, "sec": section}
                    )
                    added += 1

        print(f"Pievienoti {added} periodi, izlaisti {skipped} sadalas (jau bija)")

asyncio.run(main())
