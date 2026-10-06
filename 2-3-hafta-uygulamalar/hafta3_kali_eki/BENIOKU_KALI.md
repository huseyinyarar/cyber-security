# Hafta 3 · Ek Görev (Kali): TLS Tarama ve Ortadaki Adam

**Süre:** 45 dk · **Ortam:** Kali sanal makinesi, internet kapalı · **Araçlar:** sslscan, mitmproxy (Kali'de hazır gelir)

Bu ek görev, 3. haftanın TLS ve sertifika konusunu Kali araçlarıyla uygulamaya döker. İlk bölümde bir sunucunun TLS yapılandırmasını saldırgan gözüyle tararsınız. İkinci bölümde, derste anlattığımız ortadaki adam saldırısını (14. slayt) gerçek bir araçla, kendi tarayıcınızda görürsünüz.

Bu görev, 3. haftanın TLS/sertifika konusunun devamıdır. Bir kök CA'ya ve onun imzaladığı `lab.local` sertifikasına ihtiyaç duyar. Bunları bu klasörde tek komutla üretin (kendi öğrenci numaranızı yazın — kök CA adına gömülür):

```
python3 gorev1_pki_uret.py 232923051     # örn: python3 gorev1_pki_uret.py 20231234
```

Bu komut `pki/` klasörünü oluşturur (`ca.crt`, `ca.key`, `lab.crt`, `lab.key`). Aşağıdaki bütün adımlar bu klasörün olduğu yerden çalıştırılır. (Ana laboratuvar `hafta3_lab`'ta Görev 1'i zaten yaptıysanız ve `pki/` elinizde varsa bu adımı atlayabilirsiniz.)

### `lab.local` adını tanımlayın (Bölüm 2 için gerekli — bir kez)

Bölüm 2'de Firefox ile `https://lab.local:8443` adresine gideceksiniz. Bunun için `lab.local` adının kendi bilgisayarınıza (`127.0.0.1`) işaret etmesi gerekir. Şu satırı `/etc/hosts` dosyasına ekleyin (yönetici izni ister):
```
echo "127.0.0.1 lab.local" | sudo tee -a /etc/hosts
```
Doğrulayın: `getent hosts lab.local` komutu `127.0.0.1 lab.local` döndürmeli.

> **Yönetici izniniz yoksa / `/etc/hosts`'a dokunmak istemiyorsanız:** Sertifika `localhost` adını da kapsıyor. Bölüm 2'de `https://lab.local:8443` yerine `https://localhost:8443` kullanabilirsiniz; akış aynıdır. (Bölüm 1'deki sslscan zaten `127.0.0.1` kullandığı için bu adıma ihtiyaç duymaz.)

## Önce okuyun: etik ve yasa

- Bütün çalışma `127.0.0.1` üzerinde, kendi kurduğunuz sunucuya karşı yapılır.
- sslscan ve mitmproxy gibi araçlar yalnızca **kendi sistemlerinizde ya da yazılı izniniz olan sistemlerde** kullanılır. Başkasının trafiğine izinsiz girmek (ortadaki adam) suçtur (1. hafta, TCK 243–245).
- mitmproxy'nin kök CA'sını laboratuvar sonunda Firefox'tan **silin** (aşağıda son adım). Bu sertifika tarayıcınızda kaldığı sürece, o anahtara sahip biri sizin için sahte sertifika üretebilir.

## Bölüm 1 · sslscan ile TLS taraması (20 dk)

**1a.** Ana laboratuvardaki sunucuyu bir terminalde başlatın:
```
python3 gorev2_https_sunucu.py
```
Başka bir terminalde tarayın:
```
sslscan 127.0.0.1:8443
```
Çıktıyı inceleyin. Hangi TLS sürümleri açık? Hangi şifre takımları kabul ediliyor, hangisi tercih ediliyor? Sertifikanın konu ve veren alanları ne? **Ekran görüntüsü alın.** Çıktıyı rapora dosya olarak da alabilirsiniz:
```
sslscan 127.0.0.1:8443 > tarama_guclu.txt
```

**1b.** Şimdi kasıtlı olarak zayıf yapılandırılmış sunucuyu çalıştırın (eski TLS sürümlerine izin verir):
```
python3 zayif_sunucu.py
```
Başka terminalde:
```
sslscan 127.0.0.1:8445 > tarama_zayif.txt
```
İki taramayı karşılaştırın. **Ekran görüntüsü alın.**

> Not: Modern OpenSSL'de TLS 1.0 ve 1.1 zaten kapalı gelir; bu yüzden "zayıf" sunucuda bile en fazla TLS 1.2 açılır. Yine de iki tarama arasındaki farkı görebilirsiniz: güçlü sunucu yalnızca TLS 1.3 kabul ederken zayıf sunucu TLS 1.2'yi de kabul eder.

## Bölüm 2 · mitmproxy ile ortadaki adam (25 dk)

Bu bölümde siz saldırgan olacaksınız: trafiği kendi üzerinizden geçireceksiniz. Amaç, "bir kök CA'ya güvenmek" kararının ne kadar güçlü olduğunu canlı görmek.

> **Önce: güçlü sunucu açık olmalı.** mitmproxy'nin hedefi `https://lab.local:8443`'tür. Bölüm 1'de sunucuları kapattıysanız, bir terminalde güçlü sunucuyu yeniden başlatın ve **açık bırakın**: `python3 gorev2_https_sunucu.py`. Zayıf sunucuya (8445) bu bölümde gerek yoktur. (`pki/` zaten Adım 0'da üretildi.)

**2a.** Başka bir terminalde mitmproxy'yi başlatın. **`--ssl-insecure` ŞART:** lab sunucusunun sertifikasını kendi kök CA'nız imzaladı; bu bayrak olmadan mitmproxy sunucuya güvenmeyip `502` hatası verir, demo çalışmaz.
```
mitmproxy --listen-port 8080 --ssl-insecure
```

**2b.** Firefox'u bu proxy'ye yönlendirin: Settings › Network Settings › Manual proxy configuration. HTTP Proxy ve HTTPS Proxy olarak `127.0.0.1`, Port `8080`. (Türkçe arayüzde: Ayarlar › Ağ Ayarları › Elle proxy yapılandırması.)

**2b-EK (ŞART — yoksa "hep uyarı" sorunu yaşarsınız).** Firefox güvenlik gereği `localhost`/`127.0.0.1`'e (ve ona çözülen `lab.local`'a) giden bağlantıları varsayılan olarak **proxy'den geçirmez**. O zaman mitmproxy araya giremez ve sertifika yüklü olsa da olmasa da hep uyarı görürsünüz. Düzeltmek için:
1. Adres çubuğuna `about:config` yazın → "Accept the Risk and Continue".
2. `network.proxy.allow_hijacking_localhost` arayın → değerini **`true`** yapın.
3. `network.proxy.no_proxies_on` arayın → içinde `localhost, 127.0.0.1` varsa **silin, boş bırakın**.

> Adres olarak `localhost` yerine **`lab.local`** kullanın (Adım 0'da `/etc/hosts`'a eklediniz). Önemli: adres çubuğuna **`https://`** ile yazın — `http://` ile boş sayfa/`NS_ERROR` alırsınız.

**2c.** Henüz mitmproxy'nin kök CA'sı Firefox'ta güvenilir **değil.** HTTPS adresine gidin: `https://lab.local:8443`. Firefox sertifika uyarısı verir. **Bu, ortadaki adamın yakalandığı andır:** mitmproxy araya girip sahte bir sertifika sunuyor, ama Firefox onu imzalayan köke güvenmediği için reddediyor. **Ekran görüntüsü alın.**

**2d.** Şimdi saldırganın ihtiyacı olan tek şeyi verelim: mitmproxy'nin kök CA'sına güven. mitmproxy çalışırken tarayıcıda `http://mitm.it` adresine gidin, "Firefox" için sertifikayı indirin ve Firefox'un Authorities listesine "identify websites" yetkisiyle aktarın.

**2e.** Aynı HTTPS adresine tekrar gidin. Artık uyarı yok; mitmproxy penceresinde bütün isteklerin aktığını görürsünüz. **Ekran görüntüsü alın.** Derste anlattığımız ortadaki adam tam olarak budur: saldırgan güvenilen bir CA'ya sahip olunca, trafiği hiçbir uyarı olmadan okuyabilir. DigiNotar olayında saldırganın elindeki de buydu.

**2f. (Önemli, atlanmaz)** Laboratuvar sonunda şu üçünü de geri alın; yapmazsanız tarayıcınız savunmasız kalır:
1. Firefox'un proxy ayarını **"No proxy / Use system settings"** yapın.
2. mitmproxy'nin kök CA'sını Authorities listesinden **silin** (seç → Delete or Distrust).
3. `about:config`'te `network.proxy.allow_hijacking_localhost` değerini tekrar **`false`** yapın.

## Sorular

6.1 sslscan çıktısında güçlü sunucunuz hangi TLS sürümünü ve hangi şifre takımını tercih etti? Bu değerler ana laboratuvardaki `gorev2_istemci.py` çıktısıyla uyuşuyor mu?
6.2 Güçlü ve zayıf sunucu taramaları arasındaki fark neydi? Bir sistem yöneticisi olsanız, bir sunucuda hangi TLS sürümlerini kapatırdınız ve neden?
6.3 mitmproxy'nin CA'sını eklemeden önce Firefox neden uyarı verdi, ekledikten sonra neden vermedi? Bu, "bir kök CA'ya güvenmek" kararını nasıl açıklıyor?
6.4 Bu saldırının çalışması için saldırganın neye sahip olması gerekiyordu? Gerçek bir web sitesinde (örneğin bankanızda) bir saldırgan bunu neden kolayca yapamaz? (Sertifika Şeffaflığı ve CAA'yı hatırlayın; 27. slayt.)

## Rapora ekleyin

- Bölüm 1: güçlü ve zayıf taramaların ekran görüntüleri (ya da `tarama_*.txt` dosyaları)
- Bölüm 2: mitmproxy'nin reddedildiği (2c) ve kabul edildiği (2e) anların ekran görüntüleri
- Dört sorunun cevabı
- Onay: proxy ayarını kapattım ve mitmproxy CA'sını sildim
