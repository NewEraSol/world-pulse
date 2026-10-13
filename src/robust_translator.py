import translators as ts
import time
import re
import difflib

def clean_text(t: str) -> str:
    if not t:
        return ""
    return t.strip()

def is_substantially_different(orig: str, trans: str) -> bool:
    if not trans or not trans.strip():
        return False
    o = clean_text(orig).lower()
    t = clean_text(trans).lower()
    if not t or t == o:
        return False
    # Pre dlhsie texty testujeme difflib podobnost
    if len(o) > 10:
        ratio = difflib.SequenceMatcher(None, o, t).ratio()
        if ratio > 0.82:
            return False
    return True

def single_translate(text: str, target_lang: str) -> str:
    cleaned = clean_text(text)
    if not cleaned or len(cleaned) < 2:
        return cleaned

    for engine in ['bing', 'yandex', 'modernMt', 'google']:
        try:
            res = ts.translate_text(cleaned, translator=engine, to_language=target_lang, timeout=5)
            if is_substantially_different(cleaned, res):
                return res.strip()
        except Exception:
            continue

    return cleaned

def robust_batch_translate(texts: list, target_lang: str) -> list:
    if not texts:
        return []
    
    clean_list = [clean_text(t) for t in texts]
    joined = "\n".join(clean_list)

    # Najprv skusime bing a yandex pre batch
    for engine in ['bing', 'yandex']:
        try:
            res = ts.translate_text(joined, translator=engine, to_language=target_lang, timeout=9)
            lines = [line.strip() for line in res.strip().split("\n")]
            if len(lines) == len(clean_list):
                # Skontrolujeme, ci vacsina riadkov je skutocne prelozena
                diff_count = sum(1 for orig, tr in zip(clean_list, lines) if is_substantially_different(orig, tr))
                if diff_count >= len(clean_list) * 0.7:
                    # Validujeme riadok po riadku
                    final_lines = []
                    for orig, tr in zip(clean_list, lines):
                        if is_substantially_different(orig, tr):
                            final_lines.append(tr)
                        else:
                            final_lines.append(single_translate(orig, target_lang))
                    return final_lines
        except Exception:
            continue

    # Ak batch zlyhal alebo vynechal vela riadkov, ideme per-item
    results = []
    for t in clean_list:
        results.append(single_translate(t, target_lang))
    return results

def robust_translate(text: str, target_lang: str) -> str:
    return single_translate(text, target_lang)
