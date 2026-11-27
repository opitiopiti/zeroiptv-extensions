"""ZeroIPTV — DiziBox (SDK 3). Tek dosyalık eklenti."""

from urllib.parse import urljoin, urlsplit, urlunsplit, quote_plus
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import re

# ================================================================
# AYARLAR
# ================================================================
ID = "dizibox"
NAME = "DiziBox"
VERSION = 8
TYPE = "series"
BASE_URL = "https://www.dizibox.live"
PREVIOUS_HOSTS = ("dizibox.live", "www.dizibox.live")
ENABLED = True

# ================================================================
# HTTP BAŞLIKLARI
# ================================================================
# Bu iki sözlüğü gerektiğinde doğrudan Python ile düzenle.
M3U8_HEADERS = {'Accept': '*/*',
 'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/158.0.0.0 Safari/537.36',
 'Sec-CH-UA': '"Chromium";v="158", "Not.A/Brand";v="24", "Google Chrome";v="158"',
 'Sec-CH-UA-Mobile': '?0',
 'Sec-CH-UA-Platform': '"Windows"',
 'Sec-Fetch-Dest': 'empty',
 'Sec-Fetch-Mode': 'cors',
 'Referer': '{sourceBaseUrl}',
 'Sec-Fetch-Site': 'same-origin'}

SEGMENT_HEADERS = {'Accept': '*/*',
 'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/158.0.0.0 Safari/537.36',
 'Sec-CH-UA': '"Chromium";v="158", "Not.A/Brand";v="24", "Google Chrome";v="158"',
 'Sec-CH-UA-Mobile': '?0',
 'Sec-CH-UA-Platform': '"Windows"',
 'Sec-Fetch-Dest': 'empty',
 'Sec-Fetch-Mode': 'cors',
 'Origin': '{sourceOrigin}',
 'Referer': '{sourceOrigin}/',
 'Sec-Fetch-Site': 'cross-site'}


def headers_for(url):
    u = urlsplit(url)
    if u.hostname != "dbx.molystream.org" or not u.path.startswith("/embed/") or not u.path.endswith("/q/1"):
        return {}, {}
    origin = f"{u.scheme}://{u.netloc}"
    base = urlunsplit((u.scheme, u.netloc, u.path.removesuffix("/q/1"), u.query, ""))
    def render(values):
        return {k:v.replace("{sourceUrl}",url).replace("{sourceBaseUrl}",base).replace("{sourceOrigin}",origin) for k,v in values.items()}
    return render(M3U8_HEADERS), render(SEGMENT_HEADERS)

# ================================================================
# YARDIMCI FONKSİYONLAR
# ================================================================
def absolute(raw, base):
    if not raw: return ""
    value = urljoin(base, raw.strip().replace(r"\/", "/"))
    u = urlsplit(value)
    return value if u.scheme == "https" and u.hostname and not u.username and not u.password else ""


def path_of(raw, base):
    url = absolute(raw, base)
    if not url: return ""
    u = urlsplit(url)
    hosts = {h.removeprefix("www.").lower() for h in (*PREVIOUS_HOSTS, urlsplit(BASE_URL).hostname)}
    if u.hostname.removeprefix("www.").lower() not in hosts: return ""
    path = u.path or "/"
    if path.startswith("//"): return ""
    return urlunsplit(("", "", path, u.query, ""))


def site_url(path):
    if not path.startswith("/") or path.startswith("//"): raise ValueError("Geçersiz içerik yolu")
    return BASE_URL.rstrip("/") + path


def document(ctx, path, operation="catalog"):
    response = ctx.get(site_url(path), operation=operation)
    return BeautifulSoup(response.body, "html.parser"), response.url


def text(node):
    return node.get_text(" ", strip=True) if node else ""


def image(node, base):
    if not node: return ""
    for attr in ("data-src", "data-lazy-src", "data-original", "src"):
        result = absolute(node.get(attr), base)
        if result: return result
    return ""


def poster(card, base):
    for selector in ("img.afis", "img.wp-post-image", "a.figure-link img", "figure img", "img"):
        for node in card.select(selector):
            result = image(node, base)
            if result: return result
    return ""


def cards(doc, base, card_selector, link_selector, title_selector, kind, label_selector=None):
    result = {}
    for card in doc.select(card_selector)[:200]:
        a = card.select_one(link_selector)
        if not a: continue
        path = path_of(a.get("href"), base)
        title = text(card.select_one(title_selector)) or text(a) or a.get("title", "")
        if not path or not title: continue
        label = " ".join(text(n) for n in card.select(label_selector)) if label_selector else ""
        result.setdefault(path, dict(path=path, title=title, poster=poster(card, base), label=label, kind=kind))
    return list(result.values())

# ================================================================
# SON BÖLÜMLER
# ================================================================
def get_home(ctx, page=1):
    path = "/tum-bolumler/" if page == 1 else f"/tum-bolumler/page/{page}/"
    doc, url = document(ctx, path)
    items = cards(doc, url, "article.article-episode-card", "a.episode-card-title", "b.series-name", "episode", "span.season, b.episode")
    if page == 1 and not items: raise ValueError("Kaynak içerik vermedi")
    return dict(items=items, next=bool(items and doc.select_one(f'a[href*="/page/{page+1}/"]')))

# ================================================================
# DİZİLER — gerçek arşiv, her sayfada kendi dizi posterleri
# ================================================================
def get_series(ctx, page=1):
    if page < 1:
        raise ValueError("Sayfa numarası geçersiz")
    path = "/dizi-arsivi/" if page == 1 else f"/dizi-arsivi/page/{page}/"
    doc, url = document(ctx, path)
    items = cards(doc, url, "#page-archive article.detailed-article", "h3 a", "h3 a", "series")
    items = [item for item in items if urlsplit(item["path"]).path.startswith("/diziler/")]
    if page == 1 and not items:
        raise ValueError("Dizi arşivi içerik vermedi")
    expected = f"/dizi-arsivi/page/{page + 1}/"
    has_next = any(urlsplit(path_of(a.get("href"), url)).path == expected for a in doc.select("#page-archive a[href]"))
    return dict(items=items, next=bool(items and has_next))

# ================================================================
# ARAMA
# ================================================================
def search(ctx, query):
    doc, url = document(ctx, "/search/" + quote_plus(query.strip()) + "/", "search")
    return dict(items=cards(doc, url, "article.detailed-article", "h3 a", "h3 a", "series"), next=False)

# ================================================================
# BÖLÜMLER
# ================================================================
def number(pattern, value):
    match = re.search(pattern, value, re.I)
    return int(match.group(1)) if match else None

def collect(doc, base):
    items = []
    for a in doc.select("a.season-episode"):
        path = path_of(a.get("href"), base)
        if not path: continue
        label = text(a)
        season = number(r"(\d+)\.\s*Sezon", label) or number(r"(\d+)-sezon", path) or 1
        episode = number(r"(\d+)\.\s*Bölüm", label) or number(r"(\d+)-bolum", path)
        if episode is not None: items.append(dict(path=path, title=label or f"{episode}. Bölüm", season=season, number=episode))
    return items

# ================================================================
# SEZONLAR
# ================================================================
def get_seasons(ctx, doc, url, original_path):
    paths = list(dict.fromkeys(path_of(a.get("href"), url) for a in doc.select("div#seasons-list a")))
    paths = [p for p in paths if p and p != original_path]
    complete = len(paths) <= 30
    def load(path):
        try:
            page, base = document(ctx, path, "season")
            return collect(page, base) or None
        except Exception:
            return None
    # Calls are bounded globally by Android's HTTP bridge as well.
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(load, paths[:30]))
    return [e for result in results if result for e in result], complete and all(result is not None for result in results)

# ================================================================
# DETAY
# ================================================================
def get_details(ctx, path):
    doc, url = document(ctx, path, "details")
    title = text(doc.select_one("div.tv-overview h1 a, h1 span.tv-title-archive span[itemprop=name], h1 a"))
    if not title: raise ValueError("İçerik bilgisi bulunamadı")
    anchor = doc.select_one("div.tv-overview h1 a, h1 a")
    canonical = path_of(anchor.get("href"), url) if anchor else ""
    episodes = collect(doc, url)
    additional, complete = get_seasons(ctx, doc, url, path)
    episodes.extend(additional)
    if not episodes:
        n = number(r"(\d+)-bolum", path)
        if n is None: raise ValueError("Bölüm listesi bulunamadı")
        episodes.append(dict(path=path, title=f"{n}. Bölüm", season=number(r"(\d+)-sezon", path) or 1, number=n))
        complete = False
    episodes = sorted({e["path"]: e for e in episodes}.values(), key=lambda e:(e["season"], e["number"]))
    return dict(path=canonical or path, title=title, poster=image(doc.select_one("div.tv-overview figure img"),url) or absolute((doc.select_one('meta[property="og:image"]') or {}).get("content"), url), plot=text(doc.select_one("div.tv-story p")), episodes=episodes, complete=complete)

# ================================================================
# OYnatma / EXTRACTOR
# ================================================================
def resolve(ctx, path):
    """DiziBox'ın çalışan DBX Pro akışı. Video dosyasını indirmez."""
    episode = ctx.get(site_url(path), referer=site_url("/"), operation="resolve")
    doc = BeautifulSoup(episode.body, "html.parser")
    iframe = doc.select_one("div#video-area iframe[src]")
    if not iframe: raise ValueError("Video iframe bulunamadı")
    player_url = absolute(iframe.get("src"), episode.url)
    if not player_url: raise ValueError("Geçersiz iframe")
    # DBX Pro öncelikli; kullanılmayan Vidmoly vb. kaynaklara istek gönderilmez.
    if "/player/king/king.php" not in urlsplit(player_url).path:
        raise ValueError("DBX Pro kaynağı bulunamadı")
    player_url = player_url.replace("king.php?v=", "king.php?wmode=opaque&v=", 1)
    player = ctx.get(player_url, referer=episode.url, operation="resolve")
    iframe = BeautifulSoup(player.body, "html.parser").select_one("div#Player iframe[src]")
    if not iframe: raise ValueError("DBX Pro iframe bulunamadı")
    embed = absolute(iframe.get("src"), player.url)
    u = urlsplit(embed)
    if u.hostname != "dbx.molystream.org" or not u.path.startswith("/embed/"):
        raise ValueError("Desteklenmeyen kaynak")
    endpoint = urlunsplit((u.scheme,u.netloc,u.path.rstrip("/").removesuffix("/q/1")+"/q/1",u.query,""))
    manifest_headers, segment_headers = headers_for(endpoint)
    if not manifest_headers: raise ValueError("Manifest başlıkları tanımlı değil")
    response = ctx.get(endpoint, headers=manifest_headers, operation="resolve")
    # Bir HTML hata sayfasını medya olarak kabul etmiyoruz.
    if not response.body.lstrip("\ufeff \r\n\t").startswith("#EXTM3U"):
        raise ValueError("Kaynak geçerli HLS manifesti döndürmedi")
    return dict(url=response.url, mimeType="application/x-mpegURL", headers=segment_headers,
                manifestHeaders=manifest_headers, subtitles=[])
