"""
Skript na aplikaciu rozsirenych krajin a medii do DB na Hetzneri.
"""
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from expanded_countries import NEW_COUNTRIES, EXPANDED_MEDIA

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Vlozenie novych krajin
    for c in NEW_COUNTRIES:
        cur.execute("""
            INSERT OR REPLACE INTO countries (iso_code, name_sk, name_en, region, primary_language)
            VALUES (?, ?, ?, ?, ?)
        """, (c['iso_code'], c['name_sk'], c['name_en'], c['region'], c['primary_language']))

    # Vlozenie novych medii
    added_media = 0
    for m in EXPANDED_MEDIA:
        cur.execute("""
            INSERT OR IGNORE INTO media_outlets (country_iso, name, website_url, rss_url, category)
            VALUES (?, ?, ?, ?, ?)
        """, (m['country_iso'], m['name'], m['website_url'], m['rss_url'], m['category']))
        if cur.rowcount > 0:
            added_media += 1

    conn.commit()

    total_countries = cur.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    total_media = cur.execute("SELECT COUNT(*) FROM media_outlets WHERE is_active = 1").fetchone()[0]

    print(f"Hotovo! Pridaných {len(NEW_COUNTRIES)} nových krajín, {added_media} nových médií.")
    print(f"Celkový stav v DB: {total_countries} krajín, {total_media} aktívnych médií.")
    conn.close()

if __name__ == '__main__':
    run()
