"""
Lietuvas Otrās Republikas monētu kataloga ielāde.
Lita sērija (1991-2014) + Eiro sērija (2015-)
"""
import os, sqlite3, uuid, time, sys, requests

DB_PATH   = r"C:\Users\USER\kolekcija\backend\kolekcija.db"
UPLOADS_DIR = r"C:\Users\USER\kolekcija\backend\uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

HEADERS = {"User-Agent": "KolekcijaCatalog/1.0 (educational; vcpsia@gmail.com)"}

import urllib3; urllib3.disable_warnings()

def pr(msg):
    sys.stdout.buffer.write((str(msg)+"\n").encode("utf-8","replace"))
    sys.stdout.buffer.flush()

# ─── Monētu dati ──────────────────────────────────────────────────────────────

LITAS_1991 = [
    {
        "name": "Lietuvas 1 Centas 1991. gads",
        "year": "1991", "denomination": "1 Centas",
        "material": "Alumīnijs", "diameter_mm": "18.75", "weight_g": "0.83",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#85", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas pirmā apgrozības monēta. Kalta pēc neatkarības atjaunošanas 1990. gadā.",
        "obverse_description": "Vitenis — Lietuvas bruņinieks uz zirga. Uzraksts LIETUVA un gads.",
        "reverse_description": "Nominālvērtība VIENAS CENTAS ar divkāršo krustu.",
        "ob_file": "File:LTL 0.01 obverse (1991 issue).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 2 Centai 1991. gads",
        "year": "1991", "denomination": "2 Centai",
        "material": "Alumīnijs", "diameter_mm": "21.75", "weight_g": "1.12",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#86", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas alumīnija apgrozības monēta pēc neatkarības atjaunošanas.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība DU CENTAI.",
        "ob_file": "File:2centas 1991 Lietuva.png",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 5 Centai 1991. gads",
        "year": "1991", "denomination": "5 Centai",
        "material": "Alumīnijs", "diameter_mm": "24.40", "weight_g": "1.40",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#87", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas alumīnija apgrozības monēta. Apgrozībā no 1991. līdz 2015. gadam.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība PENKI CENTAI.",
        "ob_file": "File:5centas 1991 Lietuva.png",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 10 Centų 1991. gads",
        "year": "1991", "denomination": "10 Centų",
        "material": "Bronza", "diameter_mm": "16.00", "weight_g": "1.40",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#88", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas bronzas apgrozības monēta. Mazākā no bronzas sērijas.",
        "obverse_description": "Vitenis uz zirga ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība DEŠIMT CENTŲ.",
        "ob_file": "File:10 centai (1991).png",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 20 Centų 1991. gads",
        "year": "1991", "denomination": "20 Centų",
        "material": "Bronza", "diameter_mm": "17.50", "weight_g": "2.10",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#89", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas bronzas apgrozības monēta.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība DVIDEŠIMT CENTŲ.",
        "ob_file": "File:20 centai (1991).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 50 Centų 1991. gads",
        "year": "1991", "denomination": "50 Centų",
        "material": "Bronza", "diameter_mm": "21.00", "weight_g": "3.03",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#90", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas lielākā bronzas apgrozības monēta.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība PENKIASDEŠIMT CENTŲ.",
        "ob_file": "File:50 centai (1991).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 1 Litas 1991. gads",
        "year": "1991", "denomination": "1 Litas",
        "material": "Vara-niķeļa sakausējums", "diameter_mm": "16.75", "weight_g": "2.35",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#91", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas pirmā lita monēta. Kalta tūlīt pēc lita atjaunošanas 1993. gadā.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība VIENAS LITAS.",
        "ob_file": "File:1 litas coin (1991).png",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 2 Litai 1991. gads",
        "year": "1991", "denomination": "2 Litai",
        "material": "Vara-niķeļa sakausējums", "diameter_mm": "20.00", "weight_g": "3.50",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#92", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas vara-niķeļa apgrozības monēta.",
        "obverse_description": "Vitenis uz zirga.",
        "reverse_description": "Nominālvērtība DU LITAI.",
        "ob_file": "File:2 litai coin (1991).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 5 Litai 1991. gads",
        "year": "1991", "denomination": "5 Litai",
        "material": "Vara-niķeļa sakausējums", "diameter_mm": "27.50", "weight_g": "10.10",
        "mint": "Lielbritānijas Karaliskā kaltuve", "mintage": None,
        "catalog_number": "KM#93", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas lielākā litsa nomināla apgrozības monēta 1991. gada sērijā.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība PENKI LITAI.",
        "ob_file": "File:5 litai coin (1991).jpg",
        "rev_file": None,
    },
]

LITAS_1997 = [
    {
        "name": "Lietuvas 10 Centų 1997. gads",
        "year": "1997", "denomination": "10 Centų",
        "material": "Niķeļa misiņš", "diameter_mm": "17.00", "weight_g": "2.60",
        "mint": "Dažādas kaltuvēs", "mintage": None,
        "catalog_number": "KM#106", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas otrās sērijas niķeļa-misiņa monēta. Apgrozībā 1997–2014.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība DEŠIMT CENTŲ.",
        "ob_file": "File:10 centai (1997).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 20 Centų 1997. gads",
        "year": "1997", "denomination": "20 Centų",
        "material": "Niķeļa misiņš", "diameter_mm": "20.50", "weight_g": "4.80",
        "mint": "Dažādas kaltuvēs", "mintage": None,
        "catalog_number": "KM#107", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas niķeļa-misiņa apgrozības monēta. Kalta 1997–2014.",
        "obverse_description": "Vitenis uz zirga ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība DVIDEŠIMT CENTŲ.",
        "ob_file": "File:20 centai (1997).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 50 Centų 1997. gads",
        "year": "1997", "denomination": "50 Centų",
        "material": "Niķeļa misiņš", "diameter_mm": "23.00", "weight_g": "6.00",
        "mint": "Dažādas kaltuvēs", "mintage": None,
        "catalog_number": "KM#108", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas lielākā niķeļa-misiņa monēta. Apgrozībā 1997–2014.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība PENKIASDEŠIMT CENTŲ.",
        "ob_file": "File:50 centai (1997).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 1 Litas 1998. gads",
        "year": "1998", "denomination": "1 Litas",
        "material": "Bimetāls (vara-niķeļa centrs + alumīnija bronzas gredzens)", "diameter_mm": "22.30", "weight_g": "6.25",
        "mint": "Dažādas kaltuvēs", "mintage": None,
        "catalog_number": "KM#111", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas bimetāla apgrozības monēta. Apgrozībā 1998–2014. Pirmā bimetāla monēta Lietuvas vēsturē.",
        "obverse_description": "Vitenis — Lietuvas valsts ģerbonis centrālajā diskā.",
        "reverse_description": "Nominālvērtība VIENAS LITAS zelta krāsas gredzenā.",
        "ob_file": "File:1 litas coin (1997).jpg",
        "rev_file": "File:1 litas coin (1997)-Reversum.png",
    },
    {
        "name": "Lietuvas 2 Litai 1998. gads",
        "year": "1998", "denomination": "2 Litai",
        "material": "Bimetāls (vara-niķeļa centrs + alumīnija bronzas gredzens)", "diameter_mm": "25.00", "weight_g": "7.50",
        "mint": "Dažādas kaltuvēs", "mintage": None,
        "catalog_number": "KM#112", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas bimetāla apgrozības monēta ar vizuāli atšķirīgu divu toni dizainu.",
        "obverse_description": "Vitenis uz zirga bimetāla centrā.",
        "reverse_description": "Nominālvērtība DU LITAI.",
        "ob_file": "File:2 litai coin (1997).jpg",
        "rev_file": None,
    },
    {
        "name": "Lietuvas 5 Litai 1998. gads",
        "year": "1998", "denomination": "5 Litai",
        "material": "Bimetāls (vara-niķeļa centrs + alumīnija bronzas gredzens)", "diameter_mm": "27.50", "weight_g": "10.10",
        "mint": "Dažādas kaltuvēs", "mintage": None,
        "catalog_number": "KM#113", "coin_category": "circulation",
        "description": "Lietuvas Otrās Republikas lielākā bimetāla apgrozības monēta. Apgrozībā 1998–2014. 2015. gadā nomainīja eiro.",
        "obverse_description": "Vitenis bimetāla centrālajā daļā ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība PENKI LITAI gredzenā.",
        "ob_file": "File:5 litai coin (1997).jpg",
        "rev_file": None,
    },
]

EURO_2015 = [
    {
        "name": "Lietuvas 1 Eiro Cents 2015. gads",
        "year": "2015", "denomination": "1 Eiro Cents",
        "material": "Tērauds ar vara pārklājumu", "diameter_mm": "16.25", "weight_g": "2.30",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#205", "coin_category": "circulation",
        "description": "Lietuvas pirmā eiro monēta. Emitēta 2015. gada 1. janvārī, kad Lietuva pievienojās Eirozonas un kļuva par 19. eiro valsti. Priekšpusē Lietuvas ģerbonis.",
        "obverse_description": "Vitenis — Lietuvas bruņinieks uz zirga. Uzraksts LIETUVA un zvaigžņu gredzens.",
        "reverse_description": "Eiropas karte ar nominālvērtību 1 un eiro zvaigznēm.",
        "ob_file": None, "rev_file": None,
    },
    {
        "name": "Lietuvas 2 Eiro Centi 2015. gads",
        "year": "2015", "denomination": "2 Eiro Centi",
        "material": "Tērauds ar vara pārklājumu", "diameter_mm": "18.75", "weight_g": "3.06",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#206", "coin_category": "circulation",
        "description": "Lietuvas eiro apgrozības monēta ar Viteņa attēlu. Lietuva pievienojās Eirozonam kā 19. valsts.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība 2 eiro centi ar Eiropas karti.",
        "ob_file": None, "rev_file": None,
    },
    {
        "name": "Lietuvas 5 Eiro Centi 2015. gads",
        "year": "2015", "denomination": "5 Eiro Centi",
        "material": "Tērauds ar vara pārklājumu", "diameter_mm": "21.25", "weight_g": "3.92",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#207", "coin_category": "circulation",
        "description": "Lietuvas eiro apgrozības monēta. Visas trīs mazākā nomināla eiro monētas ir vara pārklātas tērauda monētas.",
        "obverse_description": "Vitenis uz zirga ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība 5 eiro centi.",
        "ob_file": None, "rev_file": None,
    },
    {
        "name": "Lietuvas 10 Eiro Centu 2015. gads",
        "year": "2015", "denomination": "10 Eiro Centu",
        "material": "Misiņš (Nordic Gold)", "diameter_mm": "19.75", "weight_g": "4.10",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#208", "coin_category": "circulation",
        "description": "Lietuvas zelta krāsas eiro monēta no Nordic Gold sakausējuma. Malas rievas.",
        "obverse_description": "Vitenis ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība 10 eiro centu.",
        "ob_file": None, "rev_file": None,
    },
    {
        "name": "Lietuvas 20 Eiro Centu 2015. gads",
        "year": "2015", "denomination": "20 Eiro Centu",
        "material": "Misiņš (Nordic Gold)", "diameter_mm": "22.25", "weight_g": "5.74",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#209", "coin_category": "circulation",
        "description": "Lietuvas zelta krāsas eiro monēta. Astoņas malas ar robiņiem (Spānijas zieds).",
        "obverse_description": "Vitenis uz zirga, uzraksts LIETUVA.",
        "reverse_description": "Nominālvērtība 20 eiro centu.",
        "ob_file": "File:Pièce Lituanienne 50 centimes Vytis 2015.png", "rev_file": None,
    },
    {
        "name": "Lietuvas 50 Eiro Centu 2015. gads",
        "year": "2015", "denomination": "50 Eiro Centu",
        "material": "Misiņš (Nordic Gold)", "diameter_mm": "24.25", "weight_g": "7.80",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#210", "coin_category": "circulation",
        "description": "Lietuvas lielākā zelta krāsas eiro monēta. Rievota mala. Uz priekšpuses tradicionālais Vitenis.",
        "obverse_description": "Vitenis — Lietuvas bruņinieks uz zirga ar uzrakstu LIETUVA.",
        "reverse_description": "Nominālvērtība 50 eiro centu ar Eiropas karti.",
        "ob_file": "File:Pièce Lituanienne 50 centimes Vytis 2015.png", "rev_file": None,
    },
    {
        "name": "Lietuvas 1 Eiro 2015. gads",
        "year": "2015", "denomination": "1 Eiro",
        "material": "Bimetāls: balts centrs (Cu-Ni) + dzeltenais gredzens (niķeļa misiņš)", "diameter_mm": "23.25", "weight_g": "7.50",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#211", "coin_category": "circulation",
        "description": "Lietuvas 1 eiro bimetāla apgrozības monēta. Baltais centrs ar Viteņa attēlu, dzeltenais gredzens ar eiro zvaigznēm.",
        "obverse_description": "Vitenis centrālajā baltajā diskā. Uzraksts LIETUVA.",
        "reverse_description": "Globuss ar nominālvērtību 1 EURO.",
        "ob_file": None, "rev_file": None,
    },
    {
        "name": "Lietuvas 2 Eiro 2015. gads",
        "year": "2015", "denomination": "2 Eiro",
        "material": "Bimetāls: balts centrs (Cu-Ni) + dzeltenais gredzens (Cu-Zn-Ni)", "diameter_mm": "25.75", "weight_g": "8.50",
        "mint": "Hamburgas kaltuve (Vācija)", "mintage": None,
        "catalog_number": "KM#212", "coin_category": "circulation",
        "description": "Lietuvas 2 eiro bimetāla apgrozības monēta. Malā gravēts uzraksts LAISVĖ VIENYBĖ GEROVĖ (Brīvība, Vienotība, Labklājība). Pirmā Lietuvas eiro emisiija 2015. gadā.",
        "obverse_description": "Vitenis uz zirga dzeltenajā gredzenā. Uzraksts LIETUVA.",
        "reverse_description": "Eiropas karte ar nominālvērtību 2 EURO.",
        "ob_file": None, "rev_file": None,
    },
]

# ─── Wikimedia attēlu iegūšana ────────────────────────────────────────────────

def get_url(title):
    if not title: return None
    r = requests.get("https://commons.wikimedia.org/w/api.php", params={
        "action":"query","titles":title,"prop":"imageinfo",
        "iiprop":"url","iiurlwidth":"700","format":"json",
    }, headers=HEADERS, timeout=12, verify=False)
    for page in r.json().get("query",{}).get("pages",{}).values():
        ii = page.get("imageinfo",[])
        if ii: return ii[0].get("thumburl") or ii[0].get("url")
    return None

def download(url):
    if not url: return None
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        if r.status_code==200 and len(r.content)>2000: return r.content
    except: pass
    return None

def save(content, item_id, side):
    fn = f"cat_{item_id}_{side}_{uuid.uuid4().hex[:8]}.jpg"
    with open(os.path.join(UPLOADS_DIR,fn),"wb") as f: f.write(content)
    return f"/uploads/{fn}"

def insert_coins(c, conn, period_id, coins):
    added = skipped = 0
    for coin in coins:
        c.execute("""SELECT id FROM catalog_items
                     WHERE period_id=? AND year=? AND denomination=?""",
                  (period_id, coin["year"], coin["denomination"]))
        if c.fetchone():
            pr(f"  [~] {coin['denomination']} {coin['year']} — jau ir")
            skipped += 1
            continue
        c.execute("""INSERT INTO catalog_items
            (section,period_id,name,year,denomination,material,diameter_mm,weight_g,
             mint,mintage,catalog_number,coin_category,description,
             obverse_description,reverse_description,admin_edited)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""", (
            "coins", period_id,
            coin["name"], coin["year"], coin["denomination"],
            coin["material"], coin["diameter_mm"], coin["weight_g"],
            coin["mint"], coin.get("mintage"), coin["catalog_number"],
            coin["coin_category"], coin["description"],
            coin["obverse_description"], coin["reverse_description"],
        ))
        item_id = c.lastrowid
        conn.commit()
        pr(f"  [+] {coin['denomination']} {coin['year']} (id={item_id})")

        # Atteli
        for side, fkey in (("obverse","ob_file"),("reverse","rev_file")):
            fname = coin.get(fkey)
            if not fname: continue
            pr(f"      {side}: {fname}")
            url = get_url(fname); time.sleep(0.4)
            if url:
                content = download(url)
                if content:
                    path = save(content, item_id, side)
                    col = "image_url" if side=="obverse" else "image_url_reverse"
                    c.execute(f"UPDATE catalog_items SET {col}=? WHERE id=?", (path, item_id))
                    conn.commit()
                    pr(f"      [OK] {len(content)//1024}KB")
                else:
                    pr(f"      [!] Lejupieleede neizdevaas")
            else:
                pr(f"      [!] Nav URL")
            time.sleep(0.3)
        added += 1
    return added, skipped

# ─── Galvenais ────────────────────────────────────────────────────────────────

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Lietuva jau ir: code='LT'
    c.execute("SELECT id FROM countries WHERE code='LT'")
    country_id = c.fetchone()["id"]
    pr(f"[OK] Lietuva (id={country_id})")

    # ── Periods 1: Litas ──────────────────────────────────────────────────────
    p1_name = "Antroji Respublika - Litas (1991-2014)"
    c.execute("SELECT id FROM periods WHERE country_id=? AND name=?", (country_id, p1_name))
    row = c.fetchone()
    if row:
        p1_id = row["id"]
        pr(f"[OK] Periods '{p1_name}' (id={p1_id})")
    else:
        c.execute("""INSERT INTO periods (name,year_start,year_end,country_id,section,coin_category)
                     VALUES (?,?,?,?,?,?)""",
                  (p1_name, 1991, 2014, country_id, "coins", "circulation"))
        p1_id = c.lastrowid; conn.commit()
        pr(f"[+] Periods '{p1_name}' (id={p1_id})")

    # ── Periods 2: Eiro ───────────────────────────────────────────────────────
    p2_name = "Antroji Respublika - Euras (2015-)"
    c.execute("SELECT id FROM periods WHERE country_id=? AND name=?", (country_id, p2_name))
    row = c.fetchone()
    if row:
        p2_id = row["id"]
        pr(f"[OK] Periods '{p2_name}' (id={p2_id})")
    else:
        c.execute("""INSERT INTO periods (name,year_start,year_end,country_id,section,coin_category)
                     VALUES (?,?,?,?,?,?)""",
                  (p2_name, 2015, None, country_id, "coins", "circulation"))
        p2_id = c.lastrowid; conn.commit()
        pr(f"[+] Periods '{p2_name}' (id={p2_id})")

    # ── Pievienot monetas ──────────────────────────────────────────────────────
    pr(f"\n--- 1991. gada litsa serija ({len(LITAS_1991)} mon.) ---")
    a1, s1 = insert_coins(c, conn, p1_id, LITAS_1991)

    pr(f"\n--- 1997/1998. gada litsa serija ({len(LITAS_1997)} mon.) ---")
    a2, s2 = insert_coins(c, conn, p1_id, LITAS_1997)

    pr(f"\n--- 2015. gada eiro serija ({len(EURO_2015)} mon.) ---")
    a3, s3 = insert_coins(c, conn, p2_id, EURO_2015)

    conn.close()
    pr(f"\n{'='*50}")
    pr(f"Pabeigts!")
    pr(f"  Litas 1991: +{a1}, izlaistas {s1}")
    pr(f"  Litas 1997: +{a2}, izlaistas {s2}")
    pr(f"  Eiro  2015: +{a3}, izlaistas {s3}")
    pr(f"  Kopa pievienotas: {a1+a2+a3} monetas")

if __name__ == "__main__":
    main()
