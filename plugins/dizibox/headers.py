from urllib.parse import urlsplit, urlunsplit

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
