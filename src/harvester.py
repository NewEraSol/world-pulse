"""
Background Full-Text Harvester pre Spravodajsky Tep Sveta.
Nepretrzite bezi na pozadi a stahuje cele tela clankov pre kazdy clanok v DB.
Vysledky uklada priamo do SQLite a FTS5 indexu.
"""
import sqlite3
import trafilatura
import time
import datetime
import random
import os

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0'
]

def harvest_batch(limit=25):
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Vyber clanky, ktore este nemaju stiahnuty plny text
    cur.execute("""
        SELECT a.id, a.url, a.title_orig, m.name as media_name
        FROM articles a
        JOIN media_outlets m ON a.media_id = m.id
        WHERE a.content_snippet IS NULL
        ORDER BY a.id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()

    if not rows:
        conn.close()
        return 0

    success_count = 0
    for r in rows:
        url = r['url']
        art_id = r['id']
        try:
            ua = random.choice(USER_AGENTS)
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded) if downloaded else None

            if text and len(text.strip()) > 80:
                cur.execute("""
                    UPDATE articles 
                    SET content_snippet = ? 
                    WHERE id = ?
                """, (text.strip(), art_id))
                success_count += 1
            else:
                # Ak web blokuje alebo nema text, nastav aspon prazdny marker aby sa neopakoval dokola
                cur.execute("""
                    UPDATE articles 
                    SET content_snippet = perex_orig 
                    WHERE id = ?
                """, (art_id,))
            conn.commit()
            time.sleep(0.4) # Ochrana pred zahltenim webov
        except Exception as e:
            continue

    conn.close()
    return success_count

def run_loop():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Full-Text Harvester na Hetzneri spustený...")
    while True:
        try:
            done = harvest_batch(limit=20)
            if done == 0:
                # Vsetky clanky su stiahnute, cakame na novy varku z RSS
                time.sleep(15)
            else:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Stiahnutých a zaindexovaných {done} plných tiel článkov.")
                time.sleep(2)
        except Exception as e:
            print("Chyba v harvester cykle:", e)
            time.sleep(10)

if __name__ == '__main__':
    run_loop()
