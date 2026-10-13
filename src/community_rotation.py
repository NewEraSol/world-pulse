"""
Automaticky nocny rotacny cyklus komunitnych alarmov (Midnight Evaluator).
Spusti sa o polnoci (alebo cronom kazdych 24h):
1. Vyberie TOP 5 navrhov s najvyssim skore (votes_up - votes_down).
2. Prelozi ich cez build_fts_query do vsetkych svetovych jazykov.
3. Zaradi ich do tabulky `alerts` ako zive komunitne alarmy.
4. Vyhodi staré neaktivne komunitne alarmy, aby celkovy pocet nepresiahol 20.
"""
import sqlite3
import datetime
import sys
import os

sys.path.append('/root/spravodajsky_tep/src')
from multilingual import build_fts_query

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

def run_community_rotation():
    print(f"[{datetime.datetime.now().isoformat()}] Spúšťam vyhodnotenie ALARMOV HLASOVANIA...", flush=True)
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Získaj TOP 5 návrhov
    cur.execute("""
        SELECT id, keyword, author_nick, (votes_up - votes_down) as score
        FROM community_proposals
        WHERE status = 'pending' AND (votes_up - votes_down) > 0
        ORDER BY score DESC, votes_up DESC
        LIMIT 5
    """)
    winners = cur.fetchall()

    if not winners:
        print("Žiadne čakajúce návrhy s kladným skóre. Rotácia preskočená.")
        conn.close()
        return

    print(f"Víťazné návrhy na dnešný deň ({len(winners)}):")
    for w in winners:
        print(f" - {w['keyword']} (od: {w['author_nick']}, skóre: {w['score']})")

    # 2. Deaktivujeme predchádzajúce staré komunitné alarmy (alebo necháme len najúspešnejšie)
    cur.execute("""
        UPDATE alerts 
        SET is_active = 0 
        WHERE community_proposal_id IS NOT NULL
    """)

    # 3. Zaregistrujeme víťazov do tabuľky alerts
    for w in winners:
        kw = w['keyword']
        # Vygenerujeme multilingválny pattern
        fts_pattern = build_fts_query(kw)
        
        cur.execute("""
            INSERT INTO alerts (name, query_pattern, is_active, community_proposal_id, author_nick)
            VALUES (?, ?, 1, ?, ?)
        """, (f"{kw}", fts_pattern, w['id'], w['author_nick']))
        
        # Označíme návrh ako aktívny
        cur.execute("""
            UPDATE community_proposals 
            SET status = 'active', activated_at = datetime('now')
            WHERE id = ?
        """, (w['id'],))

    conn.commit()
    conn.close()
    print("Rotácia komunitných alarmov úspešne dokončená!", flush=True)

if __name__ == '__main__':
    run_community_rotation()
