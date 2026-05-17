import sqlite3
conn = sqlite3.connect("kolekcija.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT id, section, catalog_item_id, catalog_dismissed, custom_name, custom_country, user_image, added_at FROM collection_items ORDER BY added_at DESC LIMIT 5")
rows = cur.fetchall()
print("\n=== JAUNAKIE ===")
for r in rows:
    print(dict(r))

cur.execute("SELECT id, section, custom_name, custom_country, user_image, catalog_dismissed FROM collection_items WHERE catalog_item_id IS NULL")
rows = cur.fetchall()
print("\n=== PENDING ===")
for r in rows:
    print(dict(r))
