# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('kolekcija.db')
cur = conn.cursor()

continents = [
    ('Europe',                  'Eiropa',               'EU',  '🌍'),
    ('Asia',                    'Āzija',                'AS',  '🌏'),
    ('Africa',                  'Āfrika',               'AF',  '🌍'),
    ('North America',           'Ziemeļamerika',        'NA',  '🌎'),
    ('South America',           'Dienvidamerika',       'SA',  '🌎'),
    ('Australia and Oceania',   'Austrālija un Okeānija','OC', '🌏'),
    ('Other',                   'Citi',                 'OTH', '🌐'),
]

for name, name_lv, code, icon in continents:
    cur.execute('SELECT id FROM continents WHERE code=?', (code,))
    row = cur.fetchone()
    if row:
        cur.execute('UPDATE continents SET name=?, name_lv=?, icon=? WHERE code=?',
                    (name, name_lv, icon, code))
        print(f'Atjaunots: {name_lv}')
    else:
        cur.execute('INSERT INTO continents (name, name_lv, code, icon) VALUES (?,?,?,?)',
                    (name, name_lv, code, icon))
        print(f'Pievienots: {name_lv}')

conn.commit()

cur.execute('SELECT id, name_lv, code FROM continents ORDER BY id')
print('\nKontinenti DB:')
for row in cur.fetchall():
    print(f'  [{row[0]}] {row[1]} ({row[2]})')

cur.execute('SELECT COUNT(*) FROM countries')
print(f'\nValstu skaits: {cur.fetchone()[0]}')

conn.close()
print('Pabeigts!')
