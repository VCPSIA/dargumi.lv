"""
Ielādē kontinentu → valstu → periodu struktūru no ucoin.net
un saglabā datubāzē.
"""
import asyncio
import time
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select, delete

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xhtml;q=0.9,*/*;q=0.8",
}
BASE = "https://en.ucoin.net"

def get(url, retries=3):
    for i in range(retries):
        try:
            r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True, verify=False)
            if r.status_code == 200:
                return r.text
            print(f"  [{r.status_code}] {url}")
        except Exception as e:
            print(f"  Kļūda: {e}")
        time.sleep(2 + i * 2)
    return None

def parse_catalog_page(html):
    """Iegūst kontinentus un valstis no galvenās kataloga lapas."""
    soup = BeautifulSoup(html, "html.parser")
    continents = {}

    for h2 in soup.find_all("h2"):
        cont_name = h2.get_text(strip=True)
        if not cont_name or len(cont_name) > 40:
            continue
        ul = h2.find_next_sibling("ul")
        if not ul:
            continue
        countries = []
        for a in ul.find_all("a", href=True):
            href = a["href"]
            name = a.get_text(strip=True)
            if "country=" in href and name:
                code = href.split("country=")[-1].split("&")[0].strip("/")
                countries.append({"name": name, "code": code, "url": BASE + href if href.startswith("/") else href})
        if countries:
            continents[cont_name] = countries

    return continents

def parse_country_page(html, section="coins"):
    """Iegūst periodus no valsts lapas."""
    soup = BeautifulSoup(html, "html.parser")
    periods = []

    # ucoin.net periods parasti ir <h2> vai <h3> elementi ar gadiem
    for tag in soup.find_all(["h2", "h3", "h4"]):
        text = tag.get_text(strip=True)
        if not text or len(text) > 120:
            continue
        # Meklējam gada diapazonus formātā "Name (1920-1991)" vai "Name 1920-1991"
        import re
        m = re.search(r'(\d{3,4})\s*[-–]\s*(\d{3,4}|present|today|now)', text, re.IGNORECASE)
        year_start = year_end = None
        if m:
            year_start = int(m.group(1))
            end_str = m.group(2)
            if end_str.isdigit():
                year_end = int(end_str)

        name = re.sub(r'\s*\(?\d{3,4}[\s\-–]+(?:\d{3,4}|present|today|now)\)?', '', text).strip()
        name = name.strip("()- ").strip()
        if name and len(name) > 2:
            periods.append({"name": name, "year_start": year_start, "year_end": year_end})

    # Alternatīvi — tabulas vai saraksti
    if not periods:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "period=" in href or "era=" in href:
                name = a.get_text(strip=True)
                if name and len(name) > 2:
                    periods.append({"name": name, "year_start": None, "year_end": None})

    return periods

async def seed_from_ucoin():
    from app.database import init_db, AsyncSessionLocal
    from app.models.catalog import Continent, Country, Period, SectionType

    print("Inicializē DB...")
    await init_db()

    # Ielādē kataloga lapu
    print("Ielādē ucoin.net katalogu...")
    html = get(f"{BASE}/catalog/")
    if not html:
        print("Nevar ielādēt katalogu. Izmantoju rezerves datus.")
        await seed_fallback()
        return

    continents_data = parse_catalog_page(html)
    if not continents_data:
        print("Kataloga struktūra nav atrasta. Izmantoju rezerves datus.")
        await seed_fallback()
        return

    print(f"Atrasti {len(continents_data)} kontinenti:")
    for c, countries in continents_data.items():
        print(f"  {c}: {len(countries)} valstis")

    async with AsyncSessionLocal() as db:
        # Notīrīt veco
        await db.execute(delete(Period))
        await db.execute(delete(Country))
        await db.execute(delete(Continent))
        await db.commit()

        for cont_name, countries in continents_data.items():
            cont = Continent(name=cont_name, name_lv=cont_name, code=cont_name[:3].upper())
            db.add(cont)
            await db.flush()
            print(f"\n{cont_name}:")

            for c in countries[:50]:  # max 50 valstis uz kontinentu
                country = Country(
                    name=c["name"], name_lv=c["name"],
                    code=c["code"].upper()[:5], continent_id=cont.id
                )
                db.add(country)
                await db.flush()
                print(f"  + {c['name']} ({c['code']})", end="", flush=True)

                # Periodi
                time.sleep(1.0)
                chtml = get(f"{BASE}/catalog/?country={c['code']}")
                if chtml:
                    periods = parse_country_page(chtml)
                    if not periods:
                        # Noklusējuma periodi
                        periods = default_periods(c["name"])
                    for p in periods[:20]:
                        for section in [SectionType.coins, SectionType.medals, SectionType.stamps]:
                            db.add(Period(
                                name=p["name"],
                                year_start=p["year_start"],
                                year_end=p["year_end"],
                                country_id=country.id,
                                section=section,
                            ))
                    print(f" → {len(periods)} periodi")
                else:
                    for p in default_periods(c["name"]):
                        for section in [SectionType.coins, SectionType.medals, SectionType.stamps]:
                            db.add(Period(
                                name=p["name"],
                                year_start=p["year_start"],
                                year_end=p["year_end"],
                                country_id=country.id,
                                section=section,
                            ))
                    print(f" → noklusējuma periodi")

        await db.commit()
        print("\nSeeding pabeigts!")

def default_periods(country_name):
    """Vispārīgi periodi ja ucoin.net nav pieejams."""
    return [
        {"name": "Ancient / Medieval", "year_start": None, "year_end": 1800},
        {"name": "19th Century", "year_start": 1800, "year_end": 1900},
        {"name": "Early 20th Century", "year_start": 1900, "year_end": 1950},
        {"name": "Late 20th Century", "year_start": 1950, "year_end": 2000},
        {"name": "Modern (2000–present)", "year_start": 2000, "year_end": None},
    ]

async def seed_fallback():
    """Komprehensīvi dati ja ucoin.net bloķē."""
    from app.database import init_db, AsyncSessionLocal
    from app.models.catalog import Continent, Country, Period, SectionType
    from sqlalchemy import delete

    CONTINENTS = {
        "Europe": ("Eiropa", "EU", [
            ("Albania","Albānija","AL"), ("Andorra","Andora","AD"), ("Austria","Austrija","AT"),
            ("Belarus","Baltkrievija","BY"), ("Belgium","Beļģija","BE"), ("Bosnia","Bosnija","BA"),
            ("Bulgaria","Bulgārija","BG"), ("Croatia","Horvātija","HR"), ("Cyprus","Kipra","CY"),
            ("Czech Republic","Čehija","CZ"), ("Denmark","Dānija","DK"), ("Estonia","Igaunija","EE"),
            ("Finland","Somija","FI"), ("France","Francija","FR"), ("Germany","Vācija","DE"),
            ("Greece","Grieķija","GR"), ("Hungary","Ungārija","HU"), ("Iceland","Islande","IS"),
            ("Ireland","Īrija","IE"), ("Italy","Itālija","IT"), ("Kosovo","Kosova","XK"),
            ("Latvia","Latvija","LV"), ("Liechtenstein","Lihtenšteina","LI"),
            ("Lithuania","Lietuva","LT"), ("Luxembourg","Luksemburga","LU"),
            ("Malta","Malta","MT"), ("Moldova","Moldova","MD"), ("Monaco","Monako","MC"),
            ("Montenegro","Melnkalne","ME"), ("Netherlands","Nīderlande","NL"),
            ("North Macedonia","Ziemeļmaķedonija","MK"), ("Norway","Norvēģija","NO"),
            ("Poland","Polija","PL"), ("Portugal","Portugāle","PT"), ("Romania","Rumānija","RO"),
            ("Russia","Krievija","RU"), ("San Marino","Sanmarīno","SM"),
            ("Serbia","Serbija","RS"), ("Slovakia","Slovākija","SK"),
            ("Slovenia","Slovēnija","SI"), ("Spain","Spānija","ES"), ("Sweden","Zviedrija","SE"),
            ("Switzerland","Šveice","CH"), ("Ukraine","Ukraina","UA"),
            ("United Kingdom","Lielbritānija","GB"), ("Vatican","Vatikāns","VA"),
        ]),
        "Asia": ("Āzija", "AS", [
            ("Afghanistan","Afganistāna","AF"), ("Armenia","Armēnija","AM"),
            ("Azerbaijan","Azerbaidžāna","AZ"), ("Bahrain","Bahreina","BH"),
            ("Bangladesh","Bangladeša","BD"), ("Cambodia","Kambodža","KH"),
            ("China","Ķīna","CN"), ("Georgia","Gruzija","GE"), ("India","Indija","IN"),
            ("Indonesia","Indonēzija","ID"), ("Iran","Irāna","IR"), ("Iraq","Irāka","IQ"),
            ("Israel","Izraēla","IL"), ("Japan","Japāna","JP"), ("Jordan","Jordānija","JO"),
            ("Kazakhstan","Kazahstāna","KZ"), ("Kuwait","Kuveita","KW"),
            ("Kyrgyzstan","Kirgizstāna","KG"), ("Lebanon","Libāna","LB"),
            ("Malaysia","Malaizija","MY"), ("Mongolia","Mongolija","MN"),
            ("Myanmar","Mjanma","MM"), ("Nepal","Nepāla","NP"),
            ("North Korea","Ziemeļkoreja","KP"), ("Oman","Omāna","OM"),
            ("Pakistan","Pakistāna","PK"), ("Philippines","Filipīnas","PH"),
            ("Qatar","Katara","QA"), ("Saudi Arabia","Saūda Arābija","SA"),
            ("Singapore","Singapūra","SG"), ("South Korea","Dienvidkoreja","KR"),
            ("Sri Lanka","Šrilanka","LK"), ("Syria","Sīrija","SY"),
            ("Taiwan","Taivāna","TW"), ("Tajikistan","Tadžikistāna","TJ"),
            ("Thailand","Taizeme","TH"), ("Turkey","Turcija","TR"),
            ("Turkmenistan","Turkmenistāna","TM"), ("UAE","AAE","AE"),
            ("Uzbekistan","Uzbekistāna","UZ"), ("Vietnam","Vjetnama","VN"),
            ("Yemen","Jemena","YE"),
        ]),
        "Americas": ("Amerikas", "AM", [
            ("Argentina","Argentīna","AR"), ("Bolivia","Bolīvija","BO"),
            ("Brazil","Brazīlija","BR"), ("Canada","Kanāda","CA"),
            ("Chile","Čīle","CL"), ("Colombia","Kolumbija","CO"),
            ("Costa Rica","Kostarika","CR"), ("Cuba","Kuba","CU"),
            ("Dominican Republic","Dominikāna","DO"), ("Ecuador","Ekvadora","EC"),
            ("El Salvador","Salvadora","SV"), ("Guatemala","Gvatemala","GT"),
            ("Haiti","Haiti","HT"), ("Honduras","Hondurasa","HN"),
            ("Jamaica","Jamaika","JM"), ("Mexico","Meksika","MX"),
            ("Nicaragua","Nikaragva","NI"), ("Panama","Panama","PA"),
            ("Paraguay","Paragvaja","PY"), ("Peru","Peru","PE"),
            ("Trinidad and Tobago","Trinidāda","TT"), ("United States","ASV","US"),
            ("Uruguay","Urugvaja","UY"), ("Venezuela","Venecuēla","VE"),
        ]),
        "Africa": ("Āfrika", "AF", [
            ("Algeria","Alžīrija","DZ"), ("Angola","Angola","AO"),
            ("Cameroon","Kamerūna","CM"), ("Congo","Kongo","CG"),
            ("Egypt","Ēģipte","EG"), ("Ethiopia","Etiopija","ET"),
            ("Ghana","Gana","GH"), ("Kenya","Kenija","KE"),
            ("Libya","Lībija","LY"), ("Madagascar","Madagaskara","MG"),
            ("Mali","Mali","ML"), ("Morocco","Maroka","MA"),
            ("Mozambique","Mozambika","MZ"), ("Nigeria","Nigērija","NG"),
            ("Rwanda","Ruanda","RW"), ("Senegal","Senegāla","SN"),
            ("Somalia","Somālija","SO"), ("South Africa","Dienvidāfrika","ZA"),
            ("Sudan","Sudāna","SD"), ("Tanzania","Tanzānija","TZ"),
            ("Tunisia","Tunisija","TN"), ("Uganda","Uganda","UG"),
            ("Zimbabwe","Zimbabve","ZW"),
        ]),
        "Oceania": ("Okeānija", "OC", [
            ("Australia","Austrālija","AU"), ("Fiji","Fidži","FJ"),
            ("New Zealand","Jaunzēlande","NZ"), ("Papua New Guinea","Papua Jaungvineja","PG"),
            ("Solomon Islands","Zālamana salas","SB"), ("Tonga","Tonga","TO"),
            ("Vanuatu","Vanuatu","VU"),
        ]),
        "Ancient / World": ("Senie / Pasaule", "AW", [
            ("Ancient Rome","Senā Roma","ROM"), ("Ancient Greece","Senā Grieķija","GRC"),
            ("Byzantine Empire","Bizantija","BYZ"), ("Celtic","Kelti","CEL"),
            ("Medieval Europe","Viduslaiku Eiropa","MDE"), ("Ottoman Empire","Osmaņu impērija","OTT"),
            ("Persia","Persija","PRS"), ("World / Fantasy","Pasaule / Fantāzija","WRL"),
        ]),
    }

    # Periodi pēc valsts koda
    COUNTRY_PERIODS = {
        "LV": [
            ("Russian Empire",1721,1917), ("First Republic",1918,1940),
            ("Soviet Period",1940,1991), ("Modern Latvia",1991,None),
        ],
        "DE": [
            ("Holy Roman Empire",962,1806), ("German States",1806,1871),
            ("German Empire",1871,1918), ("Weimar Republic",1919,1933),
            ("Third Reich",1933,1945), ("West Germany / FRG",1949,1990),
            ("East Germany / GDR",1949,1990), ("Reunified Germany",1990,None),
        ],
        "RU": [
            ("Tsardom of Russia",1547,1721), ("Russian Empire",1721,1917),
            ("RSFSR / Soviet Union",1917,1991), ("Russian Federation",1991,None),
        ],
        "GB": [
            ("Medieval",1066,1603), ("Stuart / Commonwealth",1603,1714),
            ("Georgian Era",1714,1830), ("Victorian Era",1837,1901),
            ("Edwardian Era",1901,1910), ("George V–VI",1910,1952),
            ("Elizabeth II",1952,2022), ("Charles III",2022,None),
        ],
        "FR": [
            ("Royal France",987,1792), ("First Republic",1792,1804),
            ("Napoleonic Era",1804,1815), ("Restoration / July Monarchy",1815,1848),
            ("Second Republic / Empire",1848,1870), ("Third Republic",1870,1940),
            ("Vichy / WWII",1940,1944), ("Fourth Republic",1944,1958),
            ("Fifth Republic",1958,None),
        ],
        "US": [
            ("Colonial Era",1607,1776), ("Early Federal",1776,1840),
            ("Antebellum / Civil War",1840,1865), ("Reconstruction / Gilded Age",1865,1900),
            ("Progressive Era",1900,1933), ("Modern United States",1933,None),
        ],
        "AT": [
            ("Habsburg Empire",1282,1804), ("Austrian Empire",1804,1867),
            ("Austro-Hungarian Empire",1867,1918), ("First Republic",1918,1938),
            ("WWII / Anschluss",1938,1945), ("Second Republic",1945,None),
        ],
        "LT": [
            ("Grand Duchy of Lithuania",1251,1795),
            ("Russian Empire",1795,1918), ("First Republic",1918,1940),
            ("Soviet Period",1940,1990), ("Modern Lithuania",1990,None),
        ],
        "EE": [
            ("Swedish / Russian Rule",1561,1918), ("First Republic",1918,1940),
            ("Soviet Period",1940,1991), ("Modern Estonia",1991,None),
        ],
        "PL": [
            ("Kingdom of Poland",966,1795), ("Partitions Era",1795,1918),
            ("Second Republic",1918,1939), ("WWII / PRL",1939,1989),
            ("Third Republic",1989,None),
        ],
        "CN": [
            ("Imperial China",221,1912), ("Republic of China",1912,1949),
            ("People's Republic",1949,None),
        ],
        "JP": [
            ("Ancient / Classical",700,1603), ("Edo Period",1603,1868),
            ("Meiji / Taisho",1868,1926), ("Showa",1926,1989),
            ("Heisei / Reiwa",1989,None),
        ],
        "IN": [
            ("Mughal Empire",1526,1857), ("British India",1857,1947),
            ("Republic of India",1947,None),
        ],
    }

    DEFAULT_PERIODS = [
        ("Ancient / Medieval", None, 1800),
        ("19th Century", 1800, 1900),
        ("Early 20th Century", 1900, 1950),
        ("Late 20th Century", 1950, 2000),
        ("Modern", 2000, None),
    ]

    async with AsyncSessionLocal() as db:
        await db.execute(delete(Period))
        await db.execute(delete(Country))
        await db.execute(delete(Continent))
        await db.commit()

        total_countries = 0
        total_periods = 0

        for cont_name, (cont_lv, cont_code, countries) in CONTINENTS.items():
            cont = Continent(name=cont_name, name_lv=cont_lv, code=cont_code)
            db.add(cont)
            await db.flush()

            for name, name_lv, code in countries:
                country = Country(name=name, name_lv=name_lv, code=code, continent_id=cont.id)
                db.add(country)
                await db.flush()
                total_countries += 1

                periods = COUNTRY_PERIODS.get(code, [(n, s, e) for n, s, e in DEFAULT_PERIODS])
                for pname, ystart, yend in periods:
                    for section in [SectionType.coins, SectionType.medals, SectionType.stamps]:
                        db.add(Period(name=pname, year_start=ystart, year_end=yend,
                                      country_id=country.id, section=section))
                        total_periods += 1

        await db.commit()
        print(f"Ielādēts: {len(CONTINENTS)} kontinenti, {total_countries} valstis, {total_periods} periodi")

async def main():
    print("Mēģinu ielādēt no ucoin.net...")
    html = get(f"{BASE}/catalog/")
    if html and parse_catalog_page(html):
        await seed_from_ucoin()
    else:
        print("ucoin.net nav pieejams — izmantoju iebūvētos datus")
        from app.database import init_db, AsyncSessionLocal
        await init_db()
        await seed_fallback()

asyncio.run(main())
