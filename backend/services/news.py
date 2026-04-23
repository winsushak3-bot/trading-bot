"""
News aggregation service — fetches crypto & forex news from RSS feeds,
caches results, and provides full-article parsing via BeautifulSoup.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from datetime import datetime, timezone

import aiohttp
import feedparser

logger = logging.getLogger(__name__)

# ── RSS Sources ──────────────────────────────────────────────

CRYPTO_FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("CoinTelegraph", "https://cointelegraph.com/rss"),
    ("Bitcoin Magazine", "https://bitcoinmagazine.com/feed"),
    ("Decrypt", "https://decrypt.co/feed"),
]

FOREX_FEEDS = [
    ("ForexLive", "https://www.forexlive.com/feed/news"),
    ("FXStreet", "https://www.fxstreet.com/rss/news"),
    ("MarketWatch", "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
]

# ── News feed cache ──────────────────────────────────────────

NEWS_CACHE_TTL = 600  # 10 minutes
_news_cache: dict[str, tuple[float, list[dict]]] = {}


async def _fetch_feed(
    session: aiohttp.ClientSession, source: str, url: str,
) -> list[dict]:
    """Fetch and parse one RSS feed into a list of article dicts."""
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=8),
        ) as resp:
            if resp.status != 200:
                logger.debug("Feed %s returned %s", source, resp.status)
                return []
            text = await resp.text()
    except Exception as e:
        logger.debug("Failed to fetch %s: %s", source, e)
        return []

    try:
        feed = feedparser.parse(text)
    except Exception as e:
        logger.debug("Failed to parse %s: %s", source, e)
        return []

    items: list[dict] = []
    for entry in feed.entries[:8]:
        title = getattr(entry, "title", "").strip()
        if not title:
            continue

        # ── Image extraction ──
        image = _extract_feed_image(entry)

        # ── Summary / content ──
        summary = _extract_feed_summary(entry)

        # ── Published time ──
        published, published_display, time_ago = _parse_published(entry)

        # ── Link ──
        link = getattr(entry, "link", "")
        if "?" in link:
            link = link.split("?")[0]

        # ── Read time estimate ──
        word_count = len(summary.split())
        read_time = max(1, round(word_count / 200))

        uid = hashlib.sha256(f"{source}|{title}".encode()).hexdigest()[:16]

        items.append({
            "id": uid,
            "source": source,
            "title": title,
            "summary": summary,
            "image": image,
            "time": time_ago or "недавно",
            "publishedAt": published_display,
            "published": published,
            "readTime": str(read_time),
            "link": link,
        })

    return items


def _extract_feed_image(entry) -> str:
    """Try multiple methods to find an image in an RSS entry."""
    # 1) media_content
    media = getattr(entry, "media_content", None)
    if media and isinstance(media, list) and media[0].get("url"):
        return media[0]["url"]

    # 2) enclosures
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image") or \
           enc.get("href", "").split("?")[0].split(".")[-1] in ("jpg", "jpeg", "png", "webp"):
            return enc.get("href", "")

    # 3) media_thumbnail
    thumbs = getattr(entry, "media_thumbnail", [])
    if thumbs:
        return thumbs[0].get("url", "")

    # 4) Extract from HTML content
    raw_html = getattr(entry, "summary", "") or getattr(entry, "description", "")
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_html)
    if img_match:
        return img_match.group(1)

    return ""


def _extract_feed_summary(entry) -> str:
    """Extract clean text summary from RSS entry, preferring content:encoded."""
    raw = ""
    if hasattr(entry, "content") and entry.content:
        raw = entry.content[0].get("value", "")
    if not raw:
        raw = getattr(entry, "summary", "") or getattr(entry, "description", "")

    text = re.sub(r"<[^>]+>", " ", raw).strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) > 3000:
        text = text[:2997] + "..."
    return text


def _parse_published(entry) -> tuple[str, str, str]:
    """Return (iso_string, display_string, time_ago) from entry.published_parsed."""
    if not (hasattr(entry, "published_parsed") and entry.published_parsed):
        return "", "", ""
    try:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        iso = dt.isoformat()
        display = dt.strftime("%d.%m.%Y %H:%M UTC")
        delta = datetime.now(timezone.utc) - dt
        mins = int(delta.total_seconds() / 60)
        if mins < 1:
            ago = "только что"
        elif mins < 60:
            ago = f"{mins} мин назад"
        elif mins < 1440:
            ago = f"{mins // 60} ч назад"
        else:
            ago = f"{mins // 1440} дн назад"
        return iso, display, ago
    except Exception:
        return "", "", ""


async def get_news(category: str) -> list[dict]:
    """Get news for a category ('crypto' | 'forex'), with caching."""
    now = time.time()
    cached = _news_cache.get(category)
    if cached and (now - cached[0]) < NEWS_CACHE_TTL:
        return cached[1]

    feeds = CRYPTO_FEEDS if category == "crypto" else FOREX_FEEDS

    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0 (compatible; TradingBot/1.0)"},
    ) as session:
        tasks = [_fetch_feed(session, src, url) for src, url in feeds]
        results = await asyncio.gather(*tasks)

    all_items: list[dict] = []
    for items in results:
        all_items.extend(items)

    # Sort newest first, deduplicate by title prefix
    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)

    seen_titles: set[str] = set()
    unique: list[dict] = []
    for item in all_items:
        short = item["title"][:60].lower()
        if short not in seen_titles:
            seen_titles.add(short)
            unique.append(item)

    unique = unique[:20]
    _news_cache[category] = (now, unique)
    return unique


# ── Full article parser ──────────────────────────────────────

_article_cache: dict[str, tuple[float, dict]] = {}
ARTICLE_CACHE_TTL = 3600  # 1 hour
_ARTICLE_CACHE_MAX_SIZE = 200

# CSS selectors per domain → main article content
# (domain_substr | None, css_selector)
_CONTENT_SELECTORS: list[tuple[str | None, str]] = [
    # Domain-specific (ordered by specificity)
    ("cointelegraph.com", ".post-content"),
    ("cointelegraph.com", ".post__content"),
    ("coindesk.com", ".at-body"),
    ("coindesk.com", "[data-module='body']"),
    ("decrypt.co", "main"),
    ("bitcoinmagazine.com", ".entry-content"),
    ("bitcoinmagazine.com", ".article-content"),
    ("investing.com", "div.WYSIWYG"),
    ("investing.com", ".articlePage"),
    ("forexlive.com", ".article-body"),
    ("forexlive.com", ".article__content"),
    ("fxstreet.com", ".fxs_article_body"),
    ("fxstreet.com", ".body-content"),
    ("marketwatch.com", ".article__body"),
    ("yahoo.com", ".caas-body"),
    ("yahoo.com", ".body"),
    # Generic — more specific first
    (None, "[itemprop='articleBody']"),
    (None, "[data-testid='article-body']"),
    (None, ".post-content"),
    (None, ".article-content"),
    (None, ".article-body"),
    (None, ".entry-content"),
    (None, ".story-body"),
    (None, "main article"),
    (None, "main"),
    (None, "article"),
    (None, "[role='main']"),
]

_MIN_CONTENT_CHARS = 150


def _extract_paragraphs(el) -> list[str]:
    """Extract readable paragraphs from a BeautifulSoup element."""
    paragraphs: list[str] = []
    seen: set[str] = set()
    for p in el.find_all(["p", "h2", "h3", "h4", "blockquote", "li"]):
        text = p.get_text(strip=True)
        if len(text) < 25 or text in seen:
            continue
        seen.add(text)
        if p.name in ("h2", "h3", "h4"):
            paragraphs.append(f"\n**{text}**\n")
        elif p.name == "blockquote":
            paragraphs.append(f'"{text}"')
        else:
            paragraphs.append(text)
    return paragraphs


def _extract_article_images(el) -> list[str]:
    """Extract article images from a BeautifulSoup element."""
    images: list[str] = []
    seen: set[str] = set()
    skip = (
        "pixel", "tracker", "1x1", "ad.", "logo", "icon", "avatar",
        "badge", "button", "emoji", "spinner", "loading", "data:image",
    )
    for img in el.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if src.startswith("//"):
            src = "https:" + src
        if not src.startswith("http") or any(x in src.lower() for x in skip):
            continue
        if src in seen:
            continue
        seen.add(src)
        images.append(src)
        if len(images) >= 5:
            break
    return images


def _is_safe_url(url: str) -> bool:
    """Проверяет URL на SSRF: блокирует file://, ftp://, внутренние IP."""
    from urllib.parse import urlparse
    import ipaddress
    try:
        parsed = urlparse(url)
        # Только HTTP/HTTPS
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Блокируем IP-адреса (private, loopback, link-local)
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except ValueError:
            pass  # Это домен, не IP — ок
        # Блокируем localhost
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return False
        return True
    except Exception:
        return False


async def fetch_full_article(url: str) -> dict:
    """Fetch a full article page and extract text + images."""
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse

    now = time.time()
    cached = _article_cache.get(url)
    if cached and (now - cached[0]) < ARTICLE_CACHE_TTL:
        return cached[1]

    # Evict expired entries and enforce max size
    if len(_article_cache) >= _ARTICLE_CACHE_MAX_SIZE:
        expired = [k for k, (ts, _) in _article_cache.items() if now - ts > ARTICLE_CACHE_TTL]
        for k in expired:
            del _article_cache[k]
        # If still over limit, remove oldest entries
        while len(_article_cache) >= _ARTICLE_CACHE_MAX_SIZE:
            oldest_key = min(_article_cache, key=lambda k: _article_cache[k][0])
            del _article_cache[oldest_key]

    empty: dict = {"content": "", "images": []}

    # SSRF защита
    if not _is_safe_url(url):
        logger.warning("Blocked unsafe URL in article fetch: %s", url)
        _article_cache[url] = (now, empty)
        return empty

    try:
        async with aiohttp.ClientSession(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
            },
        ) as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15),
                allow_redirects=True,
            ) as resp:
                if resp.status != 200:
                    logger.debug("Article fetch %s → %s", url, resp.status)
                    _article_cache[url] = (now, empty)
                    return empty
                html = await resp.text()
    except Exception as e:
        logger.debug("Article fetch failed %s: %s", url, e)
        _article_cache[url] = (now, empty)
        return empty

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for tag in soup.find_all(
        ["script", "style", "nav", "footer", "aside", "header",
         "noscript", "iframe", "form", "svg", "button"],
    ):
        tag.decompose()

    domain = ""
    try:
        domain = urlparse(url).netloc.replace("www.", "")
    except Exception:
        pass

    # Try selectors — pick first with enough text
    best_paragraphs: list[str] = []
    best_images: list[str] = []

    for sel_domain, selector in _CONTENT_SELECTORS:
        if sel_domain and sel_domain not in domain:
            continue
        el = soup.select_one(selector)
        if not el:
            continue
        paragraphs = _extract_paragraphs(el)
        total_chars = sum(len(p) for p in paragraphs)
        if total_chars > _MIN_CONTENT_CHARS:
            best_paragraphs = paragraphs
            best_images = _extract_article_images(el)
            break
        if total_chars > sum(len(p) for p in best_paragraphs):
            best_paragraphs = paragraphs
            best_images = _extract_article_images(el)

    # Ultimate fallback: entire body
    if sum(len(p) for p in best_paragraphs) < _MIN_CONTENT_CHARS:
        body = soup.body if soup.body else soup
        body_paragraphs = _extract_paragraphs(body)
        if sum(len(p) for p in body_paragraphs) > sum(len(p) for p in best_paragraphs):
            best_paragraphs = body_paragraphs
            best_images = _extract_article_images(body)

    content_text = "\n\n".join(best_paragraphs)
    if len(content_text) > 8000:
        content_text = content_text[:7997] + "..."

    result = {"content": content_text, "images": best_images}
    _article_cache[url] = (now, result)
    return result
