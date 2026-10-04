import base64
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_SALT_LEN = 32
_ITERATIONS = 480_000


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_ITERATIONS,
        backend=default_backend(),
    )
    raw = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)


def encrypt_file(file_path: str, password: str) -> tuple[bool, str]:
    try:
        path = Path(file_path)
        if not path.is_file():
            return False, "الملف غير موجود"

        data = path.read_bytes()
        salt = os.urandom(_SALT_LEN)
        key = derive_key(password, salt)
        token = Fernet(key)
        encrypted = token.encrypt(data)
        out_path = path.with_name(path.name + ".enc")
        out_path.write_bytes(salt + encrypted)

        try:
            path.unlink()
        except OSError as e:
            try:
                out_path.unlink(missing_ok=True)
            except OSError:
                pass
            return False, f"فشل حذف الملف الأصلي: {e}"

        return True, "تم التشفير بنجاح"
    except Exception as e:
        return False, str(e)


def decrypt_file(file_path: str, password: str) -> tuple[bool, str]:
    try:
        path = Path(file_path)
        if not path.name.lower().endswith(".enc"):
            return False, "هذا الملف غير مشفر. اختر ملفاً بامتداد .enc"

        if not path.is_file():
            return False, "الملف غير موجود"

        raw = path.read_bytes()
        if len(raw) < _SALT_LEN:
            return False, "ملف مشفر غير صالح أو تالف"

        salt = raw[:_SALT_LEN]
        ciphertext = raw[_SALT_LEN:]
        key = derive_key(password, salt)
        token = Fernet(key)

        try:
            plain = token.decrypt(ciphertext)
        except InvalidToken:
            return False, "كلمة المرور غير صحيحة"

        original_name = path.name[:-4] if path.name.lower().endswith(".enc") else path.name
        out_path = path.with_name(original_name)

        try:
            out_path.write_bytes(plain)
        except OSError as e:
            return False, f"فشل كتابة الملف المفكوك: {e}"

        try:
            path.unlink()
        except OSError as e:
            return False, f"تم فك التشفير لكن فشل حذف الملف المشفر: {e}"

        return True, "تم فك التشفير بنجاح"
    except Exception as e:
        return False, str(e)
