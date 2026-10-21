"""PWA / Open Graph icons drawn in pure Python (no imaging library): the site mark (a ring and a cinnabar needle, as the favicon)
on ivory. Anti-aliased with signed distances; output is deterministic, so regenerating does not churn the repository."""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
IVORY, INK, CINNABAR = (0xFA, 0xF6, 0xEF), (0x28, 0x29, 0x23), (0xA7, 0x43, 0x2C)


def _png(w: int, h: int, rows: list[bytes]) -> bytes:
    def chunk(t: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + r for r in rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def _mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def draw(w: int, h: int, cx: float, cy: float, scale: float) -> bytes:
    """Mark centred at (cx, cy); `scale` = px per unit of the favicon's 600-unit box."""
    R, half_ring = 280 * scale, 14 * scale             # ring radius and half stroke width
    a, b = 40 * scale, 170 * scale                     # needle half width / half height
    k = (a * b) / (a * a + b * b) ** 0.5
    rows = []
    for y in range(h):
        row = bytearray()
        dy = y + 0.5 - cy
        for x in range(w):
            dx = x + 0.5 - cx
            c = IVORY
            d_ring = abs((dx * dx + dy * dy) ** 0.5 - R) - half_ring
            if d_ring < 0.5:
                c = _mix(c, INK, min(1.0, 0.5 - d_ring))
            d_n = (abs(dx) / a + abs(dy) / b - 1) * k
            if d_n < 0.5:
                c = _mix(c, CINNABAR, min(1.0, 0.5 - d_n))
            row += bytes(c)
        rows.append(bytes(row))
    return _png(w, h, rows)


ICONS = {
    "icons/icon-192.png": (192, 192, 0.30),
    "icons/icon-512.png": (512, 512, 0.80),
    "icons/maskable-512.png": (512, 512, 0.62),      # mark inside the 80% safe zone of maskable icons
    "icons/apple-touch-icon.png": (180, 180, 0.27),
}


def write(web: Path = WEB) -> int:
    (web / "icons").mkdir(parents=True, exist_ok=True)
    for rel, (w, h, s) in ICONS.items():
        (web / rel).write_bytes(draw(w, h, w / 2, h / 2, s))
    (web / "icons/og.png").write_bytes(draw(1200, 630, 600, 315, 0.95))
    return len(ICONS) + 1
