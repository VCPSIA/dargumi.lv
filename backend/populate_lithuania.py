"""
Lietuvas Pirmās Republikas (1918-1940) monētu kataloga ielāde.
Izveido struktūru DB un lejupielādē attēlus no Wikimedia Commons.
"""

import os
import sqlite3
import uuid
import time
import sys
import requests

DB_PATH = r"C:\Users\USER\kolekcija\backend\kolekcija.db"
UPLOADS_DIR = r"C:\Users\USER\kolekcija\backend\uploads"
HEADERS = {"User-Agent": "Mozilla/5.0 KolekcijaCatalog/1.0 (numismatic catalog; educational)"}

os.makedirs(UPLOADS_DIR, exist_ok=True)

# ─── Monētu dati ──────────────────────────────────────────────────────────────

COINS = [
    # ── 1925. gada sērija ─────────────────────────────────────────
    {
        "name": "Lietuvas 1 Centas 1925. gads",
        "year": "1925", "denomination": "1 Centas",
        "material": "Bronza", "diameter_mm": "16.0", "weight_g": "1.60",
        "mint": "Kings Norton Metal Works, Birmingema, UK",
        "mintage": None, "catalog_number": "KM#71",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas vismazākā apgrozības monēta. Dizainēja skulptors Juozas Zikaras. Kalta Birmingemas kaltuvē.",
        "obverse_description": "Vitenis (bruņinieks uz zirga) — Lietuvas valsts ģerbonis. Uzraksts LIETUVOS RESPUBLIKA 1925.",
        "reverse_description": "Nominālvērtība VIENAS CENTAS lauru lapu vainagā.",
        "wiki_ob": "Lithuania-1925-Coin-0.01-Obverse.jpg",
        "wiki_rev": "Lithuania-1925-Coin-0.01-Reverse.jpg",
        "wiki_search": "Lithuania 1925 1 centas coin",
    },
    {
        "name": "Lietuvas 5 Centai 1925. gads",
        "year": "1925", "denomination": "5 Centai",
        "material": "Alumīnijbronza", "diameter_mm": "19.0", "weight_g": "2.10",
        "mint": "Kings Norton Metal Works, Birmingema, UK",
        "mintage": "12 000 000", "catalog_number": "KM#72",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas apgrozības monēta ar labības vārpu rotājumu. Skulptors Juozas Zikaras.",
        "obverse_description": "Vitenis — Lietuvas ģerbonis ar uzrakstu LIETUVOS RESPUBLIKA 1925.",
        "reverse_description": "Nominālvērtība PENKI CENTAI ar labības vārpu rotājumu.",
        "wiki_search": "Lithuania 1925 5 centai coin",
    },
    {
        "name": "Lietuvas 10 Centų 1925. gads",
        "year": "1925", "denomination": "10 Centų",
        "material": "Alumīnijbronza", "diameter_mm": "21.0", "weight_g": "3.00",
        "mint": "Kings Norton Metal Works, Birmingema, UK",
        "mintage": None, "catalog_number": "KM#73",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas alumīnijbronzas apgrozības monēta.",
        "obverse_description": "Vitenis — Lietuvas ģerbonis.",
        "reverse_description": "Nominālvērtība DEŠIMT CENTŲ lapu vainagā.",
        "wiki_search": "Lithuania 1925 10 centu coin",
    },
    {
        "name": "Lietuvas 20 Centų 1925. gads",
        "year": "1925", "denomination": "20 Centų",
        "material": "Alumīnijbronza", "diameter_mm": "23.0", "weight_g": "4.00",
        "mint": "Kings Norton Metal Works, Birmingema, UK",
        "mintage": None, "catalog_number": "KM#74",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas alumīnijbronzas apgrozības monēta.",
        "obverse_description": "Vitenis — Lietuvas ģerbonis ar uzrakstu LIETUVOS RESPUBLIKA.",
        "reverse_description": "Nominālvērtība DVIDEŠIMT CENTŲ lapu vainagā.",
        "wiki_search": "Lithuania 1925 20 centu coin",
    },
    {
        "name": "Lietuvas 50 Centų 1925. gads",
        "year": "1925", "denomination": "50 Centų",
        "material": "Alumīnijbronza", "diameter_mm": "25.0", "weight_g": "5.00",
        "mint": "Kings Norton Metal Works, Birmingema, UK",
        "mintage": "5 000 000", "catalog_number": "KM#75",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas lielākā alumīnijbronzas monēta.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVOS RESPUBLIKA 1925.",
        "reverse_description": "Nominālvērtība PENKIASDEŠIMT CENTŲ.",
        "wiki_search": "Lithuania 1925 50 centu coin",
    },
    {
        "name": "Lietuvas 1 Litas 1925. gads",
        "year": "1925", "denomination": "1 Litas",
        "material": "Sudrabs 500‰", "diameter_mm": "19.0", "weight_g": "2.70",
        "mint": "Karaliskā kaltuve, Londona, UK",
        "mintage": None, "catalog_number": "KM#76",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas sudraba apgrozības monēta. Litss ieviests 1922. gadā kā Lietuvas nacionālā valūta (1 litas = 100 centų).",
        "obverse_description": "Vitenis ar Gedimiņa stabiem un uzrakstu LIETUVOS RESPUBLIKA.",
        "reverse_description": "Nominālvērtība VIENAS LITAS lauru vainagā.",
        "wiki_search": "Lithuania 1925 1 litas silver coin",
    },
    {
        "name": "Lietuvas 2 Litai 1925. gads",
        "year": "1925", "denomination": "2 Litai",
        "material": "Sudrabs 500‰", "diameter_mm": "22.9", "weight_g": "5.40",
        "mint": "Karaliskā kaltuve, Londona, UK",
        "mintage": "3 000 000", "catalog_number": "KM#77",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas sudraba apgrozības monēta. Mala ar rievām. Skulptors Juozas Zikaras.",
        "obverse_description": "Vitenis — Lietuvas bruņinieks uz zirga.",
        "reverse_description": "Nominālvērtība DU LITAI ziedu vainagā.",
        "wiki_search": "Lithuania 1925 2 litai silver coin",
    },
    {
        "name": "Lietuvas 5 Litai 1925. gads",
        "year": "1925", "denomination": "5 Litai",
        "material": "Sudrabs 500‰", "diameter_mm": "29.5", "weight_g": "13.50",
        "mint": "Karaliskā kaltuve, Londona, UK",
        "mintage": "1 000 000", "catalog_number": "KM#78",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas lielākā sudraba apgrozības monēta. Dizainēja skulptors Juozas Zikaras (1881–1944).",
        "obverse_description": "Vitenis ar uzrakstu LIETUVOS RESPUBLIKA 1925.",
        "reverse_description": "Nominālvērtība PENKI LITAI ziedu vainagā.",
        "wiki_search": "Lithuania 1925 5 litai silver coin",
    },
    # ── 1936. gada sērija ─────────────────────────────────────────
    {
        "name": "Lietuvas 1 Centas 1936. gads",
        "year": "1936", "denomination": "1 Centas",
        "material": "Bronza", "diameter_mm": "16.6", "weight_g": "2.00",
        "mint": "Spindulys, Kauņa, Lietuva",
        "mintage": None, "catalog_number": "KM#79",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas bronzas monēta, kalta Kauņas kaltuvē Spindulys — pirmajā Lietuvā izveidotajā kaltuvē.",
        "obverse_description": "Vitenis — Lietuvas ģerbonis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība lauru vainagā ar gadu 1936.",
        "wiki_search": "Lithuania 1936 1 centas coin",
    },
    {
        "name": "Lietuvas 2 Centai 1936. gads",
        "year": "1936", "denomination": "2 Centai",
        "material": "Bronza", "diameter_mm": "18.5", "weight_g": "2.30",
        "mint": "Spindulys, Kauņa, Lietuva",
        "mintage": None, "catalog_number": "KM#80",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas bronzas apgrozības monēta no 1936. gada sērijas.",
        "obverse_description": "Lietuvas valsts ģerbonis — Vitenis.",
        "reverse_description": "Nominālvērtība DU CENTAI ar gadu.",
        "wiki_search": "Lithuania 1936 2 centai coin",
    },
    {
        "name": "Lietuvas 5 Centai 1936. gads",
        "year": "1936", "denomination": "5 Centai",
        "material": "Bronza", "diameter_mm": "20.0", "weight_g": "2.50",
        "mint": "Spindulys, Kauņa, Lietuva",
        "mintage": "4 800 000", "catalog_number": "KM#81",
        "coin_category": "circulation",
        "description": "Lietuvas Pirmās Republikas bronzas monēta. Mala gluda. Kalta Kauņas kaltuvē Spindulys.",
        "obverse_description": "Lietuvas valsts ģerbonis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība vainagā ar datumu augšā.",
        "wiki_search": "Lithuania 1936 5 centai coin",
    },
    # ── Piemiņas monētas ──────────────────────────────────────────
    {
        "name": "Lietuvas 5 Litai 1936 – Jons Basanavičs",
        "year": "1936", "denomination": "5 Litai",
        "material": "Sudrabs 750‰", "diameter_mm": "27.0", "weight_g": "9.00",
        "mint": "Spindulys, Kauņa, Lietuva",
        "mintage": None, "catalog_number": "KM#82",
        "coin_category": "commemorative",
        "description": "Piemiņas sudraba monēta par godu Lietuvas nacionālā atmodas tēvam Dr. Jonam Basanavičam (1851–1927) — ārstam, folkloristam un tautiskās atmodas vadītājam. Mala ar uzrakstu: TAUTOS GEROVĖ TAVO GEROVĖ (Tautas labklājība ir tava labklājība).",
        "obverse_description": "Dr. Jona Basanavičs profils, uzraksts JONAS BASANAVIČIUS un nominālvērtība 5 LITAS.",
        "reverse_description": "Vitenis — Lietuvas ģerbonis ar uzrakstu LIETUVA un gadu 1936.",
        "wiki_search": "Lithuania 5 litas 1936 Basanavičius silver",
    },
    {
        "name": "Lietuvas 10 Litų 1936 – Vytautas Lielais",
        "year": "1936", "denomination": "10 Litų",
        "material": "Sudrabs 750‰", "diameter_mm": "32.0", "weight_g": "18.00",
        "mint": "Spindulys, Kauņa, Lietuva",
        "mintage": None, "catalog_number": "KM#83",
        "coin_category": "commemorative",
        "description": "Piemiņas sudraba monēta par godu lielkņazam Vitautam Lielajam (1350–1430), kurš vadīja Lietuvas un Polijas kopvalsts varenāko periodu. Lietuvas Dižkņaziste tā laikā bija Eiropas lielākā valsts.",
        "obverse_description": "Vytautas Lielā portrets viduslaiku bruņinieka tērpā ar uzrakstu VYTAUTAS DIDYSIS.",
        "reverse_description": "Lietuvas ģerbonis ar uzrakstu LIETUVA 1936.",
        "wiki_search": "Lithuania 10 litu 1936 Vytautas coin",
    },
    {
        "name": "Lietuvas 10 Litų 1938 – 20 gadi neatkarībai",
        "year": "1938", "denomination": "10 Litų",
        "material": "Sudrabs 750‰", "diameter_mm": "32.0", "weight_g": "18.00",
        "mint": "Spindulys, Kauņa, Lietuva",
        "mintage": "180 000", "catalog_number": "KM#84",
        "coin_category": "commemorative",
        "description": "Piemiņas sudraba monēta par godu Lietuvas neatkarības 20. gadadienai (1918–1938). Tirāža 180 000 eksemplāri. Mala ar uzrakstu TAUTOS GALIA VIENYBĖJE (Tautas spēks vienotībā).",
        "obverse_description": "Prezidenta Antanasa Smetonas portrets ar uzrakstu VALSTYBĖS PREZIDENTAS A.SMETONA 10 LITAS.",
        "reverse_description": "Gedimiņa stabi ar uzrakstu LIETUVA un jubilejas tekstu 1918–1938 DVIDEŠIMT METŲ NEPRIKLAUSOMYBĖS.",
        "wiki_search": "Lithuania 10 litu 1938 Smetona independence anniversary",
    },
]


# ─── Wikimedia Commons attēlu iegūšana ────────────────────────────────────────

def wikimedia_search(query):
    """Meklē Wikimedia Commons, atgriež (obverse_url, reverse_url) vai (url, None)."""
    api = "https://commons.wikimedia.org/w/api.php"
    try:
        r = requests.get(api, params={
            "action": "query", "list": "search",
            "srsearch": query,
            "srnamespace": 6, "srlimit": 8, "format": "json",
        }, headers=HEADERS, timeout=12, verify=False)
        results = r.json().get("query", {}).get("search", [])

        ob_url = rev_url = None
        for res in results:
            title = res["title"]
            lower = title.lower()
            # Priekšroka: skaidri "obverse" vai "reverse" faili
            if "obverse" in lower or "averse" in lower or "front" in lower:
                if not ob_url:
                    ob_url = _get_file_url(title)
            elif "reverse" in lower or "back" in lower:
                if not rev_url:
                    rev_url = _get_file_url(title)
            elif not ob_url:
                ob_url = _get_file_url(title)

        # Ja nekas precīzs — ņem pirmo
        if not ob_url and results:
            ob_url = _get_file_url(results[0]["title"])

        return ob_url, rev_url
    except Exception as e:
        pr(f"    Wikimedia kļūda '{query}': {e}")
        return None, None


def _get_file_url(title):
    api = "https://commons.wikimedia.org/w/api.php"
    try:
        r = requests.get(api, params={
            "action": "query", "titles": title,
            "prop": "imageinfo", "iiprop": "url",
            "iiurlwidth": 600, "format": "json",
        }, headers=HEADERS, timeout=10, verify=False)
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            ii = page.get("imageinfo", [])
            if ii:
                return ii[0].get("thumburl") or ii[0].get("url")
    except Exception:
        pass
    return None


def download_image(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
    except Exception as e:
        pr(f"    Lejupielādes kļūda: {e}")
    return None


def save_img(content, item_id, side):
    filename = f"cat_{item_id}_{side}_{uuid.uuid4().hex[:8]}.jpg"
    path = os.path.join(UPLOADS_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


# ─── Galvenais skripts ────────────────────────────────────────────────────────

def pr(msg):
    """Print ar UTF-8 droshu kodejumu."""
    sys.stdout.buffer.write((str(msg) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Atrast vai izveidot kontinentu "Eiropa"
    c.execute("SELECT id FROM continents WHERE code='EU' OR name='Europe'")
    row = c.fetchone()
    if row:
        continent_id = row["id"]
        pr(f"[OK] Kontinents atrasts (id={continent_id})")
    else:
        c.execute("INSERT INTO continents (name, name_lv, code) VALUES (?,?,?)",
                  ("Europe", "Eiropa", "EU"))
        continent_id = c.lastrowid
        conn.commit()
        pr(f"[+] Kontinents izveidots (id={continent_id})")

    # 2. Atrast vai izveidot valsti "Lithuania"
    c.execute("SELECT id FROM countries WHERE code='LT' OR name='Lithuania'")
    row = c.fetchone()
    if row:
        country_id = row["id"]
        pr(f"[✓] Valsts atrasta (id={country_id})")
    else:
        c.execute("INSERT INTO countries (name, name_lv, code, continent_id) VALUES (?,?,?,?)",
                  ("Lithuania", "Lietuva", "LT", continent_id))
        country_id = c.lastrowid
        conn.commit()
        pr(f"[+] Valsts izveidota (id={country_id})")

    # 3. Atrast vai izveidot periodu
    period_name = "Pirmoji Respublika (1918–1940)"
    c.execute("SELECT id FROM periods WHERE country_id=? AND section='coins' AND name=?",
              (country_id, period_name))
    row = c.fetchone()
    if row:
        period_id = row["id"]
        pr(f"[✓] Periods atrasts (id={period_id})")
    else:
        c.execute("""INSERT INTO periods (name, year_start, year_end, country_id, section, coin_category)
                     VALUES (?,?,?,?,?,?)""",
                  (period_name, 1918, 1940, country_id, "coins", "circulation"))
        period_id = c.lastrowid
        conn.commit()
        pr(f"[+] Periods izveidots (id={period_id})")

    # 4. Pievienot katru monētu
    pr(f"\nPievienoju {len(COINS)} monētas...\n")
    added = 0
    skipped = 0

    for coin in COINS:
        # Pārbaudīt vai jau eksistē
        c.execute("""SELECT id FROM catalog_items
                     WHERE period_id=? AND year=? AND denomination=? AND coin_category=?""",
                  (period_id, coin["year"], coin["denomination"], coin["coin_category"]))
        existing = c.fetchone()
        if existing:
            pr(f"  ~ Izlaižu (jau eksistē): {coin['denomination']} {coin['year']}")
            skipped += 1
            continue

        # Ievietot monētu
        c.execute("""INSERT INTO catalog_items
            (section, period_id, name, year, denomination, material, diameter_mm, weight_g,
             mint, mintage, catalog_number, coin_category, description,
             obverse_description, reverse_description, admin_edited)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            "coins", period_id,
            coin["name"], coin["year"], coin["denomination"],
            coin["material"], coin["diameter_mm"], coin["weight_g"],
            coin["mint"], coin.get("mintage"), coin["catalog_number"],
            coin["coin_category"], coin["description"],
            coin["obverse_description"], coin["reverse_description"],
            1,  # admin_edited = True (manuāli ievadīts)
        ))
        item_id = c.lastrowid
        conn.commit()
        pr(f"  + {coin['denomination']} {coin['year']} (id={item_id})")

        # Meklēt un lejupielādēt attēlus
        pr(f"    Meklēju attēlus: {coin['wiki_search']!r}")
        ob_url, rev_url = wikimedia_search(coin["wiki_search"])
        time.sleep(0.5)  # Cienīt Wikimedia rate limits

        if ob_url:
            pr(f"    ↓ Priekšpuse: {ob_url[:80]}...")
            content = download_image(ob_url)
            if content:
                url_path = save_img(content, item_id, "obverse")
                c.execute("UPDATE catalog_items SET image_url=? WHERE id=?", (url_path, item_id))
                conn.commit()
                pr(f"    ✓ Priekšpuse saglabāta")
            else:
                pr(f"    ✗ Priekšpuses lejupielāde neizdevās")
        else:
            pr(f"    ✗ Priekšpuse netika atrasta")

        if rev_url:
            pr(f"    ↓ Aizmugure: {rev_url[:80]}...")
            content = download_image(rev_url)
            if content:
                url_path = save_img(content, item_id, "reverse")
                c.execute("UPDATE catalog_items SET image_url_reverse=? WHERE id=?", (url_path, item_id))
                conn.commit()
                pr(f"    ✓ Aizmugure saglabāta")

        added += 1
        time.sleep(0.3)

    conn.close()
    pr(f"\n{'='*50}")
    pr(f"Pabeigts! Pievienotas: {added}, izlaistas: {skipped}")
    pr(f"Lietuvas monētas ir pieejamas katalogā: Eiropa → Lietuva → {period_name}")


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()

