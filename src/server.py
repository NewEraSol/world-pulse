"""
FastAPI Server pre Spravodajsky Tep Sveta.
Zahŕňa multilingválnu expanziu dotazov (hľadanie v natívnych jazykoch sveta)
a kompletný preklad prepisov do SK a EN.
"""
from fastapi import FastAPI, Query, HTTPException, Body, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import datetime
import os
import re
from typing import Optional, List
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from translator import get_or_translate_article
from multilingual import expand_keyword, build_fts_query
from geo_data import COUNTRY_COORDINATES

app = FastAPI(title="Spravodajský Tep Sveta", version="1.3")

ADMIN_PIN = os.getenv("TEP_ADMIN_PIN", "3690")

def verify_admin_pin(x_admin_pin: Optional[str] = Header(None)):
    if not x_admin_pin or x_admin_pin != ADMIN_PIN:
        raise HTTPException(status_code=403, detail="Prístup zamietnutý. Neplatný Admin PIN.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    return conn

class AlertCreate(BaseModel):
    name: str
    query_pattern: str
    target_countries: Optional[str] = None
    notify_telegram: bool = True

class FavoriteCreate(BaseModel):
    article_id: int
    notes: Optional[str] = None

class MediaCreate(BaseModel):
    country_iso: str
    name: str
    website_url: str
    rss_url: str
    category: Optional[str] = "general"

@app.get("/api/stats")
def get_stats(period: Optional[str] = "all"):
    conn = get_db()
    cur = conn.cursor()

    time_filter = ""
    time_params = []

    if period and period != "all":
        now = datetime.datetime.utcnow()
        delta_map = {
            "1h": datetime.timedelta(hours=1),
            "6h": datetime.timedelta(hours=6),
            "24h": datetime.timedelta(hours=24),
            "7d": datetime.timedelta(days=7),
            "30d": datetime.timedelta(days=30)
        }
        if period in delta_map:
            since = (now - delta_map[period]).isoformat()
            time_filter = " WHERE (published_at >= ? OR scraped_at >= ?)"
            time_params = [since, since]

    total_articles = cur.execute(f"SELECT COUNT(*) FROM articles{time_filter}", tuple(time_params)).fetchone()[0]
    total_countries = cur.execute("SELECT COUNT(DISTINCT country_iso) FROM media_outlets WHERE is_active = 1").fetchone()[0]
    total_media = cur.execute("SELECT COUNT(*) FROM media_outlets WHERE is_active = 1").fetchone()[0]
    total_alerts = cur.execute("SELECT COUNT(*) FROM alerts WHERE is_active = 1").fetchone()[0]
    if time_filter:
        hits_filter = " JOIN articles a ON h.article_id = a.id WHERE (a.published_at >= ? OR a.scraped_at >= ?)"
        total_hits = cur.execute(f"SELECT COUNT(*) FROM alert_hits h {hits_filter}", tuple(time_params)).fetchone()[0]
    else:
        total_hits = cur.execute("SELECT COUNT(*) FROM alert_hits").fetchone()[0]
    total_favorites = cur.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
    last_scrape = cur.execute("SELECT MAX(scraped_at) FROM articles").fetchone()[0]
    conn.close()
    return {
        "total_articles": total_articles,
        "total_countries": total_countries,
        "total_media": total_media,
        "total_alerts": total_alerts,
        "total_alarm_hits": total_hits,
        "total_favorites": total_favorites,
        "last_scrape": last_scrape
    }

@app.get("/api/countries")
def get_countries(
    period: Optional[str] = "all",
    query: Optional[str] = None,
    alert_id: Optional[int] = None,
    alerts_only: bool = False
):
    conn = get_db()
    cur = conn.cursor()

    time_filter = ""
    time_params = []
    alert_join = ""
    if alerts_only:
        alert_join = "JOIN alert_hits ah ON a.id = ah.article_id" 
    if period and period != "all":
        now = datetime.datetime.utcnow()
        delta_map = {
            "1h": datetime.timedelta(hours=1),
            "6h": datetime.timedelta(hours=6),
            "24h": datetime.timedelta(hours=24),
            "7d": datetime.timedelta(days=7),
            "30d": datetime.timedelta(days=30)
        }
        if period in delta_map:
            since = (now - delta_map[period]).isoformat()
            time_filter = " AND (a.published_at >= ? OR a.scraped_at >= ?)"
            time_params = [since, since]

    if alert_id:
        sql = f"""
            SELECT c.*, COUNT(DISTINCT a.id) as article_count, COUNT(DISTINCT m.id) as media_count
            FROM countries c
            LEFT JOIN media_outlets m ON c.iso_code = m.country_iso AND m.is_active = 1
            LEFT JOIN (
                SELECT a.id, a.country_iso
                FROM alert_hits ah
                JOIN articles a ON ah.article_id = a.id
                WHERE ah.alert_id = ? {time_filter}
            ) a ON c.iso_code = a.country_iso
            GROUP BY c.iso_code
            ORDER BY article_count DESC, c.name_sk ASC
        """
        cur.execute(sql, (alert_id, *time_params))
    elif query:
        fts_expr = build_fts_query(query)
        sql = f"""
            SELECT c.*, COUNT(DISTINCT a.id) as article_count, COUNT(DISTINCT m.id) as media_count
            FROM countries c
            LEFT JOIN media_outlets m ON c.iso_code = m.country_iso AND m.is_active = 1
            LEFT JOIN (
                SELECT a.id, a.country_iso
                FROM articles a
                JOIN articles_fts fts ON a.id = fts.rowid
                WHERE articles_fts MATCH ? {time_filter}
            ) a ON c.iso_code = a.country_iso
            GROUP BY c.iso_code
            ORDER BY article_count DESC, c.name_sk ASC
        """
        cur.execute(sql, (fts_expr, *time_params))
    else:
        sql = f"""
            SELECT c.*, COUNT(DISTINCT a.id) as article_count, COUNT(DISTINCT m.id) as media_count
            FROM countries c
            LEFT JOIN media_outlets m ON c.iso_code = m.country_iso AND m.is_active = 1
            LEFT JOIN (
                SELECT a.id, a.country_iso
                FROM articles a
                {alert_join}
                WHERE 1=1 {time_filter}
            ) a ON c.iso_code = a.country_iso
            GROUP BY c.iso_code
            ORDER BY article_count DESC, c.name_sk ASC
        """
        cur.execute(sql, tuple(time_params))

    rows = []
    for r in cur.fetchall():
        item = dict(r)
        iso = item['iso_code']
        coords = COUNTRY_COORDINATES.get(iso, {"lat": 0.0, "lon": 0.0})
        item['lat'] = coords['lat']
        item['lon'] = coords['lon']
        rows.append(item)
    conn.close()
    return rows

@app.get("/api/articles")
def get_articles(
    country: Optional[str] = None,
    query: Optional[str] = None,
    alert_id: Optional[int] = None,
    period: Optional[str] = "all",
    alerts_only: bool = False,
    limit: int = 50,
    offset: int = 0
):
    conn = get_db()
    cur = conn.cursor()

    time_filter = ""
    params: list = []
    alert_where = ""
    if alerts_only:
        alert_where = " AND EXISTS (SELECT 1 FROM alert_hits ah WHERE ah.article_id = a.id)" 

    if period and period != "all":
        now = datetime.datetime.utcnow()
        delta_map = {
            "1h": datetime.timedelta(hours=1),
            "6h": datetime.timedelta(hours=6),
            "24h": datetime.timedelta(hours=24),
            "7d": datetime.timedelta(days=7),
            "30d": datetime.timedelta(days=30)
        }
        if period in delta_map:
            since = (now - delta_map[period]).isoformat()
            time_filter = " AND (a.published_at >= ? OR a.scraped_at >= ?)"

    if alert_id:
        # Bleskové vyhľadávanie priamo cez zachytené hity daného alarmu (<5ms odozva)
        sql = f"""
            SELECT a.id, a.country_iso, a.title_orig, a.title_sk, a.title_en, a.perex_orig, a.perex_sk, a.perex_en, 
                   a.url, a.published_at, a.scraped_at, m.name as media_name, c.name_sk as country_name,
                   CASE WHEN fav.id IS NOT NULL THEN 1 ELSE 0 END as is_favorite,
                   ah.matched_text as searched_word
            FROM alert_hits ah
            JOIN articles a ON ah.article_id = a.id
            JOIN media_outlets m ON a.media_id = m.id
            JOIN countries c ON a.country_iso = c.iso_code
            LEFT JOIN favorites fav ON a.id = fav.article_id
            WHERE ah.alert_id = ?
        """
        params.append(alert_id)
        if country:
            sql += " AND a.country_iso = ?"
            params.append(country)
        if time_filter:
            sql += time_filter
            params.extend([since, since])
        sql += " ORDER BY CASE WHEN a.published_at > datetime('now', '+5 minutes') THEN a.scraped_at ELSE a.published_at END DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cur.execute(sql, tuple(params))
    elif query:
        # Pouzitie multilingvalnej expanzie (hlada v nativnych jazykoch sveta)
        fts_expr = build_fts_query(query)
        sql = f"""
            SELECT a.id, a.country_iso, a.title_orig, a.title_sk, a.title_en, a.perex_orig, a.perex_sk, a.perex_en, 
                   a.url, a.published_at, a.scraped_at, m.name as media_name, c.name_sk as country_name,
                   CASE WHEN fav.id IS NOT NULL THEN 1 ELSE 0 END as is_favorite
                        FROM articles a
            JOIN articles_fts fts ON a.id = fts.rowid
            JOIN media_outlets m ON a.media_id = m.id
            JOIN countries c ON a.country_iso = c.iso_code
            LEFT JOIN favorites fav ON a.id = fav.article_id
            WHERE articles_fts MATCH ? {alert_where}
        """
        params.append(fts_expr)
        if country:
            sql += " AND a.country_iso = ?"
            params.append(country)
        if time_filter:
            sql += time_filter
            params.extend([since, since])
        sql += " ORDER BY CASE WHEN a.published_at > datetime('now', '+5 minutes') THEN a.scraped_at ELSE a.published_at END DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cur.execute(sql, tuple(params))
    else:
        sql = f"""
            SELECT a.id, a.country_iso, a.title_orig, a.title_sk, a.title_en, a.perex_orig, a.perex_sk, a.perex_en,
                   a.url, a.published_at, a.scraped_at, m.name as media_name, c.name_sk as country_name,
                   CASE WHEN fav.id IS NOT NULL THEN 1 ELSE 0 END as is_favorite
            FROM articles a
            JOIN media_outlets m ON a.media_id = m.id
            JOIN countries c ON a.country_iso = c.iso_code
            LEFT JOIN favorites fav ON a.id = fav.article_id
            WHERE 1=1 {alert_where}
        """
        if country:
            sql += " AND a.country_iso = ?"
            params.append(country)
        if time_filter:
            sql += time_filter
            params.extend([since, since])
        sql += " ORDER BY CASE WHEN a.published_at > datetime('now', '+5 minutes') THEN a.scraped_at ELSE a.published_at END DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cur.execute(sql, tuple(params))

    rows = [dict(r) for r in cur.fetchall()]

    # Zistime priradene alerty pre vratene clanky (z tabulky alert_hits a podla matchu)
    if rows:
        art_ids = [r['id'] for r in rows]
        placeholders = ','.join(['?'] * len(art_ids))
        cur.execute(f"""
            SELECT h.article_id, al.name as alert_name, al.query_pattern, h.matched_text
            FROM alert_hits h
            JOIN alerts al ON h.alert_id = al.id
            WHERE h.article_id IN ({placeholders})
        """, tuple(art_ids))
        hits_map = {}
        for h in cur.fetchall():
            aid = h['article_id']
            if aid not in hits_map:
                hits_map[aid] = []
            hits_map[aid].append({
                "alert_name": h['alert_name'],
                "pattern": h['query_pattern'],
                "matched_word": h['matched_text']
            })

        for r in rows:
            r['matched_alerts'] = hits_map.get(r['id'], [])
            # Ak bolo zadane vyhladavanie cez query, pridame info o hladanom slove
            if query:
                r['searched_word'] = query

    # Preklad titulkov beží plne asynchrónne na pozadí cez proces tep-title-translator,
    # takže API odpovedá okamžite bez akéhokoľvek zdržania (odozva < 100ms)

    conn.close()
    return rows

@app.get("/api/articles/{article_id}")
def get_article_detail(article_id: int):
    """
    Vrati plny prepis clanku s kompletnym prekladom do SK aj EN a priradenymi radarovymi zachytmi.
    """
    detail = get_or_translate_article(article_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Článok neexistuje.")
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT al.name as alert_name, al.query_pattern, h.matched_text
        FROM alert_hits h
        JOIN alerts al ON h.alert_id = al.id
        WHERE h.article_id = ?
    """, (article_id,))
    matched_alerts = []
    for h in cur.fetchall():
        matched_alerts.append({
            "alert_name": h['alert_name'],
            "pattern": h['query_pattern'],
            "matched_word": h['matched_text']
        })
    cur.execute("SELECT 1 FROM favorites WHERE article_id = ?", (article_id,))
    detail['is_favorite'] = 1 if cur.fetchone() else 0
    conn.close()
    detail['matched_alerts'] = matched_alerts
    return detail

@app.get("/api/keyword-frequency")
def get_keyword_frequency(
    keyword: str = Query(..., min_length=2),
    period: Optional[str] = "all"
):
    """
    Multilingvalna analyza frekvencie slova po celom svete.
    """
    conn = get_db()
    cur = conn.cursor()
    
    fts_expr = build_fts_query(keyword)
    expanded_words = expand_keyword(keyword)

    time_filter = ""
    time_params = []
    if period and period != "all":
        now = datetime.datetime.utcnow()
        delta_map = {"1h": datetime.timedelta(hours=1), "6h": datetime.timedelta(hours=6), "24h": datetime.timedelta(hours=24), "7d": datetime.timedelta(days=7), "30d": datetime.timedelta(days=30)}
        if period in delta_map:
            since = (now - delta_map[period]).isoformat()
            time_filter = " AND (a.published_at >= ? OR a.scraped_at >= ?)"
            time_params = [since, since]

    # Total count
    sql_total = f"""
        SELECT COUNT(a.id)
        FROM articles a
        JOIN articles_fts fts ON a.id = fts.rowid
        WHERE articles_fts MATCH ? {time_filter}
    """
    cur.execute(sql_total, (fts_expr, *time_params))
    total_count = cur.fetchone()[0]

    # Breakdown by country
    sql_country = f"""
        SELECT a.country_iso, c.name_sk, COUNT(a.id) as count
        FROM articles a
        JOIN articles_fts fts ON a.id = fts.rowid
        JOIN countries c ON a.country_iso = c.iso_code
        WHERE articles_fts MATCH ? {time_filter}
        GROUP BY a.country_iso
        ORDER BY count DESC
    """
    cur.execute(sql_country, (fts_expr, *time_params))
    by_country = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "keyword": keyword,
        "expanded_terms": expanded_words,
        "period": period,
        "total_occurrences": total_count,
        "breakdown_by_country": by_country
    }


class AdminVerifyRequest(BaseModel):
    pin: str

@app.post("/api/admin/verify")
def verify_pin(payload: AdminVerifyRequest):
    if payload.pin == ADMIN_PIN:
        return {"status": "ok", "valid": True}
    raise HTTPException(status_code=403, detail="Nesprávny PIN")


# ----------------- ALARMY HLASOVANIA (COMMUNITY PROPOSALS & VOTING) -----------------

class ProposalCreate(BaseModel):
    keyword: str
    author_nick: Optional[str] = "Anonym"
    voter_hash: Optional[str] = None

class ProposalVote(BaseModel):
    proposal_id: int
    voter_hash: str
    vote_type: int # 1 = UP, -1 = DOWN

@app.get("/api/community/proposals")
def get_community_proposals():
    conn = get_db()
    cur = conn.cursor()
    # Získame aktívne komunitné alarmy (ktoré už bežia v éteri)
    cur.execute("""
        SELECT a.id as alert_id, a.name, a.author_nick, a.created_at,
               COUNT(ah.id) as hits_count
        FROM alerts a
        LEFT JOIN alert_hits ah ON a.id = ah.alert_id
        WHERE a.community_proposal_id IS NOT NULL AND a.is_active = 1
        GROUP BY a.id
        ORDER BY hits_count DESC
    """)
    active_in_feed = [dict(r) for r in cur.fetchall()]

    # Získame návrhy, za ktoré sa aktuálne hlasuje
    cur.execute("""
        SELECT id, keyword, author_nick, votes_up, votes_down, 
               (votes_up - votes_down) as score, created_at
        FROM community_proposals
        WHERE status = 'pending'
        ORDER BY score DESC, votes_up DESC, id DESC
        LIMIT 50
    """)
    voting_arena = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {
        "active_community_alerts": active_in_feed,
        "voting_proposals": voting_arena
    }

@app.post("/api/community/proposals")
def create_community_proposal(payload: ProposalCreate):
    kw = payload.keyword.strip()
    nick = (payload.author_nick or "Anonym").strip()[:30]
    voter = (payload.voter_hash or "").strip()

    if not kw or len(kw) < 2 or len(kw) > 40:
        raise HTTPException(status_code=400, detail="Slovo musí mať od 2 do 40 znakov.")
    
    # Zakázané vulgárne slová / spam
    forbidden = ['kokot', 'pica', 'kurva', 'jebat', 'debil', 'chuj', 'dick', 'fuck']
    if any(f in kw.lower() for f in forbidden):
        raise HTTPException(status_code=400, detail="Nevhodné kľúčové slovo.")

    conn = get_db()
    cur = conn.cursor()

    # OCHRANA 1: Limit kapacity arény (max 50 čakajúcich kandidátov)
    cur.execute("SELECT COUNT(*) FROM community_proposals WHERE status = 'pending'")
    pending_count = cur.fetchone()[0]
    if pending_count >= 50:
        conn.close()
        raise HTTPException(status_code=400, detail="Hlasovacia aréna je plná (max. 50 slov). Zahlasuj za existujúce slová alebo počkaj na polnočné vyhodnotenie!")

    # OCHRANA 2: Limit 1 návrh na návštevníka za 24 hodín
    if voter:
        cur.execute("""
            SELECT id FROM community_proposals 
            WHERE author_nick = ? AND created_at >= datetime('now', '-24 hours')
        """, (nick,))
        # Tiež kontrola cez tabuľku hlasov / odtlačkov ak existuje
        cur.execute("""
            CREATE TABLE IF NOT EXISTS proposal_ratelimit (
                voter_hash TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            SELECT created_at FROM proposal_ratelimit 
            WHERE voter_hash = ? AND created_at >= datetime('now', '-24 hours')
        """, (voter,))
        if cur.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Dnes si už jedno slovo navrhol (limit 1 návrh na 24h)! Ďalšie môžeš pridať zajtra.")

    try:
        cur.execute("""
            INSERT INTO community_proposals (keyword, author_nick, votes_up)
            VALUES (?, ?, 1)
        """, (kw, nick))
        pid = cur.lastrowid
        
        # Zaznamenáme limit pre tohto používateľa
        if voter:
            cur.execute("""
                INSERT OR REPLACE INTO proposal_ratelimit (voter_hash, created_at)
                VALUES (?, datetime('now'))
            """, (voter,))

        conn.commit()
        conn.close()
        return {"status": "ok", "id": pid, "keyword": kw, "author_nick": nick}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Toto slovo už bolo navrhnuté! Môžeš zaň zahlasovať v aréne.")

@app.post("/api/community/vote")
def vote_community_proposal(payload: ProposalVote):
    if payload.vote_type not in [1, -1]:
        raise HTTPException(status_code=400, detail="Neplatný typ hlasu.")
    voter = payload.voter_hash.strip()
    if not voter or len(voter) < 8:
        raise HTTPException(status_code=400, detail="Neplatná identifikácia hlasujúceho.")

    conn = get_db()
    cur = conn.cursor()
    # Skontrolujeme, či už nehlasoval za tento konkrétny návrh
    cur.execute("SELECT id FROM community_votes WHERE proposal_id = ? AND voter_hash = ?", (payload.proposal_id, voter))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Za tento návrh si už hlasoval!")

    try:
        cur.execute("""
            INSERT INTO community_votes (proposal_id, voter_hash, vote_type)
            VALUES (?, ?, ?)
        """, (payload.proposal_id, voter, payload.vote_type))
        
        if payload.vote_type == 1:
            cur.execute("UPDATE community_proposals SET votes_up = votes_up + 1 WHERE id = ?", (payload.proposal_id,))
        else:
            cur.execute("UPDATE community_proposals SET votes_down = votes_down + 1 WHERE id = ?", (payload.proposal_id,))
        
        conn.commit()
        
        # Získame nové skóre
        cur.execute("SELECT votes_up, votes_down, (votes_up - votes_down) as score FROM community_proposals WHERE id = ?", (payload.proposal_id,))
        row = dict(cur.fetchone())
        conn.close()
        return {"status": "ok", **row}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


# ----------------- ALARMY & VÝSTRAHY (CRUD) -----------------


@app.get("/api/favorites")
def get_favorites(limit: int = 100, offset: int = 0):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.country_iso, a.title_orig, a.title_sk, a.title_en, a.perex_orig, a.perex_sk, a.perex_en,
               a.url, a.published_at, a.scraped_at, m.name as media_name, c.name_sk as country_name,
               f.id as favorite_id, f.saved_at, f.notes, 1 as is_favorite
        FROM favorites f
        JOIN articles a ON f.article_id = a.id
        JOIN media_outlets m ON a.media_id = m.id
        JOIN countries c ON a.country_iso = c.iso_code
        ORDER BY f.saved_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.post("/api/favorites")
def add_favorite(payload: FavoriteCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM articles WHERE id = ?", (payload.article_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Článok neexistuje.")
    try:
        cur.execute("""
            INSERT INTO favorites (article_id, notes)
            VALUES (?, ?)
        """, (payload.article_id, payload.notes))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return {"status": "ok", "article_id": payload.article_id, "is_favorite": 1}

@app.delete("/api/favorites/{article_id}")
def remove_favorite(article_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM favorites WHERE article_id = ?", (article_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "article_id": article_id, "is_favorite": 0}

@app.get("/api/alerts")
def get_alerts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, COUNT(h.id) as hit_count
        FROM alerts a
        LEFT JOIN alert_hits h ON a.id = h.alert_id
        GROUP BY a.id
        ORDER BY a.id ASC
    """)
    alerts = [dict(r) for r in cur.fetchall()]
    conn.close()
    return alerts

@app.post("/api/alerts")
def create_alert(payload: AlertCreate, x_admin_pin: Optional[str] = Header(None)):
    verify_admin_pin(x_admin_pin)
    name = payload.name.strip()
    pattern = payload.query_pattern.strip()
    if not name or not pattern:
        raise HTTPException(status_code=400, detail="Názov a kľúčové slová sú povinné.")
    
    # Automatická multilingválna expanzia vzoru ak obsahuje len 1 slovo
    print(f"[DEBUG_SERVER] Creating alert: {name}, pattern: {pattern}", flush=True)
    if '|' not in pattern:
        expanded = expand_keyword(pattern)
        print(f"[DEBUG_SERVER] Expanded result: {expanded}", flush=True)
        if len(expanded) > 1:
            pattern = "|".join(expanded)
            print(f"[DEBUG_SERVER] New pattern: {pattern}", flush=True)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alerts (name, query_pattern, target_countries, notify_telegram, is_active)
        VALUES (?, ?, ?, ?, 1)
    """, (name, pattern, payload.target_countries, 1 if payload.notify_telegram else 0))
    alert_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT id, title_orig, perex_orig FROM articles ORDER BY published_at DESC LIMIT 1000")
    articles = cur.fetchall()
    retro_hits = 0
    for art in articles:
        text = f"{art['title_orig']} {art['perex_orig'] or ''}".lower()
        match = re.search(r'\b(' + pattern + r')\b', text, re.IGNORECASE)
        if match:
            found_keyword = match.group(0)
            try:
                cur.execute("""
                    INSERT OR IGNORE INTO alert_hits (alert_id, article_id, matched_text)
                    VALUES (?, ?, ?)
                """, (alert_id, art['id'], found_keyword))
                retro_hits += 1
            except sqlite3.IntegrityError:
                pass
    conn.commit()
    conn.close()

    return {"status": "ok", "alert_id": alert_id, "query_pattern": pattern, "retro_hits": retro_hits}

@app.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: int, x_admin_pin: Optional[str] = Header(None)):
    verify_admin_pin(x_admin_pin)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM alert_hits WHERE alert_id = ?", (alert_id,))
    cur.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}


class IssueReport(BaseModel):
    article_id: int
    reason: Optional[str] = "nepreložené / zlá kvalita"

@app.post("/api/translation-issues")
def report_translation_issue(payload: IssueReport):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title_orig FROM articles WHERE id = ?", (payload.article_id,))
    art = cur.fetchone()
    if not art:
        conn.close()
        raise HTTPException(status_code=404, detail="Článok neexistuje.")
    
    cur.execute("""
        INSERT INTO translation_issues (article_id, reason)
        VALUES (?, ?)
    """, (payload.article_id, payload.reason))
    conn.commit()
    issue_id = cur.lastrowid
    conn.close()
    return {"status": "ok", "issue_id": issue_id, "article_id": payload.article_id}

@app.get("/api/translation-issues")
def list_translation_issues(limit: int = 50):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, i.article_id, i.reported_at, i.reason, i.status,
               a.title_orig, a.title_sk, a.title_en, a.url, a.published_at,
               m.name as media_name, c.name_sk as country_name, c.primary_language
        FROM translation_issues i
        JOIN articles a ON i.article_id = a.id
        JOIN media_outlets m ON a.media_id = m.id
        JOIN countries c ON a.country_iso = c.iso_code
        ORDER BY i.reported_at DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ----------------- SPRÁVA ZDROJOV / MÉDIÍ (CRUD) -----------------

@app.get("/api/media")
def get_media(country: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    if country:
        cur.execute("""
            SELECT m.*, c.name_sk as country_name, COUNT(a.id) as article_count
            FROM media_outlets m
            JOIN countries c ON m.country_iso = c.iso_code
            LEFT JOIN articles a ON m.id = a.media_id
            WHERE m.country_iso = ?
            GROUP BY m.id
            ORDER BY m.is_active DESC, m.name ASC
        """, (country,))
    else:
        cur.execute("""
            SELECT m.*, c.name_sk as country_name, COUNT(a.id) as article_count
            FROM media_outlets m
            JOIN countries c ON m.country_iso = c.iso_code
            LEFT JOIN articles a ON m.id = a.media_id
            GROUP BY m.id
            ORDER BY c.name_sk ASC, m.name ASC
        """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.post("/api/media")
def create_media(payload: MediaCreate, x_admin_pin: Optional[str] = Header(None)):
    verify_admin_pin(x_admin_pin)
    name = payload.name.strip()
    web_url = payload.website_url.strip()
    rss_url = payload.rss_url.strip()
    country_iso = payload.country_iso.strip().upper()
    category = payload.category or "general"

    # Automatická normalizácia pre Telegram kanály (napr. @bbbreaking alebo t.me/bbbreaking)
    if category == 'telegram' or 't.me/' in rss_url or rss_url.startswith('@'):
        channel_handle = rss_url.replace('https://t.me/s/', '').replace('https://t.me/', '').replace('http://t.me/s/', '').replace('http://t.me/', '').replace('@', '').strip().strip('/')
        rss_url = f"https://t.me/s/{channel_handle}"
        if not web_url or web_url == 'https://...':
            web_url = f"https://t.me/{channel_handle}"
        category = 'telegram'

    if not name or not web_url or not rss_url or not country_iso:
        raise HTTPException(status_code=400, detail="Všetky polia sú povinné.")
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT iso_code FROM countries WHERE iso_code = ?", (country_iso,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Krajina s týmto kódom neexistuje.")
    
    try:
        cur.execute("""
            INSERT INTO media_outlets (country_iso, name, website_url, rss_url, category, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (country_iso, name, web_url, rss_url, category))
        media_id = cur.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Zdroj s týmto názvom alebo URL už existuje.")
    
    conn.close()
    return {"status": "ok", "media_id": media_id}

@app.delete("/api/media/{media_id}")
def delete_media(media_id: int, x_admin_pin: Optional[str] = Header(None)):
    verify_admin_pin(x_admin_pin)
    conn = get_db()
    cur = conn.cursor()
    # Vymažeme prípadné články alebo označíme ako neaktívny
    cur.execute("DELETE FROM articles WHERE media_id = ?", (media_id,))
    cur.execute("DELETE FROM media_outlets WHERE id = ?", (media_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.get("/api/alert-hits")
def get_alert_hits(limit: int = 50, country: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    where_clause = ""
    params = []
    if country:
        where_clause = "WHERE ar.country_iso = ?"
        params.append(country.upper())
    params.append(limit)
    cur.execute(f"""
        SELECT h.id as hit_id, h.article_id, al.name as alert_name, ar.title_orig, ar.url, ar.published_at, 
               m.name as media_name, c.name_sk as country_name, ar.country_iso, h.matched_text, h.triggered_at
        FROM alert_hits h
        JOIN alerts al ON h.alert_id = al.id
        JOIN articles ar ON h.article_id = ar.id
        JOIN media_outlets m ON ar.media_id = m.id
        JOIN countries c ON ar.country_iso = c.iso_code
        {where_clause}
        ORDER BY h.triggered_at DESC
        LIMIT ?
    """, tuple(params))
    hits = [dict(r) for r in cur.fetchall()]
    conn.close()
    return hits

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def index_page():
    html_path = '/root/spravodajsky_tep/web/index.html'
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Spravodajský Tep Sveta API beží.</h1>"
