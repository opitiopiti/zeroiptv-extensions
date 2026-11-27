# ZeroIPTV — Python Eklenti Geliştirme Kılavuzu (V14 / SDK 3)

Bu belge hem insan geliştiriciler hem de ChatGPT gibi kod üreten araçlar için **tam eklenti sözleşmesidir**. Yeni bir site için bu README'yi ve sitenin mevcut Python kodunu, örnek HTML/API yanıtlarını vererek ZeroIPTV uyumlu bir eklenti isteyebilirsiniz. Android kodunu yeniden yazmak gerekmez; aşağıdaki sözleşmeye uyulmalıdır.

ZeroIPTV Android uygulaması Kotlin, Chaquopy ve Python 3.11 kullanır. Eklentiler gerçek Python dosyalarıdır. CloudStream, JSON eklenti tanımı, harici sunucu veya yeni oynatıcı gerekmez. Dahili veri aktarımı JSON serileştirme kullanabilir; eklenti geliştiricisi Python `dict` ve `list` döndürür.

## 1. Kurulum Talimatı

Yeni bir eklenti hazırlatırken aşağıdaki talimatı bu README'nin tamamı ve siteye ait mevcut kaynak kodu ile birlikte gönderin:

> Bu README'deki ZeroIPTV V14 SDK 3 sözleşmesine uygun **tek dosyalık** Python eklentisi hazırla. Verdiğim site kaynak kodunu ve HTML/API örneklerini incele; bilinen URL ve ayrıştırma mantığını koru. `plugins/<id>.py` dosyasının tam kodunu ver. Metadata sabitlerini, HTTP başlıklarını, yalnız gerçekten desteklenen `get_home`, `get_series`, `get_movies`, `get_animes` fonksiyonlarını, zorunlu `search`, `get_details`, `resolve` fonksiyonlarını ve yardımcıları aynı dosyada yaz. Desteklenmeyen bölüm için boş fonksiyon veya sahte veri oluşturma. Kategori, Popüler, Trend gibi yeni ekran bölümü ekleme. Tüm ağ çağrılarında `ctx.get` kullan; yalnız erişim yetkisi olan kaynaklarla çalış. Manifest ve segment başlıklarını ayrı döndür. İçerik yolları domain'den bağımsız olsun. Yeni eklentide VERSION=1; mevcut eklentide VERSION artır. Python 3.11 ve BeautifulSoup kullan, başka bağımlılık ekleme. Dönüş biçimlerini bu README'deki alanlarla birebir eşleştir. Bilinmeyen HTML seçicilerini, URL yollarını veya oynatma yöntemlerini uydurma; doğrulanamayan yerleri belirt. Çevrimdışı fixture testleri ve yayınlama adımlarını da ver. Repo indeksini elle yazma; `build.py` ile üret. Android kodunu, Xtream API'yi, oynatıcıları ve diğer eklentileri değiştirme.

Güncelleme için mevcut `plugins/<id>.py` dosyasını da gönderin. Yeni eklenti geliştirmek için tüm Android projesi gerekmez.

## 2. Dört sabit içerik bölümü

| Tek dosyadaki fonksiyon | Ekran adı | Kart türü (`kind`) |
|---|---|---|
| `get_home(ctx, page=1)` | Son Bölümler | `episode` |
| `get_series(ctx, page=1)` | Diziler | `series` |
| `get_movies(ctx, page=1)` | Filmler | `movie` |
| `get_animes(ctx, page=1)` | Animeler | `series`, `episode` veya `movie` |

- Dört fonksiyon isteğe bağlıdır; en az biri bulunmalıdır. Fonksiyon varsa ilgili bölüm gösterilir, yoksa hiç gösterilmez. Boş `def`, `pass`, `...` ile sahte fonksiyon tanımlamayın. Sıra sabittir: Son Bölümler → Diziler → Filmler → Animeler.
- `build.py` dosyayı çalıştırmadan AST ile üst düzey `def` tanımlarını bulur ve `repo.tsv` üretir. Android paketi çalıştırırken gerçek çağrılabilir fonksiyonların indeksle eşleşmesini kontrol eder. Fonksiyon eklemek veya kaldırmak için APK değiştirilmez; VERSION artırılır ve paket yeniden üretilir.
- `get_popular`, `get_genres` vb. yardımcı olabilir ama yeni ekran bölümü oluşturmaz. Özel row listeleri ve kategori paneli yoktur. Arama ve yenileme araç çubuğundadır.
- Kaynak seçimi korunur. İlk mevcut bölüm açılır; bütün bölümler aynı anda ağdan çekilmez. Anime filmse `kind="movie"`, bölümlü anime ise `kind="series"` veya `"episode"` döndürün. Ayrı anime oynatıcısı yoktur.
- DiziBox yalnız `get_home` ve `get_series` içerir. Diziler fonksiyonu V13'teki üç tür yolunu tek listede birleştirir; eksiksiz site kataloğu olduğu doğrulanmamıştır.

## 3. Dosya düzeni ve metadata

```text
zeroiptv-extensions/
├── plugins/
│   ├── dizibox.py           # Tek dosya (mevcut)
│   └── orneksite.py         # Yeni site için örnek isim
├── common/                  # İsteğe bağlı ortak yardımcılar
│   ├── __init__.py
│   └── utils.py
├── build.py
├── test_plugins.py
├── requirements.txt
├── repo.tsv                 # Otomatik üretilir
├── packages/                # Otomatik sürümlü ZIP'ler
├── .github/workflows/build.yml
└── README.md
```

Her site için yalnız bir `.py` dosyası yazılır. Eski `plugins/dizibox/` benzeri klasörler SDK 3 oluşturucusu tarafından kullanılmaz. Paket oluşturucu tek dosyayı ZIP içindeki sürüme özel `__init__.py` olarak paketler; bunu kendiniz oluşturmayın. İsteğe bağlı `common/` yardımcılarını tüm paketlere sürümlü olarak ekler. `from .common.utils import absolute_https, text` gibi göreli import kullanılabilir; diğer eklentileri import etmeyin. `common/` değişirse tüm aktif eklentilerin VERSION değerlerini artırın, çünkü paket hash'leri değişir. DiziBox tek başına gerekli yardımcıları içerir.

### Dosyanın üst kısmındaki metadata

```python
ID = "orneksite"                 # dosya adıyla aynı, kalıcı
NAME = "Örnek Site"
VERSION = 1                      # pozitif tam sayı, her değişiklikte artır
TYPE = "mixed"                   # series / movie / mixed
BASE_URL = "https://example.com"  # yalnız HTTPS origin, sonda / yok
PREVIOUS_HOSTS = ()               # eski domainler, protokol/yol yok
ENABLED = True
```

Yedi metadata alanı zorunlu, üst düzey ve literal değer olmalıdır (hesaplanan ifadeler değil). ID küçük ASCII harfle başlar, küçük harf/rakam/alt çizgi kullanır, en fazla 50 karakterdir. Domain değiştiğinde ID değiştirmeden BASE_URL ve PREVIOUS_HOSTS güncellenir; VERSION artırılır. İçerik yolları `/ornek-dizi/` gibi domain bağımsız olmalıdır. Poster, altyazı ve gerçek medya için tam HTTPS URL kullanılır.

### Fonksiyon kuralları

Zorunlu: `search(ctx, query)`, `get_details(ctx, path)`, `resolve(ctx, path)`. Dört içerik fonksiyonundan en az biri zorunludur. Tüm bu fonksiyonlar üst düzey normal `def`, iki konumsal parametre olmalıdır; `async def`, decorator ile değiştirme, dinamik alias veya iç içe fonksiyon kullanmayın. Liste fonksiyonları için `page=1` önerilir. Sezon, bölüm, şifreleme, HTTP başlığı ve diğer yardımcı fonksiyonların isimleri serbesttir; hepsini aynı dosyada yazın. Android işlemleri arka plan thread'inde çağırır. Import sırasında ağ isteği veya uzun işlem başlatmayın.

## 4. HTTP, Logcat ve ayrıştırma

```python
from bs4 import BeautifulSoup

def get_document(ctx, path, operation="catalog"):
    response = ctx.get(BASE_URL + path, operation=operation)
    return BeautifulSoup(response.body, "html.parser"), response.url
```

`ctx.get(url, referer=None, headers=None, operation="catalog")` dönen nesnede `body` (metin), `url` (son adres) ve `content_type` vardır. Başarısız HTTP durumları istisna üretir; `response.status_code` alanı yoktur. İşlem adları: `catalog`, `search`, `details`, `season`, `resolve`, `extractor`. Gerçek istekler, durum kodları, süreler ve bağlantı hataları `tag:ZeroExtensions` Logcat'te bulunur. Ayrıntılı aday URL listeleri varsayılan olarak kapalıdır. Medya istekleri ortak oynatıcı katmanında loglanır.

Desteklenen başlıklar: `Accept`, `Accept-Language`, `User-Agent`, `Referer`, `Origin`, `Sec-CH-UA`, `Sec-CH-UA-Mobile`, `Sec-CH-UA-Platform`, `Sec-Fetch-Dest`, `Sec-Fetch-Mode`, `Sec-Fetch-Site`. `Host`, `Range`, `Connection`, `Accept-Encoding` otomatik yönetilir. Standart Python 3.11 ve BeautifulSoup 4.13.4 hazırdır. POST, özel cookie oturumu ve ek üçüncü taraf paketler SDK'da hazır değildir. Doğrudan `requests` veya `urllib` ağ çağrısı ortak Logcat/timeout katmanını atlayabilir; `ctx.get` kullanın. Köprü HTTPS, bağlantı/adres kontrolleri, 3 eşzamanlı HTTP isteği, en çok 2 MB yanıt ve zaman aşımı uygular. Çok büyük sayfalarda sayfalama kullanın.

## 5. Liste fonksiyonları ve dönüş biçimi

Her içerik fonksiyonu aşağıdaki Python sözlüğünü döndürür. `page` 1'den başlar. Motor sayfa numarasını ve cache'i yönetir; sayfanın kendisini baştan sona taramayın.

```python
# Tek eklenti dosyasında (sentetik sözleşme örneği)
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

`get_home(ctx, page=1)` için aynı sözleşme ve `kind="episode"`; `get_movies(ctx, page=1)` için `kind="movie"`; `get_animes(ctx, page=1)` için ve gerçek içerik türü kullanılır. Sonraki sayfa yoksa `next=False`. Gerçek boş sonuç `{"items": [], "next": False}`; kaynak hatasını boş katalog gibi döndürmeyin, istisna üretin. Böylece son başarılı cache korunabilir.

## 6. Arama — search

```python
def search(ctx, query):
    # Siteye uygun arama ve URL kodlaması burada yapılır.
    return {"items": [], "next": False}
```

Arama seçili eklenti genelindedir; seçili içerik sekmesiyle filtrelenmesi zorunlu değildir. Aynı kart sözleşmesini döndürür. Arama sayfalaması bu sürümde yoktur. `query` metindir, URL'ye eklemeden önce uygun biçimde kodlayın. Örnekteki boş sonuç yalnız sözleşmeyi göstermek içindir; gerçek eklenti kaynak aramasını uygulamalıdır.

## 7. Bilgi paneli, sezon ve bölümler — get_details

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

`path`, `title`, `episodes` zorunludur. `poster` ve `plot` boş olabilir. `season` ve `number` tam sayı; `path` ve `title` metin olmalıdır. Film için `episodes=[]`, `path` filmin oynatılacak yolu. Diziye son bölüm kartından girildiğinde `path` mümkünse dizinin ana yoluna normalleştirilir. Sezon ve bölüm yardımcı fonksiyonlarının isimleri serbesttir; `get_details` bunları çağırıp **tek** sonuç döndürür. Eksik sezon isteği varsa `complete=False`; mevcut cache'deki bölümlerle birleştirilir. Tam başarıda `complete=True`. Sezon ve bölüm sırasını sayısal tutun, aynı yolları tekrarlamayın.

Kartın üzerine gelindiğinde motor site detayını otomatik çekmez; hazır detay cache'i ve mevcut TMDB paneli kullanılır. `get_details` içerik açıldığında çağrılır. `year`, `rating`, `actors` gibi özel alanlar bu SDK'nın kaynak detay modelinde okunmaz; bunlar için mevcut TMDB arayüzü kullanılmaya devam eder. Panel tasarımı Kotlin'dedir, `detailpanel.py` yazmayın.

## 8. Video çözümleme — resolve ve HTTP başlıkları

`resolve(ctx, path)` sadece kullanıcı oynatmayı seçtiğinde çalışır. Video dosyasını Python indirmez ve dönüştürmez; erişim yetkisi olan oynatılabilir HTTPS medya URL'sini ve başlıkları döndürür. `url` bir HTML sayfası değil gerçek HLS/MP4/DASH kaynağı olmalıdır. Geçerli yetkilendirme yoksa açık hata üretin.

```python
# Aynı dosyada başlık sözlükleri — örnek
M3U8_HEADERS = {"Accept": "*/*"}
SEGMENT_HEADERS = {"Accept": "*/*"}
```

```python
# Aynı dosyada resolve — sentetik dönüş örneği (gerçek video değildir)

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

1. `plugins/<id>.py` dosyasını oluşturun. En az bir içerik fonksiyonu, zorunlu metadata ve zorunlu fonksiyonlar bulunmalıdır. `VERSION=1` ile başlayın.
2. Mevcut eklentide her kod veya ayar değişikliğinde `VERSION` artırın. Eski pakete geri dönmek için eski kodu daha yüksek VERSION ile yayınlayın.
3. Proje kökünde çalıştırın (Python 3.11 önerilir):

```bash
python -m pip install -r requirements.txt
python build.py
python -m unittest -v test_plugins
```

4. `plugins/`, oluşturulan `repo.tsv` ve `packages/<id>-<version>.zip` dosyalarını aynı Git commit'inde yükleyin. GitHub Actions otomatik üretim yapabilir; yazma izni gereklidir. Dal koruması veya eşzamanlı push varsa yerel üretip tek commit tercih edin. Eski paketler yeni indekste referans edilmiyorsa artık kullanılmaz.
5. Uygulamada Depoyu yenile seçeneğine basın veya yeniden açın. APK'yı her eklenti güncellemesinde derlemeniz gerekmez. Ancak yeni SDK yeteneği/bağımlılık gerekiyorsa APK güncellemesi gerekir.
6. Bölüm kaldırmak için ilgili içerik fonksiyonunu silin, VERSION artırıp yeniden paketleyin. Eklentiyi tamamen kaldırmak için dosyasını silin veya `ENABLED=False` yapıp indeksi yeniden üretin.

### İndeks (otomatik)

`repo.tsv` ilk satırı `ZEROIPTV-PYTHON-3` ve her satır 9 tab ayrımlı alan içerir: ID, VERSION, NAME, TYPE, BASE_URL, PREVIOUS_HOSTS (virgüllü), bölüm ID'leri (virgüllü), paket yolu, SHA-256. Bölüm ID'leri yalnız `sonbolumler,diziler,filmler,animeler` olabilir. Elle düzenlemeyin. V12/V13 indeks biçimi ile uyumlu değildir; V14 APK gereklidir. Paket adı `zeroext_<id>_v<version>`; ZIP ana `__init__.py` ve isteğe bağlı `common/*.py` dosyalarını içerir, en çok 100 dosya, her biri en fazla 500 KB, toplam açılmış boyut 2 MB. Uygulama hash ve paket yapısını doğrular.

Varsayılan depo: `https://raw.githubusercontent.com/opitiopiti/zeroiptv-extensions/refs/heads/main/repo.tsv`. İlk V14 kurulumunda bu depoya ZIP içeriğini `.github` dahil yükleyin; eski `repo.json`, `plugins/dizibox.json`, `plugins/dizibox/` klasörü ve `packages/dizibox-6.zip` kaldırılabilir. V12/V13 APK'lar yeni indeksi okuyamaz; geçişte V14 derleyin. Başka depoya geçmek APK ayarı gerektirir.

## 11. Kontrol ve hata ayıklama

- Fonksiyon adları birebir doğru mu? Yalnız gerçekten desteklenen içerik fonksiyonları var mı? Dosyanın VERSION değeri arttı mı?
- Tüm kartların `kind`, `path`, `title` değerleri doğru mu? Sayfalama gerçekten sona eriyor mu? Bölümler tekil ve sıralı mı?
- Manifest ve segment başlıkları ayrı mı? Kaynak erişim yetkisi var mı? JSON değil, Python sözlükleri mi dönüyor?
- `python build.py` ve çevrimdışı testler geçiyor mu? Repo ve paket aynı commit'te mi?
- Android Studio Logcat filtresi `tag:ZeroExtensions`. Repo/paket HTTP istekleri, katalog ve oynatıcı HTTP sonuçları görünür. 200 tek başına video başarısı anlamına gelmez. Hata durumunda HTTP satırları, kullanılan eklenti sürümü ve ilgili kaynak fixture'ını paylaşın.

## 12. Güvenlik ve sınırlar

Yalnız güvenilen ve kullanma/dağıtma hakkınız bulunan kaynaklar için eklenti yazın. Eklenti paketleri çalıştırılabilir Python kodudur. SHA-256 aktarım bütünlüğünü denetler, bağımsız imza veya sandbox değildir. Python uygulama yetkileriyle çalışabilir; Xtream hesap bilgileri SDK'ya verilmez ancak bu gerçek izolasyon değildir. GitHub yazma izinlerini koruyun, üçüncü taraf kodlarını otomatik çalıştırmayın. Platform dağıtım kurallarını kontrol edin.

Bu V14 paketinde çevrimdışı Python fixture testleri vardır. Gerçek Android APK derlemesi, Android TV kumanda davranışı, canlı site kataloğu ve oynatma bu ortamda doğrulanmamıştır. DiziBox'ın önceki çözümleme ve HTTP başlık mantığı tek dosyaya taşınmıştır.
