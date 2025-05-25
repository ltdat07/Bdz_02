import re
import hashlib
from typing import Dict

def normalize_text(text: str) -> str:
    tokens = re.findall(r'\w+', text.lower())
    return "".join(tokens)

def compute_text_hash(text: str) -> str:
    norm = normalize_text(text)
    return hashlib.sha256(norm.encode('utf-8')).hexdigest()

def count_paragraphs(text: str) -> int:
    """
    Считает абзацы: разделителем считается один или несколько подряд идущих переводов строки
    (\n или \r\n).
    """
    parts = re.split(r'(?:\r?\n){2,}', text)
    return sum(1 for p in parts if p.strip())

def count_words(text: str) -> int:
    words = re.findall(r'\w+', text)
    return len(words)

def count_characters(text: str, include_spaces: bool = True) -> int:
    if include_spaces:
        return len(text)
    else:
        return len(text) - text.count(' ') - text.count('\n') - text.count('\r')

def analyze_text(text: str) -> Dict[str, int]:
    return {
        "paragraphs": count_paragraphs(text),
        "words": count_words(text),
        "characters": count_characters(text),
    }
