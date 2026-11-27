"""Mevcut üç doğrulanmamış canlı tür yolunu tek Dizi listesinde birleştirir.
Tam site kataloğu olduğu iddia edilmez; kaynak yolu doğrulanınca değiştirilebilir.
"""
from .common import document, cards

def get_series(ctx, page=1):
    items = {}
    next_page = False
    for genre in ("dram", "komedi", "korku"):
        path = f"/tur/{genre}/" + (f"page/{page}/" if page > 1 else "")
        doc, url = document(ctx, path)
        batch = cards(doc, url, "article.article-series-poster", "a.poster-title", "a.poster-title", "series")
        for card in batch:
            items.setdefault(card["path"], card)
        next_page |= bool(batch and doc.select_one(f'a[href*="/page/{page+1}/"]'))
    return dict(items=list(items.values()), next=next_page)
