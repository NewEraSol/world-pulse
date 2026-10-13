"""
Asynchronny zberac spravodajskych RSS feedov A VEREJNYCH TELEGRAM KANALOV pre Spravodajsky Tep Sveta.
Podporuje standardne RSS/Atom feedy aj t.me/s/<channel> HTML preview.
"""
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

def parse_views_count(view_str: str) -> int:
    if not view_str:
        return 0
    v = view_str.strip().upper()
    try:
        if 'K' in v:
            return int(float(v.replace('K', '')) * 1000)
        elif 'M' in v:
            return int(float(v.replace('M', '')) * 1000000)
        return int(re.sub(r'[^\d]', '', v) or 0)
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
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, country_iso, name, rss_url, category FROM media_outlets WHERE is_active = 1 AND rss_url IS NOT NULL")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_active_alerts() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name, query_pattern FROM alerts WHERE is_active = 1")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

async def collect_all():
    media_list = get_active_media()
    alerts = get_active_alerts()
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Spúšťam zber pre {len(media_list)} médií a Telegram kanálov...")

    connector = aiohttp.TCPConnector(limit=30, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_source(session, m) for m in media_list]
        results = await asyncio.gather(*tasks)

    new_articles_count = 0
    alert_hits_count = 0
    active_alerts = get_active_alerts()

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
                    
                    # Titulok ako prvá veta alebo prvých 100 znakov
                    first_line = full_text.split('\n')[0].strip()
                    first_sentence = re.split(r'[.!?]', first_line)[0].strip()
                    title = first_sentence if len(first_sentence) > 15 else first_line[:120]
                    if not title:
                        title = full_text[:120]

                    date_el = m.find('time', class_='time')
                    views_el = m.find('span', class_='tgme_widget_message_views')
                    link_el = m.find('a', class_='tgme_widget_message_date')
                    post_url = link_el['href'] if link_el else f"{rss_url}/{hashlib.md5(full_text.encode()).hexdigest()}"
                    
                    views_count = parse_views_count(views_el.text) if views_el else 0
                    published = date_el['datetime'] if date_el and date_el.has_attr('datetime') else datetime.datetime.utcnow().isoformat()
                    guid = post_url

                    parsed_entries.append({
                        "title": title,
                        "url": post_url,
                        "perex": full_text[:400],
                        "full_text": full_text,
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

                # Clamp future published dates to current time so they don't block the feed
                now_iso = datetime.datetime.utcnow().isoformat()
                if published and published > now_iso:
                    published = now_iso

                # Okamžitý inline preklad nového titulku priamo pri zbere (nulové čakanie pre používateľa)
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

                    # Kontrola alertov s presnou extrakciou zachyteneho slova
                    search_str = f"{title} {perex} {full_text or ''}".lower()
                    for alert in alerts:
                        pattern = alert['query_pattern']
                        match = re.search(r'\b(' + pattern + r')\b', search_str, re.IGNORECASE)
                        if match:
                            found_keyword = match.group(0)
                            cur.execute("""
                                INSERT OR IGNORE INTO alert_hits (alert_id, article_id, matched_text)
                                VALUES (?, ?, ?)
                            """, (alert['id'], article_id, found_keyword))
                            alert_hits_count += 1
                            print(f"🚨 [ALARM: {alert['name']} | '{found_keyword}'] ({media['country_iso']} - {media['name']}): {title[:80]}")

                except sqlite3.IntegrityError:
                    pass

            cur.execute("UPDATE media_outlets SET last_scraped_at = CURRENT_TIMESTAMP WHERE id = ?", (media['id'],))

        except Exception as e:
            continue

    conn.commit()
    conn.close()
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Zber dokončený. Nových článkov/postov: {new_articles_count} | Odpálených alarmov: {alert_hits_count}")
    return new_articles_count, alert_hits_count

if __name__ == '__main__':
    asyncio.run(collect_all())
