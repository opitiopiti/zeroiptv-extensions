from .common import document, text, image, path_of
from .episodes import collect, number
from .seasons import get_seasons

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
    return dict(path=canonical or path, title=title, poster=image(doc.select_one("div.tv-overview figure img"),url), plot=text(doc.select_one("div.tv-story p")), episodes=episodes, complete=complete)
