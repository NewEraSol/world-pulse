"""
Katalog krajin a TOP 5 medii pre Spravodajsky Tep Sveta.
Zamerane na mienkotvorne, najcitanersie a overene spravodajske a ekonomicke domy.
"""

INITIAL_COUNTRIES = [
    {"iso_code": "SK", "name_sk": "Slovensko", "name_en": "Slovakia", "region": "Europe", "primary_language": "sk"},
    {"iso_code": "CZ", "name_sk": "Česká republika", "name_en": "Czech Republic", "region": "Europe", "primary_language": "cs"},
    {"iso_code": "US", "name_sk": "Spojené štáty", "name_en": "United States", "region": "North America", "primary_language": "en"},
    {"iso_code": "GB", "name_sk": "Veľká Británia", "name_en": "United Kingdom", "region": "Europe", "primary_language": "en"},
    {"iso_code": "DE", "name_sk": "Nemecko", "name_en": "Germany", "region": "Europe", "primary_language": "de"},
    {"iso_code": "FR", "name_sk": "Francúzsko", "name_en": "France", "region": "Europe", "primary_language": "fr"},
    {"iso_code": "CN", "name_sk": "Čína", "name_en": "China", "region": "Asia", "primary_language": "zh"},
    {"iso_code": "RU", "name_sk": "Rusko", "name_en": "Russia", "region": "Europe/Asia", "primary_language": "ru"},
    {"iso_code": "JP", "name_sk": "Japonsko", "name_en": "Japan", "region": "Asia", "primary_language": "ja"},
    {"iso_code": "SA", "name_sk": "Saudská Arábia", "name_en": "Saudi Arabia", "region": "Middle East", "primary_language": "ar"},
    {"iso_code": "IN", "name_sk": "India", "name_en": "India", "region": "Asia", "primary_language": "en"},
    {"iso_code": "BR", "name_sk": "Brazília", "name_en": "Brazil", "region": "South America", "primary_language": "pt"},
    {"iso_code": "IL", "name_sk": "Izrael", "name_en": "Israel", "region": "Middle East", "primary_language": "he"},
    {"iso_code": "IR", "name_sk": "Irán", "name_en": "Iran", "region": "Middle East", "primary_language": "fa"},
    {"iso_code": "PL", "name_sk": "Poľsko", "name_en": "Poland", "region": "Europe", "primary_language": "pl"},
    {"iso_code": "UA", "name_sk": "Ukrajina", "name_en": "Ukraine", "region": "Europe", "primary_language": "uk"},
    {"iso_code": "AU", "name_sk": "Austrália", "name_en": "Australia", "region": "Oceania", "primary_language": "en"},
    {"iso_code": "CA", "name_sk": "Kanada", "name_en": "Canada", "region": "North America", "primary_language": "en"},
    {"iso_code": "CH", "name_sk": "Švajčiarsko", "name_en": "Switzerland", "region": "Europe", "primary_language": "de"},
    {"iso_code": "SG", "name_sk": "Singapur", "name_en": "Singapore", "region": "Asia", "primary_language": "en"}
]

# TOP 5 portalov pre kazdu krajinu so spolahlivymi RSS feedmi
MEDIA_OUTLETS = [
    # SLOVENSKO (SK)
    {"country_iso": "SK", "name": "Aktuality.sk", "website_url": "https://www.aktuality.sk", "rss_url": "https://www.aktuality.sk/rss/", "category": "general"},
    {"country_iso": "SK", "name": "SME.sk", "website_url": "https://www.sme.sk", "rss_url": "https://rss.sme.sk/rss/rss.asp?id=frontpage", "category": "general"},
    {"country_iso": "SK", "name": "Pravda.sk", "website_url": "https://spravy.pravda.sk", "rss_url": "https://spravy.pravda.sk/rss/xml/", "category": "general"},
    {"country_iso": "SK", "name": "Hospodárske noviny", "website_url": "https://hnonline.sk", "rss_url": "https://hnonline.sk/feed", "category": "business"},
    {"country_iso": "SK", "name": "Denník N", "website_url": "https://dennikn.sk", "rss_url": "https://dennikn.sk/feed/", "category": "general"},

    # ČESKO (CZ)
    {"country_iso": "CZ", "name": "Novinky.cz", "website_url": "https://www.novinky.cz", "rss_url": "https://www.novinky.cz/rss", "category": "general"},
    {"country_iso": "CZ", "name": "iDNES.cz", "website_url": "https://www.idnes.cz", "rss_url": "https://servis.idnes.cz/rss.aspx?c=zpravodaj", "category": "general"},
    {"country_iso": "CZ", "name": "Seznam Zprávy", "website_url": "https://www.seznamzpravy.cz", "rss_url": "https://www.seznamzpravy.cz/rss", "category": "general"},
    {"country_iso": "CZ", "name": "ČT24", "website_url": "https://ct24.ceskatelevize.cz", "rss_url": "https://ct24.ceskatelevize.cz/rss/hlavni-zpravy", "category": "general"},
    {"country_iso": "CZ", "name": "E15.cz", "website_url": "https://www.e15.cz", "rss_url": "https://www.e15.cz/rss", "category": "business"},

    # SPOJENÉ ŠTÁTY (US)
    {"country_iso": "US", "name": "Reuters US", "website_url": "https://www.reuters.com", "rss_url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best", "category": "business"},
    {"country_iso": "US", "name": "Wall Street Journal", "website_url": "https://www.wsj.com", "rss_url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "category": "business"},
    {"country_iso": "US", "name": "New York Times", "website_url": "https://www.nytimes.com", "rss_url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "category": "general"},
    {"country_iso": "US", "name": "CNBC", "website_url": "https://www.cnbc.com", "rss_url": "https://search.cnbc.com/rs/search/combined hazard/rss/rss.html?partnerId=wrss01&id=100003114", "category": "business"},
    {"country_iso": "US", "name": "Bloomberg Markets", "website_url": "https://www.bloomberg.com", "rss_url": "https://feeds.bloomberg.com/markets/news.rss", "category": "business"},

    # VEĽKÁ BRITÁNIA (GB)
    {"country_iso": "GB", "name": "BBC News", "website_url": "https://www.bbc.com/news", "rss_url": "https://feeds.bbci.co.uk/news/world/rss.xml", "category": "general"},
    {"country_iso": "GB", "name": "Financial Times", "website_url": "https://www.ft.com", "rss_url": "https://www.ft.com/world?format=rss", "category": "business"},
    {"country_iso": "GB", "name": "The Guardian", "website_url": "https://www.theguardian.com", "rss_url": "https://www.theguardian.com/world/rss", "category": "general"},
    {"country_iso": "GB", "name": "The Telegraph", "website_url": "https://www.telegraph.co.uk", "rss_url": "https://www.telegraph.co.uk/news/rss.xml", "category": "general"},
    {"country_iso": "GB", "name": "The Economist", "website_url": "https://www.economist.com", "rss_url": "https://www.economist.com/the-world-this-week/rss.xml", "category": "business"},

    # NEMECKO (DE)
    {"country_iso": "DE", "name": "Der Spiegel", "website_url": "https://www.spiegel.de", "rss_url": "https://www.spiegel.de/schlagzeilen/index.rss", "category": "general"},
    {"country_iso": "DE", "name": "Handelsblatt", "website_url": "https://www.handelsblatt.com", "rss_url": "https://www.handelsblatt.com/contentexport/feed/top-themen", "category": "business"},
    {"country_iso": "DE", "name": "Frankfurter Allgemeine (FAZ)", "website_url": "https://www.faz.net", "rss_url": "https://www.faz.net/rss/aktuell/", "category": "general"},
    {"country_iso": "DE", "name": "Die Welt", "website_url": "https://www.welt.de", "rss_url": "https://www.welt.de/feeds/topnews.rss", "category": "general"},
    {"country_iso": "DE", "name": "Tagesschau", "website_url": "https://www.tagesschau.de", "rss_url": "https://www.tagesschau.de/xml/rss2/", "category": "general"},

    # FRANCÚZSKO (FR)
    {"country_iso": "FR", "name": "Le Monde", "website_url": "https://www.lemonde.fr", "rss_url": "https://www.lemonde.fr/rss/une.xml", "category": "general"},
    {"country_iso": "FR", "name": "Le Figaro", "website_url": "https://www.lefigaro.fr", "rss_url": "https://www.lefigaro.fr/rss/figaro_actualites.xml", "category": "general"},
    {"country_iso": "FR", "name": "Les Echos", "website_url": "https://www.lesechos.fr", "rss_url": "https://services.lesechos.fr/rss/les-echos-une.xml", "category": "business"},
    {"country_iso": "FR", "name": "France 24", "website_url": "https://www.france24.com/fr", "rss_url": "https://www.france24.com/fr/rss", "category": "general"},
    {"country_iso": "FR", "name": "Libération", "website_url": "https://www.liberation.fr", "rss_url": "https://www.liberation.fr/arc/outboundfeeds/rss-all/collection/accueil-une/", "category": "general"},

    # ČÍNA (CN) - štátne + medzinárodné anglické aj čínske vydania
    {"country_iso": "CN", "name": "Xinhua News (EN)", "website_url": "https://english.news.cn", "rss_url": "https://www.news.cn/english/rss/worldrss.xml", "category": "general"},
    {"country_iso": "CN", "name": "South China Morning Post", "website_url": "https://www.scmp.com", "rss_url": "https://www.scmp.com/rss/91/feed", "category": "general"},
    {"country_iso": "CN", "name": "Global Times", "website_url": "https://www.globaltimes.cn", "rss_url": "https://www.globaltimes.cn/rss/world.xml", "category": "general"},
    {"country_iso": "CN", "name": "Caixin Global", "website_url": "https://www.caixinglobal.com", "rss_url": "https://www.caixinglobal.com/upload/rss/business.xml", "category": "business"},
    {"country_iso": "CN", "name": "People's Daily Online", "website_url": "http://en.people.cn", "rss_url": "http://en.people.cn/rss/90000.xml", "category": "general"},

    # RUSKO (RU)
    {"country_iso": "RU", "name": "Kommersant", "website_url": "https://www.kommersant.ru", "rss_url": "https://www.kommersant.ru/RSS/news.xml", "category": "business"},
    {"country_iso": "RU", "name": "RBC (РБК)", "website_url": "https://www.rbc.ru", "rss_url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss", "category": "business"},
    {"country_iso": "RU", "name": "TASS", "website_url": "https://tass.com", "rss_url": "https://tass.com/rss/v2.xml", "category": "general"},
    {"country_iso": "RU", "name": "Vedomosti", "website_url": "https://www.vedomosti.ru", "rss_url": "https://www.vedomosti.ru/rss/news", "category": "business"},
    {"country_iso": "RU", "name": "RIA Novosti", "website_url": "https://ria.ru", "rss_url": "https://ria.ru/export/rss2/archive/index.xml", "category": "general"},

    # JAPONSKO (JP)
    {"country_iso": "JP", "name": "Nikkei Asia", "website_url": "https://asia.nikkei.com", "rss_url": "https://asia.nikkei.com/rss/feed/nar", "category": "business"},
    {"country_iso": "JP", "name": "The Japan Times", "website_url": "https://www.japantimes.co.jp", "rss_url": "https://www.japantimes.co.jp/feed/", "category": "general"},
    {"country_iso": "JP", "name": "NHK World", "website_url": "https://www3.nhk.or.jp/nhkworld/", "rss_url": "https://www3.nhk.or.jp/rss/news/cat0.xml", "category": "general"},
    {"country_iso": "JP", "name": "Asahi Shimbun", "website_url": "https://www.asahi.com", "rss_url": "http://rss.asahi.com/rss/asahi/newsheadlines.rdf", "category": "general"},
    {"country_iso": "JP", "name": "Mainichi Shimbun", "website_url": "https://mainichi.jp", "rss_url": "https://mainichi.jp/rss/etc/mainichi-flash.rss", "category": "general"},

    # SAUDSKÁ ARÁBIA & PERZSKÝ ZÁLIV (SA)
    {"country_iso": "SA", "name": "Arab News", "website_url": "https://www.arabnews.com", "rss_url": "https://www.arabnews.com/rss.xml", "category": "general"},
    {"country_iso": "SA", "name": "Al Arabiya (EN)", "website_url": "https://english.alarabiya.net", "rss_url": "https://english.alarabiya.net/.mrss/en/news.xml", "category": "general"},
    {"country_iso": "SA", "name": "Saudi Gazette", "website_url": "https://saudigazette.com.sa", "rss_url": "https://saudigazette.com.sa/rss", "category": "general"},
    {"country_iso": "SA", "name": "Asharq Al-Awsat (EN)", "website_url": "https://english.aawsat.com", "rss_url": "https://english.aawsat.com/feed", "category": "general"},
    {"country_iso": "SA", "name": "Argaam Financial", "website_url": "https://www.argaam.com", "rss_url": "https://www.argaam.com/en/rss", "category": "business"},

    # INDIA (IN)
    {"country_iso": "IN", "name": "The Economic Times", "website_url": "https://economictimes.indiatimes.com", "rss_url": "https://economictimes.indiatimes.com/rssfeedsdefault.cms", "category": "business"},
    {"country_iso": "IN", "name": "Times of India", "website_url": "https://timesofindia.indiatimes.com", "rss_url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "category": "general"},
    {"country_iso": "IN", "name": "Business Standard", "website_url": "https://www.business-standard.com", "rss_url": "https://www.business-standard.com/rss/home_page_top_stories.rss", "category": "business"},
    {"country_iso": "IN", "name": "The Hindu", "website_url": "https://www.thehindu.com", "rss_url": "https://www.thehindu.com/news/national/feeder/default.rss", "category": "general"},
    {"country_iso": "IN", "name": "NDTV", "website_url": "https://www.ndtv.com", "rss_url": "https://feeds.feedburner.com/ndtvnews-top-stories", "category": "general"}
]
