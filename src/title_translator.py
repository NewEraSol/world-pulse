"""
Ultra-rychly davkovy prekladac titulkov (Batch Title Translator).
Preklada naraz davky po 15-20 titulkoch spojene cez newline,
cim zrychli preklad celej databazy z hodin na par minut.
"""
import sqlite3
import time
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from robust_translator import robust_batch_translate, robust_translate

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

def process_batch():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Zvolime davku 15 clankov, ktore nemaju title_en
    cur.execute("""
        SELECT a.id, a.title_orig, a.country_iso, c.primary_language
        FROM articles a
        JOIN countries c ON a.country_iso = c.iso_code
        WHERE a.title_en IS NULL
        ORDER BY a.id DESC
        LIMIT 15
    """)
    rows = cur.fetchall()

    if not rows:
        conn.close()
        return 0

    ids = [r['id'] for r in rows]
    titles = [r['title_orig'] for r in rows]

    # Preklad do EN
    en_translations = robust_batch_translate(titles, 'en')

    # Preklad do SK (pre tie co nemaju title_sk)
    sk_translations = robust_batch_translate(titles, 'sk')

    for i, r in enumerate(rows):
        t_en = en_translations[i] if i < len(en_translations) else titles[i]
        t_sk = sk_translations[i] if i < len(sk_translations) else titles[i]
        
        cur.execute("""
            UPDATE articles 
            SET title_en = ?, title_sk = COALESCE(title_sk, ?)
            WHERE id = ?
        """, (t_en, t_sk, r['id']))

    conn.commit()
    conn.close()
    return len(rows)

def run_loop():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Batch Title Translator spustený...", flush=True)
    while True:
        try:
            done = process_batch()
            if done == 0:
                time.sleep(5)
            else:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Preložená dávka {done} titulkov.", flush=True)
                time.sleep(0.3)
        except Exception as e:
            print("Chyba v batch translation:", e, flush=True)
            time.sleep(3)

if __name__ == '__main__':
    run_loop()
