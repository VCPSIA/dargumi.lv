"""
Iegust attelu URL no Wikimedia Commons kategorijas un pipaso pie Lietuvas monetam.
"""
import os, sqlite3, uuid, time, sys, re, requests

DB_PATH = r"C:\Users\USER\kolekcija\backend\kolekcija.db"
UPLOADS_DIR = r"C:\Users\USER\kolekcija\backend\uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "KolekcijaCatalog/1.0 (educational numismatic catalog; contact: vcpsia@gmail.com)",
    "Accept": "application/json",
}

def pr(msg):
    sys.stdout.buffer.write((str(msg) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

def api(params):
    """Wikimedia Commons API pieprasijums."""
    r = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        params={**params, "format": "json"},
        headers=HEADERS, timeout=15, verify=False,
    )
    r.raise_for_status()
    return r.json()

def get_category_files(category):
    """Atgriez sarakstu ar File: nosaukumiem kategorija."""
    files = []
    cmcontinue = None
    while True:
        params = {
            "action": "query", "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": "100", "cmtype": "file",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
        data = api(params)
        for m in data.get("query", {}).get("categorymembers", []):
            files.append(m["title"])
        cont = data.get("continue", {})
        cmcontinue = cont.get("cmcontinue")
        if not cmcontinue:
            break
        time.sleep(0.3)
    return files

def get_file_urls(titles):
    """Atgriez {title: url} varda tabulu."""
    result = {}
    for i in range(0, len(titles), 20):
        batch = titles[i:i+20]
        data = api({
            "action": "query",
            "titles": "|".join(batch),
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "600",
        })
        for page in data.get("query", {}).get("pages", {}).values():
            ii = page.get("imageinfo", [])
            if ii:
                url = ii[0].get("thumburl") or ii[0].get("url")
                result[page["title"]] = url
        time.sleep(0.3)
    return result

def download(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        if r.status_code == 200 and len(r.content) > 2000:
            return r.content
    except Exception as e:
        pr(f"  Lejupieleedes kluda: {e}")
    return None

def save_img(content, item_id, side):
    fn = f"cat_{item_id}_{side}_{uuid.uuid4().hex[:8]}.jpg"
    with open(os.path.join(UPLOADS_DIR, fn), "wb") as f:
        f.write(content)
    return f"/uploads/{fn}"

# Atslegu vardi katrai monetai: (item_id, year, denom) -> meklesanas fragments
def match_score(filename, year, denom):
    """Cik labi fails atbilst monetai (augstaks = labaks)."""
    fn = filename.lower()
    score = 0
    if year and year in fn:
        score += 10
    # Denominacijas skaitlis
    denom_num = re.search(r"[\d]+", str(denom) or "")
    if denom_num and denom_num.group() in fn:
        score += 5
    if "lithuania" in fn or "litua" in fn or "lietuv" in fn:
        score += 3
    if "litas" in fn or "litu" in fn or "centas" in fn or "centai" in fn or "centu" in fn:
        score += 2
    return score

def main():
    import urllib3
    urllib3.disable_warnings()

    pr("Iegusstu Wikimedia Commons kategorijas failus...")
    try:
        files = get_category_files("Coins of Lithuania 1918-1940")
        pr(f"  Atrasti {len(files)} faili kategorijaa")
    except Exception as e:
        pr(f"  Kategorijas kluda: {e}")
        files = []

    # Papildus mekleesana no vispaarejjas Lietuvas monetu kategorijas
    try:
        files2 = get_category_files("Coins of Lithuania")
        pr(f"  + {len(files2)} faili no 'Coins of Lithuania'")
        files = list(set(files + files2))
    except Exception as e:
        pr(f"  Kluda: {e}")

    # Zina failu nosaukumi (kaa rezerve)
    known = [
        "File:Lithuania-1925-Coin-0.01-Obverse.jpg",
        "File:Lithuania-1925-Coin-0.01-Reverse.jpg",
        "File:Lithuania-1925-Coin-0.05-Obverse.jpg",
        "File:Lithuania-1925-Coin-0.05-Reverse.jpg",
        "File:Lithuania-1925-Coin-0.10-Obverse.jpg",
        "File:Lithuania-1925-Coin-0.10-Reverse.jpg",
        "File:Lithuania-1925-Coin-0.20-Obverse.jpg",
        "File:Lithuania-1925-Coin-0.20-Reverse.jpg",
        "File:Lithuania-1925-Coin-0.50-Obverse.jpg",
        "File:Lithuania-1925-Coin-0.50-Reverse.jpg",
        "File:Lithuania-1925-Coin-1.00-Obverse.jpg",
        "File:Lithuania-1925-Coin-1.00-Reverse.jpg",
        "File:Lithuania-1925-Coin-2.00-Obverse.jpg",
        "File:Lithuania-1925-Coin-2.00-Reverse.jpg",
        "File:Lithuania-1925-Coin-5.00-Obverse.jpg",
        "File:Lithuania-1925-Coin-5.00-Reverse.jpg",
        "File:Lithuania-1936-Coin-0.01-Obverse.jpg",
        "File:Lithuania-1936-Coin-0.01-Reverse.jpg",
        "File:Lithuania-1936-Coin-0.02-Obverse.jpg",
        "File:Lithuania-1936-Coin-0.02-Reverse.jpg",
        "File:Lithuania-1936-Coin-0.05-Obverse.jpg",
        "File:Lithuania-1936-Coin-0.05-Reverse.jpg",
        "File:1936 5 litai coin Basanavicius obverse.jpg",
        "File:1936 5 litai coin Basanavicius reverse.jpg",
        "File:1936 10 litu coin Vytautas obverse.jpg",
        "File:1938 10 litu coin Smetona obverse.jpg",
    ]
    all_files = list(set(files + known))
    pr(f"  Kopaa {len(all_files)} unikali faili")

    # Iegust URL visiem failiem
    pr("\nIegusstu failu URL...")
    url_map = {}
    try:
        url_map = get_file_urls(all_files)
        pr(f"  Ieguti {len(url_map)} URL")
    except Exception as e:
        pr(f"  URL kluda: {e}")

    # Savienot ar DB monetaam
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""SELECT ci.id, ci.year, ci.denomination, ci.image_url, ci.image_url_reverse
                 FROM catalog_items ci
                 JOIN periods p ON ci.period_id = p.id
                 JOIN countries co ON p.country_id = co.id
                 WHERE co.code = 'LT' AND ci.section = 'coins'
                 ORDER BY ci.year, ci.denomination""")
    coins = c.fetchall()
    pr(f"\nAtrastas {len(coins)} Lietuvas monetas DB")

    updated = 0
    for coin in coins:
        item_id = coin["id"]
        year = str(coin["year"] or "")
        denom = str(coin["denomination"] or "")
        has_ob = bool(coin["image_url"])
        has_rev = bool(coin["image_url_reverse"])

        if has_ob and has_rev:
            pr(f"  [OK] {denom} {year} - bildes jau ir")
            continue

        # Atrast labako failu
        ob_candidates = []
        rev_candidates = []
        for title, url in url_map.items():
            if not url:
                continue
            fn_low = title.lower()
            score = match_score(fn_low, year, denom)
            if score < 5:
                continue
            is_rev = "reverse" in fn_low or "-rev" in fn_low or "_rev" in fn_low
            is_ob = "obverse" in fn_low or "averse" in fn_low or "-ob" in fn_low
            if is_rev:
                rev_candidates.append((score, title, url))
            elif is_ob:
                ob_candidates.append((score, title, url))
            else:
                ob_candidates.append((score - 1, title, url))

        ob_candidates.sort(reverse=True)
        rev_candidates.sort(reverse=True)

        pr(f"\n  {denom} {year} (id={item_id})")
        pr(f"    Ob kandidaati: {len(ob_candidates)}, Rev kandidaati: {len(rev_candidates)}")

        if not has_ob and ob_candidates:
            title, url = ob_candidates[0][1], ob_candidates[0][2]
            pr(f"    Ob: {title[:60]}")
            content = download(url)
            if content:
                path = save_img(content, item_id, "obverse")
                c.execute("UPDATE catalog_items SET image_url=? WHERE id=?", (path, item_id))
                conn.commit()
                pr(f"    [OK] Priekspuse saglabaata ({len(content)//1024}KB)")
                updated += 1
            time.sleep(0.4)

        if not has_rev and rev_candidates:
            title, url = rev_candidates[0][1], rev_candidates[0][2]
            pr(f"    Rev: {title[:60]}")
            content = download(url)
            if content:
                path = save_img(content, item_id, "reverse")
                c.execute("UPDATE catalog_items SET image_url_reverse=? WHERE id=?", (path, item_id))
                conn.commit()
                pr(f"    [OK] Aizmugure saglabaata ({len(content)//1024}KB)")
            time.sleep(0.4)

    conn.close()
    pr(f"\nPabeigts! Atjaunotas bildes: {updated} monetaam")

if __name__ == "__main__":
    main()
