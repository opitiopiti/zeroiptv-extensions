import re
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup
from .common import absolute, site_url
from .headers import headers_for


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
