# ZeroIPTV Extensions V4

`repo.json` ve `plugins/` klasörünü GitHub deposunun main dalının köküne yükleyin. V9 Android motoru gerekir.

`playback.headerProfiles` alanında `host`, `pathPrefix`, `pathSuffix`, `requestHeaders`, `mediaHeaders` tanımlanabilir. İlk eşleşen profil uygulanır. `requestHeaders` kaynak isteği ve aynı başlangıç manifesti için, `mediaHeaders` sonraki medya/alt playlist/segment/altyazı istekleri içindir. `{sourceBaseUrl}` son yol ekini çıkarır, `{sourceOrigin}` kaynak origin'ini üretir. Host, Range, Accept-Encoding ve Connection HTTP istemcisine bırakılır. Kimlik bilgilerini JSON'a koymayın.

Domain veya başka kurallar değişirse repo ve plugin version birlikte artırılır. schemaVersion=1 kalır. Sadece yetkili içerikler için kullanın. APK derleme ve canlı oynatma henüz doğrulanmamıştır.
