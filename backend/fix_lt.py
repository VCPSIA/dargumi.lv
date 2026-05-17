# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('kolekcija.db')
cur = conn.cursor()

# Vecā Lithuania: id=1 (LIT, Citi), jaunā: id=27 (LT, Eiropa)
# Pārvietot periodus no vecās uz jauno
cur.execute("UPDATE periods SET country_id=27 WHERE country_id=1")
print(f'Periodi pārvietoti: {cur.rowcount}')

# Pārvietot catalog items periodus (ja ir)
cur.execute("SELECT COUNT(*) FROM catalog_items WHERE period_id IN (SELECT id FROM periods WHERE country_id=27)")
print(f'Catalog items skaits (Lietuva): {cur.fetchone()[0]}')

# Dzēst veco Lietuvas ierakstu
cur.execute("DELETE FROM countries WHERE id=1")
print(f'Veco Lietuvu dzēsa: {cur.rowcount}')

# Pārbaudīt
cur.execute("SELECT id, name, name_lv, code, continent_id FROM countries WHERE name LIKE '%Lith%' OR name LIKE '%Lietuva%'")
for r in cur.fetchall(): print('Lietuva:', r)

cur.execute("SELECT id, name, country_id, year_start, year_end FROM periods")
for r in cur.fetchall(): print('Periods:', r)

conn.commit()
conn.close()
print('Pabeigts!')
