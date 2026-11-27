"""Site bağımsız, ağ çağrısı yapmayan yardımcılar."""
from urllib.parse import urljoin, urlsplit

def absolute_https(raw, base):
    if not raw:
        return ""
    value = urljoin(base, raw.strip())
    u = urlsplit(value)
    return value if u.scheme == "https" and u.hostname and not u.username and not u.password else ""

def text(node):
    return node.get_text(" ", strip=True) if node else ""
