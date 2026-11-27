# ZeroIPTV Extensions

ZeroIPTV'ye özel deklaratif JSON eklenti deposu. CloudStream veya çalıştırılabilir DEX bağımlılığı yoktur.

## Kurulum
Public GitHub deposu `opitiopiti/zeroiptv-extensions`, dal `main` önerilmiştir. `repo.json` ve `plugins/` doğrudan depo köküne yüklenir. Android kaynakta ExtensionSettings.REPO_URL bu adrese işaret eder; başka bir depo adı seçilirse uygulamadaki sabit değişmelidir.

## DiziBox
`plugins/dizibox.json` içindeki `baseUrl` güncel HTTPS site kökü, `previousHosts` geçmiş alan adlarıdır. Domain değişikliğinde eski host'u listeye ekleyin; yeni baseUrl yazın. Kurallar veya domain değişince hem repo.json hem plugin JSON version değerini aynı sayıya yükseltin. `enabled: false` ile eklenti kapatılır. Kullanıcı dış depo ekleyemez.

APK 30 dakikada bir (eklenti ekranı açıkken) repo ve katalog kontrolü yapar; manuel yenileme mümkündür. GitHub erişilemiyorsa yerel son geçerli tanım korunur. Video URL'leri bu depoda saklanmaz.

## Şema v1
- repo: schemaVersion, name, plugins[id, name, version, enabled, file]
- plugin: schemaVersion, id, version, name, type (`series` / `movie`), baseUrl, previousHosts, rows, search, detail, playback
- rows/search: göreli path, CSS cards/link/title seçicileri, isteğe bağlı label, kind
- detail: başlık, poster, açıklama, sezon ve bölüm seçicileri; bölüm numaraları için düzenli ifadeler
- playback: HTML içindeki medya/altyazı/iframe seçicileri ve sınırlı çözümleme seçenekleri

Bu örnek, verilen Kotlin sağlayıcıdan uyarlanan ilk DiziBox tanımıdır. Canlı kaynak ve tüm video hostları test edilmedi; CloudStream extractor uyumluluğu sunmaz. Yalnız yetkili içeriklerle kullanın. JSON motorunun tanımadığı yeni davranışlar Android motorunda geliştirme gerektirir.
