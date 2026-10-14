"""
Automaticky nocny rotacny cyklus komunitnych alarmov (Midnight Evaluator).
Spusti sa o polnoci (alebo cronom kazdych 24h):
1. Vyberie čakajúcich kandidátov s kladným skóre (votes_up - votes_down > 0), max 5.
2. Ak je nových víťazov napr. 2, do éteru pribudnú títo 2 a vyradia sa len 2 najstaršie/najslabšie doterajšie komunitné alarmy.
3. V éteri tak zostáva stabilne presne 5 (alebo podľa potreby) aktívnych komunitných alarmov.
4. Pre nových víťazov vygeneruje multilingválny dotaz (build_fts_query) a aktivuje ich v tabuľke `alerts`.
"""
import sqlite3
import datetime
import sys
import os

sys.path.append('/root/spravodajsky_tep/src')
from multilingual import build_fts_query

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'
TARGET_COMMUNITY_ALERTS_COUNT = 5

def run_community_rotation():
    print(f"[{datetime.datetime.now().isoformat()}] Spúšťam plynulé vyhodnotenie ALARMOV HLASOVANIA...", flush=True)
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Získaj TOP kandidátov z arény s kladným skóre (max do limitu TARGET_COMMUNITY_ALERTS_COUNT)
    cur.execute("""
        SELECT id, keyword, author_nick, (votes_up - votes_down) as score
        FROM community_proposals
        WHERE status = 'pending' AND (votes_up - votes_down) > 0
        ORDER BY score DESC, votes_up DESC, id ASC
        LIMIT ?
    """, (TARGET_COMMUNITY_ALERTS_COUNT,))
    new_winners = cur.fetchall()

    if not new_winners:
        print("Žiadne čakajúce návrhy s kladným skóre. Doterajšie alarmy v éteri pokračujú bezo zmeny.")
        conn.close()
        return

    num_new = len(new_winners)
    print(f"Víťazné návrhy na zaradenie do éteru ({num_new}):")
    for w in new_winners:
        print(f" + {w['keyword']} (od: {w['author_nick']}, skóre: {w['score']})")

    # 2. Zisti aktuálne bežiace komunitné alarmy zoradené podľa úspešnosti (zásahy) a času vytvorenia
    cur.execute("""
        SELECT a.id, a.name, COUNT(h.id) as hits, a.created_at
        FROM alerts a
        LEFT JOIN alert_hits h ON a.id = h.alert_id
        WHERE a.community_proposal_id IS NOT NULL AND a.is_active = 1
        GROUP BY a.id
        ORDER BY hits ASC, a.created_at ASC
    """)
    current_active = cur.fetchall()
    total_active_now = len(current_active)

    # Koľko starých musíme deaktivovať, aby po pridaní nových bolo celkovo TARGET_COMMUNITY_ALERTS_COUNT?
    # Ak máme teraz napr. 5 a prichádzajú 2 noví: musíme uvoľniť 2 miesta (5 + 2 - 5 = 2).
    to_retire_count = max(0, (total_active_now + num_new) - TARGET_COMMUNITY_ALERTS_COUNT)

    if to_retire_count > 0:
        to_retire = current_active[:to_retire_count]
        print(f"Vyraďujem {len(to_retire)} najstarších/najslabších alarmov z éteru:")
        for r in to_retire:
            print(f" - ID {r['id']}: {r['name']} ({r['hits']} zásahov)")
            cur.execute("UPDATE alerts SET is_active = 0 WHERE id = ?", (r['id'],))

    # 3. Zaregistrujeme nových víťazov do tabuľky alerts
    for w in new_winners:
        kw = w['keyword']
        # Vygenerujeme multilingválny pattern
        try:
            fts_pattern = build_fts_query(kw)
        except Exception as e:
            fts_pattern = f'"{kw}"'
            print(f"Chyba pri generovaní multilingválneho query pre {kw}: {e}")

        cur.execute("""
            INSERT INTO alerts (name, query_pattern, is_active, community_proposal_id, author_nick)
            VALUES (?, ?, 1, ?, ?)
        """, (f"{kw}", fts_pattern, w['id'], w['author_nick']))

        # Označíme návrh ako aktívny v návrhoch
        cur.execute("""
            UPDATE community_proposals 
            SET status = 'active', activated_at = datetime('now')
            WHERE id = ?
        """, (w['id'],))

    conn.commit()

    # Kontrolný výpis nového stavu éteru
    cur.execute("""
        SELECT a.id, a.name, a.author_nick, COUNT(h.id) as hits
        FROM alerts a
        LEFT JOIN alert_hits h ON a.id = h.alert_id
        WHERE a.community_proposal_id IS NOT NULL AND a.is_active = 1
        GROUP BY a.id
        ORDER BY hits DESC, a.id DESC
    """)
    final_active = cur.fetchall()
    print(f"\nAktuálny stav v éteri po rotácii ({len(final_active)} aktívnych tém):")
    for a in final_active:
        print(f" • {a['name']} (autor: {a['author_nick']}, zásahy: {a['hits']})")

    conn.close()
    print("Rotácia komunitných alarmov úspešne dokončená!", flush=True)

if __name__ == '__main__':
    run_community_rotation()
