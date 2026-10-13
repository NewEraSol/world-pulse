"""
Overeny zoznam oficialnych Telegram kanalov najvyssich statnikov a vladnych institucii.
Vsetky kanaly maju otestovany a overeny verejny web preview (t.me/s/...).
"""
import sqlite3

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

LEADERS_CHANNELS = [
    # Ukrajina
    {"country_iso": "UA", "name": "Volodymyr Zelenskyj (Prezident UA)", "website_url": "https://t.me/V_Zelenskiy_official", "rss_url": "https://t.me/s/V_Zelenskiy_official", "category": "telegram"},
    {"country_iso": "UA", "name": "Kancelária prezidenta UA (OPU)", "website_url": "https://t.me/OP_UA", "rss_url": "https://t.me/s/OP_UA", "category": "telegram"},
    {"country_iso": "UA", "name": "GUR Vojenská rozviedka UA", "website_url": "https://t.me/DIUkraine", "rss_url": "https://t.me/s/DIUkraine", "category": "telegram"},

    # Rusko
    {"country_iso": "RU", "name": "Kremeľ / Prezident RF (Oficiálny)", "website_url": "https://t.me/news_kremlin_ru", "rss_url": "https://t.me/s/news_kremlin_ru", "category": "telegram"},
    {"country_iso": "RU", "name": "Dmitrij Medvedev (Bezpečnostná rada)", "website_url": "https://t.me/medvedev_telegram", "rss_url": "https://t.me/s/medvedev_telegram", "category": "telegram"},
    {"country_iso": "RU", "name": "Ministerstvo obrany RF (MO)", "website_url": "https://t.me/mod_russia", "rss_url": "https://t.me/s/mod_russia", "category": "telegram"},
    {"country_iso": "RU", "name": "MZV Ruska (Oficiálne)", "website_url": "https://t.me/MID_Russia", "rss_url": "https://t.me/s/MID_Russia", "category": "telegram"},
    {"country_iso": "RU", "name": "Vláda Ruskej federácie", "website_url": "https://t.me/government_rus", "rss_url": "https://t.me/s/government_rus", "category": "telegram"},

    # Izrael
    {"country_iso": "IL", "name": "Benjamin Netanjahu (Premiér IL)", "website_url": "https://t.me/bnetanyahu", "rss_url": "https://t.me/s/bnetanyahu", "category": "telegram"},
    {"country_iso": "IL", "name": "IDF Izraelské obranné sily", "website_url": "https://t.me/idfofficial", "rss_url": "https://t.me/s/idfofficial", "category": "telegram"},

    # Irán
    {"country_iso": "IR", "name": "Ajatolláh Chameneí (Oficiálny FA)", "website_url": "https://t.me/Khamenei_ir", "rss_url": "https://t.me/s/Khamenei_ir", "category": "telegram"},
    {"country_iso": "IR", "name": "Ajatolláh Chameneí (Oficiálny EN)", "website_url": "https://t.me/Khamenei_en", "rss_url": "https://t.me/s/Khamenei_en", "category": "telegram"},
    {"country_iso": "IR", "name": "IRGC Revolučné gardy (Sepah News)", "website_url": "https://t.me/Sepahnews", "rss_url": "https://t.me/s/Sepahnews", "category": "telegram"},

    # Turecko
    {"country_iso": "TR", "name": "Recep Tayyip Erdoğan (Prezident TR)", "website_url": "https://t.me/RTErdogan", "rss_url": "https://t.me/s/RTErdogan", "category": "telegram"},

    # Francúzsko
    {"country_iso": "FR", "name": "Emmanuel Macron (Prezident FR)", "website_url": "https://t.me/emmanuelmacron", "rss_url": "https://t.me/s/emmanuelmacron", "category": "telegram"},

    # Slovensko
    {"country_iso": "SK", "name": "SMER-SD / Vládna koalícia (Oficiálny TG)", "website_url": "https://t.me/smersd", "rss_url": "https://t.me/s/smersd", "category": "telegram"}
]

def seed_leaders():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    added = 0
    for ch in LEADERS_CHANNELS:
        cur.execute("""
            INSERT OR IGNORE INTO media_outlets (country_iso, name, website_url, rss_url, category, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (ch['country_iso'], ch['name'], ch['website_url'], ch['rss_url'], ch['category']))
        if cur.rowcount > 0:
            added += 1

    conn.commit()
    print(f"Úspešne pridaných {added} oficiálnych kanálov štátnikov do databázy.")
    conn.close()

if __name__ == '__main__':
    seed_leaders()
