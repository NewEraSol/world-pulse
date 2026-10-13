"""
Naplnenie databazy zakladnymi krajinami a mediami.
"""
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from initial_data import INITIAL_COUNTRIES, MEDIA_OUTLETS

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Vlozenie krajin
    for c in INITIAL_COUNTRIES:
        cur.execute("""
            INSERT OR REPLACE INTO countries (iso_code, name_sk, name_en, region, primary_language)
            VALUES (?, ?, ?, ?, ?)
        """, (c['iso_code'], c['name_sk'], c['name_en'], c['region'], c['primary_language']))

    # Vlozenie medii
    for m in MEDIA_OUTLETS:
        cur.execute("""
            INSERT OR IGNORE INTO media_outlets (country_iso, name, website_url, rss_url, category)
            VALUES (?, ?, ?, ?, ?)
        """, (m['country_iso'], m['name'], m['website_url'], m['rss_url'], m['category']))

    # Prvotne default alerty (Zlato, ropa, nehody, kríza)
    default_alerts = [
        ("Zlato (Gold)", "zlato|gold|bullion|xau", None),
        ("Ropa a Plyn (Energy)", "ropa|crude|brent|wti|oil price|gas pipeline", None),
        ("Letecké a námorné nešťastia", "pád lietadla|plane crash|potopenie lode|ship sank|air disaster", None),
        ("Nukleárne a eskalácia", "jadrov|nuclear strike|nuclear weapon|ballistic missile", None),
        ("Umelá inteligencia (AI)", "artificial intelligence|openai|deepseek|nvidia|ai model", None)
    ]

    for name, pattern, target_countries in default_alerts:
        cur.execute("""
            INSERT OR IGNORE INTO alerts (name, query_pattern, target_countries)
            VALUES (?, ?, ?)
        """, (name, pattern, target_countries))

    conn.commit()
    print(f"Seed dokončený: {len(INITIAL_COUNTRIES)} krajín, {len(MEDIA_OUTLETS)} kľúčových médií, {len(default_alerts)} predvolených alarmov.")
    conn.close()

if __name__ == '__main__':
    seed()
