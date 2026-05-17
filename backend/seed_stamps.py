#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed script: Stamps catalog — Latvian, Soviet, German, British, US, and classic world stamps.
Run from backend directory: python seed_stamps.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import asyncio
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.catalog import Country, Period, CatalogItem, SectionType

DATABASE_URL = "sqlite+aiosqlite:///./kolekcija.db"
engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ── Latvian First Republic stamps (1918–1940) ─────────────────────────────────
LV_FIRST_REPUBLIC_STAMPS = [
    {
        "name": "Pirmā Latvijas pastmarka — 5 kap.",
        "year": "1918",
        "cat_no": "Mi#1",
        "denom": "5 kapeiku",
        "mat": "Laid paper",
        "perf": "imperf",
        "color": "Carmine",
        "mint": "Rīgas Latviešu Biedrības spiestuve",
        "mintage": "approx. 500000",
        "obs": "Latvian coat of arms (rising sun, three stars, ox, griffin, lion) in oval frame. LATVIJA 5 KAPEIKU.",
        "desc": "First Latvian postage stamp, issued 18 December 1918 — just weeks after proclamation of independence. Printed on back of German military maps due to paper shortage. Imperforate. Michel #1.",
    },
    {
        "name": "Latvijas pastmarka — 10 kap.",
        "year": "1918",
        "cat_no": "Mi#2",
        "denom": "10 kapeiku",
        "mat": "Laid paper (German map backs)",
        "perf": "imperf",
        "color": "Blue",
        "mint": "Rīgas Latviešu Biedrības spiestuve",
        "mintage": "approx. 400000",
        "obs": "Latvian coat of arms in oval. LATVIJA 10 KAPEIKU.",
        "desc": "Second Latvian stamp, issued simultaneously with Mi#1 in December 1918. Printed on the reverse of captured German military topographic maps — a famous philatelic curiosity. Michel #2.",
    },
    {
        "name": "Latvijas pastmarka — 35 kap.",
        "year": "1918",
        "cat_no": "Mi#3",
        "denom": "35 kapeiku",
        "mat": "Laid paper",
        "perf": "imperf",
        "color": "Brown",
        "mint": "Rīgas Latviešu Biedrības spiestuve",
        "mintage": "approx. 300000",
        "obs": "Latvian coat of arms in oval. LATVIJA 35 KAPEIKU.",
        "desc": "Third Latvian stamp from the first 1918 issue. Map-back variety known. Michel #3.",
    },
    {
        "name": "Ģerbonis — 5 santīmi (perfed)",
        "year": "1919",
        "cat_no": "Mi#8",
        "denom": "5 santīmi",
        "mat": "Wove paper",
        "perf": "11.5",
        "color": "Red",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 2000000",
        "obs": "Latvian coat of arms in ornate oval frame. LATVIJA 5 SANT.",
        "desc": "Coat of Arms definitive series, first perforated issue. Currency changed from kopecks to santīmi in 1919. Michel #8.",
    },
    {
        "name": "Ģerbonis — 50 santīmi",
        "year": "1919",
        "cat_no": "Mi#12",
        "denom": "50 santīmi",
        "mat": "Wove paper",
        "perf": "11.5",
        "color": "Green and brown",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 1500000",
        "obs": "Larger Latvian coat of arms in ornate frame. LATVIJA 50 SANT.",
        "desc": "Higher value from the 1919 definitive coat of arms series. Michel #12.",
    },
    {
        "name": "Rīga — Rātslaukums 2 lati",
        "year": "1928",
        "cat_no": "Mi#131",
        "denom": "2 lati",
        "mat": "Chalk-surfaced paper",
        "perf": "10.5",
        "color": "Dark blue",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 500000",
        "obs": "View of Riga Town Hall Square (Rātslaukums) with baroque architecture. LATVIJA 2 LATI.",
        "desc": "Riga landscape series stamp showing the historic Town Hall Square. Issued for the 10th anniversary of the Latvian Republic. Michel #131.",
    },
    {
        "name": "Latvijas neatkarības 10 gadi — 6 santīmi",
        "year": "1928",
        "cat_no": "Mi#126",
        "denom": "6 santīmi",
        "mat": "Wove paper",
        "perf": "11.5",
        "color": "Rose carmine",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 1000000",
        "obs": "Allegorical figure of Latvia breaking chains. 1918–1928. LATVIJA.",
        "desc": "Commemorative stamp for the 10th anniversary of Latvian independence. Michel #126.",
    },
    {
        "name": "Ģenerālis Jānis Balodis — 10 santīmi",
        "year": "1934",
        "cat_no": "Mi#224",
        "denom": "10 santīmi",
        "mat": "Chalk-surfaced paper",
        "perf": "10",
        "color": "Green",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 800000",
        "obs": "Portrait of General Jānis Balodis (commander of Latvian army in Liberation War) in military uniform.",
        "desc": "Portrait series of Latvian military leaders. General Balodis led Latvia to victory in the Liberation War (1918-1920). Michel #224.",
    },
    {
        "name": "Prezidents Kārlis Ulmanis — 35 santīmi",
        "year": "1934",
        "cat_no": "Mi#230",
        "denom": "35 santīmi",
        "mat": "Chalk-surfaced paper",
        "perf": "10",
        "color": "Red-brown",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 600000",
        "obs": "Portrait of President Kārlis Ulmanis in civilian attire, facing right.",
        "desc": "Portrait stamp of President Kārlis Ulmanis, who led Latvia from 1934 as national leader (Tautas vadonis). Michel #230.",
    },
    {
        "name": "Latvijas ainava — Sigulda 20 santīmi",
        "year": "1933",
        "cat_no": "Mi#215",
        "denom": "20 santīmi",
        "mat": "Chalk-surfaced paper",
        "perf": "10.5",
        "color": "Blue-green",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 700000",
        "obs": "Panoramic view of Gauja River valley near Sigulda with medieval castle ruins and forests.",
        "desc": "Latvian landscape series. Sigulda and the Gauja River valley — Latvia's national park region known as the 'Switzerland of Latvia'. Michel #215.",
    },
    {
        "name": "Gaisa pasts — 10 santīmi",
        "year": "1921",
        "cat_no": "Mi#74",
        "denom": "10 santīmi",
        "mat": "Wove paper",
        "perf": "11.5",
        "color": "Blue and black",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 100000",
        "obs": "Biplane in flight over Latvian landscape. LATVIJA GAISA PASTS.",
        "desc": "First Latvian airmail stamp, overprinted for Riga-Königsberg airmail route (one of Europe's first regular airmail services). Michel #74. Scarce.",
    },
    {
        "name": "Palīdzības pastmarka — Bērni 2+2 santīmi",
        "year": "1938",
        "cat_no": "Mi#268",
        "denom": "2+2 santīmi",
        "mat": "Chalk-surfaced paper",
        "perf": "10",
        "color": "Green",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 400000",
        "obs": "Two Latvian children in traditional dress. LATVIJA 2+2 SANT.",
        "desc": "Semi-postal stamp with surcharge for child welfare. Part of a charity series. Michel #268.",
    },
    {
        "name": "Rīgas pilsēta — Doms 50 santīmi",
        "year": "1936",
        "cat_no": "Mi#248",
        "denom": "50 santīmi",
        "mat": "Chalk-surfaced paper",
        "perf": "10",
        "color": "Dark violet",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 300000",
        "obs": "Riga's Dome Cathedral (Dom Church) with distinctive gothic and baroque architecture. LATVIJA.",
        "desc": "Riga architecture series, featuring the iconic Dome Cathedral — Latvia's largest church, founded 1211. Michel #248.",
    },
    {
        "name": "Latvijas 20 gadi — 40 santīmi",
        "year": "1938",
        "cat_no": "Mi#270",
        "denom": "40 santīmi",
        "mat": "Chalk-surfaced paper",
        "perf": "10",
        "color": "Ultramarine",
        "mint": "Latvian State Printing House",
        "mintage": "approx. 500000",
        "obs": "Allegorical design showing Latvia's progress 1918–1938. Rising sun over map of Latvia. 1918 LATVIJA 1938.",
        "desc": "Commemorative stamp for the 20th anniversary of Latvian independence. One of the last large commemorative sets before Soviet occupation. Michel #270.",
    },
]

# ── Latvian Second Republic stamps (1991–present) ────────────────────────────
LV_REPUBLIC_STAMPS = [
    {
        "name": "Pirmā marka pēc neatkarības atjaunošanas — 10 kap.",
        "year": "1991",
        "cat_no": "Mi#316",
        "denom": "10 kapeiku",
        "mat": "Gummed paper",
        "perf": "12.5",
        "color": "Red and gold",
        "mint": "Goznak, Moscow (printing) / State Printing House of Latvia",
        "mintage": "approx. 1000000",
        "obs": "Latvian coat of arms with three stars and rising sun. LATVIJA.",
        "desc": "First Latvian postage stamp after restoration of independence (declared 4 May 1990). Coat of arms definitive. Michel #316.",
    },
    {
        "name": "Brīvības piemineklis — 15 santīmi",
        "year": "1992",
        "cat_no": "Mi#330",
        "denom": "15 santīmi",
        "mat": "Gummed paper",
        "perf": "13.5",
        "color": "Blue-green",
        "mint": "Finnish State Printing Centre (Setec)",
        "mintage": "approx. 2000000",
        "obs": "Freedom Monument (Brīvības piemineklis) in Riga — the woman Milda holding three stars. LATVIJA.",
        "desc": "Definitive stamp featuring Latvia's iconic Freedom Monument in Riga, built 1935. Inscription 'Tēvzemei un Brīvībai' (For Fatherland and Freedom). Michel #330.",
    },
    {
        "name": "Latvijas karogs — 5 santīmi",
        "year": "1992",
        "cat_no": "Mi#323",
        "denom": "5 santīmi",
        "mat": "Self-adhesive",
        "perf": "imperf",
        "color": "Dark red and white",
        "mint": "State Printing House of Latvia",
        "mintage": "approx. 5000000",
        "obs": "Latvian national flag (carmine red-white-carmine red horizontal stripes). LATVIJA 5 SANT.",
        "desc": "National flag definitive stamp. The distinctive dark red (carmine) of the Latvian flag — one of the oldest national flags in the world, first documented 1279. Michel #323.",
    },
    {
        "name": "Dziesmu svētki — 100 gadi",
        "year": "1998",
        "cat_no": "Mi#472",
        "denom": "10 santīmi",
        "mat": "Gummed paper",
        "perf": "13",
        "color": "Blue and gold",
        "mint": "Lithuanian State Printing House",
        "mintage": "approx. 600000",
        "obs": "Choir singers in traditional Latvian dress, Riga Song Festival grounds. LATVIJA. 100 gadi.",
        "desc": "Centenary of the Latvian Song and Dance Festival. The Latvian Song Festival (Dziesmu svētki) is a UNESCO Intangible Cultural Heritage tradition dating back to 1873. Michel #472.",
    },
    {
        "name": "Rīga — Eiropas kultūras galvaspilsēta 2014",
        "year": "2014",
        "cat_no": "Mi#880",
        "denom": "50 santīmi",
        "mat": "Gummed paper",
        "perf": "13.75x13",
        "color": "Multicolour",
        "mint": "State Printing House of Latvia",
        "mintage": "approx. 400000",
        "obs": "Riga cityscape with Art Nouveau buildings and Daugava River. RĪGA 2014. LATVIJA.",
        "desc": "Commemorating Riga as European Capital of Culture 2014. Riga has the largest concentration of Art Nouveau/Jugendstil architecture in the world. Michel #880.",
    },
    {
        "name": "Latvija NATO — 50 centi",
        "year": "2004",
        "cat_no": "Mi#604",
        "denom": "50 santimu",
        "mat": "Gummed paper",
        "perf": "13.25",
        "color": "Blue and gold",
        "mint": "State Printing House of Latvia",
        "mintage": "approx. 300000",
        "obs": "NATO compass rose with Latvian flag colors. LATVIJA NATO 2004.",
        "desc": "Commemorating Latvia's accession to NATO on 29 March 2004. Issued jointly with similar stamps from Estonia and Lithuania. Michel #604.",
    },
    {
        "name": "Latvijas dabas ainava — Gauja 22 centi",
        "year": "2010",
        "cat_no": "Mi#779",
        "denom": "22 santīmi",
        "mat": "Gummed paper",
        "perf": "13.75",
        "color": "Multicolour",
        "mint": "State Printing House of Latvia",
        "mintage": "approx. 500000",
        "obs": "Aerial view of Gauja River winding through Gauja National Park forests in autumn colors.",
        "desc": "Latvian nature series featuring the Gauja National Park — Latvia's oldest and largest national park, established 1973. Michel #779.",
    },
    {
        "name": "Lāčplēsis — nacionālais varonis 35 centi",
        "year": "2012",
        "cat_no": "Mi#826",
        "denom": "35 santīmi",
        "mat": "Gummed paper",
        "perf": "13.75x14",
        "color": "Multicolour",
        "mint": "State Printing House of Latvia",
        "mintage": "approx. 250000",
        "obs": "Illustration of Lāčplēsis the Bear-Slayer from the national epic poem by Andrejs Pumpurs. LATVIJA.",
        "desc": "Featuring Lāčplēsis — hero of the Latvian national epic and symbol of freedom. The annual Lāčplēsis Day (11 November) commemorates fighters for Latvian independence. Michel #826.",
    },
]

# ── USSR / Soviet stamps ───────────────────────────────────────────────────────
USSR_STAMPS = [
    {
        "name": "Ļeņins — standarta marka 1 kap.",
        "year": "1961",
        "cat_no": "Mi#2369",
        "denom": "1 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12.5",
        "color": "Orange",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 100000000",
        "obs": "Portrait of V.I. Lenin facing left. ПОЧТА СССР 1 коп.",
        "desc": "Standard definitive series stamp featuring Lenin portrait. Part of the long-running Lenin definitive series used throughout the Soviet era. Michel #2369.",
    },
    {
        "name": "Sputnik-1 — kosmosa pastmarka",
        "year": "1957",
        "cat_no": "Mi#2013",
        "denom": "40 kopek",
        "mat": "Wove paper",
        "perf": "12",
        "color": "Blue and silver",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 5000000",
        "obs": "Sputnik-1 satellite orbiting Earth against starry background. ПЕРВЫЙ ИСКУССТВЕННЫЙ СПУТНИК ЗЕМЛИ. ПОЧТА СССР.",
        "desc": "Issued to commemorate Sputnik-1, the world's first artificial satellite launched 4 October 1957. One of the most recognizable Soviet space stamps. Michel #2013.",
    },
    {
        "name": "Jurijs Gagarins — kosmonauts",
        "year": "1961",
        "cat_no": "Mi#2462",
        "denom": "6 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12.5",
        "color": "Blue and red",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 20000000",
        "obs": "Portrait of cosmonaut Yuri Gagarin in space helmet. Vostok spacecraft in background. 12.IV.1961. ПОЧТА СССР.",
        "desc": "Commemorating Yuri Gagarin's historic first human spaceflight on 12 April 1961. Issued within days of the flight. One of the most collected Soviet stamps worldwide. Michel #2462.",
    },
    {
        "name": "Lunohods-1 uz Mēness",
        "year": "1971",
        "cat_no": "Mi#3923",
        "denom": "10 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12x11.5",
        "color": "Multicolour",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 8000000",
        "obs": "Lunokhod-1 lunar rover on the Moon's surface. Earth visible in background. ЛУНОХОД-1. ПОЧТА СССР.",
        "desc": "Lunokhod-1 — the first robotic lunar rover, landed on Moon 17 November 1970. Operated for 11 months, travelling 10.5 km on the lunar surface. Michel #3923.",
    },
    {
        "name": "Maskava — 1980. gada Olimpiskie spēles",
        "year": "1980",
        "cat_no": "Mi#4943",
        "denom": "10 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12",
        "color": "Multicolour",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 10000000",
        "obs": "Olympic Misha bear mascot with Olympic rings. МОСКВА 1980. ПОЧТА СССР.",
        "desc": "Moscow 1980 Summer Olympics stamp featuring the famous Misha bear mascot designed by Viktor Chizhikov. The games were boycotted by USA and Western allies due to Soviet invasion of Afghanistan. Michel #4943.",
    },
    {
        "name": "Ļeņina 100. dzimšanas diena — bloks",
        "year": "1970",
        "cat_no": "Mi#3763",
        "denom": "50 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12.5",
        "color": "Red and gold",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 3000000",
        "obs": "Large portrait of Lenin. Red flag and crowd in background. 1870–1970. ПОЧТА СССР.",
        "desc": "Commemorating the 100th anniversary of Lenin's birth. Central stamp in a large souvenir sheet. Michel #3763.",
    },
    {
        "name": "Krievijas māksla — Ermitāža 4 kap.",
        "year": "1965",
        "cat_no": "Mi#3069",
        "denom": "4 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12x12.5",
        "color": "Multicolour",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 6000000",
        "obs": "Painting 'Madonna Litta' by Leonardo da Vinci from Hermitage Museum collection. ПОЧТА СССР.",
        "desc": "Soviet art series featuring masterpieces from the Hermitage Museum in Leningrad. The Hermitage houses one of the world's largest art collections. Michel #3069.",
    },
    {
        "name": "Uzvaras diena — 9. maijs 4 kap.",
        "year": "1965",
        "cat_no": "Mi#3041",
        "denom": "4 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12",
        "color": "Red and black",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 15000000",
        "obs": "Soviet soldier with Victory flag at Berlin's Reichstag. Fireworks. 9 МАЯ — ДЕНЬ ПОБЕДЫ. ПОЧТА СССР.",
        "desc": "20th anniversary of Victory in WWII. Soviet Victory Day (9 May) commemorates the surrender of Nazi Germany. Michel #3041.",
    },
    {
        "name": "Latvijas PSR — Rīgas panorāma 10 kap.",
        "year": "1960",
        "cat_no": "Mi#2399",
        "denom": "10 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12.5",
        "color": "Blue and brown",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 4000000",
        "obs": "Riga skyline with Daugava River, showing Riga Castle, St. Peter's Church spire. LATVIJSKAJA SSR. ПОЧТА СССР.",
        "desc": "Soviet Republics capitals series featuring Riga, capital of the Latvian Soviet Socialist Republic. Michel #2399.",
    },
    {
        "name": "PSRS Kosmosa programma — Valentīna Tereškova",
        "year": "1963",
        "cat_no": "Mi#2779",
        "denom": "6 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "11.5",
        "color": "Blue and carmine",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 12000000",
        "obs": "Portrait of Valentina Tereshkova in space helmet. Vostok-6 capsule. 16–19.VI.1963. ПОЧТА СССР.",
        "desc": "Valentina Tereshkova — first woman in space, aboard Vostok-6 on 16 June 1963. She remains the only woman to have completed a solo space mission. Michel #2779.",
    },
    {
        "name": "Ziemeļu polus ekspedīcija — 40 kap.",
        "year": "1948",
        "cat_no": "Mi#1222",
        "denom": "40 kopek",
        "mat": "Chalk-surfaced paper",
        "perf": "12.5",
        "color": "Blue and black",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 2000000",
        "obs": "Soviet icebreaker ship in Arctic ice. Polar bear on ice floe. СЕВЕРНЫЙ ПОЛЮС. ПОЧТА СССР.",
        "desc": "Arctic exploration series commemorating Soviet polar expeditions. The USSR was a pioneer of Arctic exploration and the first to establish a permanent drifting research station at the North Pole. Michel #1222.",
    },
    {
        "name": "Maskavas metro 10 kap.",
        "year": "1935",
        "cat_no": "Mi#484",
        "denom": "10 kopek",
        "mat": "Wove paper",
        "perf": "11",
        "color": "Red and black",
        "mint": "Goznak, Moscow",
        "mintage": "approx. 3000000",
        "obs": "Worker and Moscow Metro entrance arch. Red star at top. МЕТРО. ПОЧТА СССР.",
        "desc": "Commemorating the opening of Moscow Metro on 15 May 1935. The Moscow Metro is famous for its ornate Stalin-era stations, often called 'underground palaces'. Michel #484.",
    },
]

# ── German stamps ─────────────────────────────────────────────────────────────
DE_STAMPS = [
    {
        "name": "Hindenburg — Vikboldas (Weimarer Republik) 5 Pf",
        "year": "1932",
        "cat_no": "Mi#469",
        "denom": "5 Pfennig",
        "mat": "Chalk-surfaced paper",
        "perf": "14",
        "color": "Yellow-green",
        "mint": "Reichsdruckerei, Berlin",
        "mintage": "approx. 50000000",
        "obs": "Profile portrait of President Paul von Hindenburg facing right. DEUTSCHES REICH 5.",
        "desc": "Hindenburg definitive series of the Weimar Republic. Paul von Hindenburg was German President 1925–1934. This design continued into the early Nazi period. Michel #469.",
    },
    {
        "name": "Ādolfs Hitlers — standarta marka 6+4 Pf",
        "year": "1941",
        "cat_no": "Mi#781",
        "denom": "6+4 Pfennig",
        "mat": "Chalk-surfaced paper",
        "perf": "14",
        "color": "Brown-red",
        "mint": "Reichsdruckerei, Berlin",
        "mintage": "approx. 80000000",
        "obs": "Profile portrait of Adolf Hitler facing right. DEUTSCHES REICH 6+4.",
        "desc": "Standard Nazi-era definitive stamp. The Hitler portrait definitives were the most common German stamps of 1941–1944. Historically significant collectible. Michel #781.",
    },
    {
        "name": "Trešais Reihs — Olimpiskās spēles Berlīne 15+10 Pf",
        "year": "1936",
        "cat_no": "Mi#615",
        "denom": "15+10 Pfennig",
        "mat": "Chalk-surfaced paper",
        "perf": "13.5",
        "color": "Brown-red",
        "mint": "Reichsdruckerei, Berlin",
        "mintage": "approx. 10000000",
        "obs": "Brandenburg Gate with Olympic rings. Athlete carrying torch. DEUTSCHES REICH. 1936.",
        "desc": "Berlin 1936 Summer Olympics semi-postal stamp. The 1936 Olympics were used extensively for Nazi propaganda. Jesse Owens famously won 4 gold medals. Michel #615.",
    },
    {
        "name": "VFR — Zināmnieks Konrads Adenauers 80 Pf",
        "year": "1968",
        "cat_no": "Mi#552",
        "denom": "80 Pfennig",
        "mat": "Chalk-surfaced paper",
        "perf": "14",
        "color": "Black",
        "mint": "Bundesdruckerei, Berlin",
        "mintage": "approx. 6000000",
        "obs": "Portrait of Chancellor Konrad Adenauer (1876–1967). DEUTSCHE BUNDESPOST.",
        "desc": "Memorial stamp for Konrad Adenauer, West Germany's first chancellor (1949–1963), who guided West Germany's post-war recovery and European integration. Michel #552.",
    },
    {
        "name": "VFR — Braniborgas vārti 100 Pf",
        "year": "1987",
        "cat_no": "Mi#1341",
        "denom": "100 Pfennig",
        "mat": "Chalk-surfaced paper",
        "perf": "14",
        "color": "Deep blue",
        "mint": "Bundesdruckerei, Berlin",
        "mintage": "approx. 15000000",
        "obs": "Brandenburg Gate (Brandenburger Tor) with Berlin Wall visible in foreground. DEUTSCHE BUNDESPOST BERLIN.",
        "desc": "High-value definitive stamp from West Berlin. The Brandenburg Gate was the most powerful symbol of German division during the Cold War, standing in the no-man's land of the Berlin Wall. Michel #1341.",
    },
    {
        "name": "VFR — Berlīnes mūra krišana 100 Pf",
        "year": "1990",
        "cat_no": "Mi#1477",
        "denom": "100 Pfennig",
        "mat": "Chalk-surfaced paper",
        "perf": "14",
        "color": "Multicolour",
        "mint": "Bundesdruckerei, Berlin",
        "mintage": "approx. 20000000",
        "obs": "Citizens celebrating at the Berlin Wall being demolished. Brandenburg Gate visible. 9.11.1989. DEUTSCHE BUNDESPOST.",
        "desc": "Commemorating the fall of the Berlin Wall on 9 November 1989 — one of the most momentous events of the 20th century. German reunification followed on 3 October 1990. Michel #1477.",
    },
    {
        "name": "NDR — Staļins 84 Pf",
        "year": "1953",
        "cat_no": "Mi#DDR#383",
        "denom": "84 Pfennig",
        "mat": "Wove paper",
        "perf": "13.5",
        "color": "Brown",
        "mint": "East German printing house",
        "mintage": "approx. 2000000",
        "obs": "Portrait of Josef Stalin facing left. DEUTSCHE DEMOKRATISCHE REPUBLIK.",
        "desc": "East German (DDR) memorial stamp for Josef Stalin who died 5 March 1953. East Germany had close ties with the Soviet Union and issued Stalin tribute stamps. Michel DDR#383.",
    },
]

# ── British stamps ─────────────────────────────────────────────────────────────
UK_STAMPS = [
    {
        "name": "Penny Black — pirmā pasaules pastmarka",
        "year": "1840",
        "cat_no": "SG#1",
        "denom": "1 penny",
        "mat": "Hand-made wove paper",
        "perf": "imperf",
        "color": "Black",
        "mint": "Perkins Bacon & Co., London",
        "mintage": "approx. 68158080",
        "obs": "Profile portrait of young Queen Victoria facing left in oval medallion. POSTAGE. ONE PENNY. Corner letters A-A through T-L.",
        "desc": "The world's first adhesive postage stamp, issued 1 May 1840. Designed by Henry Corbould based on a medal by William Wyon. The black ink was changed to brown-red (Penny Red) in 1841 due to cancellation visibility issues. Stanley Gibbons #1. Among the most famous stamps in the world.",
    },
    {
        "name": "Penny Red (perforated)",
        "year": "1858",
        "cat_no": "SG#43",
        "denom": "1 penny",
        "mat": "Wove paper",
        "perf": "14",
        "color": "Red",
        "mint": "Perkins Bacon & Co., London",
        "mintage": "approx. 21 billion (1841–1879)",
        "obs": "Profile portrait of Queen Victoria. POSTAGE. ONE PENNY. Plate number visible in corner letters.",
        "desc": "The Penny Red replaced the Penny Black in 1841. Perforated version from 1858 with plate numbers — plate 77 being extremely rare. The most used stamp design in history. Stanley Gibbons #43.",
    },
    {
        "name": "Two Penny Blue",
        "year": "1840",
        "cat_no": "SG#5",
        "denom": "2 pence",
        "mat": "Hand-made wove paper",
        "perf": "imperf",
        "color": "Pale blue",
        "mint": "Perkins Bacon & Co., London",
        "mintage": "approx. 6404880",
        "obs": "Profile portrait of young Queen Victoria. POSTAGE. TWO PENCE. White corner letters.",
        "desc": "Issued simultaneously with the Penny Black on 6 May 1840 for double-weight letters. Less famous than the Penny Black but equally historic as the second adhesive postage stamp. Stanley Gibbons #5.",
    },
    {
        "name": "Lielbritānija — Ēdvards VII 1 šiliņš",
        "year": "1902",
        "cat_no": "SG#257",
        "denom": "1 shilling",
        "mat": "Chalk-surfaced paper",
        "perf": "14",
        "color": "Dull green",
        "mint": "De La Rue, London",
        "mintage": "approx. 5000000",
        "obs": "Profile portrait of King Edward VII facing right. POSTAGE. ONE SHILLING.",
        "desc": "Edward VII definitive series — the first British stamps after Queen Victoria's 64-year reign. Edward VII was king 1901–1910. Stanley Gibbons #257.",
    },
    {
        "name": "Džordžs V — 'Sea Horses' 2 šiliņi 6 pensi",
        "year": "1913",
        "cat_no": "SG#400",
        "denom": "2 shillings 6 pence",
        "mat": "Thick paper",
        "perf": "11x12",
        "color": "Brown",
        "mint": "Waterlow & Sons, London",
        "mintage": "approx. 1000000",
        "obs": "Britannia riding two sea horses (hippocampi). Britannia figure wearing helmet, holding shield. POSTAGE REVENUE.",
        "desc": "'Sea Horses' high-value definitives — among the most elegant British stamps ever issued. Named after the mythological sea-horse design by Bertram Mackennal. Used for heavy mail. Stanley Gibbons #400.",
    },
    {
        "name": "Elizabete II — standarta marka 3 pensi",
        "year": "1952",
        "cat_no": "SG#519",
        "denom": "3 pence",
        "mat": "Chalk-surfaced paper",
        "perf": "14.75x14",
        "color": "Deep lilac",
        "mint": "Harrison & Sons, London",
        "mintage": "approx. 200000000",
        "obs": "Portrait of Queen Elizabeth II in oval by Dorothy Wilding. POSTAGE REVENUE. 3D.",
        "desc": "First Elizabeth II definitive series issued after her coronation (June 1953). The Wilding portrait was used 1952–1967. Stanley Gibbons #519.",
    },
    {
        "name": "Pirmā klase — Elizabete II (Machins)",
        "year": "1967",
        "cat_no": "SG#U1",
        "denom": "1st class",
        "mat": "Phosphor-coated paper",
        "perf": "15x14",
        "color": "Orange-red",
        "mint": "De La Rue / Harrison, London",
        "mintage": "approx. 20 billion (ongoing)",
        "obs": "Sculpted profile portrait of Queen Elizabeth II by Arnold Machin, without country name (UK does not name itself on stamps — oldest postal service).",
        "desc": "Machin definitive series — the most collected stamp series in history, with over 400 variations since 1967. The simple Machin portrait has appeared on more stamps than any other design. No country name used — a unique Royal Mail tradition since 1840. Stanley Gibbons #U1.",
    },
    {
        "name": "Titāniks — katastrofas 100 gadi",
        "year": "2012",
        "cat_no": "SG#3239",
        "denom": "1st class",
        "mat": "Gummed paper",
        "perf": "14.5x14",
        "color": "Blue and black",
        "mint": "De La Rue, Dunstable",
        "mintage": "approx. 2000000",
        "obs": "RMS Titanic at sea, lifeboats being lowered. TITANIC 100 YEARS. ROYAL MAIL 1ST.",
        "desc": "Centenary of the sinking of RMS Titanic (15 April 1912). One of the 20th century's most famous disasters — 1,514 lives lost. Part of a miniature sheet of 4 stamps. Stanley Gibbons #3239.",
    },
]

# ── US stamps ──────────────────────────────────────────────────────────────────
US_STAMPS = [
    {
        "name": "Inverted Jenny — lidmašīna ar kļūdu",
        "year": "1918",
        "cat_no": "Scott#C3a",
        "denom": "24 cents",
        "mat": "Flat plate, wove paper",
        "perf": "11",
        "color": "Carmine and blue",
        "mint": "Bureau of Engraving and Printing, Washington",
        "mintage": "100 (error sheet)",
        "obs": "Curtiss JN-4 'Jenny' biplane printed upside-down (error) in blue. Carmine border. UNITED STATES POSTAGE 24 CENTS.",
        "desc": "The 'Inverted Jenny' — the most famous stamp error in US philatelic history. An entire sheet of 100 stamps was accidentally printed with the airplane inverted. William Robey purchased the only known error sheet in 1918. Now worth over $1 million per stamp. Scott #C3a.",
    },
    {
        "name": "Kolumba atklājumi — 1 dolārs",
        "year": "1893",
        "cat_no": "Scott#241",
        "denom": "1 dollar",
        "mat": "Wove paper",
        "perf": "12",
        "color": "Salmon red",
        "mint": "American Bank Note Company",
        "mintage": "approx. 55050",
        "obs": "Isabella pledges her jewels scene (Queen Isabella offering jewelry to Columbus to fund the voyage). UNITED STATES OF AMERICA. ONE DOLLAR.",
        "desc": "Columbian Exposition issue — the first US commemorative stamps, issued for the World's Columbian Exposition in Chicago (400th anniversary of Columbus's voyage). The high values are scarce. Scott #241.",
    },
    {
        "name": "Bens Frānklins — pirmā pastmarka 5 centi",
        "year": "1847",
        "cat_no": "Scott#1",
        "denom": "5 cents",
        "mat": "Wove paper, no gum variety",
        "perf": "imperf",
        "color": "Red-brown",
        "mint": "Rawdon, Wright, Hatch & Edson, New York",
        "mintage": "approx. 3700000",
        "obs": "Portrait of Benjamin Franklin, first US Postmaster General, in oval medallion. FIVE CENTS.",
        "desc": "First official United States postage stamp, issued 1 July 1847. Benjamin Franklin as Postmaster General is a fitting choice for the first stamp. 5 cents covered single letter rate. Scott #1. One of the most famous and valuable US stamps.",
    },
    {
        "name": "Vašingtons — pirmā pastmarka 10 centi",
        "year": "1847",
        "cat_no": "Scott#2",
        "denom": "10 cents",
        "mat": "Wove paper",
        "perf": "imperf",
        "color": "Black",
        "mint": "Rawdon, Wright, Hatch & Edson, New York",
        "mintage": "approx. 891000",
        "obs": "Portrait of President George Washington in oval medallion. TEN CENTS.",
        "desc": "Second US postage stamp, issued simultaneously with the 5-cent Franklin. 10 cents covered double-weight or coastal letter rates. George Washington appears on US currency and many stamps. Scott #2. Rare.",
    },
    {
        "name": "Brīvības statuja — gaisa pasts 13 centi",
        "year": "1961",
        "cat_no": "Scott#C58",
        "denom": "13 cents airmail",
        "mat": "Tagged paper",
        "perf": "11",
        "color": "Black and red",
        "mint": "Bureau of Engraving and Printing",
        "mintage": "approx. 200000000",
        "obs": "Statue of Liberty torch and crown from below. American flag visible. US AIR MAIL 13c.",
        "desc": "Airmail definitive featuring the Statue of Liberty — symbol of American freedom given by France in 1886. One of the most reproduced American images. Scott #C58.",
    },
    {
        "name": "Nīls Ārmstrongs uz Mēness",
        "year": "1969",
        "cat_no": "Scott#C76",
        "denom": "10 cents airmail",
        "mat": "Tagged paper",
        "perf": "11",
        "color": "Multicolour",
        "mint": "Bureau of Engraving and Printing",
        "mintage": "approx. 152364800",
        "obs": "Astronaut on Moon's surface with Earth visible in background. US flag planted. IN THE BEGINNING GOD… US AIRMAIL 10c.",
        "desc": "Commemorating Apollo 11 Moon landing on 20 July 1969. Neil Armstrong was the first human on the Moon. Unique among US stamps — the design was approved and printed before the mission landed, as NASA was confident of success. Scott #C76.",
    },
    {
        "name": "Linkolna piemiņa 4 centi",
        "year": "1959",
        "cat_no": "Scott#1116",
        "denom": "4 cents",
        "mat": "Flat plate",
        "perf": "11",
        "color": "Blue-violet",
        "mint": "Bureau of Engraving and Printing",
        "mintage": "approx. 126500000",
        "obs": "Lincoln Memorial reflecting pool and monument. UNITED STATES POSTAGE 4 cents. 1809–1959.",
        "desc": "150th anniversary of Abraham Lincoln's birth. The Lincoln Memorial in Washington D.C. was dedicated in 1922. Lincoln's assassination in 1865 after the Civil War made him a martyr figure. Scott #1116.",
    },
]

# ── Classic world stamps (notable and collectible) ─────────────────────────────
SWEDEN_STAMPS = [
    {
        "name": "Treskilling Yellow — retākā pastmarka pasaulē",
        "year": "1855",
        "cat_no": "Facit#1",
        "denom": "3 skilling",
        "mat": "Wove paper",
        "perf": "imperf",
        "color": "Yellow (error — should be blue-green)",
        "mint": "Royal Swedish Printing House",
        "mintage": "1 (known example)",
        "obs": "Swedish coat of arms (three crowns) in oval frame. SVERIGE 3 SKILL. Bco.",
        "desc": "The 'Treskilling Yellow' — considered the world's rarest and most valuable stamp. A unique printing error: the 3-skilling stamp was printed in yellow (color of the 8-skilling) instead of its correct blue-green. Sold for CHF 2.88 million in 1996, estimated at $6–10 million today. Only one example known to exist.",
    },
]

FRANCE_STAMPS = [
    {
        "name": "Ceres — pirmā Francijas pastmarka 20 centimu",
        "year": "1849",
        "cat_no": "Yvert#3",
        "denom": "20 centimes",
        "mat": "Wove paper",
        "perf": "imperf",
        "color": "Black",
        "mint": "Imprimerie du Gouvernement, Paris",
        "mintage": "approx. 3000000",
        "obs": "Ceres (goddess of grain and harvest) portrait facing left. REPUBLIQUE FRANÇAISE. 20c.",
        "desc": "First French postage stamp, issued January 1849. Ceres was chosen as a symbol of the new republic. The rarest value (1 franc vermilion, Yvert#7) is worth hundreds of thousands today. Yvert #3.",
    },
    {
        "name": "Napoleons III — 1 franks",
        "year": "1853",
        "cat_no": "Yvert#13",
        "denom": "1 franc",
        "mat": "Imperf, laid paper",
        "perf": "imperf",
        "color": "Carmine",
        "mint": "Imprimerie Impériale, Paris",
        "mintage": "approx. 500000",
        "obs": "Profile portrait of Emperor Napoleon III facing left. EMPIRE FRANÇAIS. 1 FRANC.",
        "desc": "High-value Napoleon III stamp. The French Empire period (1852–1870) produced distinctive Imperial stamps. The 1 franc carmine is a classic French philatelic item. Yvert #13.",
    },
    {
        "name": "Eifela tornis — 100. gadadiena 2.20 franki",
        "year": "1989",
        "cat_no": "Yvert#2573",
        "denom": "2.20 francs",
        "mat": "Gummed paper",
        "perf": "13",
        "color": "Multicolour",
        "mint": "Imprimerie des timbres-poste, Périgueux",
        "mintage": "approx. 4000000",
        "obs": "The Eiffel Tower illuminated at night against Parisian sky. 1889–1989. FRANCE.",
        "desc": "Centenary of the Eiffel Tower, built for the 1889 World's Fair. The tower was originally intended as a temporary structure but became France's most recognized symbol. Designed by Gustave Eiffel. Yvert #2573.",
    },
]


async def find_period(db, country_name: str, section: str, year_hint: int | None = None) -> Period | None:
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

    return periods[0]


async def stamp_exists(db, period_id: int, name: str) -> bool:
    r = await db.execute(
        select(CatalogItem).where(
            CatalogItem.period_id == period_id,
            CatalogItem.name == name,
            CatalogItem.section == SectionType.stamps,
        )
    )
    return r.scalars().first() is not None


async def add_stamp(db, period: Period, s: dict) -> bool:
    if await stamp_exists(db, period.id, s["name"]):
        return False
    item = CatalogItem(
        section=SectionType.stamps,
        period_id=period.id,
        name=s["name"],
        year=s.get("year"),
        description=s.get("desc"),
        denomination=s.get("denom"),
        material=s.get("mat"),
        perforation=s.get("perf"),
        color=s.get("color"),
        mint=s.get("mint"),
        mintage=s.get("mintage"),
        catalog_number=s.get("cat_no"),
        obverse_description=s.get("obs"),
        coin_category="stamp",
    )
    db.add(item)
    return True


async def seed():
    added = 0
    skipped = 0

    async with Session() as db:

        # ── 1. Latvian First Republic stamps ──────────────────────────────────
        print("\n[LV-I] Pievienoju Latvijas Pirmās Republikas pastmarkas (1918–1940)...")
        period_lv1 = await find_period(db, "Latvia", "stamps", 1930)
        if period_lv1:
            for s in LV_FIRST_REPUBLIC_STAMPS:
                ok = await add_stamp(db, period_lv1, s)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_FIRST_REPUBLIC_STAMPS)} pastmarkas -> periods: {period_lv1.name}")
        else:
            print("  [!] Latvia stamps periods nav atrasts")

        # ── 2. Latvian Second Republic stamps ─────────────────────────────────
        print("\n[LV-II] Pievienoju Latvijas Otras Republikas pastmarkas (1991–)...")
        period_lv2 = await find_period(db, "Latvia", "stamps", 2000)
        if period_lv2:
            for s in LV_REPUBLIC_STAMPS:
                ok = await add_stamp(db, period_lv2, s)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(LV_REPUBLIC_STAMPS)} pastmarkas -> periods: {period_lv2.name}")
        else:
            print("  [!] Latvia 1991+ stamps periods nav atrasts")

        # ── 3. Soviet / USSR stamps ────────────────────────────────────────────
        print("\n[USSR] Pievienoju PSRS pastmarkas...")
        period_ussr = await find_period(db, "Soviet Union", "stamps", 1961)
        if not period_ussr:
            period_ussr = await find_period(db, "Russia", "stamps", 1961)
        if period_ussr:
            for s in USSR_STAMPS:
                ok = await add_stamp(db, period_ussr, s)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(USSR_STAMPS)} pastmarkas -> periods: {period_ussr.name}")
        else:
            print("  [!] USSR/Russia stamps periods nav atrasts")

        # ── 4. German stamps ───────────────────────────────────────────────────
        print("\n[DE] Pievienoju Vācijas pastmarkas...")
        period_de_nazi = await find_period(db, "Germany", "stamps", 1941)
        period_de_wmar = await find_period(db, "Germany", "stamps", 1932)
        period_de_brd  = await find_period(db, "Germany", "stamps", 1968)

        nazi_stamps  = [s for s in DE_STAMPS if int(s["year"]) >= 1933 and int(s["year"]) <= 1945]
        weimar_stamps = [s for s in DE_STAMPS if int(s["year"]) < 1933]
        brd_stamps   = [s for s in DE_STAMPS if int(s["year"]) > 1945]

        for s in weimar_stamps:
            p = period_de_wmar or period_de_nazi
            if p:
                ok = await add_stamp(db, p, s)
                if ok: added += 1
                else: skipped += 1

        for s in nazi_stamps:
            p = period_de_nazi
            if p:
                ok = await add_stamp(db, p, s)
                if ok: added += 1
                else: skipped += 1

        for s in brd_stamps:
            p = period_de_brd or period_de_nazi
            if p:
                ok = await add_stamp(db, p, s)
                if ok: added += 1
                else: skipped += 1

        await db.commit()
        print(f"  [ok] {len(DE_STAMPS)} pastmarkas")

        # ── 5. British stamps ──────────────────────────────────────────────────
        print("\n[UK] Pievienoju Lielbritānijas pastmarkas...")
        for year, stamps in [
            (1845, [s for s in UK_STAMPS if int(s["year"]) < 1900]),
            (1920, [s for s in UK_STAMPS if 1900 <= int(s["year"]) < 1960]),
            (1985, [s for s in UK_STAMPS if int(s["year"]) >= 1960]),
        ]:
            if not stamps:
                continue
            p = await find_period(db, "United Kingdom", "stamps", year)
            if not p:
                p = await find_period(db, "Great Britain", "stamps", year)
            if p:
                for s in stamps:
                    ok = await add_stamp(db, p, s)
                    if ok: added += 1
                    else: skipped += 1
        await db.commit()
        print(f"  [ok] {len(UK_STAMPS)} pastmarkas")

        # ── 6. US stamps ───────────────────────────────────────────────────────
        print("\n[US] Pievienoju ASV pastmarkas...")
        for year, stamps in [
            (1847, [s for s in US_STAMPS if int(s["year"]) < 1900]),
            (1918, [s for s in US_STAMPS if 1900 <= int(s["year"]) < 1960]),
            (1969, [s for s in US_STAMPS if int(s["year"]) >= 1960]),
        ]:
            if not stamps:
                continue
            p = await find_period(db, "United States", "stamps", year)
            if not p:
                p = await find_period(db, "USA", "stamps", year)
            if p:
                for s in stamps:
                    ok = await add_stamp(db, p, s)
                    if ok: added += 1
                    else: skipped += 1
        await db.commit()
        print(f"  [ok] {len(US_STAMPS)} pastmarkas")

        # ── 7. Sweden — Treskilling Yellow ────────────────────────────────────
        print("\n[SE] Pievienoju Zviedrijas pastmarkas...")
        period_se = await find_period(db, "Sweden", "stamps", 1855)
        if period_se:
            for s in SWEDEN_STAMPS:
                ok = await add_stamp(db, period_se, s)
                if ok: added += 1
                else: skipped += 1
            await db.commit()
            print(f"  [ok] {len(SWEDEN_STAMPS)} pastmarkas -> periods: {period_se.name}")
        else:
            print("  [!] Sweden stamps periods nav atrasts")

        # ── 8. French stamps ───────────────────────────────────────────────────
        print("\n[FR] Pievienoju Francijas pastmarkas...")
        for year, stamps in [
            (1849, [s for s in FRANCE_STAMPS if int(s["year"]) < 1900]),
            (1989, [s for s in FRANCE_STAMPS if int(s["year"]) >= 1900]),
        ]:
            if not stamps:
                continue
            p = await find_period(db, "France", "stamps", year)
            if p:
                for s in stamps:
                    ok = await add_stamp(db, p, s)
                    if ok: added += 1
                    else: skipped += 1
        await db.commit()
        print(f"  [ok] {len(FRANCE_STAMPS)} pastmarkas")

    print(f"\n{'='*50}")
    print(f"PABEIGTS! Pievienots: {added}, izlaists (jau eksiste): {skipped}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(seed())
