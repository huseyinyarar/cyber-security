#!/usr/bin/env python3
"""
Hafta 2 · Görev 5 (Kali) hazırlık: kırılacak özet dosyalarını üretir.

Çalıştırma:  python3 gorev5_ozet_uret.py OGRENCI_NO
Örn:         python3 gorev5_ozet_uret.py 20231234

Bu betik üç dosya üretir:
  ekip_md5.txt      - bir sızıntıdan geldiğini varsaydığımız tuzsuz MD5 özetleri
  ekip_sha256.txt   - aynı parolaların tuzsuz SHA-256 özetleri
  ekip_bcrypt.txt   - aynı parolaların bcrypt (yavaş, tuzlu) özetleri
Parolalar öğrenci numaranıza bağlı olarak seçilir; herkesin listesi farklıdır.
Hiçbir dosya gerçek bir kişinin parolasını içermez.
"""
import hashlib
import os
import sys

# Kasıtlı olarak zayıf parolalar: hepsi yaygın sızıntı listelerinde bulunur.
HAVUZ = [
    "123456", "password", "qwerty", "iloveyou", "superman", "passw0rd",
    "123456789", "monkey", "dragon", "letmein", "trustno1", "abc123",
    "111111", "sunshine", "princess", "football", "welcome", "admin123",
    "master", "shadow", "ankara06", "istanbul34", "besiktas", "trabzon61",
]
KULLANICILAR = ["ayse", "burak", "cem", "deniz", "efe", "fatma", "gokhan", "hale"]


def bcrypt_uret(parola):
    try:
        import bcrypt
    except ImportError:
        return None
    return bcrypt.hashpw(parola.encode(), bcrypt.gensalt(rounds=10)).decode()


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print("Kullanım: python3 gorev5_ozet_uret.py OGRENCI_NO")
        print("Örn:      python3 gorev5_ozet_uret.py 20231234")
        return 1
    no = int(sys.argv[1])
    # Öğrenci numarasına göre 8 parola seç (herkeste farklı ama tekrarlanabilir)
    rastgele = __import__("random").Random(no)
    secili = rastgele.sample(HAVUZ, len(KULLANICILAR))

    with open("ekip_md5.txt", "w") as md5d, open("ekip_sha256.txt", "w") as shad:
        for parola in secili:
            md5d.write(hashlib.md5(parola.encode()).hexdigest() + "\n")
            shad.write(hashlib.sha256(parola.encode()).hexdigest() + "\n")

    satirlar = []
    for parola in secili:
        h = bcrypt_uret(parola)
        if h is None:
            print("[UYARI] bcrypt kütüphanesi yok; ekip_bcrypt.txt üretilmedi.")
            print("        Kali'de hazır gelir. Kurmak için: pip install bcrypt")
            break
        satirlar.append(h)
    else:
        open("ekip_bcrypt.txt", "w").write("\n".join(satirlar) + "\n")

    print(f"Öğrenci {no} için özetler üretildi:")
    print(f"  ekip_md5.txt     ({len(secili)} özet)")
    print(f"  ekip_sha256.txt  ({len(secili)} özet)")
    if satirlar:
        print(f"  ekip_bcrypt.txt  ({len(satirlar)} özet)")
    print("\nBu listelerdeki parolalar kasıtlı olarak zayıftır ve yalnızca")
    print("ders amaçlıdır. Üretilen özetleri ve çözümleri rapor dışında paylaşmayın.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
