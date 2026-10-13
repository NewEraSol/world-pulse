"""
Multilingual Query Expansion Engine pre Spravodajsky Tep Sveta.
Automaticky rozsiruje vyhladavane slovo (alebo frazu) do klucovych jazykov:
SK, CS, EN, DE, FR, ES, RU, ZH (Cinstina), JA (Japoncina), AR (Arabstina).
"""
import translators as ts
from typing import List, Set

COMMON_TRANSLATIONS = {
    "ai": ["ai", "artificial intelligence", "umelá inteligencia", "umělá inteligence", "künstliche intelligenz", "intelligence artificielle", "inteligencia artificial", "искусственный интеллект", "人工智能", "الذكاء الاصطناعي"],
    "drony": ["dron", "drony", "drone", "drones", "uav", "drohne", "беспилотник", "дрон", "дроны", "无人机", "طائرة مسيرة"],
    "sankcie": ["sankcie", "sankce", "sanctions", "sanktionen", "sanciones", "санкции", "制裁", "عقوبات"],
    "voľby": ["voľby", "volby", "election", "elections", "wahl", "wahlen", "élections", "elecciones", "выборы", "选举", "انتخابات"],
    "útok": ["útok", "utok", "attack", "angriff", "attaque", "ataque", "атака", "удар", "袭击", "هجوم"],
    "zlato": ["zlato", "gold", "oro", "or", "золото", "黄金", "金", "ذهب", "ouro", "guld"],
    "striebro": ["striebro", "stříbro", "silver", "silber", "argent", "plata", "серебро", "白银", "银", "فضة"],
    "ropa": ["ropa", "oil", "crude", "crude oil", "erdöl", "pétrole", "petróleo", "нефть", "原油", "石油", "نفط"],
    "zemný plyn": ["zemný plyn", "zemní plyn", "natural gas", "erdgas", "gaz naturel", "gas natural", "природный газ", "天然气", "غاز طبيعي"],
    "plyn": ["plyn", "gas", "erdgas", "gaz", "газ", "燃气", "غاز"],
    "pád lietadla": ["pád lietadla", "havária lietadla", "plane crash", "aircraft crash", "flugzeugabsturz", "crash aérien", "accidente aéreo", "крушение самолета", "авиакатастрофа", "坠机", "تحطم طائرة"],
    "potopenie lode": ["potopenie lode", "ship sank", "shipwreck", "schiff gesunken", "naufrage", "naufragio", "затопление корабля", "кораблекрушение", "沉船", "غرق سفينة"],
    "vojna": ["vojna", "válka", "war", "krieg", "guerre", "guerra", "война", "战争", "حرب"],
    "jadrové": ["jadrov", "nukleár", "nuclear", "atom", "nucléaire", "nuclear", "ядерн", "核", "نووي"],
    "inflácia": ["inflácia", "inflace", "inflation", "inflación", "инфляция", "通胀", "通货膨胀", "تضخم"],
    "úrokové sadzby": ["úrokové sadzby", "úrokové sazby", "interest rates", "leitzins", "taux d'intérêt", "tasas de interés", "процентные ставки", "利率", "أسعار الفائدة"],
    "fúzia": ["fúzia", "fúze", "merger", "acquisition", "übernahme", "fusion", "adquisición", "слияние", "并购", "اندماج"],
}

TARGET_LANGS = [
    ('en', 'Angličtina'),
    ('de', 'Nemčina'),
    ('fr', 'Francúzština'),
    ('ru', 'Ruština'),
    ('zh', 'Čínština'),
    ('ar', 'Arabčina'),
    ('es', 'Španielčina')
]

def expand_keyword(keyword: str) -> List[str]:
    """
    Vrati zoznam alternativnych vyrazov vo viacerych svetovych jazykoch.
    """
    clean_k = keyword.strip().lower()
    if not clean_k:
        return []

    # 1. Rychla lookup tabulka (0 ms latency)
    for base_word, variants in COMMON_TRANSLATIONS.items():
        if clean_k == base_word or clean_k in [v.lower() for v in variants]:
            return list(set(variants))

    # 2. Dynamicky on-the-fly preklad do top svetovych jazykov (Bing Translator)
    expanded: Set[str] = {clean_k}
    for lang_code, lang_name in TARGET_LANGS:
        try:
            trans = None
            try:
                trans = ts.translate_text(clean_k, translator='bing', to_language=lang_code)
            except Exception:
                trans = ts.translate_text(clean_k, translator='google', to_language=lang_code)
            if trans and len(trans.strip()) > 0:
                expanded.add(trans.strip())
        except Exception as e:
            print(f"[MULTILINGUAL ERROR] {lang_code}: {type(e)} {e}", flush=True)

    return list(expanded)

def build_fts_query(keyword: str) -> str:
    """
    Vytvori FTS5 MATCH retazec napr: "zlato" OR "gold" OR "золото" OR "黄金"
    Podporuje aj spojenie pomocou ' OR ' alebo '|' (viacero kľúčových slov naraz).
    """
    raw = keyword.strip()
    if not raw:
        return ""
    
    # Rozdelenie podla ' OR ' alebo '|' ak bolo zadanych viac slov
    delimiters = [' OR ', ' or ', '|']
    tokens = [raw]
    for d in delimiters:
        new_tokens = []
        for t in tokens:
            if d in t:
                new_tokens.extend([part.strip() for part in t.split(d) if part.strip()])
            else:
                new_tokens.append(t)
        tokens = new_tokens

    all_expanded_words = []
    seen = set()
    for tok in tokens:
        expanded = expand_keyword(tok)
        if not expanded:
            expanded = [tok]
        for w in expanded:
            w_clean = w.replace('"', '""').strip()
            w_lower = w_clean.lower()
            if w_clean and w_lower not in seen:
                seen.add(w_lower)
                all_expanded_words.append(f'"{w_clean}"')

    if not all_expanded_words:
        return f'"{raw}"'

    return " OR ".join(all_expanded_words)
