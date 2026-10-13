"""
Seedovanie overených verejných Telegramových kanálov do databázy Spravodajského Tepu.
"""
import sqlite3

DB_PATH = '/root/spravodajsky_tep/data/tep_sveta.db'

TELEGRAM_CHANNELS = [
    # Globálne & USA
    {"country_iso": "US", "name": "Disclose.tv (TG)", "website_url": "https://t.me/disclosetv", "rss_url": "https://t.me/s/disclosetv", "category": "telegram"},
    {"country_iso": "US", "name": "The Spectator Index (TG)", "website_url": "https://t.me/spectatorindex", "rss_url": "https://t.me/s/spectatorindex", "category": "telegram"},
    {"country_iso": "US", "name": "Intel Republic (TG)", "website_url": "https://t.me/intelrepublic", "rss_url": "https://t.me/s/intelrepublic", "category": "telegram"},
    
    # Rusko / Východná Európa
    {"country_iso": "RU", "name": "Раньше всех. Ну почти (TG)", "website_url": "https://t.me/bbbreaking", "rss_url": "https://t.me/s/bbbreaking", "category": "telegram"},
    {"country_iso": "RU", "name": "Военный Осведомитель (TG)", "website_url": "https://t.me/milinfolive", "rss_url": "https://t.me/s/milinfolive", "category": "telegram"},
    {"country_iso": "RU", "name": "Рыбарь (TG)", "website_url": "https://t.me/rybar", "rss_url": "https://t.me/s/rybar", "category": "telegram"},
    
    # Ukrajina
    {"country_iso": "UA", "name": "Реальна Війна (TG)", "website_url": "https://t.me/voynareal", "rss_url": "https://t.me/s/voynareal", "category": "telegram"},
    {"country_iso": "UA", "name": "Лачен пише (TG)", "website_url": "https://t.me/lachentyt", "rss_url": "https://t.me/s/lachentyt", "category": "telegram"},
    
    # Blízky východ (Izrael / Irán)
    {"country_iso": "IL", "name": "Abu Ali Express (EN/TG)", "website_url": "https://t.me/abualiexpress", "rss_url": "https://t.me/s/abualiexpress", "category": "telegram"},
    {"country_iso": "IR", "name": "Tasnim News TG (EN)", "website_url": "https://t.me/Tasnimnews_EN", "rss_url": "https://t.me/s/Tasnimnews_EN", "category": "telegram"},
    
    # Slovensko & Česko
    {"country_iso": "SK", "name": "Správy RTVS / Aktuálne (TG)", "website_url": "https://t.me/spravysk", "rss_url": "https://t.me/s/spravysk", "category": "telegram"},
    {"country_iso": "CZ", "name": "ČT24 Zprávy (TG)", "website_url": "https://t.me/ct24zpravy", "rss_url": "https://t.me/s/ct24zpravy", "category": "telegram"}
]

def seed_telegram():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    added = 0
    for ch in TELEGRAM_CHANNELS:
        cur.execute("""
            INSERT OR IGNORE INTO media_outlets (country_iso, name, website_url, rss_url, category, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (ch['country_iso'], ch['name'], ch['website_url'], ch['rss_url'], ch['category']))
        if cur.rowcount > 0:
            added += 1

    conn.commit()
    print(f"Úspešne pridaných {added} verejných Telegram kanálov do databázy.")
    conn.close()

if __name__ == '__main__':
    seed_telegram()
