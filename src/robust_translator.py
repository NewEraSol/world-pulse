"""
Robustny viac-motorovy prekladac titulkov a textov.
Podporuje Google, Bing, Yandex s automatickym prepinanim pri chybe
a detekciou, ci preklad skutocne prebehol.
"""
import translators as ts
import time
import re

def clean_text(t: str) -> str:
    if not t:
        return ""
    # Zachováme odseky, len odstránime extrémne medzery na začiatku a konci
    return t.strip()

def is_substantially_different(orig: str, trans: str) -> bool:
    if not trans or not trans.strip():
        return False
    o = re.sub(r'[\s\W_]+', '', orig.lower())
    t = re.sub(r'[\s\W_]+', '', trans.lower())
    if not t or t == o:
        return False
    return True

def single_translate(text: str, target_lang: str) -> str:
    cleaned = clean_text(text)
    if not cleaned or len(cleaned) < 2:
        return cleaned

    # Pokus 1: Google
    try:
        res = ts.translate_text(cleaned, translator='google', to_language=target_lang)
        if is_substantially_different(cleaned, res):
            return res.strip()
    except Exception:
        pass

    # Pokus 2: Bing
    try:
        res = ts.translate_text(cleaned, translator='bing', to_language=target_lang)
        if is_substantially_different(cleaned, res):
            return res.strip()
    except Exception:
        pass

    # Pokus 3: Yandex
    try:
        res = ts.translate_text(cleaned, translator='yandex', to_language=target_lang)
        if is_substantially_different(cleaned, res):
            return res.strip()
    except Exception:
        pass

    return cleaned

def robust_batch_translate(texts: list, target_lang: str) -> list:
    if not texts:
        return []
    
    clean_list = [clean_text(t) for t in texts]
    joined = "\n".join(clean_list)

    # 1. Google batch
    try:
        res = ts.translate_text(joined, translator='google', to_language=target_lang)
        lines = [line.strip() for line in res.strip().split("\n")]
        if len(lines) == len(clean_list):
            return lines
    except Exception:
        pass

    # 2. Bing batch
    try:
        res = ts.translate_text(joined, translator='bing', to_language=target_lang)
        lines = [line.strip() for line in res.strip().split("\n")]
        if len(lines) == len(clean_list):
            return lines
    except Exception:
        pass

    # 3. Individual fallback
    results = []
    for t in clean_list:
        results.append(single_translate(t, target_lang))
    return results

def robust_translate(text: str, target_lang: str) -> str:
    return single_translate(text, target_lang)
