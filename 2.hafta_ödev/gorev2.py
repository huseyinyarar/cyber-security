import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_and_show(image_path):
    img = Image.open(image_path).convert('RGB')
    img_np = np.array(img)
    shape = img_np.shape

    data = img_np.tobytes()

    key = os.urandom(32)  # 256-bit AES
    iv = os.urandom(16)   # 128-bit IV

    # 1. AES-ECB Şifreleme
    cipher_ecb = Cipher(algorithms.AES(key), modes.ECB())
    encryptor_ecb = cipher_ecb.encryptor()
    pad_len = (16 - (len(data) % 16)) % 16
    padded_data = data + b'\x00' * pad_len
    ecb_bytes = (encryptor_ecb.update(padded_data) + encryptor_ecb.finalize())[:len(data)]

    # 2. AES-CTR Şifreleme
    cipher_ctr = Cipher(algorithms.AES(key), modes.CTR(iv))
    encryptor_ctr = cipher_ctr.encryptor()
    ctr_bytes = encryptor_ctr.update(data) + encryptor_ctr.finalize()

    # Diziye geri çevir
    ecb_np = np.frombuffer(ecb_bytes, dtype=np.uint8).reshape(shape)
    ctr_np = np.frombuffer(ctr_bytes, dtype=np.uint8).reshape(shape)

    # Yan yana ekrana çizdir
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.title("Orijinal Resim")
    plt.imshow(img_np)
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.title("AES-ECB (Siluet Belli Olur)")
    plt.imshow(ecb_np)
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.title("AES-CTR (Tam Rastgele)")
    plt.imshow(ctr_np)
    plt.axis('off')

    plt.tight_layout()
    plt.show()

encrypt_and_show('ornek.png')
