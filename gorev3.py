import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = os.urandom(32)
iv = os.urandom(16)
original_msg = b"Tutar: 100 TL"

print("==================================================")
print("--- 1. AES-CTR (Bütünlük Kontrolü Yok / Saldırı Başarılı) ---")
# Şifreleme
cipher_ctr = Cipher(algorithms.AES(key), modes.CTR(iv))
enc = cipher_ctr.encryptor()
ciphertext = bytearray(enc.update(original_msg) + enc.finalize())

# Bit Flipping Saldırısı: '1' karakterini '9' yapıyoruz (İndeks 7)
ciphertext[7] ^= ord('1') ^ ord('9')

# Deşifre Etme
dec_cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
dec = dec_cipher.decryptor()
modified_msg = dec.update(bytes(ciphertext)) + dec.finalize()
print("Değiştirilmiş Mesaj (CTR):", modified_msg.decode('utf-8', errors='ignore'))

print("\n--- 2. AES-GCM (Bütünlük Kontrolü Var / Saldırı Engellenir) ---")
aesgcm = AESGCM(key)
nonce = os.urandom(12)
gcm_ciphertext = bytearray(aesgcm.encrypt(nonce, original_msg, None))

# Aynı müdahaleyi yapıyoruz
gcm_ciphertext[7] ^= ord('1') ^ ord('9')

try:
    decrypted_gcm = aesgcm.decrypt(nonce, bytes(gcm_ciphertext), None)
    print("GCM Deşifre:", decrypted_gcm)
except Exception as e:
    print("AES-GCM UYARISI: Şifreli metin değiştirilmiş! Kimlik doğrulaması başarısız oldu (Integrity Fail).")
print("==================================================")
