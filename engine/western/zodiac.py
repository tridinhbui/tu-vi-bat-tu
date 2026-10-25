"""Sign arithmetic and formatting (tropical zodiac: 0 degrees Aries = the March equinox point of date)."""
from __future__ import annotations

SIGNS = ("aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces")
ELEMENT = ("fire", "earth", "air", "water") * 3
MODALITY = ("cardinal", "fixed", "mutable") * 4


def sign_index(lon: float) -> int:
    return int((lon % 360.0) // 30.0) % 12


def sign_of(lon: float) -> str:
    return SIGNS[sign_index(lon)]


def deg_in_sign(lon: float) -> float:
    return (lon % 360.0) - sign_index(lon) * 30.0


def dms(x: float) -> tuple[int, int, int]:
    """Degrees, minutes, seconds of a non-negative angle, rounded to the second without ever showing 60."""
    s = round(abs(x) * 3600)
    return s // 3600, (s % 3600) // 60, s % 60


def fmt_in_sign(lon: float, seconds: bool = False) -> str:
    """'17°23′' (or with seconds) inside its sign. Rounding never pushes 29°59′59.6″ into the next sign's 0°."""
    lon = lon % 360.0
    x = deg_in_sign(lon)
    total = int(x * 3600) if seconds else int(x * 60) * 60      # truncate like an ephemeris, so the sign shown is the true sign
    d, m, s = total // 3600, (total % 3600) // 60, total % 60
    return f"{d}°{m:02d}′{s:02d}″" if seconds else f"{d}°{m:02d}′"


def angdiff(a: float, b: float) -> float:
    """Signed smallest difference a - b in (-180, 180]."""
    x = (a - b) % 360.0
    return x - 360.0 if x > 180.0 else x


def separation(a: float, b: float) -> float:
    """Unsigned angular distance along the ecliptic, 0..180."""
    return abs(angdiff(a, b))


def sign_distance(a: float, b: float) -> int:
    """Whole-sign count from the sign of a to the sign of b, 0..11 (0 = same sign)."""
    return (sign_index(b) - sign_index(a)) % 12
