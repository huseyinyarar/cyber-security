#!/usr/bin/env python3
"""Hafta 3 Lab · Gorev 1 (yeniden uretim) · PKI olusturucu.

Kali ekinin ihtiyac duydugu pki/ klasorunu uretir:
  pki/ca.crt , pki/ca.key   -> kok CA (ogrenci numarasiyla isimlenir)
  pki/lab.crt, pki/lab.key  -> lab.local yaprak sertifikasi (kok CA imzalar)

Kullanim:
    python3 gorev1_pki_uret.py OGRENCI_NO      # orn: python3 gorev1_pki_uret.py 20231234

Internet gerekmez. Yalnizca Python 'cryptography' kutuphanesini kullanir
(Kali'de hazir gelir; yoksa:  pip install cryptography).
"""
import sys
import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def ogrenci_no():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    print("Uyari: ogrenci numarasi verilmedi, ornek '20231234' kullaniliyor.")
    print("Dogrusu:  python3 gorev1_pki_uret.py SENIN_NUMARAN")
    return "20231234"


def yaz(klasor, ad, veri):
    yol = klasor / ad
    yol.write_bytes(veri)
    print(f"  yazildi: {yol}")


def main():
    no = ogrenci_no()
    pki = Path("pki")
    pki.mkdir(exist_ok=True)

    # Sertifikalar gecmise biraz tasarsin ki saat kaymasinda gecersiz olmasin.
    simdi = datetime.datetime.now(datetime.timezone.utc)
    basla = simdi - datetime.timedelta(days=1)
    bitis = simdi + datetime.timedelta(days=825)  # ~2 yil, tarayici sinirlari icinde

    # ---- 1) Kok CA ----
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_adi = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "TR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Siber Guvenlik Ders"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"Siber Güvenlik Ders Kök CA - {no}"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_adi)
        .issuer_name(ca_adi)  # kok -> kendini imzalar
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(basla)
        .not_valid_after(bitis)
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=False, content_commitment=False,
                key_encipherment=False, data_encipherment=False,
                key_agreement=False, key_cert_sign=True, crl_sign=True,
                encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
        .sign(ca_key, hashes.SHA256())
    )

    # ---- 2) lab.local yaprak sertifikasi ----
    lab_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    lab_adi = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "TR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Siber Guvenlik Ders"),
        x509.NameAttribute(NameOID.COMMON_NAME, "lab.local"),
    ])
    lab_cert = (
        x509.CertificateBuilder()
        .subject_name(lab_adi)
        .issuer_name(ca_adi)
        .public_key(lab_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(basla)
        .not_valid_after(bitis)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("lab.local"),
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            ]),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=False,
                key_encipherment=True, data_encipherment=False,
                key_agreement=False, key_cert_sign=False, crl_sign=False,
                encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    pem = serialization.Encoding.PEM
    no_enc = serialization.NoEncryption()
    pkcs8 = serialization.PrivateFormat.TraditionalOpenSSL

    print("PKI uretiliyor (pki/):")
    yaz(pki, "ca.crt", ca_cert.public_bytes(pem))
    yaz(pki, "ca.key", ca_key.private_bytes(pem, pkcs8, no_enc))
    yaz(pki, "lab.crt", lab_cert.public_bytes(pem))
    yaz(pki, "lab.key", lab_key.private_bytes(pem, pkcs8, no_enc))

    print()
    print("Bitti. Kontrol:")
    print("  openssl x509 -in pki/lab.crt -noout -subject -issuer -ext subjectAltName")
    print(f"  Beklenen Issuer: Siber Güvenlik Ders Kök CA - {no}")


if __name__ == "__main__":
    main()
