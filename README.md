# ZeroIPTV — Python Eklenti Geliştirme Kılavuzu (V13 / SDK 2)

Bu belge hem insan geliştiriciler hem de ChatGPT gibi kod üreten araçlar için **tam eklenti sözleşmesidir**. Yeni bir site için bu README'yi ve sitenin mevcut Python kodunu, örnek HTML/API yanıtlarını vererek ZeroIPTV uyumlu bir eklenti isteyebilirsiniz. Android kodunu yeniden yazmak gerekmez; aşağıdaki sözleşmeye uyulmalıdır.

ZeroIPTV Android uygulaması Kotlin, Chaquopy ve Python 3.11 kullanır. Eklentiler gerçek Python dosyalarıdır. CloudStream, JSON eklenti tanımı, harici sunucu veya yeni oynatıcı gerekmez. Dahili veri aktarımı JSON serileştirme kullanabilir; eklenti geliştiricisi Python `dict` ve `list` döndürür.

## 1. ChatGPT'ye kopyalanacak talimat

Yeni bir eklenti hazırlatırken aşağıdaki talimatı bu README'nin tamamı ve siteye ait mevcut kaynak kodu ile birlikte gönderin:

> Bu README'deki ZeroIPTV V13 SDK 2 sözleşmesine uygun bir Python eklentisi hazırla. Verdiğim kaynak kodunu incele, mevcut URL'leri ve ayrıştırma mantığını koru. Yalnız gerçekten desteklenen Son Bölümler, Diziler, Filmler, Animeler dosyalarını oluştur. Desteklenmeyen bölümler için boş dosya ya da sahte içerik üretme. Kategori/Popüler/Trend gibi ayrı ekran bölümleri ekleme. `config.py`, `__init__.py`, `search.py`, `detail.py`, `extractor.py` ve gerekli yardımcı dosyaları eksiksiz yaz. Tüm ağ çağrılarında `ctx.get` kullan; erişim yetkisi olan medya kaynaklarıyla çalış. Manifest ve segment başlıklarını ayrı döndür. Dizi ve film için ZeroIPTV'nin mevcut oynatıcı sözleşmesini kullan. İçerik yollarını domain'den bağımsız tut. `VERSION` değerini artır. Dosya bazında tam kodları, kurulum adımlarını ve çevrimdışı fixture testlerini ver. Bilinmeyen HTML seçicilerini, URL yollarını veya oynatma yöntemlerini uydurma; doğrulanamayan yerleri açıkça belirt. Mümkünse `plugins/<id>/` klasörünü ZIP olarak paylaş. Repo indeksini elle yazma; `build.py` ile üret.

Bir eklentiye değişiklik yaptırırken mevcut `plugins/<id>/` klasörünü de gönderin. Diğer eklentilere, Android projesine, Xtream API veya ortak oynatıcılara gereksiz müdahale edilmemelidir.

## 2. Dört sabit içerik bölümü

| Python dosyası | Ekran adı | Çağrılan fonksiyon | Kart türü (`kind`) |
|---|---|---|---|
| `sonbolumler.py` | Son Bölümler | `get_home(ctx, page=1)` | `episode` |
| `diziler.py` | Diziler | `get_series(ctx, page=1)` | `series` |
| `filmler.py` | Filmler | `get_movies(ctx, page=1)` | `movie` |
| `animeler.py` | Animeler | `get_animes(ctx, page=1)` | `series`, `episode` veya `movie` |

- Bu dosyalar isteğe bağlıdır; en az biri bulunmalıdır. Dosya varsa bölüm görünür, yoksa bölüm hiç görünmez. Sıra sabittir: Son Bölümler → Diziler → Filmler → Animeler.
- `build.py` dosya varlığını otomatik kontrol eder ve `repo.tsv` içine ekler. APK bu metadatanın paketteki dosyalarla eşleşmesini doğrular. Bölüm eklemek veya kaldırmak için APK değiştirilmez; paket sürümünü artırın.
- `populer.py`, `dram.py`, `kategoriler.py` gibi yardımcı dosyalar yazılabilir ama ayrı UI bölümü oluşturmaz. `HOME_LABEL`, özel row listeleri ve kategori menüleri yoktur. Arama ve yenileme içerik bölümü değil, araç çubuğundaki işlevlerdir.
- Kaynak eklenti seçimi korunur. Seçili eklentinin mevcut bölümleri gösterilir; ilk mevcut bölüm varsayılan olarak açılır. Dört bölümün tamamını aynı anda ağdan çekmeyiz.
- Anime filmse `kind="movie"`, bölümlü anime ise `kind="series"` ya da `"episode"` döndürün. `kind="anime"` kullanmayın; ayrı anime oynatıcısı yoktur.

Örnek: DiziBox paketinde `sonbolumler.py` ve `diziler.py` var; dolayısıyla sadece Son Bölümler ve Diziler görünür. Bu örnekte Diziler listesi önceki eklentideki üç tür yolunu (dram, komedi, korku) tek listede birleştirir, eksiksiz site kataloğu olduğu garanti edilmez. Doğru genel dizi listeleme yolu doğrulandığında sadece `diziler.py` düzenlenebilir. Türler ekranda ayrı gösterilmez.

## 3. Klasör düzeni

```text
zeroiptv-extensions/
├── build.py                 # Paket ve indeks üretir
├── test_plugins.py          # Çevrimdışı testler
├── requirements.txt
├── repo.tsv                 # Otomatik, elle değiştirme
├── packages/                # Otomatik sürümlü ZIP dosyaları
├── .github/workflows/build.yml
└── plugins/
    └── orneksite/
        ├── __init__.py      # Zorunlu, boş olabilir
        ├── config.py        # Zorunlu
        ├── sonbolumler.py   # İsteğe bağlı
        ├── diziler.py      # İsteğe bağlı
        ├── filmler.py      # İsteğe bağlı
        ├── animeler.py     # İsteğe bağlı
        ├── search.py       # Zorunlu
        ├── detail.py       # Zorunlu
        ├── extractor.py    # Zorunlu
        ├── seasons.py      # İsteğe bağlı yardımcı
        ├── episodes.py     # İsteğe bağlı yardımcı
        ├── headers.py      # İsteğe bağlı yardımcı
        └── common.py       # İsteğe bağlı yardımcı
```

Tüm Python fonksiyonları normal `def` olmalıdır, `async def` değil. Android bunları işçi thread'inde çağırır. `__init__.py` boş kalabilir; motor ilgili modülü doğrudan yükler. Yardımcı dosyalarda göreli import (`from .common import ...`) kullanın. Modül import edilirken ağ isteği başlatmayın. Her eklenti klasörü kendi yardımcılarını içermelidir; diğer eklentilere bağımlı olmayın.

### config.py

```python
ID = "orneksite"                  # klasör adı ile aynı, kalıcı
NAME = "Örnek Site"
VERSION = 1                      # pozitif tam sayı, her değişiklikte artır
TYPE = "mixed"                   # series / movie / mixed
BASE_URL = "https://example.com"  # yalnız HTTPS origin, sonda / yok
PREVIOUS_HOSTS = ()               # eski domainler, protokol/yol yok
ENABLED = True
```

`ID` küçük ASCII harfle başlar, sadece küçük harf/rakam/alt çizgi kullanır, en fazla 50 karakterdir. Site adresi değişirse ID değiştirilmez; `BASE_URL` güncellenir ve eski domain `PREVIOUS_HOSTS` listesine eklenir. İçerik yolları `/ornek-dizi/` gibi domain bağımsız olmalıdır. Tam URL'ler poster, altyazı ve gerçek medya için kullanılabilir. Eski yollar değişmişse Python'da açık eşleme gerekebilir.

## 4. HTTP, Logcat ve ayrıştırma

```python
from bs4 import BeautifulSoup
from .config import BASE_URL

def get_document(ctx, path, operation="catalog"):
    response = ctx.get(BASE_URL + path, operation=operation)
    return BeautifulSoup(response.body, "html.parser"), response.url
```

`ctx.get(url, referer=None, headers=None, operation="catalog")` dönen nesnede `body` (metin), `url` (son adres) ve `content_type` vardır. Başarısız HTTP durumları istisna üretir; `response.status_code` alanı yoktur. İşlem adları: `catalog`, `search`, `details`, `season`, `resolve`, `extractor`. Gerçek istekler, durum kodları, süreler ve bağlantı hataları `tag:ZeroExtensions` Logcat'te bulunur. Ayrıntılı aday URL listeleri varsayılan olarak kapalıdır. Medya istekleri ortak oynatıcı katmanında loglanır.

Desteklenen başlıklar: `Accept`, `Accept-Language`, `User-Agent`, `Referer`, `Origin`, `Sec-CH-UA`, `Sec-CH-UA-Mobile`, `Sec-CH-UA-Platform`, `Sec-Fetch-Dest`, `Sec-Fetch-Mode`, `Sec-Fetch-Site`. `Host`, `Range`, `Connection`, `Accept-Encoding` otomatik yönetilir. Standart Python 3.11 ve BeautifulSoup 4.13.4 hazırdır. POST, özel cookie oturumu ve ek üçüncü taraf paketler SDK'da hazır değildir. Doğrudan `requests` veya `urllib` ağ çağrısı ortak Logcat/timeout katmanını atlayabilir; `ctx.get` kullanın. Köprü HTTPS, bağlantı/adres kontrolleri, 3 eşzamanlı HTTP isteği, en çok 2 MB yanıt ve zaman aşımı uygular. Çok büyük sayfalarda sayfalama kullanın.

## 5. Liste dosyaları ve dönüş biçimi

Her içerik fonksiyonu aşağıdaki Python sözlüğünü döndürür. `page` 1'den başlar. Motor sayfa numarasını ve cache'i yönetir; sayfanın kendisini baştan sona taramayın.

```python
# diziler.py (sentetik sözleşme örneği, gerçek site seçicisi değil)
def get_series(ctx, page=1):
    return {
        "items": [
            {"path": "/sample-series/", "title": "Örnek Dizi",
             "poster": "https://example.com/poster.jpg", "label": "2026", "kind": "series"}
        ] if page == 1 else [],
        "next": False,
    }
```

| Alan | Tip | Açıklama |
|---|---|---|
| `items` | list | İçerik kartları; zorunlu |
| `next` | bool | Gerçekten sonraki sayfa varsa True |
| `path` | str | Kalıcı site içi yol; `/` ile başlar, `//` ile başlamaz |
| `title` | str | Görünen film/dizi adı |
| `poster` | str | Tam HTTPS görsel adresi veya boş metin |
| `label` | str | Örn. `1. Sezon 5. Bölüm`; yoksa boş |
| `kind` | str | `episode`, `series`, `movie`; açıkça belirtin |

`sonbolumler.py` için aynı sözleşme, `def get_home(ctx, page=1)` ve `kind="episode"`; `filmler.py` için `def get_movies(ctx, page=1)` ve `kind="movie"`; `animeler.py` için `def get_animes(ctx, page=1)` ve gerçek içerik türü kullanılır. Sonraki sayfa yoksa `next=False`. Gerçek boş sonuç `{"items": [], "next": False}`; kaynak hatasını boş katalog gibi döndürmeyin, istisna üretin. Böylece son başarılı cache korunabilir.

## 6. Arama — search.py

```python
def search(ctx, query):
    # Siteye uygun arama ve URL kodlaması burada yapılır.
    return {"items": [], "next": False}
```

Arama seçili eklenti genelindedir; seçili içerik sekmesiyle filtrelenmesi zorunlu değildir. Aynı kart sözleşmesini döndürür. Arama sayfalaması bu sürümde yoktur. `query` metindir, URL'ye eklemeden önce uygun biçimde kodlayın. Örnekteki boş sonuç yalnız sözleşmeyi göstermek içindir; gerçek eklenti kaynak aramasını uygulamalıdır.

## 7. Bilgi paneli, sezon ve bölümler — detail.py

```python
def get_details(ctx, path):
    return {
        "path": "/sample-series/",     # dizinin kalıcı ana yolu
        "title": "Örnek Dizi",
        "poster": "https://example.com/poster.jpg",
        "plot": "Örnek açıklama.",
        "episodes": [
            {"path": "/sample-series-s1-e1/", "title": "1. Bölüm", "season": 1, "number": 1},
            {"path": "/sample-series-s1-e2/", "title": "2. Bölüm", "season": 1, "number": 2},
        ],
        "complete": True,
    }
```

`path`, `title`, `episodes` zorunludur. `poster` ve `plot` boş olabilir. `season` ve `number` tam sayı; `path` ve `title` metin olmalıdır. Film için `episodes=[]`, `path` filmin oynatılacak yolu. Diziye son bölüm kartından girildiğinde `path` mümkünse dizinin ana yoluna normalleştirilir. `episodes.py` ve `seasons.py` yardımcı dosyalardır; fonksiyon isimleri serbesttir, `detail.py` bunları çağırıp **tek** sonuç döndürür. Eksik sezon isteği varsa `complete=False`; mevcut cache'deki bölümlerle birleştirilir. Tam başarıda `complete=True`. Sezon ve bölüm sırasını sayısal tutun, aynı yolları tekrarlamayın.

Kartın üzerine gelindiğinde motor site detayını otomatik çekmez; hazır detay cache'i ve mevcut TMDB paneli kullanılır. `get_details` içerik açıldığında çağrılır. `year`, `rating`, `actors` gibi özel alanlar bu SDK'nın kaynak detay modelinde okunmaz; bunlar için mevcut TMDB arayüzü kullanılmaya devam eder. Panel tasarımı Kotlin'dedir, `detailpanel.py` yazmayın.

## 8. Video çözümleme — extractor.py ve headers.py

`resolve(ctx, path)` sadece kullanıcı oynatmayı seçtiğinde çalışır. Video dosyasını Python indirmez ve dönüştürmez; erişim yetkisi olan oynatılabilir HTTPS medya URL'sini ve başlıkları döndürür. `url` bir HTML sayfası değil gerçek HLS/MP4/DASH kaynağı olmalıdır. Geçerli yetkilendirme yoksa açık hata üretin.

```python
# headers.py — örnek, yalnız kaynağın belgelenmiş gereksinimleri eklenir
M3U8_HEADERS = {"Accept": "*/*"}
SEGMENT_HEADERS = {"Accept": "*/*"}
```

```python
# extractor.py — sentetik dönüş örneği (gerçek video değildir)
from .headers import M3U8_HEADERS, SEGMENT_HEADERS

def resolve(ctx, path):
    # Gerçek eklentide yetkili kaynak API'sinden medya URL'sini alın.
    return {
        "url": "https://example.com/authorized/master.m3u8",
        "mimeType": "application/x-mpegURL",
        "manifestHeaders": dict(M3U8_HEADERS),
        "headers": dict(SEGMENT_HEADERS),
        "subtitles": [
            {"url": "https://example.com/authorized/tr.vtt", "language": "tr",
             "label": "Türkçe", "mimeType": "text/vtt"}
        ],
    }
```

| Alan | Görev |
|---|---|
| `url` | Gerçek oynatılabilir HTTPS adresi (zorunlu) |
| `mimeType` | HLS için `application/x-mpegURL`, MP4 için `video/mp4`, DASH için `application/dash+xml` veya boş (otomatik) |
| `manifestHeaders` | İlk manifest isteğinin başlıkları |
| `headers` | Diğer medya isteklerinin ortak başlıkları (alt manifest, segment, vb.) |
| `subtitles` | İsteğe bağlı liste, yoksa `[]` |

Başlık değerleri tamamlanmış metin olmalıdır; gerekiyorsa dinamik değerleri Python içinde oluşturun. SDK genel amaçlı `{sourceUrl}` şablonlarını otomatik çözmez. Altyazıda `url` ve `mimeType` zorunlu, `language` ve `label` isteğe bağlı. WebVTT için `text/vtt`, SRT için `application/x-subrip`. HLS içindeki çoklu ses ve altyazı Media3 tarafından desteklenir; Python sonucu ayrı ses listesi kabul etmez. Dizi ve anime bölümleri `SeriesPlayer`, film ve anime filmleri `MoviesPlayer` ile açılır. Oynatma adresi kalıcı katalog cache'ine yazılmaz.

## 9. Önbellek ve çalışma sırası

- Uygulama açılışında, başarılı Xtream oturumundan sonra GitHub kontrolü yapılır; anasayfa bunu beklemez. Python ilk katalog/detay/oynatma çağrısında başlatılır.
- Depo, liste, arama ve detay cache süresi 30 dakikadır. Ekranda eski kayıt varsa gösterilir, ihtiyaç halinde yenilenir. Bir bölüm yalnız görünürken veya ilgili detay/arama akışı sırasında yenilenir; dört bölüm sürekli topluca taranmaz. Uygulama kapalıyken 30 dakikalık kontrol garanti edilmez.
- Manuel yenileme ve depo yenileme mevcuttur. Kaynak hatasında eski katalog korunur. Eklenti paketi/indeks yükseltilince yeni bölüm metadatası güncellenir. İçerik cache'i sekme ve sayfa bazında ayrılır.
- `ctx.get` ağ sınırlarını uygular; Python'da sonsuz döngü, sınırsız thread, toplu site taraması ve beklemeler kullanmayın. Gerekirse sınırlı paralellik kullanın. Oynatma işlemini açılışta tetiklemeyin.

## 10. Yeni eklenti yayınlama ve güncelleme

1. `plugins/<id>/` klasörünü oluşturun ve yukarıdaki dosyaları ekleyin. En az bir içerik dosyası ve zorunlu fonksiyonlar bulunmalıdır. `VERSION=1` ile başlayın.
2. Mevcut eklentide her kod veya ayar değişikliğinde `VERSION` artırın. Eski pakete geri dönmek için eski kodu daha yüksek VERSION ile yayınlayın.
3. Proje kökünde çalıştırın (Python 3.11 önerilir):

```bash
python -m pip install -r requirements.txt
python build.py
python -m unittest -v test_plugins
```

4. `plugins/`, oluşturulan `repo.tsv` ve `packages/<id>-<version>.zip` dosyalarını aynı Git commit'inde yükleyin. GitHub Actions otomatik üretim yapabilir; yazma izni gereklidir. Dal koruması veya eşzamanlı push varsa yerel üretip tek commit tercih edin. Eski paketler yeni indekste referans edilmiyorsa artık kullanılmaz.
5. Uygulamada Depoyu yenile seçeneğine basın veya yeniden açın. APK'yı her eklenti güncellemesinde derlemeniz gerekmez. Ancak yeni SDK yeteneği/bağımlılık gerekiyorsa APK güncellemesi gerekir.
6. Bölüm kaldırmak için ilgili `.py` dosyasını silin, VERSION artırıp yeniden paketleyin. Eklentiyi tamamen kaldırmak için klasörünü silin veya `ENABLED=False` yapıp indeksi yeniden üretin.

### İndeks (otomatik)

`repo.tsv` ilk satırı `ZEROIPTV-PYTHON-2` ve her satır 9 tab ayrımlı alan içerir: ID, VERSION, NAME, TYPE, BASE_URL, PREVIOUS_HOSTS (virgüllü), bölüm ID'leri (virgüllü), paket yolu, SHA-256. Bölüm ID'leri yalnız `sonbolumler,diziler,filmler,animeler` olabilir. Elle düzenlemeyin. V12 indeks biçimi ile uyumlu değildir; V13 APK gereklidir. Paket adı `zeroext_<id>_v<version>`; ZIP sadece Python dosyaları içermeli, en çok 100 dosya, her biri en fazla 500 KB, toplam açılmış boyut 2 MB. Uygulama hash ve paket yapısını doğrular.

Varsayılan depo: `https://raw.githubusercontent.com/opitiopiti/zeroiptv-extensions/refs/heads/main/repo.tsv`. İlk V13 kurulumunda bu depoya ZIP içeriğini `.github` dahil yükleyin; eski `repo.json` ve `plugins/dizibox.json` gerekmez. V12 APK'lar yeni indeksi okuyamaz; geçişte V13 derleyin. Başka depoya geçmek APK ayarı gerektirir.

## 11. Kontrol ve hata ayıklama

- Fonksiyon adları birebir doğru mu? Yalnız desteklenen dört içerik dosyası var mı? `config.py` sürümü arttı mı?
- Tüm kartların `kind`, `path`, `title` değerleri doğru mu? Sayfalama gerçekten sona eriyor mu? Bölümler tekil ve sıralı mı?
- Manifest ve segment başlıkları ayrı mı? Kaynak erişim yetkisi var mı? JSON değil, Python sözlükleri mi dönüyor?
- `python build.py` ve çevrimdışı testler geçiyor mu? Repo ve paket aynı commit'te mi?
- Android Studio Logcat filtresi `tag:ZeroExtensions`. Repo/paket HTTP istekleri, katalog ve oynatıcı HTTP sonuçları görünür. 200 tek başına video başarısı anlamına gelmez. Hata durumunda HTTP satırları, kullanılan eklenti sürümü ve ilgili kaynak fixture'ını paylaşın.

## 12. Güvenlik ve sınırlar

Yalnız güvenilen ve kullanma/dağıtma hakkınız bulunan kaynaklar için eklenti yazın. Eklenti paketleri çalıştırılabilir Python kodudur. SHA-256 aktarım bütünlüğünü denetler, bağımsız imza veya sandbox değildir. Python uygulama yetkileriyle çalışabilir; Xtream hesap bilgileri SDK'ya verilmez ancak bu gerçek izolasyon değildir. GitHub yazma izinlerini koruyun, üçüncü taraf kodlarını otomatik çalıştırmayın. Platform dağıtım kurallarını kontrol edin.

Bu V13 paketinde çevrimdışı Python fixture testleri vardır. Gerçek Android APK derlemesi, Android TV kumanda davranışı, canlı site kataloğu ve oynatma bu ortamda doğrulanmamıştır. DiziBox'ın önceki extractor ve HTTP başlık dosyaları değişmeden korunmuştur.
