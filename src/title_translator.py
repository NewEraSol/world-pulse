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
from robust_translator import robust_batch_translate, robust_translate, is_substantially_different

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

def process_batch():
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Zvolime davku 15 clankov, ktore nemaju title_sk alebo je zly / neprelozeny
    cur.execute("""
        SELECT a.id, a.title_orig, a.country_iso, c.primary_language, a.title_sk, a.title_en
        FROM articles a
        JOIN countries c ON a.country_iso = c.iso_code
        WHERE a.title_en IS NULL 
           OR a.title_sk IS NULL 
           OR a.title_sk = ''
           OR (c.primary_language NOT IN ('sk', 'cs') AND a.title_sk = a.title_orig)
        ORDER BY a.id DESC
        LIMIT 15
    """)
    rows = cur.fetchall()

    if not rows:
        # Ak nie su ziadne priame zhody, hladame clanky za poslednych 48h s vysokou podobnostou (bad translations)
        cur.execute("""
            SELECT a.id, a.title_orig, a.country_iso, c.primary_language, a.title_sk, a.title_en
            FROM articles a
            JOIN countries c ON a.country_iso = c.iso_code
            WHERE c.primary_language NOT IN ('sk', 'cs')
              AND a.published_at >= datetime('now', '-48 hours')
              AND a.title_sk IS NOT NULL
              AND LENGTH(a.title_orig) > 10
            ORDER BY a.id DESC
            LIMIT 50
        """)
        cand_rows = cur.fetchall()
        bad_rows = []
        for r in cand_rows:
            if not is_substantially_different(r['title_orig'], r['title_sk']):
                bad_rows.append(r)
                if len(bad_rows) >= 15:
                    break
        rows = bad_rows

    if not rows:
        conn.close()
        return 0

    ids = [r['id'] for r in rows]
    titles = [r['title_orig'] for r in rows]

    # Preklad do EN
    en_translations = robust_batch_translate(titles, 'en')

    # Preklad do SK
    sk_translations = robust_batch_translate(titles, 'sk')

    for i, r in enumerate(rows):
        orig = titles[i]
        lang = r['primary_language']
        
        t_en = en_translations[i] if i < len(en_translations) and en_translations[i] else orig
        t_sk = sk_translations[i] if i < len(sk_translations) and sk_translations[i] else orig
        
        if lang in ['sk', 'cs']:
            t_sk = orig
        if lang == 'en':
            t_en = orig

        # Poistka pre SK preklad
        if lang not in ['sk', 'cs'] and not is_substantially_different(orig, t_sk):
            single = robust_translate(orig, 'sk')
            if is_substantially_different(orig, single):
                t_sk = single

        cur.execute("""
            UPDATE articles 
            SET title_en = ?, title_sk = ?
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
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Preložená dávka {done} titulkov (SK & EN).", flush=True)
                time.sleep(0.5)
        except Exception as e:
            print("Chyba v batch translation:", e, flush=True)
            time.sleep(3)

if __name__ == '__main__':
    run_loop()
