"""
Modul pre automaticky preklad a extrakciu plneho textu clankov (Full-text On Demand & Caching).
Preklada cele telo clanku do Slovenciny aj Anglictiny s ukladanim do DB a robustnymi fallbackmi.
"""
import sqlite3
import trafilatura
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from robust_translator import robust_translate, robust_batch_translate, is_substantially_different

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

def translate_chunks(text: str, target_lang: str) -> str:
    """
    Rozdeli dlhy text na odseky a prelozi ich spolahlivo do cieloveho jazyka.
    """
    if not text or len(text.strip()) == 0:
        return ""
    
    raw_lines = text.split("\n")
    paragraphs = []
    for line in raw_lines:
        c = line.strip()
        if c:
            paragraphs.append(c)

    if not paragraphs:
        return ""

    translated_paras = []
    current_chunk = []
    current_len = 0

    for p in paragraphs:
        if current_len + len(p) > 700:
            chunk_text = "\n".join(current_chunk)
            t = robust_translate(chunk_text, target_lang)
            translated_paras.append(t if t else chunk_text)
            current_chunk = [p]
            current_len = len(p)
        else:
            current_chunk.append(p)
            current_len += len(p) + 1

    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        t = robust_translate(chunk_text, target_lang)
        translated_paras.append(t if t else chunk_text)

    return "\n\n".join(translated_paras)

def get_or_translate_article(article_id: int):
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT a.*, m.name as media_name, c.name_sk as country_name, c.primary_language
        FROM articles a
        JOIN media_outlets m ON a.media_id = m.id
        JOIN countries c ON a.country_iso = c.iso_code
        WHERE a.id = ?
    """, (article_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    art = dict(row)
    needs_update = False

    # 1. Extrakcia plného originálneho textu článku, ak ešte nie je v DB
    full_text_orig = art.get('content_snippet')
    if not full_text_orig or len(full_text_orig.strip()) < 100:
        try:
            downloaded = trafilatura.fetch_url(art['url'])
            if downloaded:
                extracted = trafilatura.extract(downloaded)
                if extracted and len(extracted.strip()) > len(full_text_orig or ""):
                    full_text_orig = extracted
                    needs_update = True
        except Exception:
            pass

    if not full_text_orig:
        full_text_orig = art.get('perex_orig') or "Originálny plný text sa nepodarilo automaticky stiahnuť. Prosím použite priamy odkaz na stránku média."

    # 2. Preklad titulku
    orig_lang = art.get('primary_language', 'en')
    title_sk = art.get('title_sk')
    title_en = art.get('title_en')

    # Ak je cudzojazycny a preklad sa rovna originalu (chybna cache), vynutime novy preklad
    if not title_sk or (orig_lang not in ['sk', 'cs'] and title_sk == art['title_orig']):
        if orig_lang == 'sk':
            title_sk = art['title_orig']
        else:
            title_sk = robust_translate(art['title_orig'], 'sk')
        needs_update = True

    if not title_en or (orig_lang != 'en' and title_en == art['title_orig']):
        if orig_lang == 'en':
            title_en = art['title_orig']
        else:
            title_en = robust_translate(art['title_orig'], 'en')
        needs_update = True

    # 3. Preklad celého tela článku (Full Text do SK a EN) s ukladaním do DB
    full_text_sk = art.get('content_sk') or ""
    full_text_en = art.get('content_en') or ""

    if orig_lang in ['sk', 'cs']:
        full_text_sk = full_text_orig
        if not full_text_en:
            full_text_en = translate_chunks(full_text_orig[:4000], 'en')
            needs_update = True
    elif orig_lang == 'en':
        full_text_en = full_text_orig
        if not full_text_sk:
            full_text_sk = translate_chunks(full_text_orig[:4000], 'sk')
            needs_update = True
    else:
        # Cudzí jazyk (ukrajinčina, ruština, čínština, nemčina atď.)
        if not full_text_sk or full_text_sk == full_text_orig or not is_substantially_different(full_text_orig, full_text_sk):
            full_text_sk = translate_chunks(full_text_orig[:4000], 'sk')
            needs_update = True
        if not full_text_en or full_text_en == full_text_orig or not is_substantially_different(full_text_orig, full_text_en):
            full_text_en = translate_chunks(full_text_orig[:4000], 'en')
            needs_update = True

    if needs_update:
        cur.execute("""
            UPDATE articles
            SET title_sk = ?, title_en = ?, content_snippet = ?, content_sk = ?, content_en = ?
            WHERE id = ?
        """, (title_sk, title_en, full_text_orig, full_text_sk, full_text_en, article_id))
        conn.commit()

    art['title_sk'] = title_sk
    art['title_en'] = title_en
    art['full_text_orig'] = full_text_orig
    art['full_text_sk'] = full_text_sk or full_text_orig
    art['full_text_en'] = full_text_en or full_text_orig

    # Zoznam aktívnych alertov pre zvýraznenie
    cur.execute("SELECT name, query_pattern FROM alerts WHERE is_active = 1")
    alerts = [dict(a) for a in cur.fetchall()]
    art['active_radar_patterns'] = alerts

    conn.close()
    return art
