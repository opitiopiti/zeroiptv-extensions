from concurrent.futures import ThreadPoolExecutor
from .common import document, path_of
from .episodes import collect

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
