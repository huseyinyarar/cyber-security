# Hafta 2 · Ek Görev (Kali): Parola Kırma

**Süre:** 45 dk · **Ortam:** Kali sanal makinesi, internet kapalı · **Araçlar:** hashcat, john (Kali'de hazır gelir)

Bu ek görev, 2. haftanın parola saklama konusunu Kali'nin kendi araçlarıyla uygulamaya döker. Derste "zayıf özet hızlı kırılır, yavaş özet kırılmaz" dedik; burada bunu kendiniz ölçeceksiniz. Saldırgan rolüne geçip sızmış bir özet listesini kıracak, sonra aynı parolaların bcrypt'e geçince neden kırılamadığını göreceksiniz.

## Önce okuyun: etik ve yasa

- Buradaki bütün özetler bu görev için üretilmiştir; **hiçbiri gerçek bir kişinin parolası değildir**.
- Parola kırma araçları yalnızca **kendi sistemlerinizde ya da yazılı izniniz olan sistemlerde** kullanılır. Başkasının parola özetini izinsiz kırmak, 1. haftada gördüğümüz TCK 243 ve 244 kapsamında suçtur.
- Bu araçları Kali dışına çıkarmayın; ürettiğiniz özet ve çözüm dosyalarını rapor dışında paylaşmayın.

## Hazırlık

Bu klasörü Kali'ye kopyalayın ve terminalde klasöre girin. Önce kırılacak özetleri üretin (numaranızı yazın; herkesin listesi farklı olur):

```
python3 gorev5_ozet_uret.py 232923051
```

Bu komut üç dosya üretir: `ekip_md5.txt`, `ekip_sha256.txt` ve `ekip_bcrypt.txt`. Üçü de aynı sekiz parolanın farklı yöntemlerle alınmış özetleridir. Yanında küçük bir sözlük dosyası var: `ders_sozluk.txt`. (Gerçek saldırılarda `rockyou.txt` gibi milyonlarca satırlık listeler kullanılır; Kali'de `/usr/share/wordlists/rockyou.txt` olarak bulunur. Biz internetsiz ve hızlı çalışsın diye küçük bir liste kullanıyoruz.)

## Adım 1 · Tuzsuz MD5'i kırın (10 dk)

```
hashcat -m 0 -a 0 ekip_md5.txt ders_sozluk.txt
hashcat -m 0 ekip_md5.txt --show
```

`-m 0` MD5, `-a 0` sözlük saldırısı demektir. İkinci komut kırılan parolaları `özet:parola` biçiminde gösterir. **Ekran görüntüsü alın.** Kaç özet kırıldı, ne kadar sürdü?

> Çıkmazsa: aynı özeti ikinci kez kırmaya çalışırsanız hashcat "önceki sonuçtan" okur. Sıfırdan görmek için komutun sonuna `--potfile-disable` ekleyin.

## Adım 2 · Aynı parolalar, SHA-256 (5 dk)

```
hashcat -m 1400 -a 0 ekip_sha256.txt ders_sozluk.txt
hashcat -m 1400 ekip_sha256.txt --show
```

`-m 1400` SHA-256. Aynı parolalar yine kırılır. SHA-256, MD5'ten daha modern bir özet; buna rağmen parola saklama için neden yeterli olmadığını not edin.

## Adım 3 · Aynı parolalar, bcrypt (15 dk)

```
hashcat -m 3200 -a 0 ekip_bcrypt.txt ders_sozluk.txt
```

`-m 3200` bcrypt. Bu kez her deneme çok daha yavaş. Küçük sözlükte parolalar yine bulunur ama tek tek denemenin ne kadar yavaşladığını göreceksiniz. **Ekran görüntüsü alın.**

## Adım 4 · Hızı ölçün (10 dk)

hashcat'in karşılaştırma kipi, makinenizin saniyede kaç deneme yaptığını söyler:

```
hashcat -b -m 0
hashcat -b -m 1400
hashcat -b -m 3200
```

Her birinde `Speed` satırındaki değeri not edin. MD5 ve SHA-256 saniyede milyonlarca/on milyonlarca deneme yaparken bcrypt yüzlerce mertebesinde kalır. Bu fark, derste anlattığımız "yavaş özet" fikrinin ta kendisidir: bcrypt ve Argon2id kasıtlı olarak yavaştır, böylece saldırganın deneme hızını düşürür.

## Sorular

5.1 Aynı sekiz parolanın MD5, SHA-256 ve bcrypt özetlerini kırdınız. Üçünde de süre ve deneme hızı nasıldı? Adım 4'teki sayılarla açıklayın.
5.2 MD5 ile SHA-256 arasında kırma kolaylığı bakımından önemli bir fark gördünüz mü? SHA-256 "daha güçlü" bir özet olduğu halde parola saklama için neden hâlâ yetersiz?
5.3 bcrypt'in yavaşlığı normal kullanıcıya (giriş yaparken) ne kadar zaman kaybettirir, saldırgana ne kadar? Bu neden iyi bir denge?
5.4 Üç listede de aynı parolalar vardı. Gerçek bir sızıntıda iki kullanıcının MD5 özeti aynı çıkarsa bu ne anlama gelir? Tuz (salt) bunu nasıl önler? (2. hafta, tuz slaytını hatırlayın.)

## İsteğe bağlı (+5): john ile karşılaştırma

Kali'de john'un jumbo sürümü kuruludur. Aynı MD5 listesini onunla da kırın ve komut/çıktı farkını yazın:

```
john --format=raw-md5 --wordlist=ders_sozluk.txt ekip_md5.txt
john --format=raw-md5 --show ekip_md5.txt
```

## Rapora ekleyin

- Adım 1 ve 3'ün ekran görüntüleri (kırılan parolalar ve bcrypt'in yavaşlığı görünecek şekilde)
- Adım 4'teki üç hız değeri
- Dört sorunun cevabı

Ürettiğiniz özetlerde öğrenci numaranıza özel parolalar olduğu için çıktınız size aittir.
