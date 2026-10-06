#!/usr/bin/env python3
"""Hafta 3 Lab · Gorev 2 (yeniden uretim) · Guclu HTTPS sunucu.

Yalnizca TLS 1.3 kabul eden "guclu" sunucu. pki/ klasorundeki lab.local
sertifikasini sunar. Kali ekinin Bolum 1'i (sslscan) bunu tarar.

Once pki/ uretin:   python3 gorev1_pki_uret.py OGRENCI_NO
Sonra bu sunucu:    python3 gorev2_https_sunucu.py        # port 8443
Baska terminalde:   sslscan 127.0.0.1:8443

Karsilastirma icin zayif sunucu (TLS 1.2'yi de acar):
                    python3 zayif_sunucu.py               # port 8445
"""
import http.server
import ssl
import sys
from pathlib import Path

HOST, PORT = "127.0.0.1", 8443
CERT, KEY = "pki/lab.crt", "pki/lab.key"

if not (Path(CERT).exists() and Path(KEY).exists()):
    sys.exit(
        "HATA: pki/lab.crt veya pki/lab.key yok.\n"
        "Once calistirin:  python3 gorev1_pki_uret.py OGRENCI_NO"
    )

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Guclu yapilandirma: yalnizca TLS 1.3.
ctx.minimum_version = ssl.TLSVersion.TLSv1_3
ctx.maximum_version = ssl.TLSVersion.TLSv1_3
ctx.load_cert_chain(CERT, KEY)


class SessizHandler(http.server.SimpleHTTPRequestHandler):
    """sslscan yalnizca el sikismayi dener ve baglantiyi keser; bu da
    normalde ekrana yigin dokumu (BrokenPipe) olarak dusuyor. Tarama
    acisindan zararsiz, bu yuzden sessizce yutuyoruz ki terminal temiz kalsin."""

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionError, ssl.SSLError, OSError):
            self.close_connection = True

    def log_message(self, *a):
        pass


httpd = http.server.HTTPServer((HOST, PORT), SessizHandler)
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

print(f"Guclu sunucu (yalnizca TLS 1.3) calisiyor: https://{HOST}:{PORT}")
print("Durdurmak icin Ctrl+C. Taramak icin:  sslscan 127.0.0.1:8443")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nSunucu durduruldu.")
