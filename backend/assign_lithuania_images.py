"""
Preciza Lietuvas monetu attelu pieskiersana.
Izmanto zinamus Wikimedia Commons failu nosaukumus.
"""
import os, sqlite3, uuid, time, sys, requests

DB_PATH = r"C:\Users\USER\kolekcija\backend\kolekcija.db"
UPLOADS_DIR = r"C:\Users\USER\kolekcija\backend\uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

HEADERS = {"User-Agent": "KolekcijaCatalog/1.0 (educational; vcpsia@gmail.com)"}

import urllib3
urllib3.disable_warnings()

def pr(msg):
    sys.stdout.buffer.write((str(msg)+"\n").encode("utf-8","replace"))
    sys.stdout.buffer.flush()

def get_url(title):
    r = requests.get("https://commons.wikimedia.org/w/api.php", params={
        "action":"query","titles":title,"prop":"imageinfo",
        "iiprop":"url","iiurlwidth":"700","format":"json",
    }, headers=HEADERS, timeout=12, verify=False)
    pages = r.json().get("query",{}).get("pages",{})
    for page in pages.values():
        ii = page.get("imageinfo",[])
        if ii:
            return ii[0].get("thumburl") or ii[0].get("url")
    return None

def download(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        if r.status_code==200 and len(r.content)>2000:
            return r.content
    except Exception as e:
        pr(f"  Kluda: {e}")
    return None

def save(content, item_id, side):
    fn = f"cat_{item_id}_{side}_{uuid.uuid4().hex[:8]}.jpg"
    with open(os.path.join(UPLOADS_DIR,fn),"wb") as f: f.write(content)
    return f"/uploads/{fn}"

# Preciza kartesana: (year, denomination) -> (obverse_file, reverse_file)
# Balstoties uz Wikimedia Commons "Coins of Lithuania 1918-1940" kategoriju
IMAGE_MAP = {
    ("1925","1 Centas"):  ("File:Litwa 1c.jpg",                 None),
    ("1925","5 Centai"):  ("File:Litwa 5c.jpg",                 None),
    ("1925","10 Centų"):  ("File:Litwa 10c.jpg",                None),
    ("1925","20 Centų"):  ("File:Litwa 20c.jpg",                None),
    ("1925","50 Centų"):  ("File:Litwa 50c.jpg",                None),
    ("1925","1 Litas"):   ("File:1 LT 1925 A.png",              "File:1 LT 1925 R.png"),
    ("1925","2 Litai"):   ("File:2 LT 1925 A.png",              "File:2 LT 1925 R.png"),
    ("1925","5 Litai"):   ("File:5 LT 1925 A.png",              "File:5 LT 1925 R.png"),
    ("1936","1 Centas"):  ("File:Litwa 1c 1936.jpg",            None),
    ("1936","2 Centai"):  ("File:Litwa 2c.jpg",                 None),  # nav 1936-specific
    ("1936","5 Centai"):  ("File:Litwa 5c 1936.jpg",            None),
    ("1936","5 Litai"):   ("File:5 LT 1936 A.png",              "File:5 LT 1936 R.png"),
    ("1936","10 Litų"):   ("File:10 LT 1936 A Vytautas.png",    "File:10 LT 1936 R Vytautas.png"),
    ("1938","10 Litų"):   ("File:10 LT 1938 A Smetona.png",     "File:10 LT 1938 R Smetona.png"),
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Dzest nepareizas bildes (vienada bilde daudzam monetam)
    pr("Dzesu nepareizas bildes...")
    c.execute("""SELECT id, year, denomination, image_url, image_url_reverse
                 FROM catalog_items
                 WHERE id BETWEEN 380 AND 393""")
    coins = c.fetchall()

    for coin in coins:
        item_id = coin["id"]
        key = (str(coin["year"]), str(coin["denomination"]))
        if key in IMAGE_MAP:
            # Notirit veco bildi
            for col in ("image_url","image_url_reverse"):
                old = coin[col]
                if old and old.startswith("/uploads/"):
                    path = "C:\\Users\\USER\\kolekcija\\backend" + old.replace("/","\\" )
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                    except Exception:
                        pass
            c.execute("UPDATE catalog_items SET image_url=NULL, image_url_reverse=NULL WHERE id=?", (item_id,))
    conn.commit()
    pr("  Notirits.")

    # Pielidet pareizas bildes
    pr("\nPielieku precizas bildes...\n")
    updated = 0

    for (year, denom), (ob_file, rev_file) in IMAGE_MAP.items():
        c.execute("SELECT id FROM catalog_items WHERE year=? AND denomination=? AND id BETWEEN 380 AND 393",
                  (year, denom))
        row = c.fetchone()
        if not row:
            pr(f"  [!] Nav atrasts: {denom} {year}")
            continue
        item_id = row["id"]
        pr(f"  {denom} {year} (id={item_id})")

        if ob_file:
            pr(f"    Ob: {ob_file}")
            url = get_url(ob_file)
            time.sleep(0.4)
            if url:
                content = download(url)
                if content:
                    path = save(content, item_id, "obverse")
                    c.execute("UPDATE catalog_items SET image_url=? WHERE id=?", (path, item_id))
                    conn.commit()
                    pr(f"    [OK] {len(content)//1024}KB saglabaats")
                    updated += 1
                else:
                    pr(f"    [!] Lejupieleede neizdevaas")
            else:
                pr(f"    [!] URL nav atrasts: {ob_file}")
        time.sleep(0.3)

        if rev_file:
            pr(f"    Rev: {rev_file}")
            url = get_url(rev_file)
            time.sleep(0.4)
            if url:
                content = download(url)
                if content:
                    path = save(content, item_id, "reverse")
                    c.execute("UPDATE catalog_items SET image_url_reverse=? WHERE id=?", (path, item_id))
                    conn.commit()
                    pr(f"    [OK] {len(content)//1024}KB saglabaats")
                else:
                    pr(f"    [!] Aizmugures lejupieleede neizdevaas")
            else:
                pr(f"    [!] Rev URL nav atrasts: {rev_file}")
            time.sleep(0.3)

    conn.close()
    pr(f"\nPabeigts! Atjaunotas {updated} priekspuses bildes.")

if __name__ == "__main__":
    main()
