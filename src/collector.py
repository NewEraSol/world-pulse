"""
Asynchronny zberac spravodajskych RSS feedov A VEREJNYCH TELEGRAM KANALOV pre Spravodajsky Tep Sveta.
Podporuje standardne RSS/Atom feedy aj t.me/s/<channel> HTML preview.
"""
import sys
def print_flush(*args, **kwargs):
    kwargs['flush'] = True
    print(*args, **kwargs)

import asyncio
import aiohttp
import feedparser
import sqlite3
import re
import datetime
import hashlib
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from robust_translator import robust_translate, is_substantially_different

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return ' '.join(cleantext.split()).strip()

def extract_telegram_clean_content(text_el):
    if not text_el:
        return '', '', ''
    full_text = text_el.get_text(separator='\n').strip()
    if not full_text:
        return '', '', ''

    # Odstranenie úvodných emoji a prázdnych symbolov
    clean_no_lead_emoji = re.sub(r'^[\s\W_]+', '', full_text).strip()
    one_line = ' '.join([l.strip() for l in clean_no_lead_emoji.split('\n') if l.strip()])
    
    # Vyhľadanie prvej zmysluplnej vety
    sentences = re.split(r'(?<=[.!?])\s+', one_line)
    if sentences and len(sentences[0]) >= 12:
        title = sentences[0]
    else:
        title = one_line
        
    if len(title) > 130:
        title = title[:127] + '...'
    if not title:
        title = full_text[:80]

    perex = full_text[:400]
    return title.strip(), perex, full_text

def parse_views_count(view_str: str) -> int:
    if not view_str:
        return 0
    v = view_str.strip().upper()
    try:
        if 'K' in v:
            return int(float(v.replace('K', '')) * 1000)
        elif 'M' in v:
            return int(float(v.replace('M', '')) * 1000000)
        return int(v)
    except Exception:
        return 0

async def fetch_source(session: aiohttp.ClientSession, media: Dict[str, Any]) -> tuple:
    rss_url = media['rss_url']
    if not rss_url:
        return media, None
    try:
        async with session.get(rss_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=12)) as response:
            if response.status == 200:
                text = await response.text()
                return media, text
            else:
                return media, None
    except Exception:
        return media, None

def get_active_media() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, country_iso, name, rss_url, category FROM media_outlets WHERE is_active = 1 AND rss_url IS NOT NULL")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_active_alerts() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name, query_pattern FROM alerts WHERE is_active = 1")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

async def collect_all():
    media_list = get_active_media()
    alerts = get_active_alerts()
    print_flush(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Spúšťam zber pre {len(media_list)} médií a Telegram kanálov...")

    connector = aiohttp.TCPConnector(limit=30, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_source(session, m) for m in media_list]
        results = await asyncio.gather(*tasks)

    # Otvoríme databázu
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    cur = conn.cursor()

    new_articles_count = 0
    alert_hits_count = 0

    for media, raw_content in results:
        if not raw_content:
            continue
        try:
            category = media.get('category', 'general')
            rss_url = media['rss_url']
            is_telegram = category == 'telegram' or 't.me/s/' in rss_url

            parsed_entries = []

            # ---------------- A: TELEGRAM CHANNEL PARSER ----------------
            if is_telegram:
                soup = BeautifulSoup(raw_content, 'html.parser')
                messages = soup.find_all('div', class_='tgme_widget_message_wrap')
                for m in messages:
                    text_el = m.find('div', class_='tgme_widget_message_text')
                    if not text_el:
                        continue
                    full_text = text_el.get_text(separator='\n').strip()
                    if not full_text:
                        continue
                    
                    title, perex, clean_full_text = extract_telegram_clean_content(text_el)
                    if not title or len(title) < 4:
                        continue

                    post_link_el = m.find('a', class_='tgme_widget_message_date')
                    post_url = post_link_el['href'] if post_link_el and post_link_el.has_attr('href') else rss_url

                    views_el = m.find('span', class_='tgme_widget_message_views')
                    views_count = parse_views_count(views_el.text) if views_el else 0

                    date_el = m.find('time', class_='time')
                    published = date_el['datetime'] if date_el and date_el.has_attr('datetime') else datetime.datetime.utcnow().isoformat()
                    guid = post_url

                    parsed_entries.append({
                        "title": title,
                        "url": post_url,
                        "perex": perex,
                        "full_text": clean_full_text,
                        "published": published,
                        "guid": guid,
                        "views": views_count
                    })

            # ---------------- B: STANDARD RSS / ATOM PARSER ----------------
            else:
                feed = feedparser.parse(raw_content)
                if feed.entries:
                    for entry in feed.entries[:30]:
                        title = clean_html(entry.get('title', ''))
                        if not title:
                            continue
                        link = entry.get('link', '')
                        perex = clean_html(entry.get('summary', '') or entry.get('description', ''))
                        guid = entry.get('id', link)
                        if not guid:
                            guid = hashlib.md5((title + link).encode('utf-8')).hexdigest()

                        published = None
                        if 'published_parsed' in entry and entry.published_parsed:
                            published = datetime.datetime(*entry.published_parsed[:6]).isoformat()
                        elif 'updated_parsed' in entry and entry.updated_parsed:
                            published = datetime.datetime(*entry.updated_parsed[:6]).isoformat()
                        else:
                            published = datetime.datetime.utcnow().isoformat()

                        parsed_entries.append({
                            "title": title,
                            "url": link,
                            "perex": perex,
                            "full_text": None,
                            "published": published,
                            "guid": guid,
                            "views": 0
                        })

            # Uloženie položiek do databázy
            for item in parsed_entries:
                title = item['title']
                link = item['url']
                perex = item['perex']
                guid = item['guid']
                published = item['published']
                full_text = item['full_text']
                views = item['views']

                now_iso = datetime.datetime.utcnow().isoformat()
                if published and published > now_iso:
                    published = now_iso

                # Rýchla kontrola, či guid už v DB existuje
                cur.execute("SELECT id FROM articles WHERE guid = ? LIMIT 1", (guid,))
                if cur.fetchone():
                    continue

                # Preklad nového článku
                c_iso = media.get('country_iso', '')
                t_sk = None
                t_en = None
                if c_iso in ['SK', 'CZ']:
                    t_sk = title
                elif c_iso in ['US', 'GB', 'CA', 'AU']:
                    t_en = title
                    try:
                        t_sk = robust_translate(title, 'sk')
                    except Exception:
                        t_sk = None
                else:
                    try:
                        t_sk = robust_translate(title, 'sk')
                        t_en = robust_translate(title, 'en')
                    except Exception:
                        pass

                try:
                    cur.execute("""
                        INSERT INTO articles (media_id, country_iso, guid, url, title_orig, title_sk, title_en, perex_orig, content_snippet, published_at, engagement_likes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (media['id'], media['country_iso'], guid, link, title, t_sk, t_en, perex, full_text, published, views))
                    article_id = cur.lastrowid
                    new_articles_count += 1
                    conn.commit() # Commitneme každý nový článok okamžite!

                    # Kontrola alertov
                    searched_text = (title + " " + (perex or "")).lower()
                    for alert in alerts:
                        query_p = alert['query_pattern'].lower()
                        terms = [t.strip() for t in query_p.replace(';', '|').replace(',', '|').split('|') if t.strip()]
                        matched_word = None
                        for term in terms:
                            is_simple_word = bool(re.match(r'^[a-zA-Z0-9á-žÁ-Ž]+$', term))
                            if is_simple_word:
                                if re.search(r'\b' + re.escape(term) + r'\b', searched_text):
                                    matched_word = term
                                    break
                            else:
                                if term in searched_text:
                                    matched_word = term
                                    break

                        if matched_word:
                            cur.execute("""
                                INSERT OR IGNORE INTO alert_hits (alert_id, article_id, matched_text)
                                VALUES (?, ?, ?)
                            """, (alert['id'], article_id, matched_word))
                            alert_hits_count += 1
                            conn.commit()
                            print_flush(f"🚨 [ALARM: {alert['name']} | '{matched_word}'] ({media['country_iso']} - {media['name']}): {title[:80]}")

                except sqlite3.IntegrityError:
                    pass

            cur.execute("UPDATE media_outlets SET last_scraped_at = CURRENT_TIMESTAMP WHERE id = ?", (media['id'],))
            conn.commit()

        except Exception as e:
            continue

    conn.close()
    print_flush(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Zber dokončený. Nových článkov/postov: {new_articles_count} | Odpálených alarmov: {alert_hits_count}")
    return new_articles_count, alert_hits_count

if __name__ == '__main__':
    asyncio.run(collect_all())
