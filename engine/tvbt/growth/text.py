"""Text helpers: Vietnamese diacritic folding for keyword matching, and the language guard the QA tests (and the dialogue) rely on."""
from __future__ import annotations

import re
import unicodedata


def fold(s: str) -> str:
    """'Tại sao tôi luôn mắc kẹt?' -> 'tai sao toi luon mac ket?' (lower case, no diacritics, đ -> d, single spaces)."""
    s = (s or "").replace("đ", "d").replace("Đ", "D")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"\s+", " ", s).strip()


def hits(text: str, keys) -> list[str]:
    """Keywords (already folded) found in text as whole-word sequences."""
    t = f" {re.sub(r'[^a-z0-9 ]', ' ', fold(text))} "
    t = re.sub(r"\s+", " ", t)
    return [k for k in keys if f" {k} " in t]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", fold(s)).strip("_")


def clip(s: str, n: int = 200) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# Output language guard. Folded phrases that must never appear in generated text: fatalism, certainty about events, decisions taken
# for the reader, and empty slogans. Tested over many charts and every endpoint.
FATALISM = ["chac chan se", "dinh menh da", "so phan da", "da an bai", "khong the thay doi duoc", "nhat dinh se", "khong tranh khoi",
            "se ly hon", "se chet", "tai hoa", "dai hoa", "dinh san", "chac chan ban", "ban se that bai", "ban se thanh cong"]
DECIDING = ["ban nen chon", "hay chon phuong an", "lua chon dung la", "lua chon tot nhat la", "ban phai chon", "toi khuyen ban chon"]
CLICHE = ["hay luon tich cuc", "moi chuyen roi se on", "hay la chinh minh", "suy nghi tich cuc len", "vu tru se", "luat hap dan", "cu tin vao ban than la du"]
BANNED = FATALISM + DECIDING + CLICHE


def lint(text: str) -> list[str]:
    """Banned phrases present as whole-word sequences ('thấy là chính mình' must not trip 'hãy là chính mình')."""
    return hits(text, BANNED)


def walk_strings(obj, skip_keys=("echo", "user_text", "text_user")):
    """All strings in a JSON-like object, skipping fields that only echo the user's own words."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in skip_keys:
                yield from walk_strings(v, skip_keys)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from walk_strings(v, skip_keys)
