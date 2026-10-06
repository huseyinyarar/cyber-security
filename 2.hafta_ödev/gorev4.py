import time
import hashlib
from argon2 import PasswordHasher

password = b"SuperGizliParola123!"

# 1. SHA-256 Süre Ölçümü (1000 kez çalıştırıp ortalamasını alıyoruz)
start_time = time.perf_counter()
for _ in range(1000):
    hashlib.sha256(password).hexdigest()
end_time = time.perf_counter()
sha_duration = (end_time - start_time) / 1000

print("==================================================")
print(f"SHA-256   (Tek bir hash süresi) : {sha_duration:.8f} saniye")

# 2. Argon2id Süre Ölçümü
ph = PasswordHasher()
start_time = time.perf_counter()
argon_hash = ph.hash(password)
end_time = time.perf_counter()
argon_duration = end_time - start_time

print(f"Argon2id  (Tek bir hash süresi) : {argon_duration:.8f} saniye")
print(f"\nSonuç: Argon2id, SHA-256'dan yaklaşık {argon_duration / sha_duration:.0f} kat daha yavaş ve güvenlidir.")
print("==================================================")
