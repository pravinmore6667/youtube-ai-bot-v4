import os
import json
import time
import requests
import uuid
from config import config
from utils.logger import get_logger
from utils.provider_health import check_provider_health, record_success, record_failure

log = get_logger("StockRouter")

CACHE_DIR = "cache/stock"
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_TTL = 24 * 60 * 60  # 24 hours

def _get_cache_key(query: str, provider: str) -> str:
    return os.path.join(CACHE_DIR, f"{provider}_{hash(query)}.json")

def _check_cache(query: str, provider: str) -> list[str]:
    cache_path = _get_cache_key(query, provider)
    if os.path.exists(cache_path):
        if os.path.getmtime(cache_path) + CACHE_TTL > time.time():
            try:
                with open(cache_path, "r") as f:
                    return json.load(f)
            except:
                pass
    return []

def _save_cache(query: str, provider: str, urls: list[str]):
    cache_path = _get_cache_key(query, provider)
    with open(cache_path, "w") as f:
        json.dump(urls, f)

def _pixabay_search(query: str, n: int = 5) -> list[str]:
    try:
        r = requests.get("https://pixabay.com/api/videos/",
            params={"key": config.PIXABAY_API_KEY, "q": query,
                    "per_page": n, "video_type": "film"}, timeout=15)
        r.raise_for_status()
        urls = []
        for hit in r.json().get("hits", []):
            for q in ["large","medium","small"]:
                url = hit.get("videos",{}).get(q,{}).get("url")
                if url: urls.append(url); break
        return urls
    except Exception as e:
        log.warning(f"Pixabay search failed for '{query}': {e}")
        raise

def _pexels_search(query: str, n: int = 5) -> list[str]:
    try:
        r = requests.get("https://api.pexels.com/videos/search",
            headers={"Authorization": config.PEXELS_API_KEY},
            params={"query": query, "per_page": n, "orientation": "landscape", "size": "large"},
            timeout=15)
        r.raise_for_status()
        urls = []
        for v in r.json().get("videos", []):
            files = sorted(v.get("video_files",[]), key=lambda f: f.get("height",0), reverse=True)
            for f in files:
                if f.get("link") and f.get("height",0) >= 720:
                    urls.append(f["link"]); break
        return urls
    except Exception as e:
        log.warning(f"Pexels search failed for '{query}': {e}")
        raise

def get_stock_video(query: str, dest: str, n: int = 5) -> str | None:
    """
    Intelligently routes to stock video providers.
    Tries Pixabay first, then Pexels as a fallback.
    Downloads the first successful clip.
    """
    clean = query[:60].split(",")[0].split("(")[0].strip()

    # Try Pixabay
    if check_provider_health("pixabay"):
        try:
            cached_urls = _check_cache(clean, "pixabay")
            if cached_urls:
                urls = cached_urls
            else:
                urls = _pixabay_search(clean, n)
                _save_cache(clean, "pixabay", urls)

            for url in urls:
                path = _download_clip(url, dest)
                if path:
                    record_success("pixabay")
                    return path
        except Exception:
            record_failure("pixabay")
            log.info("[Stock Router] Pixabay failed, Switching to Pexels")
    else:
        log.info("[Stock Router] Pixabay degraded, Switching to Pexels")

    # Fallback to Pexels
    if check_provider_health("pexels"):
        try:
            cached_urls = _check_cache(clean, "pexels")
            if cached_urls:
                urls = cached_urls
            else:
                urls = _pexels_search(clean, n)
                _save_cache(clean, "pexels", urls)

            for url in urls:
                path = _download_clip(url, dest)
                if path:
                    record_success("pexels")
                    log.info("[Stock Router] Pexels success")
                    return path
        except Exception:
            record_failure("pexels")
            log.warning("[Stock Router] Pexels failed")

    return None

def _download_clip(url: str, dest: str) -> str | None:
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        path = os.path.join(dest, f"{uuid.uuid4().hex}.mp4")
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192): f.write(chunk)
        return path
    except Exception as e:
        log.warning(f"Download failed: {e}")
        return None
