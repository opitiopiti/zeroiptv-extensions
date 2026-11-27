from .common import document, cards

def get_home(ctx, page=1):
    path = "/tum-bolumler/" if page == 1 else f"/tum-bolumler/page/{page}/"
    doc, url = document(ctx, path)
    items = cards(doc, url, "article.article-episode-card", "a.episode-card-title", "b.series-name", "episode", "span.season, b.episode")
    if page == 1 and not items: raise ValueError("Kaynak içerik vermedi")
    return dict(items=items, next=bool(items and doc.select_one(f'a[href*="/page/{page+1}/"]')))
