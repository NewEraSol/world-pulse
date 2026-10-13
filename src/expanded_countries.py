"""
Rozsireny zoznam krajin a TOP medii pre Spravodajsky Tep Sveta.
Pokryva:
- Zvysnych 9 krajin z povodnych 20 (AU, CA, BR, PL, UA, IL, IR, CH, SG)
- Dalsie klucove geopoliticke a ekonomicke staty:
  Turecko (TR), UAE (AE), Juzna Korea (KR), Taiwan (TW), Taliansko (IT), Spanielsko (ES),
  Holandsko (NL), Norsko (NO), Svedsko (SE), Rakusko (AT), Madarsko (HU),
  Mexiko (MX), Argentina (AR), Juzna Afrika (ZA), Indonezia (ID), Vietnam (VN), Egypt (EG), Grecko (GR)
"""

NEW_COUNTRIES = [
    # Doplnenie chyStorage
    {"iso_code": "TR", "name_sk": "Turecko", "name_en": "Turkey", "region": "Middle East/Europe", "primary_language": "tr"},
    {"iso_code": "AE", "name_sk": "Spojené arabské emiráty", "name_en": "United Arab Emirates", "region": "Middle East", "primary_language": "ar"},
    {"iso_code": "KR", "name_sk": "Južná Kórea", "name_en": "South Korea", "region": "Asia", "primary_language": "ko"},
    {"iso_code": "TW", "name_sk": "Taiwan", "name_en": "Taiwan", "region": "Asia", "primary_language": "zh"},
    {"iso_code": "IT", "name_sk": "Taliansko", "name_en": "Italy", "region": "Europe", "primary_language": "it"},
    {"iso_code": "ES", "name_sk": "Španielsko", "name_en": "Spain", "region": "Europe", "primary_language": "es"},
    {"iso_code": "NL", "name_sk": "Holandsko", "name_en": "Netherlands", "region": "Europe", "primary_language": "nl"},
    {"iso_code": "NO", "name_sk": "Nórsko", "name_en": "Norway", "region": "Europe", "primary_language": "no"},
    {"iso_code": "SE", "name_sk": "Švédsko", "name_en": "Sweden", "region": "Europe", "primary_language": "sv"},
    {"iso_code": "AT", "name_sk": "Rakúsko", "name_en": "Austria", "region": "Europe", "primary_language": "de"},
    {"iso_code": "HU", "name_sk": "Maďarsko", "name_en": "Hungary", "region": "Europe", "primary_language": "hu"},
    {"iso_code": "MX", "name_sk": "Mexiko", "name_en": "Mexico", "region": "North America", "primary_language": "es"},
    {"iso_code": "AR", "name_sk": "Argentína", "name_en": "Argentina", "region": "South America", "primary_language": "es"},
    {"iso_code": "ZA", "name_sk": "Južná Afrika", "name_en": "South Africa", "region": "Africa", "primary_language": "en"},
    {"iso_code": "ID", "name_sk": "Indonézia", "name_en": "Indonesia", "region": "Asia", "primary_language": "id"},
    {"iso_code": "VN", "name_sk": "Vietnam", "name_en": "Vietnam", "region": "Asia", "primary_language": "vi"},
    {"iso_code": "EG", "name_sk": "Egypt", "name_en": "Egypt", "region": "Middle East/Africa", "primary_language": "ar"},
    {"iso_code": "GR", "name_sk": "Grécko", "name_en": "Greece", "region": "Europe", "primary_language": "el"},
    {"iso_code": "QA", "name_sk": "Katar", "name_en": "Qatar", "region": "Middle East", "primary_language": "ar"}
]

EXPANDED_MEDIA = [
    # AUSTRÁLIA (AU)
    {"country_iso": "AU", "name": "ABC News Australia", "website_url": "https://www.abc.net.au", "rss_url": "https://www.abc.net.au/news/feed/51120/rss.xml", "category": "general"},
    {"country_iso": "AU", "name": "Sydney Morning Herald", "website_url": "https://www.smh.com.au", "rss_url": "https://www.smh.com.au/rss/feed.xml", "category": "general"},
    {"country_iso": "AU", "name": "The Age", "website_url": "https://www.theage.com.au", "rss_url": "https://www.theage.com.au/rss/feed.xml", "category": "general"},
    {"country_iso": "AU", "name": "SBS News", "website_url": "https://www.sbs.com.au", "rss_url": "https://www.sbs.com.au/news/topic/latest/feed", "category": "general"},

    # KANADA (CA)
    {"country_iso": "CA", "name": "CBC News", "website_url": "https://www.cbc.ca", "rss_url": "https://www.cbc.ca/cmlink/rss-topstories", "category": "general"},
    {"country_iso": "CA", "name": "The Globe and Mail", "website_url": "https://www.theglobeandmail.com", "rss_url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/", "category": "business"},
    {"country_iso": "CA", "name": "Financial Post", "website_url": "https://financialpost.com", "rss_url": "https://financialpost.com/feed", "category": "business"},
    {"country_iso": "CA", "name": "Toronto Star", "website_url": "https://www.thestar.com", "rss_url": "https://www.thestar.com/search/?f=rss&t=article&c=news*&l=50&s=start_time&sd=desc", "category": "general"},

    # BRAZÍLIA (BR)
    {"country_iso": "BR", "name": "G1 Globo", "website_url": "https://g1.globo.com", "rss_url": "https://g1.globo.com/rss/g1/", "category": "general"},
    {"country_iso": "BR", "name": "Folha de S.Paulo", "website_url": "https://www.folha.uol.com.br", "rss_url": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml", "category": "general"},
    {"country_iso": "BR", "name": "Valor Econômico", "website_url": "https://valor.globo.com", "rss_url": "https://valor.globo.com/rss/brasil/", "category": "business"},
    {"country_iso": "BR", "name": "Poder360", "website_url": "https://www.poder360.com.br", "rss_url": "https://www.poder360.com.br/feed/", "category": "politics"},

    # POĽSKO (PL)
    {"country_iso": "PL", "name": "Onet.pl", "website_url": "https://www.onet.pl", "rss_url": "https://wiadomosci.onet.pl/.feed", "category": "general"},
    {"country_iso": "PL", "name": "Wirtualna Polska (WP)", "website_url": "https://www.wp.pl", "rss_url": "https://wiadomosci.wp.pl/rss.xml", "category": "general"},
    {"country_iso": "PL", "name": "Rzeczpospolita", "website_url": "https://www.rp.pl", "rss_url": "https://www.rp.pl/rss/ekonomia", "category": "business"},
    {"country_iso": "PL", "name": "Bankier.pl", "website_url": "https://www.bankier.pl", "rss_url": "https://www.bankier.pl/rss/wiadomosci.xml", "category": "business"},

    # UKRAJINA (UA)
    {"country_iso": "UA", "name": "Ukrayinska Pravda", "website_url": "https://www.pravda.com.ua", "rss_url": "https://www.pravda.com.ua/rss/", "category": "general"},
    {"country_iso": "UA", "name": "The Kyiv Independent (EN)", "website_url": "https://kyivindependent.com", "rss_url": "https://kyivindependent.com/feed/", "category": "general"},
    {"country_iso": "UA", "name": "UNIAN", "website_url": "https://www.unian.ua", "rss_url": "https://rss.unian.ua/site/news_ukr.rss", "category": "general"},
    {"country_iso": "UA", "name": "NV.ua", "website_url": "https://nv.ua", "rss_url": "https://nv.ua/rss/all.xml", "category": "general"},

    # IZRAEL (IL)
    {"country_iso": "IL", "name": "The Times of Israel (EN)", "website_url": "https://www.timesofisrael.com", "rss_url": "https://www.timesofisrael.com/feed/", "category": "general"},
    {"country_iso": "IL", "name": "The Jerusalem Post", "website_url": "https://www.jpost.com", "rss_url": "https://www.jpost.com/rss/rssfeedsfrontpage.aspx", "category": "general"},
    {"country_iso": "IL", "name": "Haaretz (EN)", "website_url": "https://www.haaretz.com", "rss_url": "https://www.haaretz.com/cmlink/1.4605988", "category": "general"},
    {"country_iso": "IL", "name": "Globes Israel Business", "website_url": "https://en.globes.co.il", "rss_url": "https://en.globes.co.il/webservice/rss/rssfeeden.xml", "category": "business"},

    # IRÁN (IR)
    {"country_iso": "IR", "name": "Tehran Times (EN)", "website_url": "https://www.tehrantimes.com", "rss_url": "https://www.tehrantimes.com/rss", "category": "general"},
    {"country_iso": "IR", "name": "Press TV (EN)", "website_url": "https://www.presstv.ir", "rss_url": "https://www.presstv.ir/RSS", "category": "general"},
    {"country_iso": "IR", "name": "Tasnim News (EN)", "website_url": "https://www.tasnimnews.com/en", "rss_url": "https://www.tasnimnews.com/en/rss/feed/0/0/0/all", "category": "general"},
    {"country_iso": "IR", "name": "Mehr News (EN)", "website_url": "https://en.mehrnews.com", "rss_url": "https://en.mehrnews.com/rss", "category": "general"},

    # ŠVAJČIARSKO (CH)
    {"country_iso": "CH", "name": "Neue Zürcher Zeitung (NZZ)", "website_url": "https://www.nzz.ch", "rss_url": "https://www.nzz.ch/recent.rss", "category": "general"},
    {"country_iso": "CH", "name": "Tages-Anzeiger", "website_url": "https://www.tagesanzeiger.ch", "rss_url": "https://www.tagesanzeiger.ch/rss", "category": "general"},
    {"country_iso": "CH", "name": "SWI swissinfo.ch (EN)", "website_url": "https://www.swissinfo.ch", "rss_url": "https://www.swissinfo.ch/eng/rss", "category": "general"},
    {"country_iso": "CH", "name": "Finanz und Wirtschaft", "website_url": "https://www.fuw.ch", "rss_url": "https://www.fuw.ch/rss", "category": "business"},

    # SINGAPUR (SG)
    {"country_iso": "SG", "name": "The Straits Times", "website_url": "https://www.straitstimes.com", "rss_url": "https://www.straitstimes.com/news/world/rss.xml", "category": "general"},
    {"country_iso": "SG", "name": "CNA (Channel NewsAsia)", "website_url": "https://www.channelnewsasia.com", "rss_url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml", "category": "general"},
    {"country_iso": "SG", "name": "Business Times Singapore", "website_url": "https://www.businesstimes.com.sg", "rss_url": "https://www.businesstimes.com.sg/rss.xml", "category": "business"},

    # TURECKO (TR)
    {"country_iso": "TR", "name": "Anadolu Agency (EN)", "website_url": "https://www.aa.com.tr/en", "rss_url": "https://www.aa.com.tr/en/rss/default?cat=current", "category": "general"},
    {"country_iso": "TR", "name": "Hürriyet Daily News", "website_url": "https://www.hurriyetdailynews.com", "rss_url": "https://www.hurriyetdailynews.com/rss", "category": "general"},
    {"country_iso": "TR", "name": "Daily Sabah (EN)", "website_url": "https://www.dailysabah.com", "rss_url": "https://www.dailysabah.com/rss/world", "category": "general"},
    {"country_iso": "TR", "name": "Dünya Gazetesi", "website_url": "https://www.dunya.com", "rss_url": "https://www.dunya.com/rss", "category": "business"},

    # SPOJENÉ ARABSKÉ EMIRÁTY (AE)
    {"country_iso": "AE", "name": "The National (UAE)", "website_url": "https://www.thenationalnews.com", "rss_url": "https://www.thenationalnews.com/arc/outboundfeeds/rss/?outputType=xml", "category": "general"},
    {"country_iso": "AE", "name": "Gulf News", "website_url": "https://gulfnews.com", "rss_url": "https://gulfnews.com/rss/business", "category": "business"},
    {"country_iso": "AE", "name": "Khaleej Times", "website_url": "https://www.khaleejtimes.com", "rss_url": "https://www.khaleejtimes.com/rss", "category": "general"},
    {"country_iso": "AE", "name": "Arabian Business", "website_url": "https://www.arabianbusiness.com", "rss_url": "https://www.arabianbusiness.com/feed", "category": "business"},

    # JUŽNÁ KÓREA (KR)
    {"country_iso": "KR", "name": "Yonhap News Agency (EN)", "website_url": "https://en.yna.co.kr", "rss_url": "https://en.yna.co.kr/RSS/news.xml", "category": "general"},
    {"country_iso": "KR", "name": "The Korea Herald", "website_url": "https://www.koreaherald.com", "rss_url": "https://www.koreaherald.com/rss/010100000000.xml", "category": "general"},
    {"country_iso": "KR", "name": "The Korea Times", "website_url": "https://www.koreatimes.co.kr", "rss_url": "https://www.koreatimes.co.kr/www/rss/rss.xml", "category": "general"},
    {"country_iso": "KR", "name": "Maeil Business Newspaper (EN)", "website_url": "https://pulsenews.co.kr", "rss_url": "https://pulsenews.co.kr/rss/", "category": "business"},

    # TAIWAN (TW)
    {"country_iso": "TW", "name": "Focus Taiwan (CNA)", "website_url": "https://focustaiwan.tw", "rss_url": "https://focustaiwan.tw/rss/all.aspx", "category": "general"},
    {"country_iso": "TW", "name": "Taipei Times", "website_url": "https://www.taipeitimes.com", "rss_url": "https://www.taipeitimes.com/xml/index.rss", "category": "general"},
    {"country_iso": "TW", "name": "Taiwan News", "website_url": "https://www.taiwannews.com.tw", "rss_url": "https://www.taiwannews.com.tw/rss/news", "category": "general"},
    {"country_iso": "TW", "name": "Digitimes (Tech/Chips)", "website_url": "https://www.digitimes.com", "rss_url": "https://www.digitimes.com/rss/daily.xml", "category": "tech"},

    # TALIANSKO (IT)
    {"country_iso": "IT", "name": "Corriere della Sera", "website_url": "https://www.corriere.it", "rss_url": "https://xml2.corriereobjects.it/rss/homepage.xml", "category": "general"},
    {"country_iso": "IT", "name": "La Repubblica", "website_url": "https://www.repubblica.it", "rss_url": "https://www.repubblica.it/rss/homepage/rss2.0.xml", "category": "general"},
    {"country_iso": "IT", "name": "Il Sole 24 Ore", "website_url": "https://www.ilsole24ore.com", "rss_url": "https://www.ilsole24ore.com/rss/finanza-e-mercati.xml", "category": "business"},
    {"country_iso": "IT", "name": "ANSA News", "website_url": "https://www.ansa.it", "rss_url": "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml", "category": "general"},

    # ŠPANIELSKO (ES)
    {"country_iso": "ES", "name": "El País", "website_url": "https://elpais.com", "rss_url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "category": "general"},
    {"country_iso": "ES", "name": "El Mundo", "website_url": "https://www.elmundo.es", "rss_url": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml", "category": "general"},
    {"country_iso": "ES", "name": "Cinco Días", "website_url": "https://cincodias.elpais.com", "rss_url": "https://feeds.elpais.com/mrss-s/pages/cd/site/cincodias.elpais.com/portada", "category": "business"},
    {"country_iso": "ES", "name": "Expansion", "website_url": "https://www.expansion.com", "rss_url": "https://e00-expansion.uecdn.es/rss/mercados.xml", "category": "business"},

    # HOLANDSKO (NL)
    {"country_iso": "NL", "name": "NOS Nieuws", "website_url": "https://nos.nl", "rss_url": "https://feeds.nos.nl/nosnieuwsalgemeen", "category": "general"},
    {"country_iso": "NL", "name": "De Telegraaf", "website_url": "https://www.telegraaf.nl", "rss_url": "https://www.telegraaf.nl/rss", "category": "general"},
    {"country_iso": "NL", "name": "Het Financieele Dagblad", "website_url": "https://fd.nl", "rss_url": "https://fd.nl/?rss", "category": "business"},
    {"country_iso": "NL", "name": "NL Times (EN)", "website_url": "https://nltimes.nl", "rss_url": "https://nltimes.nl/rss.xml", "category": "general"},

    # NÓRSKO (NO)
    {"country_iso": "NO", "name": "NRK Nyheter", "website_url": "https://www.nrk.no", "rss_url": "https://www.nrk.no/toppsaker.rss", "category": "general"},
    {"country_iso": "NO", "name": "Aftenposten", "website_url": "https://www.aftenposten.no", "rss_url": "https://www.aftenposten.no/rss", "category": "general"},
    {"country_iso": "NO", "name": "Dagens Næringsliv", "website_url": "https://www.dn.no", "rss_url": "https://www.dn.no/rss", "category": "business"},

    # ŠVÉDSKO (SE)
    {"country_iso": "SE", "name": "SVT Nyheter", "website_url": "https://www.svt.se", "rss_url": "https://www.svt.se/nyheter/rss.xml", "category": "general"},
    {"country_iso": "SE", "name": "Dagens Nyheter", "website_url": "https://www.dn.se", "rss_url": "https://www.dn.se/rss/", "category": "general"},
    {"country_iso": "SE", "name": "Dagens Industri", "website_url": "https://www.di.se", "rss_url": "https://www.di.se/rss", "category": "business"},

    # RAKÚSKO (AT)
    {"country_iso": "AT", "name": "Der Standard", "website_url": "https://www.derstandard.at", "rss_url": "https://www.derstandard.at/rss", "category": "general"},
    {"country_iso": "AT", "name": "Die Presse", "website_url": "https://www.diepresse.com", "rss_url": "https://www.diepresse.com/rss/Wirtschaft", "category": "business"},
    {"country_iso": "AT", "name": "Kurier", "website_url": "https://kurier.at", "rss_url": "https://kurier.at/xml/rss", "category": "general"},
    {"country_iso": "AT", "name": "ORF News", "website_url": "https://orf.at", "rss_url": "https://rss.orf.at/news.xml", "category": "general"},

    # MAĎARSKO (HU)
    {"country_iso": "HU", "name": "HVG.hu", "website_url": "https://hvg.hu", "rss_url": "https://hvg.hu/rss", "category": "general"},
    {"country_iso": "HU", "name": "Portfolio.hu (Financie)", "website_url": "https://www.portfolio.hu", "rss_url": "https://www.portfolio.hu/rss/all.xml", "category": "business"},
    {"country_iso": "HU", "name": "Index.hu", "website_url": "https://index.hu", "rss_url": "https://index.hu/24ora/rss/", "category": "general"},
    {"country_iso": "HU", "name": "Telex.hu", "website_url": "https://telex.hu", "rss_url": "https://telex.hu/rss", "category": "general"},

    # MEXIKO (MX)
    {"country_iso": "MX", "name": "El Universal", "website_url": "https://www.eluniversal.com.mx", "rss_url": "https://www.eluniversal.com.mx/arc/outboundfeeds/rss/?outputType=xml", "category": "general"},
    {"country_iso": "MX", "name": "El Economista", "website_url": "https://www.eleconomista.com.mx", "rss_url": "https://www.eleconomista.com.mx/rss/mercados.xml", "category": "business"},
    {"country_iso": "MX", "name": "Milenio", "website_url": "https://www.milenio.com", "rss_url": "https://www.milenio.com/rss", "category": "general"},

    # ARGENTÍNA (AR)
    {"country_iso": "AR", "name": "Clarín", "website_url": "https://www.clarin.com", "rss_url": "https://www.clarin.com/rss/lo-ultimo/", "category": "general"},
    {"country_iso": "AR", "name": "La Nación", "website_url": "https://www.lanacion.com.ar", "rss_url": "https://arc-anglerfish-arc2-prod-lanacionar.s3.amazonaws.com/public/resources/rss/economia.xml", "category": "business"},
    {"country_iso": "AR", "name": "Ámbito Financiero", "website_url": "https://www.ambito.com", "rss_url": "https://www.ambito.com/rss/pages/home.xml", "category": "business"},

    # JUŽNÁ AFRIKA (ZA)
    {"country_iso": "ZA", "name": "News24", "website_url": "https://www.news24.com", "rss_url": "https://feeds.24.com/articles/news24/TopStories/rss", "category": "general"},
    {"country_iso": "ZA", "name": "BusinessDay", "website_url": "https://www.businesslive.co.za", "rss_url": "https://www.businesslive.co.za/rss/?publication=bd", "category": "business"},
    {"country_iso": "ZA", "name": "Daily Maverick", "website_url": "https://www.dailymaverick.co.za", "rss_url": "https://www.dailymaverick.co.za/feed/", "category": "general"},

    # INDONÉZIA (ID)
    {"country_iso": "ID", "name": "The Jakarta Post (EN)", "website_url": "https://www.thejakartapost.com", "rss_url": "https://www.thejakartapost.com/rss/latest", "category": "general"},
    {"country_iso": "ID", "name": "Kompas.com", "website_url": "https://www.kompas.com", "rss_url": "https://news.kompas.com/rss", "category": "general"},
    {"country_iso": "ID", "name": "Antara News (EN)", "website_url": "https://en.antaranews.com", "rss_url": "https://en.antaranews.com/rss/news.xml", "category": "general"},

    # VIETNAM (VN)
    {"country_iso": "VN", "name": "VnExpress (EN)", "website_url": "https://e.vnexpress.net", "rss_url": "https://e.vnexpress.net/rss/news.rss", "category": "general"},
    {"country_iso": "VN", "name": "Vietnam News (EN)", "website_url": "https://vietnamnews.vn", "rss_url": "https://vietnamnews.vn/rss/economy.rss", "category": "business"},
    {"country_iso": "VN", "name": "Tuoi Tre News", "website_url": "https://tuoitrenews.vn", "rss_url": "https://tuoitrenews.vn/rss/business", "category": "business"},

    # EGYPT (EG)
    {"country_iso": "EG", "name": "Al-Ahram (EN)", "website_url": "https://english.ahram.org.eg", "rss_url": "https://english.ahram.org.eg/rss/Economy.aspx", "category": "business"},
    {"country_iso": "EG", "name": "Daily News Egypt", "website_url": "https://dailynewsegypt.com", "rss_url": "https://dailynewsegypt.com/feed/", "category": "general"},
    {"country_iso": "EG", "name": "Egypt Today", "website_url": "https://www.egypttoday.com", "rss_url": "https://www.egypttoday.com/rss/Section/3/Business", "category": "business"},

    # GRÉCKO (GR)
    {"country_iso": "GR", "name": "Ekathimerini (EN)", "website_url": "https://www.ekathimerini.com", "rss_url": "https://www.ekathimerini.com/feed/", "category": "general"},
    {"country_iso": "GR", "name": "Naftemporiki (Financie)", "website_url": "https://www.naftemporiki.gr", "rss_url": "https://www.naftemporiki.gr/feed/", "category": "business"},
    {"country_iso": "GR", "name": "Proto Thema", "website_url": "https://www.protothema.gr", "rss_url": "https://www.protothema.gr/rss/", "category": "general"},

    # KATAR (QA)
    {"country_iso": "QA", "name": "Al Jazeera English", "website_url": "https://www.aljazeera.com", "rss_url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "general"},
    {"country_iso": "QA", "name": "Gulf Times (Qatar)", "website_url": "https://www.gulf-times.com", "rss_url": "https://www.gulf-times.com/rss/all", "category": "general"},
    {"country_iso": "QA", "name": "The Peninsula Qatar", "website_url": "https://thepeninsulaqatar.com", "rss_url": "https://thepeninsulaqatar.com/rss/business", "category": "business"}
]
