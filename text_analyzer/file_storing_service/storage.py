import os
from pathlib import Path
import hashlib

# Каталог для хранения всегда относительно рабочей директории
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "/data/files"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def compute_hash(content: bytes) -> str:
    """Возвращает SHA256-хэш."""
    return hashlib.sha256(content).hexdigest()


def save_file(content: bytes, filename: str) -> str:
    """
    Сохраняет файл в STORAGE_DIR.
    Возвращает относительный путь (location), под которым файл лежит.
    """
    # Можно использовать хэш в названии, чтобы избежать коллизий
    h = compute_hash(content)
    ext = Path(filename).suffix
    store_name = f"{h}{ext}"
    full_path = STORAGE_DIR / store_name

    with open(full_path, "wb") as f:
        f.write(content)

    # location = относительный путь внутри стораджа
    return str(store_name)


def load_file(location: str) -> bytes:
    """
    Читает файл по относительному пути внутри STORAGE_DIR.
    """
    full_path = STORAGE_DIR / location
    with open(full_path, "rb") as f:
        return f.read()
