import http.server, ssl, warnings

class SessizHandler(http.server.SimpleHTTPRequestHandler):
    # sslscan baglantiyi erken keser; BrokenPipe yigin dokumunu sessizce yut.
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionError, ssl.SSLError, OSError):
            self.close_connection = True
    def log_message(self, *a):
        pass

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Kasitli zayif: eski TLS surumlerine izin istiyoruz. Modern OpenSSL 1.0/1.1'i
# kutuphane duzeyinde zaten kapatir, bu yuzden pratikte en fazla TLS 1.2 acilir
# (cevap anahtari Soru 6.2 bunu aciklar). Niyeti gostermek icin TLSv1 birakiyoruz.
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    ctx.minimum_version = ssl.TLSVersion.TLSv1
ctx.load_cert_chain("pki/lab.crt", "pki/lab.key")
s = http.server.HTTPServer(("127.0.0.1", 8445), SessizHandler)
s.socket = ctx.wrap_socket(s.socket, server_side=True)
print("Zayif sunucu (TLS 1.2 de acik) calisiyor: https://127.0.0.1:8445")
try:
    s.serve_forever()
except KeyboardInterrupt:
    print("\nSunucu durduruldu.")
