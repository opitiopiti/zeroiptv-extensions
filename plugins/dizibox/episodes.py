import re
from .common import path_of, text

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
