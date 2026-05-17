# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('kolekcija.db')
cur = conn.cursor()
cur.execute("SELECT id, name, name_lv, code, continent_id FROM countries WHERE code IN ('LT','LIT') OR name LIKE '%Lithu%'")
for r in cur.fetchall(): print('VALSTS:', r)
cur.execute("SELECT id, name, country_id, section, year_start, year_end FROM periods")
for r in cur.fetchall(): print('PERIODS:', r)
conn.close()
