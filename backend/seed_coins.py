#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed script: Euro coins (all Eurozone countries) + Latvian historical coins + USSR coins.
Run from backend directory: python seed_coins.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import asyncio
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, or_
from app.models.catalog import Country, Period, CatalogItem, SectionType

DATABASE_URL = "sqlite+aiosqlite:///./kolekcija.db"
engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ── Euro coin specifications (common reverse: map of Europe) ──────────────────
EURO_SPECS = [
    {"denom": "1 cent",  "mat": "Copper-plated steel",                       "dia": "16.25", "wt": "2.30"},
    {"denom": "2 cent",  "mat": "Copper-plated steel",                       "dia": "18.75", "wt": "3.06"},
    {"denom": "5 cent",  "mat": "Copper-plated steel",                       "dia": "21.25", "wt": "3.92"},
    {"denom": "10 cent", "mat": "Nordic gold",                               "dia": "19.75", "wt": "4.10"},
    {"denom": "20 cent", "mat": "Nordic gold",                               "dia": "22.25", "wt": "5.74"},
    {"denom": "50 cent", "mat": "Nordic gold",                               "dia": "24.25", "wt": "7.80"},
    {"denom": "1 Euro",  "mat": "Bimetallic (nickel brass/cupronickel)",     "dia": "23.25", "wt": "7.50"},
    {"denom": "2 Euro",  "mat": "Bimetallic (cupronickel/nickel brass)",     "dia": "25.75", "wt": "8.50"},
]
EURO_REVERSE = "Map of Europe without borders, denomination in centre, surrounded by 12 EU stars."

# country English name → {euro_since, obverse per denom group, mint}
EUROZONE = {
    "Germany": {
        "since": 2002,
        "obs_small":  "Brandenburg Gate (Brandenburger Tor), Berlin. BUNDESREPUBLIK DEUTSCHLAND.",
        "obs_medium": "Brandenburg Gate. BUNDESREPUBLIK DEUTSCHLAND.",
        "obs_large":  "Federal Eagle (Bundesadler) surrounded by 12 EU stars. BUNDESREPUBLIK DEUTSCHLAND.",
        "mint": "Berlin (A), Munich (D), Stuttgart (F), Karlsruhe (G), Hamburg (J)",
        "km":   {"1 cent":"KM#207","2 cent":"KM#208","5 cent":"KM#209","10 cent":"KM#210",
                 "20 cent":"KM#211","50 cent":"KM#212","1 Euro":"KM#213","2 Euro":"KM#214"},
    },
    "France": {
        "since": 2002,
        "obs_small":  "Marianne sowing seeds (La Semeuse), RF.",
        "obs_medium": "Marianne face profile, RF.",
        "obs_large":  "1€: Tree of Life, Liberté Égalité Fraternité, RF. 2€: La Semeuse figure, RF.",
        "mint": "Monnaie de Paris",
        "km":   {"1 cent":"KM#1282","2 cent":"KM#1283","5 cent":"KM#1284","10 cent":"KM#1285",
                 "20 cent":"KM#1286","50 cent":"KM#1287","1 Euro":"KM#1288","2 Euro":"KM#1289"},
    },
    "Italy": {
        "since": 2002,
        "obs_small":  "Castel del Monte (Apulia). Repubblica Italiana.",
        "obs_medium": "Flavian Amphitheatre (Colosseum), Rome. Repubblica Italiana.",
        "obs_large":  "1€: Birth of Venus by Botticelli. 2€: Dante Alighieri portrait. Repubblica Italiana.",
        "mint": "Istituto Poligrafico e Zecca dello Stato, Rome",
        "km":   {"1 cent":"KM#210","2 cent":"KM#211","5 cent":"KM#212","10 cent":"KM#213",
                 "20 cent":"KM#214","50 cent":"KM#215","1 Euro":"KM#216","2 Euro":"KM#217"},
    },
    "Spain": {
        "since": 2002,
        "obs_small":  "Cathedral of Santiago de Compostela. España.",
        "obs_medium": "Cervantes with windmills. España.",
        "obs_large":  "King Juan Carlos I portrait. España.",
        "mint": "Real Casa de la Moneda, Madrid",
        "km":   {"1 cent":"KM#1040","2 cent":"KM#1041","5 cent":"KM#1042","10 cent":"KM#1043",
                 "20 cent":"KM#1044","50 cent":"KM#1045","1 Euro":"KM#1046","2 Euro":"KM#1047"},
    },
    "Netherlands": {
        "since": 2002,
        "obs_small":  "Portrait of Queen Beatrix, BEATRIX KONINGIN DER NEDERLANDEN.",
        "obs_medium": "Portrait of Queen Beatrix, BEATRIX KONINGIN DER NEDERLANDEN.",
        "obs_large":  "Portrait of Queen Beatrix, BEATRIX KONINGIN DER NEDERLANDEN.",
        "mint": "Royal Dutch Mint (Koninklijke Nederlandse Munt), Utrecht",
        "km":   {"1 cent":"KM#234","2 cent":"KM#235","5 cent":"KM#236","10 cent":"KM#237",
                 "20 cent":"KM#238","50 cent":"KM#239","1 Euro":"KM#240","2 Euro":"KM#241"},
    },
    "Belgium": {
        "since": 2002,
        "obs_small":  "Portrait of King Albert II, BELGIQUE BELGIE BELGIEN.",
        "obs_medium": "Portrait of King Albert II, BELGIQUE BELGIE BELGIEN.",
        "obs_large":  "Portrait of King Albert II, BELGIQUE BELGIE BELGIEN.",
        "mint": "Royal Mint of Belgium, Brussels",
        "km":   {"1 cent":"KM#224","2 cent":"KM#225","5 cent":"KM#226","10 cent":"KM#227",
                 "20 cent":"KM#228","50 cent":"KM#229","1 Euro":"KM#230","2 Euro":"KM#231"},
    },
    "Austria": {
        "since": 2002,
        "obs_small":  "Gentian flower (Enzian). ÖSTERREICH.",
        "obs_medium": "St. Stephen's Cathedral (Stephansdom), Vienna. ÖSTERREICH.",
        "obs_large":  "1€: Mozart portrait. 2€: Bertha von Suttner (peace Nobel laureate). ÖSTERREICH.",
        "mint": "Austrian Mint (Münze Österreich), Vienna",
        "km":   {"1 cent":"KM#3082","2 cent":"KM#3083","5 cent":"KM#3084","10 cent":"KM#3085",
                 "20 cent":"KM#3086","50 cent":"KM#3087","1 Euro":"KM#3088","2 Euro":"KM#3089"},
    },
    "Finland": {
        "since": 2002,
        "obs_small":  "Heraldic lion of Finland. SUOMI FINLAND.",
        "obs_medium": "Heraldic lion of Finland. SUOMI FINLAND.",
        "obs_large":  "1€: Flying whooper swans. 2€: Cloudberry plant. SUOMI FINLAND.",
        "mint": "Mint of Finland (Rahapaja), Vantaa",
        "km":   {"1 cent":"KM#98","2 cent":"KM#99","5 cent":"KM#100","10 cent":"KM#101",
                 "20 cent":"KM#102","50 cent":"KM#103","1 Euro":"KM#104","2 Euro":"KM#105"},
    },
    "Portugal": {
        "since": 2002,
        "obs_small":  "Royal seal of 1134, first coat of arms of Portugal. PORTUGAL.",
        "obs_medium": "Royal seal of 1144 with castle and shield. PORTUGAL.",
        "obs_large":  "Royal seal of 1144. PORTUGAL.",
        "mint": "Imprensa Nacional–Casa da Moeda, Lisbon",
        "km":   {"1 cent":"KM#740","2 cent":"KM#741","5 cent":"KM#742","10 cent":"KM#743",
                 "20 cent":"KM#744","50 cent":"KM#745","1 Euro":"KM#746","2 Euro":"KM#747"},
    },
    "Ireland": {
        "since": 2002,
        "obs_small":  "Celtic harp (Brian Boru's harp). ÉIRE.",
        "obs_medium": "Celtic harp. ÉIRE.",
        "obs_large":  "Celtic harp. ÉIRE.",
        "mint": "Central Bank of Ireland / Royal Mint",
        "km":   {"1 cent":"KM#32","2 cent":"KM#33","5 cent":"KM#34","10 cent":"KM#35",
                 "20 cent":"KM#36","50 cent":"KM#37","1 Euro":"KM#38","2 Euro":"KM#39"},
    },
    "Luxembourg": {
        "since": 2002,
        "obs_small":  "Portrait of Grand Duke Henri. LËTZEBUERG.",
        "obs_medium": "Portrait of Grand Duke Henri. LËTZEBUERG.",
        "obs_large":  "Portrait of Grand Duke Henri. LËTZEBUERG.",
        "mint": "Royal Dutch Mint, Utrecht (on behalf of Luxembourg)",
        "km":   {"1 cent":"KM#75","2 cent":"KM#76","5 cent":"KM#77","10 cent":"KM#78",
                 "20 cent":"KM#79","50 cent":"KM#80","1 Euro":"KM#81","2 Euro":"KM#82"},
    },
    "Greece": {
        "since": 2002,
        "obs_small":  "Athenian trireme (ancient warship). ΕΛΛΗΝΙΚΗ ΔΗΜΟΚΡΑΤΙΑ.",
        "obs_medium": "Modern clipper ship (corvette). ΕΛΛΗΝΙΚΗ ΔΗΜΟΚΡΑΤΙΑ.",
        "obs_large":  "1€: Athenian owl with olive branch. 2€: Europa riding the bull (ancient mosaic). ΕΛΛΗΝΙΚΗ ΔΗΜΟΚΡΑΤΙΑ.",
        "mint": "Bank of Greece Mint, Athens",
        "km":   {"1 cent":"KM#181","2 cent":"KM#182","5 cent":"KM#183","10 cent":"KM#184",
                 "20 cent":"KM#185","50 cent":"KM#186","1 Euro":"KM#187","2 Euro":"KM#188"},
    },
    "Slovenia": {
        "since": 2007,
        "obs_small":  "Triglav mountain, Slovenija.",
        "obs_medium": "Prince's stone (Knežji kamen) of Carinthia, Slovenija.",
        "obs_large":  "1€: Primož Trubar, father of Slovenian literature. 2€: Lipizzaner horse. Slovenija.",
        "mint": "Austrian Mint, Vienna",
        "km":   {"1 cent":"KM#68","2 cent":"KM#69","5 cent":"KM#70","10 cent":"KM#71",
                 "20 cent":"KM#72","50 cent":"KM#73","1 Euro":"KM#74","2 Euro":"KM#75"},
    },
    "Cyprus": {
        "since": 2008,
        "obs_small":  "Mouflon (wild mountain sheep, national animal). ΚΥΠΡΟΣ KIBRIS.",
        "obs_medium": "Kyrenia Ship (ancient merchant vessel). ΚΥΠΡΟΣ KIBRIS.",
        "obs_large":  "1€: Idol of Pomos (Chalcolithic statuette). 2€: Idol of Lemba. ΚΥΠΡΟΣ KIBRIS.",
        "mint": "Royal Dutch Mint, Utrecht",
        "km":   {"1 cent":"KM#78","2 cent":"KM#79","5 cent":"KM#80","10 cent":"KM#81",
                 "20 cent":"KM#82","50 cent":"KM#83","1 Euro":"KM#84","2 Euro":"KM#85"},
    },
    "Malta": {
        "since": 2008,
        "obs_small":  "Maltese Cross. MALTA.",
        "obs_medium": "Mnajdra Temples (Neolithic, UNESCO World Heritage). MALTA.",
        "obs_large":  "1€: Maltese Cross. 2€: Coat of Arms of Malta. MALTA.",
        "mint": "Royal Dutch Mint, Utrecht",
        "km":   {"1 cent":"KM#125","2 cent":"KM#126","5 cent":"KM#127","10 cent":"KM#128",
                 "20 cent":"KM#129","50 cent":"KM#130","1 Euro":"KM#131","2 Euro":"KM#132"},
    },
    "Slovakia": {
        "since": 2009,
        "obs_small":  "Kriváň mountain peak (Tatra). SLOVENSKO.",
        "obs_medium": "Bratislava Castle. SLOVENSKO.",
        "obs_large":  "1€: Cross on three hills (coat of arms). 2€: Coat of Arms of Slovakia. SLOVENSKO.",
        "mint": "State Mint of Slovakia, Kremnica",
        "km":   {"1 cent":"KM#95","2 cent":"KM#96","5 cent":"KM#97","10 cent":"KM#98",
                 "20 cent":"KM#99","50 cent":"KM#100","1 Euro":"KM#101","2 Euro":"KM#102"},
    },
    "Estonia": {
        "since": 2011,
        "obs_small":  "Map of Estonia with geographic outline. EESTI.",
        "obs_medium": "Map of Estonia with geographic outline. EESTI.",
        "obs_large":  "Map of Estonia with geographic outline. EESTI.",
        "mint": "Royal Dutch Mint / Finnish Mint",
        "km":   {"1 cent":"KM#61","2 cent":"KM#62","5 cent":"KM#63","10 cent":"KM#64",
                 "20 cent":"KM#65","50 cent":"KM#66","1 Euro":"KM#67","2 Euro":"KM#68"},
    },
    "Latvia": {
        "since": 2014,
        "obs_small":  "Latvian Maid (Latvijas Māriņa) with oak leaves. LATVIJA.",
        "obs_medium": "Latvian Maid with oak leaves. LATVIJA.",
        "obs_large":  "Latvian Maid with oak leaves. LATVIJA.",
        "mint": "Royal Dutch Mint, Utrecht / Lithuanian Mint",
        "km":   {"1 cent":"KM#150","2 cent":"KM#151","5 cent":"KM#152","10 cent":"KM#153",
                 "20 cent":"KM#154","50 cent":"KM#155","1 Euro":"KM#156","2 Euro":"KM#157"},
    },
    "Lithuania": {
        "since": 2015,
        "obs_small":  "Vytis (Knight on horseback), national coat of arms. LIETUVA.",
        "obs_medium": "Vytis. LIETUVA.",
        "obs_large":  "Vytis. LIETUVA.",
        "mint": "Lithuanian Mint (Lietuvos monetų kalykla), Vilnius",
        "km":   {"1 cent":"KM#205","2 cent":"KM#206","5 cent":"KM#207","10 cent":"KM#208",
                 "20 cent":"KM#209","50 cent":"KM#210","1 Euro":"KM#211","2 Euro":"KM#212"},
    },
    "Croatia": {
        "since": 2023,
        "obs_small":  "Marten (Kuna) on map of Croatia. HRVATSKA.",
        "obs_medium": "Nikola Tesla portrait. HRVATSKA.",
        "obs_large":  "1€: Map of Croatia. 2€: Map of Croatia with inscription. HRVATSKA.",
        "mint": "Croatian National Bank / Bavarian State Mint",
        "km":   {"1 cent":"KM#601","2 cent":"KM#602","5 cent":"KM#603","10 cent":"KM#604",
                 "20 cent":"KM#605","50 cent":"KM#606","1 Euro":"KM#607","2 Euro":"KM#608"},
    },
}

# ── Historical Latvian coins (Lats era 1922–1940) ─────────────────────────────
LV_LATS_COINS = [
    {"name": "1 Santīms", "year": "1922", "denom": "1 santīms",
     "mat": "Bronze", "dia": "17.00", "wt": "1.65", "km": "KM#1",
     "obs": "Stylized sun with rays above inscription LATVIJA.", "mintage": "10000000",
     "rev": "Value 1 SANTĪMS surrounded by a wreath of oak."},
    {"name": "2 Santīmi", "year": "1922", "denom": "2 santīmi",
     "mat": "Bronze", "dia": "19.00", "wt": "3.00", "km": "KM#2",
     "obs": "Stylized sun with rays. LATVIJA.", "mintage": "5000000",
     "rev": "Value 2 SANTĪMI surrounded by oak wreath."},
    {"name": "5 Santīmi", "year": "1922", "denom": "5 santīmi",
     "mat": "Bronze", "dia": "22.00", "wt": "3.50", "km": "KM#3",
     "obs": "Stylized sun. LATVIJA.", "mintage": "5000000",
     "rev": "Value 5 SANTĪMI."},
    {"name": "10 Santīmu", "year": "1922", "denom": "10 santīmu",
     "mat": "Nickel", "dia": "17.50", "wt": "2.70", "km": "KM#4",
     "obs": "Three stars above LATVIJA.", "mintage": "6000000",
     "rev": "Value 10 SANTĪMU and date, oak wreath."},
    {"name": "20 Santīmu", "year": "1922", "denom": "20 santīmu",
     "mat": "Nickel", "dia": "20.00", "wt": "4.00", "km": "KM#5",
     "obs": "Three stars above LATVIJA.", "mintage": "5000000",
     "rev": "Value 20 SANTĪMU and date, oak wreath."},
    {"name": "50 Santīmu", "year": "1922", "denom": "50 santīmu",
     "mat": "Nickel", "dia": "23.00", "wt": "5.00", "km": "KM#6",
     "obs": "Three stars above LATVIJA.", "mintage": "4000000",
     "rev": "Value 50 SANTĪMU and date, oak wreath."},
    {"name": "1 Lats", "year": "1924", "denom": "1 lats",
     "mat": "Silver 0.835", "dia": "23.00", "wt": "5.00", "km": "KM#7",
     "obs": "Female head (Latvian Maid) facing left, LATVIJA.", "mintage": "3000000",
     "rev": "Crowned national coat of arms, 1 LATS, oak wreath."},
    {"name": "2 Lati", "year": "1925", "denom": "2 lati",
     "mat": "Silver 0.835", "dia": "27.00", "wt": "10.00", "km": "KM#8",
     "obs": "Female head (Latvian Maid) facing left, LATVIJA.", "mintage": "2000000",
     "rev": "Crowned national coat of arms, 2 LATI, oak wreath."},
    {"name": "5 Lati", "year": "1929", "denom": "5 lati",
     "mat": "Silver 0.835", "dia": "37.00", "wt": "25.00", "km": "KM#9",
     "obs": "Female head (Latvian Maid) facing left, LATVIJA.", "mintage": "700000",
     "rev": "Crowned national coat of arms, 5 LATI, oak and laurel wreath."},
    {"name": "1 Lats (Salmon)", "year": "1938", "denom": "1 lats",
     "mat": "Silver 0.835", "dia": "23.00", "wt": "5.00", "km": "KM#11",
     "obs": "Atlantic salmon (Salmo salar) leaping. LATVIJA.", "mintage": "500000",
     "rev": "Crowned coat of arms, 1 LATS."},
    {"name": "1 Lats (Archer)", "year": "1929", "denom": "1 lats",
     "mat": "Silver 0.835", "dia": "23.00", "wt": "5.00", "km": "KM#12",
     "obs": "Latvian archer (Latvju strēlnieks). LATVIJA.", "mintage": "1000000",
     "rev": "Crowned coat of arms, 1 LATS."},
]

# ── Latvian Second Republic coins (1992–2013) ─────────────────────────────────
LV_REPUBLIC_COINS = [
    {"name": "1 Santīms (Republic)", "year": "1992", "denom": "1 santīms",
     "mat": "Copper-plated steel", "dia": "15.65", "wt": "1.60", "km": "KM#15",
     "obs": "Latvian coat of arms (sun rising over sea). LATVIJAS REPUBLIKA.", "mintage": "50000000",
     "rev": "Value 1 SANTĪMS and year."},
    {"name": "2 Santīmi (Republic)", "year": "1992", "denom": "2 santīmi",
     "mat": "Copper-plated steel", "dia": "17.00", "wt": "2.00", "km": "KM#16",
     "obs": "Latvian coat of arms. LATVIJAS REPUBLIKA.", "mintage": "30000000",
     "rev": "Value 2 SANTĪMI and year."},
    {"name": "5 Santīmi (Republic)", "year": "1992", "denom": "5 santīmi",
     "mat": "Copper-plated steel", "dia": "18.50", "wt": "2.50", "km": "KM#17",
     "obs": "Latvian coat of arms. LATVIJAS REPUBLIKA.", "mintage": "30000000",
     "rev": "Value 5 SANTĪMI and year."},
    {"name": "10 Santīmu (Republic)", "year": "1992", "denom": "10 santīmu",
     "mat": "Copper-plated steel (later nickel-plated)", "dia": "17.00", "wt": "1.65", "km": "KM#18",
     "obs": "Latvian coat of arms. LATVIJAS REPUBLIKA.", "mintage": "40000000",
     "rev": "Value 10 SANTĪMU and year."},
    {"name": "20 Santīmu (Republic)", "year": "1992", "denom": "20 santīmu",
     "mat": "Nickel-plated steel", "dia": "18.50", "wt": "2.20", "km": "KM#19",
     "obs": "Latvian coat of arms. LATVIJAS REPUBLIKA.", "mintage": "30000000",
     "rev": "Value 20 SANTĪMU and year."},
    {"name": "50 Santīmu (Republic)", "year": "1992", "denom": "50 santīmu",
     "mat": "Copper-plated steel", "dia": "18.50", "wt": "1.85", "km": "KM#13",
     "obs": "Latvian coat of arms. LATVIJAS REPUBLIKA.", "mintage": "25000000",
     "rev": "Value 50 SANTĪMU and year."},
    {"name": "1 Lats (Republic)", "year": "1992", "denom": "1 lats",
     "mat": "Copper-nickel", "dia": "21.75", "wt": "4.80", "km": "KM#20",
     "obs": "Latvian coat of arms. LATVIJAS REPUBLIKA.", "mintage": "15000000",
     "rev": "Value 1 LATS and year."},
    {"name": "2 Lati (Republic)", "year": "1992", "denom": "2 lati",
     "mat": "Bimetallic (copper-nickel/brass)", "dia": "26.30", "wt": "6.25", "km": "KM#21",
     "obs": "Latvian coat of arms. LATVIJAS REPUBLIKA.", "mintage": "10000000",
     "rev": "Value 2 LATI and year."},
    {"name": "1 Lats (Pretzel)", "year": "2007", "denom": "1 lats",
     "mat": "Copper-nickel", "dia": "21.75", "wt": "4.80", "km": "KM#101",
     "obs": "Latvian pretzel (kliņģeris). LATVIJAS REPUBLIKA.", "mintage": "1000000",
     "rev": "Value 1 LATS and year.", "coin_cat": "commemorative"},
    {"name": "1 Lats (Snowflake)", "year": "2007", "denom": "1 lats",
     "mat": "Copper-nickel", "dia": "21.75", "wt": "4.80", "km": "KM#105",
     "obs": "Snowflake pattern. LATVIJAS REPUBLIKA.", "mintage": "1000000",
     "rev": "Value 1 LATS and year.", "coin_cat": "commemorative"},
    {"name": "1 Lats (Wagtail)", "year": "2002", "denom": "1 lats",
     "mat": "Copper-nickel", "dia": "21.75", "wt": "4.80", "km": "KM#55",
     "obs": "White wagtail (Motacilla alba), national bird of Latvia. LATVIJAS REPUBLIKA.", "mintage": "2000000",
     "rev": "Value 1 LATS and year.", "coin_cat": "commemorative"},
    {"name": "1 Lats (Mushroom)", "year": "2004", "denom": "1 lats",
     "mat": "Copper-nickel", "dia": "21.75", "wt": "4.80", "km": "KM#69",
     "obs": "Porcini mushroom (Boletus edulis). LATVIJAS REPUBLIKA.", "mintage": "1000000",
     "rev": "Value 1 LATS and year.", "coin_cat": "commemorative"},
    {"name": "1 Lats (Ant)", "year": "2003", "denom": "1 lats",
     "mat": "Copper-nickel", "dia": "21.75", "wt": "4.80", "km": "KM#63",
     "obs": "Wood ant (Formica rufa). LATVIJAS REPUBLIKA.", "mintage": "1000000",
     "rev": "Value 1 LATS and year.", "coin_cat": "commemorative"},
]

# ── USSR / Soviet coins ────────────────────────────────────────────────────────
USSR_COINS = [
    {"name": "1 Kopek", "year": "1961", "denom": "1 kopek",
     "mat": "Aluminium-bronze", "dia": "15.00", "wt": "1.00", "km": "KM#126a",
     "obs": "Soviet state emblem (hammer and sickle on globe, rays). СССР.", "mintage": "500000000",
     "rev": "Value 1 КОПЕЙКА, wheat sprigs, date."},
    {"name": "2 Kopeki", "year": "1961", "denom": "2 kopeki",
     "mat": "Brass", "dia": "18.00", "wt": "2.00", "km": "KM#127a",
     "obs": "Soviet state emblem. СССР.", "mintage": "300000000",
     "rev": "Value 2 КОПЕЙКИ, wheat sprigs."},
    {"name": "3 Kopeki", "year": "1961", "denom": "3 kopeki",
     "mat": "Brass", "dia": "22.00", "wt": "3.00", "km": "KM#128a",
     "obs": "Soviet state emblem. СССР.", "mintage": "400000000",
     "rev": "Value 3 КОПЕЙКИ, wheat sprigs."},
    {"name": "5 Kopeek", "year": "1961", "denom": "5 kopeek",
     "mat": "Brass", "dia": "25.00", "wt": "5.00", "km": "KM#129a",
     "obs": "Soviet state emblem. СССР.", "mintage": "600000000",
     "rev": "Value 5 КОПЕЕК, wheat sprigs."},
    {"name": "10 Kopeek", "year": "1961", "denom": "10 kopeek",
     "mat": "Copper-nickel", "dia": "17.27", "wt": "1.60", "km": "KM#130",
     "obs": "Soviet state emblem. СССР.", "mintage": "700000000",
     "rev": "Value 10 КОПЕЕК, wheat sprigs."},
    {"name": "15 Kopeek", "year": "1961", "denom": "15 kopeek",
     "mat": "Copper-nickel", "dia": "19.56", "wt": "2.50", "km": "KM#131",
     "obs": "Soviet state emblem. СССР.", "mintage": "500000000",
     "rev": "Value 15 КОПЕЕК, wheat sprigs."},
    {"name": "20 Kopeek", "year": "1961", "denom": "20 kopeek",
     "mat": "Copper-nickel", "dia": "21.80", "wt": "3.40", "km": "KM#132",
     "obs": "Soviet state emblem. СССР.", "mintage": "400000000",
     "rev": "Value 20 КОПЕЕК, wheat sprigs."},
    {"name": "50 Kopeek", "year": "1961", "denom": "50 kopeek",
     "mat": "Copper-nickel", "dia": "24.00", "wt": "4.40", "km": "KM#133a",
     "obs": "Soviet state emblem. СССР.", "mintage": "200000000",
     "rev": "Value 50 КОПЕЕК, wheat sprigs."},
    {"name": "1 Ruble", "year": "1961", "denom": "1 ruble",
     "mat": "Copper-nickel", "dia": "27.00", "wt": "7.50", "km": "KM#134a",
     "obs": "Soviet state emblem. СССР.", "mintage": "100000000",
     "rev": "Value 1 РУБЛЬ, wheat sprigs."},
    {"name": "1 Ruble (Lenin)", "year": "1970", "denom": "1 ruble",
     "mat": "Copper-nickel", "dia": "31.00", "wt": "12.80", "km": "KM#140",
     "obs": "Portrait of V.I. Lenin facing right. USSR.", "mintage": "60000000",
     "rev": "Soviet state emblem, 100 years since birth of Lenin.", "coin_cat": "commemorative"},
    {"name": "1 Ruble (Gagarin)", "year": "1981", "denom": "1 ruble",
     "mat": "Copper-nickel", "dia": "31.00", "wt": "12.80", "km": "KM#188",
     "obs": "Portrait of Yuri Gagarin, first cosmonaut. USSR.", "mintage": "3000000",
     "rev": "Soviet state emblem, 20th anniversary of first human spaceflight.", "coin_cat": "commemorative"},
    {"name": "1 Ruble (Moscow Olympics)", "year": "1977", "denom": "1 ruble",
     "mat": "Copper-nickel", "dia": "31.00", "wt": "12.80", "km": "KM#153",
     "obs": "Moscow 1980 Olympic logo. СССР.", "mintage": "4000000",
     "rev": "Soviet state emblem, XXII Olympiad.", "coin_cat": "commemorative"},
]

# ── German historical coins (West Germany, 1949-1990) ─────────────────────────
DE_MARK_COINS = [
    {"name": "1 Pfennig", "year": "1950", "denom": "1 Pfennig",
     "mat": "Copper-plated steel", "dia": "16.50", "wt": "2.00", "km": "KM#105",
     "obs": "Oak seedling with five leaves. BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "500000000",
     "rev": "Value 1 PFENNIG and date."},
    {"name": "2 Pfennig", "year": "1950", "denom": "2 Pfennig",
     "mat": "Copper-plated steel", "dia": "19.25", "wt": "3.25", "km": "KM#106",
     "obs": "Oak seedling. BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "300000000",
     "rev": "Value 2 PFENNIG and date."},
    {"name": "5 Pfennig", "year": "1950", "denom": "5 Pfennig",
     "mat": "Brass-plated steel", "dia": "18.50", "wt": "3.00", "km": "KM#107",
     "obs": "Oak seedling. BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "700000000",
     "rev": "Value 5 PFENNIG and date."},
    {"name": "10 Pfennig", "year": "1950", "denom": "10 Pfennig",
     "mat": "Brass-plated steel", "dia": "21.50", "wt": "4.00", "km": "KM#108",
     "obs": "Oak seedling. BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "800000000",
     "rev": "Value 10 PFENNIG and date."},
    {"name": "50 Pfennig", "year": "1950", "denom": "50 Pfennig",
     "mat": "Copper-nickel", "dia": "20.00", "wt": "3.50", "km": "KM#109",
     "obs": "Woman planting an oak sapling. BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "200000000",
     "rev": "Value 50 PFENNIG and date."},
    {"name": "1 Deutsche Mark", "year": "1950", "denom": "1 Deutsche Mark",
     "mat": "Copper-nickel", "dia": "23.50", "wt": "5.50", "km": "KM#110",
     "obs": "Federal Eagle (Bundesadler). BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "500000000",
     "rev": "Value 1 DEUTSCHE MARK and date, oak wreath."},
    {"name": "2 Deutsche Mark (Heuss)", "year": "1957", "denom": "2 Deutsche Mark",
     "mat": "Copper-nickel", "dia": "26.75", "wt": "7.00", "km": "KM#116",
     "obs": "Portrait of Theodor Heuss (first West German President). BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "100000000",
     "rev": "Federal Eagle, 2 DEUTSCHE MARK, date."},
    {"name": "5 Deutsche Mark", "year": "1951", "denom": "5 Deutsche Mark",
     "mat": "Silver 0.625", "dia": "29.00", "wt": "11.20", "km": "KM#112",
     "obs": "Federal Eagle. BUNDESREPUBLIK DEUTSCHLAND.", "mintage": "50000000",
     "rev": "Value 5 DEUTSCHE MARK and date, oak wreath."},
]

# ── US coins (classic) ────────────────────────────────────────────────────────
US_COINS = [
    {"name": "Lincoln Cent", "year": "1909", "denom": "1 cent",
     "mat": "Bronze (copper 95%)", "dia": "19.05", "wt": "3.11", "km": "KM#132",
     "obs": "Portrait of Abraham Lincoln facing right. IN GOD WE TRUST. LIBERTY.", "mintage": "72702618",
     "rev": "TWO WHEAT EARS, ONE CENT, UNITED STATES OF AMERICA, E PLURIBUS UNUM."},
    {"name": "Buffalo Nickel", "year": "1913", "denom": "5 cents",
     "mat": "Copper-nickel", "dia": "21.21", "wt": "5.00", "km": "KM#134",
     "obs": "Native American Indian chief in profile. LIBERTY.", "mintage": "30993520",
     "rev": "American bison (buffalo) standing. UNITED STATES OF AMERICA, FIVE CENTS."},
    {"name": "Mercury Dime", "year": "1916", "denom": "10 cents",
     "mat": "Silver 0.900", "dia": "17.91", "wt": "2.50", "km": "KM#140",
     "obs": "Winged Liberty Head (often mistaken for Mercury). LIBERTY, IN GOD WE TRUST.", "mintage": "22180080",
     "rev": "Fasces with olive branch. UNITED STATES OF AMERICA, ONE DIME."},
    {"name": "Morgan Silver Dollar", "year": "1878", "denom": "1 dollar",
     "mat": "Silver 0.900", "dia": "38.10", "wt": "26.73", "km": "KM#110",
     "obs": "Liberty head facing left with Phrygian cap. E PLURIBUS UNUM, LIBERTY.", "mintage": "10509550",
     "rev": "Heraldic eagle with arrows and olive branch. UNITED STATES OF AMERICA, ONE DOLLAR."},
    {"name": "Walking Liberty Half Dollar", "year": "1916", "denom": "50 cents",
     "mat": "Silver 0.900", "dia": "30.61", "wt": "12.50", "km": "KM#142",
     "obs": "Liberty walking towards sunrise, flag draped over shoulder. IN GOD WE TRUST, LIBERTY.", "mintage": "608000",
     "rev": "Bald eagle on rock. UNITED STATES OF AMERICA, HALF DOLLAR."},
]

# ── British coins ─────────────────────────────────────────────────────────────
UK_COINS = [
    {"name": "Penny (Elizabeth II)", "year": "1971", "denom": "1 penny",
     "mat": "Bronze", "dia": "20.32", "wt": "3.56", "km": "KM#915",
     "obs": "Portrait of Queen Elizabeth II facing right. ELIZABETH II DEI GRATIA REGINA FID DEF.", "mintage": "1521666250",
     "rev": "Portcullis with chains. ONE PENNY."},
    {"name": "Fifty Pence (Decimal)", "year": "1969", "denom": "50 pence",
     "mat": "Copper-nickel", "dia": "30.00", "wt": "13.50", "km": "KM#913",
     "obs": "Portrait of Queen Elizabeth II. ELIZABETH II DEI GRATIA REGINA.", "mintage": "188400000",
     "rev": "Britannia seated with shield and trident. FIFTY PENCE."},
    {"name": "One Pound Coin", "year": "1983", "denom": "1 pound",
     "mat": "Nickel-brass", "dia": "22.50", "wt": "9.50", "km": "KM#933",
     "obs": "Portrait of Queen Elizabeth II. ELIZABETH II DEI GRATIA REGINA.", "mintage": "443053510",
     "rev": "Royal Coat of Arms. ONE POUND."},
    {"name": "Two Pounds (Industrial Revolution)", "year": "1986", "denom": "2 pounds",
     "mat": "Bimetallic (nickel-brass/nickel)", "dia": "28.40", "wt": "12.00", "km": "KM#947",
     "obs": "Portrait of Queen Elizabeth II. ELIZABETH II DEI GRATIA REGINA.", "mintage": "8212184",
     "rev": "Rotating gears symbolising the Industrial Revolution. TWO POUNDS."},
    {"name": "Crown (Winston Churchill)", "year": "1965", "denom": "5 shillings (crown)",
     "mat": "Copper-nickel", "dia": "38.61", "wt": "28.28", "km": "KM#910",
     "obs": "Portrait of Queen Elizabeth II. ELIZABETH II DEI GRATIA REGINA.", "mintage": "19640000",
     "rev": "Portrait of Winston Churchill. CHURCHILL. IN MEMORIAM.", "coin_cat": "commemorative"},
]


async def find_period(db, country_name: str, section: str, year_hint: int | None = None) -> Period | None:
    """Find the best-matching period for a country/section/year."""
    r = await db.execute(select(Country).where(Country.name.ilike(country_name)))
    country = r.scalars().first()
    if not country:
        r = await db.execute(select(Country).where(Country.name.ilike(f"%{country_name}%")))
        country = r.scalars().first()
    if not country:
        return None

    q = select(Period).where(
        Period.country_id == country.id,
        Period.section == section,
    )
    r = await db.execute(q.order_by(Period.year_start.desc()))
    periods = r.scalars().all()
    if not periods:
        return None

    if year_hint:
        for p in periods:
            ys = p.year_start or 0
            ye = p.year_end or 9999
            if ys <= year_hint <= ye:
                return p

    return periods[0]  # fallback: latest period


async def coin_exists(db, period_id: int, denomination: str) -> bool:
    r = await db.execute(
        select(CatalogItem).where(
            CatalogItem.period_id == period_id,
            CatalogItem.denomination == denomination,
            CatalogItem.section == SectionType.coins,
        )
    )
    return r.scalars().first() is not None


async def add_coin(db, period: Period, name: str, year: str, denom: str,
                   mat: str, dia: str, wt: str, obs: str, rev: str,
                   mintage: str | None, km: str | None,
                   coin_cat: str = "circulation") -> bool:
    if await coin_exists(db, period.id, denom):
        return False
    item = CatalogItem(
        section=SectionType.coins,
        period_id=period.id,
        name=name,
        year=year,
        denomination=denom,
        material=mat,
        diameter_mm=dia,
        weight_g=wt,
        obverse_description=obs,
        reverse_description=rev,
        mintage=mintage,
        catalog_number=km,
        coin_category=coin_cat,
    )
    db.add(item)
    return True


async def seed():
    added = 0
    skipped = 0

    async with Session() as db:

        # ── 1. Euro coins ─────────────────────────────────────────────────────
        print("\n[EURO] Pievienoju Euro monetas...")
        for country_name, cd in EUROZONE.items():
            period = await find_period(db, country_name, "coins", cd["since"])
            if not period:
                print(f"  [!] {country_name}: periods nav atrasts, izlaizu")
                continue

            for spec in EURO_SPECS:
                d = spec["denom"]
                # Pick obverse text
                if d in ("1 cent", "2 cent", "5 cent"):
                    obs = cd["obs_small"]
                elif d in ("10 cent", "20 cent", "50 cent"):
                    obs = cd["obs_medium"]
                else:
                    obs = cd.get("obs_large", cd["obs_medium"])

                coin_name = f"{country_name} {d} Euro coin"
                year_str = str(cd["since"])
                km_no = cd.get("km", {}).get(d)

                ok = await add_coin(
                    db, period,
                    name=coin_name,
                    year=year_str,
                    denom=d,
                    mat=spec["mat"],
                    dia=spec["dia"],
                    wt=spec["wt"],
                    obs=obs,
                    rev=EURO_REVERSE,
                    mintage=None,
                    km=km_no,
                    coin_cat="circulation",
                )
                if ok:
                    added += 1
                else:
                    skipped += 1

            print(f"  [ok] {country_name} ({cd['since']}-) -> {len(EURO_SPECS)} denominations")

        await db.commit()

        # ── 2. Latvian Lats era (1922-1940) ──────────────────────────────────
        print("\n[LV] Pievienoju Latvijas Latu periods (1922-1940)...")
        period_lats = await find_period(db, "Latvia", "coins", 1930)
        if period_lats:
            for c in LV_LATS_COINS:
                ok = await add_coin(
                    db, period_lats,
                    name=c["name"], year=c["year"], denom=c["denom"],
                    mat=c["mat"], dia=c["dia"], wt=c["wt"],
                    obs=c["obs"], rev=c.get("rev", ""),
                    mintage=c.get("mintage"), km=c.get("km"),
                    coin_cat=c.get("coin_cat", "circulation"),
                )
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_LATS_COINS)} monetas")
        else:
            print("  [!] Latvia 1922-1940 periods nav atrasts")

        # ── 3. Latvian Second Republic (1992-2013) ────────────────────────────
        print("\n[LV] Pievienoju Latvijas Otra Republika (1992-2013)...")
        period_rep = await find_period(db, "Latvia", "coins", 2000)
        if period_rep:
            for c in LV_REPUBLIC_COINS:
                ok = await add_coin(
                    db, period_rep,
                    name=c["name"], year=c["year"], denom=c["denom"],
                    mat=c["mat"], dia=c["dia"], wt=c["wt"],
                    obs=c["obs"], rev=c.get("rev", ""),
                    mintage=c.get("mintage"), km=c.get("km"),
                    coin_cat=c.get("coin_cat", "circulation"),
                )
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_REPUBLIC_COINS)} monetas")
        else:
            print("  [!] Latvia 1992-2013 periods nav atrasts")

        # ── 4. USSR / Soviet coins ────────────────────────────────────────────
        print("\n[USSR] Pievienoju PSRS monetas...")
        period_ussr = await find_period(db, "Soviet Union", "coins", 1970)
        if not period_ussr:
            period_ussr = await find_period(db, "Russia", "coins", 1970)
        if period_ussr:
            for c in USSR_COINS:
                ok = await add_coin(
                    db, period_ussr,
                    name=c["name"], year=c["year"], denom=c["denom"],
                    mat=c["mat"], dia=c["dia"], wt=c["wt"],
                    obs=c["obs"], rev=c.get("rev", ""),
                    mintage=c.get("mintage"), km=c.get("km"),
                    coin_cat=c.get("coin_cat", "circulation"),
                )
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(USSR_COINS)} monetas")
        else:
            print("  [!] USSR/Russia periods nav atrasts")

        # ── 5. West Germany Deutsche Mark ─────────────────────────────────────
        print("\n[DE] Pievienoju Vacijas Deutschmark monetas...")
        period_dm = await find_period(db, "Germany", "coins", 1970)
        if period_dm:
            for c in DE_MARK_COINS:
                ok = await add_coin(
                    db, period_dm,
                    name=c["name"], year=c["year"], denom=c["denom"],
                    mat=c["mat"], dia=c["dia"], wt=c["wt"],
                    obs=c["obs"], rev=c.get("rev", ""),
                    mintage=c.get("mintage"), km=c.get("km"),
                )
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(DE_MARK_COINS)} monetas")
        else:
            print("  [!] Germany periods nav atrasts")

        # ── 6. US coins ────────────────────────────────────────────────────────
        print("\n[US] Pievienoju ASV klasiskas monetas...")
        period_us = await find_period(db, "United States", "coins", 1950)
        if not period_us:
            period_us = await find_period(db, "USA", "coins", 1950)
        if period_us:
            for c in US_COINS:
                ok = await add_coin(
                    db, period_us,
                    name=c["name"], year=c["year"], denom=c["denom"],
                    mat=c["mat"], dia=c["dia"], wt=c["wt"],
                    obs=c["obs"], rev=c.get("rev", ""),
                    mintage=c.get("mintage"), km=c.get("km"),
                    coin_cat=c.get("coin_cat", "circulation"),
                )
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(US_COINS)} monetas")
        else:
            print("  [!] United States periods nav atrasts")

        # ── 7. British coins ───────────────────────────────────────────────────
        print("\n[UK] Pievienoju Lielbritanijas monetas...")
        period_uk = await find_period(db, "United Kingdom", "coins", 1970)
        if not period_uk:
            period_uk = await find_period(db, "Great Britain", "coins", 1970)
        if period_uk:
            for c in UK_COINS:
                ok = await add_coin(
                    db, period_uk,
                    name=c["name"], year=c["year"], denom=c["denom"],
                    mat=c["mat"], dia=c["dia"], wt=c["wt"],
                    obs=c["obs"], rev=c.get("rev", ""),
                    mintage=c.get("mintage"), km=c.get("km"),
                    coin_cat=c.get("coin_cat", "circulation"),
                )
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(UK_COINS)} monetas")
        else:
            print("  [!] United Kingdom periods nav atrasts")

    print(f"\n{'='*50}")
    print(f"PABEIGTS! Pievienots: {added}, izlaists (jau eksiste): {skipped}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(seed())
