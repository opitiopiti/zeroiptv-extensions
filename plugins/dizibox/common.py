from urllib.parse import urljoin, urlsplit, urlunsplit
from bs4 import BeautifulSoup
from . import config


def absolute(raw, base):
    if not raw: return ""
    value = urljoin(base, raw.strip().replace(r"\/", "/"))
    u = urlsplit(value)
    return value if u.scheme == "https" and u.hostname and not u.username and not u.password else ""


def path_of(raw, base):
    url = absolute(raw, base)
    if not url: return ""
    u = urlsplit(url)
    hosts = {h.removeprefix("www.").lower() for h in (*config.PREVIOUS_HOSTS, urlsplit(config.BASE_URL).hostname)}
    if u.hostname.removeprefix("www.").lower() not in hosts: return ""
    path = u.path or "/"
    if path.startswith("//"): return ""
    return urlunsplit(("", "", path, u.query, ""))


def site_url(path):
    if not path.startswith("/") or path.startswith("//"): raise ValueError("Geçersiz içerik yolu")
    return config.BASE_URL.rstrip("/") + path


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
