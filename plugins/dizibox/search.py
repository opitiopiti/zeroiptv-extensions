from urllib.parse import quote_plus
from .common import document, cards

def search(ctx, query):
    doc, url = document(ctx, "/search/" + quote_plus(query.strip()) + "/", "search")
    return dict(items=cards(doc, url, "article.detailed-article", "h3 a", "h3 a", "series"), next=False)
