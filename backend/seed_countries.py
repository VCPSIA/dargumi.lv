# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('kolekcija.db')
cur = conn.cursor()

# Iegūt kontinentu ID
cur.execute('SELECT code, id FROM continents')
cont = {row[0]: row[1] for row in cur.fetchall()}
print('Kontinenti:', cont)

EU = cont['EU']
AS = cont['AS']
AF = cont['AF']
NA = cont['NA']
SA = cont['SA']
OC = cont['OC']
OTH = cont['OTH']

# (name_en, name_lv, iso2, continent_id, is_extinct)
countries = [
    # Eiropa
    ('Albania',             'Albānija',             'AL', EU, False),
    ('Andorra',             'Andora',               'AD', EU, False),
    ('Austria',             'Austrija',             'AT', EU, False),
    ('Belarus',             'Baltkrievija',         'BY', EU, False),
    ('Belgium',             'Beļģija',              'BE', EU, False),
    ('Bosnia and Herz.',    'Bosnija un Hercegovina','BA', EU, False),
    ('Bulgaria',            'Bulgārija',            'BG', EU, False),
    ('Croatia',             'Horvātija',            'HR', EU, False),
    ('Cyprus',              'Kipra',                'CY', EU, False),
    ('Czech Republic',      'Čehija',               'CZ', EU, False),
    ('Denmark',             'Dānija',               'DK', EU, False),
    ('Estonia',             'Igaunija',             'EE', EU, False),
    ('Finland',             'Somija',               'FI', EU, False),
    ('France',              'Francija',             'FR', EU, False),
    ('Germany',             'Vācija',               'DE', EU, False),
    ('Gibraltar',           'Gibraltārs',           'GI', EU, False),
    ('Greece',              'Grieķija',             'GR', EU, False),
    ('Hungary',             'Ungārija',             'HU', EU, False),
    ('Iceland',             'Islande',              'IS', EU, False),
    ('Ireland',             'Īrija',                'IE', EU, False),
    ('Isle of Man',         'Menas sala',           'IM', EU, False),
    ('Italy',               'Itālija',              'IT', EU, False),
    ('Kosovo',              'Kosova',               'XK', EU, False),
    ('Latvia',              'Latvija',              'LV', EU, False),
    ('Liechtenstein',       'Lihtenšteina',         'LI', EU, False),
    ('Lithuania',           'Lietuva',              'LT', EU, False),
    ('Luxembourg',          'Luksemburga',          'LU', EU, False),
    ('Malta',               'Malta',                'MT', EU, False),
    ('Moldova',             'Moldova',              'MD', EU, False),
    ('Monaco',              'Monako',               'MC', EU, False),
    ('Montenegro',          'Melnkalne',            'ME', EU, False),
    ('Netherlands',         'Nīderlande',           'NL', EU, False),
    ('North Macedonia',     'Ziemeļmaķedonija',     'MK', EU, False),
    ('Norway',              'Norvēģija',            'NO', EU, False),
    ('Poland',              'Polija',               'PL', EU, False),
    ('Portugal',            'Portugāle',            'PT', EU, False),
    ('Romania',             'Rumānija',             'RO', EU, False),
    ('Russia',              'Krievija',             'RU', EU, False),
    ('San Marino',          'Sanmarīno',            'SM', EU, False),
    ('Serbia',              'Serbija',              'RS', EU, False),
    ('Slovakia',            'Slovākija',            'SK', EU, False),
    ('Slovenia',            'Slovēnija',            'SI', EU, False),
    ('Spain',               'Spānija',              'ES', EU, False),
    ('Sweden',              'Zviedrija',            'SE', EU, False),
    ('Switzerland',         'Šveice',               'CH', EU, False),
    ('Turkey',              'Turcija',              'TR', EU, False),
    ('Ukraine',             'Ukraina',              'UA', EU, False),
    ('United Kingdom',      'Lielbritānija',        'GB', EU, False),
    ('Vatican City',        'Vatikāns',             'VA', EU, False),
    # Āzija
    ('Afghanistan',         'Afganistāna',          'AF', AS, False),
    ('Armenia',             'Armēnija',             'AM', AS, False),
    ('Azerbaijan',          'Azerbaidžāna',         'AZ', AS, False),
    ('Bahrain',             'Bahreina',             'BH', AS, False),
    ('Bangladesh',          'Bangladeša',           'BD', AS, False),
    ('Bhutan',              'Butāna',               'BT', AS, False),
    ('Brunei',              'Bruneja',              'BN', AS, False),
    ('Cambodia',            'Kambodža',             'KH', AS, False),
    ('China',               'Ķīna',                 'CN', AS, False),
    ('Georgia',             'Gruzija',              'GE', AS, False),
    ('India',               'Indija',               'IN', AS, False),
    ('Indonesia',           'Indonēzija',           'ID', AS, False),
    ('Iran',                'Irāna',                'IR', AS, False),
    ('Iraq',                'Irāka',                'IQ', AS, False),
    ('Israel',              'Izraēla',              'IL', AS, False),
    ('Japan',               'Japāna',               'JP', AS, False),
    ('Jordan',              'Jordānija',            'JO', AS, False),
    ('Kazakhstan',          'Kazahstāna',           'KZ', AS, False),
    ('Kuwait',              'Kuveita',              'KW', AS, False),
    ('Kyrgyzstan',          'Kirgizstāna',          'KG', AS, False),
    ('Laos',                'Laosa',                'LA', AS, False),
    ('Lebanon',             'Libāna',               'LB', AS, False),
    ('Malaysia',            'Malaizija',            'MY', AS, False),
    ('Maldives',            'Maldīvija',            'MV', AS, False),
    ('Mongolia',            'Mongolija',            'MN', AS, False),
    ('Myanmar',             'Mjanma',               'MM', AS, False),
    ('Nepal',               'Nepāla',               'NP', AS, False),
    ('North Korea',         'Ziemeļkoreja',         'KP', AS, False),
    ('Oman',                'Omāna',                'OM', AS, False),
    ('Pakistan',            'Pakistāna',            'PK', AS, False),
    ('Palestine',           'Palestīna',            'PS', AS, False),
    ('Philippines',         'Filipīnas',            'PH', AS, False),
    ('Qatar',               'Katara',               'QA', AS, False),
    ('Saudi Arabia',        'Saūda Arābija',        'SA', AS, False),
    ('Singapore',           'Singapūra',            'SG', AS, False),
    ('South Korea',         'Dienvidkoreja',        'KR', AS, False),
    ('Sri Lanka',           'Šrilanka',             'LK', AS, False),
    ('Syria',               'Sīrija',               'SY', AS, False),
    ('Taiwan',              'Taivāna',              'TW', AS, False),
    ('Tajikistan',          'Tadžikistāna',         'TJ', AS, False),
    ('Thailand',            'Taizeme',              'TH', AS, False),
    ('Turkmenistan',        'Turkmenistāna',        'TM', AS, False),
    ('United Arab Emirates','Apvienotie Arābu Emirāti','AE', AS, False),
    ('Uzbekistan',          'Uzbekistāna',          'UZ', AS, False),
    ('Vietnam',             'Vjetnama',             'VN', AS, False),
    ('Yemen',               'Jemena',               'YE', AS, False),
    # Āfrika
    ('Algeria',             'Alžīrija',             'DZ', AF, False),
    ('Angola',              'Angola',               'AO', AF, False),
    ('Botswana',            'Botsvāna',             'BW', AF, False),
    ('Cameroon',            'Kamerūna',             'CM', AF, False),
    ('Congo',               'Kongo',                'CG', AF, False),
    ('DR Congo',            'Kongo DR',             'CD', AF, False),
    ('Egypt',               'Ēģipte',               'EG', AF, False),
    ('Ethiopia',            'Etiopija',             'ET', AF, False),
    ('Ghana',               'Gana',                 'GH', AF, False),
    ('Guinea',              'Gvineja',              'GN', AF, False),
    ('Ivory Coast',         'Ziloņkaula krasts',    'CI', AF, False),
    ('Kenya',               'Kenija',               'KE', AF, False),
    ('Libya',               'Lībija',               'LY', AF, False),
    ('Madagascar',          'Madagaskara',          'MG', AF, False),
    ('Mali',                'Mali',                 'ML', AF, False),
    ('Morocco',             'Maroka',               'MA', AF, False),
    ('Mozambique',          'Mozambika',            'MZ', AF, False),
    ('Namibia',             'Namībija',             'NA', AF, False),
    ('Nigeria',             'Nigērija',             'NG', AF, False),
    ('Rwanda',              'Ruanda',               'RW', AF, False),
    ('Senegal',             'Senegāla',             'SN', AF, False),
    ('Sierra Leone',        'Sjerraleone',          'SL', AF, False),
    ('Somalia',             'Somālija',             'SO', AF, False),
    ('South Africa',        'Dienvidāfrika',        'ZA', AF, False),
    ('Sudan',               'Sudāna',               'SD', AF, False),
    ('Tanzania',            'Tanzānija',            'TZ', AF, False),
    ('Tunisia',             'Tunisija',             'TN', AF, False),
    ('Uganda',              'Uganda',               'UG', AF, False),
    ('Zambia',              'Zambija',              'ZM', AF, False),
    ('Zimbabwe',            'Zimbabve',             'ZW', AF, False),
    # Ziemeļamerika
    ('Bahamas',             'Bahamas',              'BS', NA, False),
    ('Barbados',            'Barbadosa',            'BB', NA, False),
    ('Belize',              'Beliza',               'BZ', NA, False),
    ('Canada',              'Kanāda',               'CA', NA, False),
    ('Costa Rica',          'Kostarika',            'CR', NA, False),
    ('Cuba',                'Kuba',                 'CU', NA, False),
    ('Dominican Republic',  'Dominikānas Republika','DO', NA, False),
    ('El Salvador',         'Salvadora',            'SV', NA, False),
    ('Guatemala',           'Gvatemala',            'GT', NA, False),
    ('Haiti',               'Haiti',                'HT', NA, False),
    ('Honduras',            'Hondurasa',            'HN', NA, False),
    ('Jamaica',             'Jamaika',              'JM', NA, False),
    ('Mexico',              'Meksika',              'MX', NA, False),
    ('Nicaragua',           'Nikaragva',            'NI', NA, False),
    ('Panama',              'Panama',               'PA', NA, False),
    ('Trinidad and Tobago', 'Trinidāda un Tobāgo',  'TT', NA, False),
    ('United States',       'ASV',                  'US', NA, False),
    # Dienvidamerika
    ('Argentina',           'Argentīna',            'AR', SA, False),
    ('Bolivia',             'Bolīvija',             'BO', SA, False),
    ('Brazil',              'Brazīlija',            'BR', SA, False),
    ('Chile',               'Čīle',                 'CL', SA, False),
    ('Colombia',            'Kolumbija',            'CO', SA, False),
    ('Ecuador',             'Ekvadora',             'EC', SA, False),
    ('Guyana',              'Gajāna',               'GY', SA, False),
    ('Paraguay',            'Paragvaja',            'PY', SA, False),
    ('Peru',                'Peru',                 'PE', SA, False),
    ('Uruguay',             'Urugvaja',             'UY', SA, False),
    ('Venezuela',           'Venecuēla',            'VE', SA, False),
    # Austrālija un Okeānija
    ('Australia',           'Austrālija',           'AU', OC, False),
    ('Fiji',                'Fidži',                'FJ', OC, False),
    ('Kiribati',            'Kiribati',             'KI', OC, False),
    ('Marshall Islands',    'Māršala salas',        'MH', OC, False),
    ('Nauru',               'Nauru',                'NR', OC, False),
    ('New Zealand',         'Jaunzēlande',          'NZ', OC, False),
    ('Palau',               'Palau',                'PW', OC, False),
    ('Papua New Guinea',    'Papua Jaungineja',     'PG', OC, False),
    ('Samoa',               'Samoa',                'WS', OC, False),
    ('Solomon Islands',     'Zālamana salas',       'SB', OC, False),
    ('Tonga',               'Tonga',                'TO', OC, False),
    ('Tuvalu',              'Tuvalu',               'TV', OC, False),
    ('Vanuatu',             'Vanuatu',              'VU', OC, False),
    # Izmirušās valstis
    ('Soviet Union',        'Padomju Savienība',    'SU', EU, True),
    ('Yugoslavia',          'Dienvidslāvija',       'YU', EU, True),
    ('Czechoslovakia',      'Čehoslovākija',        'CS', EU, True),
    ('East Germany',        'VDR (Austrumvācija)',  'DD', EU, True),
    ('Prussia',             'Prūsija',              'PU', EU, True),
    ('Ottoman Empire',      'Osmaņu impērija',      'OT', AS, True),
    ('Austro-Hungary',      'Austro-Ungārija',      'AH', EU, True),
    ('Roman Empire',        'Romas impērija',       'RM', EU, True),
    ('Byzantine Empire',    'Bizantijas impērija',  'BZ', EU, True),
]

added = 0
skipped = 0
for name, name_lv, code, cont_id, is_ext in countries:
    cur.execute('SELECT id FROM countries WHERE code=? OR (name=? AND continent_id=?)', (code, name, cont_id))
    row = cur.fetchone()
    if row:
        # Atjaunot ja jau ir
        cur.execute('UPDATE countries SET name=?, name_lv=?, code=?, continent_id=?, is_extinct=? WHERE id=?',
                    (name, name_lv, code, cont_id, is_ext, row[0]))
        skipped += 1
    else:
        cur.execute('INSERT INTO countries (name, name_lv, code, continent_id, is_extinct) VALUES (?,?,?,?,?)',
                    (name, name_lv, code, cont_id, is_ext))
        added += 1

conn.commit()
cur.execute('SELECT COUNT(*) FROM countries')
total = cur.fetchone()[0]
print(f'Pievienotas: {added}, Atjaunotas: {skipped}, Kopā: {total}')
conn.close()
print('Pabeigts!')
