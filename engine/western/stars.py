"""Lilly's fixed stars: the three of his table of accidental dignities (Christian Astrology p.115: Cor Leonis, Spica, Caput Algol)
and the six 'of Kingly signification' of his honour rules (p.616: Oculus Tauri, Hercules, Cor Leonis, Spica, Lucida Lancis, Cor
Scorpii). Each name is matched to a star by the 1647 longitude Lilly prints, carried forward by precession (all within 0.5°):
Oculus Tauri = Aldebaran, Hercules = Pollux, Lucida Lancis = Zubenelgenubi (α Lib). A star's longitude grows by about 50" a year
with precession, so they are computed for the chart's own date: apparent geocentric position on the true ecliptic of date, from
the Hipparcos astrometry (ESA 1997, new reduction van Leeuwen 2007, as given by SIMBAD: ICRS J2000 position, proper motion,
parallax, radial velocity). Checked against Swiss Ephemeris' star file: under 0.1" from 1900 to 2050."""
from __future__ import annotations

from functools import lru_cache

from skyfield.api import Star
from skyfield.framelib import ecliptic_frame

from . import ephemeris as E

# key: (name, RA h m s, Dec d m s, pm RA* mas/yr, pm Dec mas/yr, parallax mas, radial velocity km/s)
CATALOG = {
    "regulus": ("Cor Leonis (Regulus, α Leo, HIP 49669)", (10, 8, 22.311), (11, 58, 1.95), -248.73, 5.59, 41.13, 5.9),
    "spica": ("Spica (α Vir, HIP 65474)", (13, 25, 11.579), (-11, 9, 40.75), -42.35, -30.67, 13.06, 1.0),
    "algol": ("Caput Algol (β Per, HIP 14576)", (3, 8, 10.132), (40, 57, 20.33), 2.99, -1.66, 36.27, 4.0),
    "aldebaran": ("Oculus Tauri (Aldebaran, α Tau, HIP 21421)", (4, 35, 55.239), (16, 30, 33.49), 63.45, -188.94, 48.94, 54.26),
    "pollux": ("Hercules (Pollux, β Gem, HIP 37826)", (7, 45, 18.950), (28, 1, 34.32), -626.55, -45.80, 96.54, 3.23),
    "zubenelgenubi": ("Lucida Lancis (Zubenelgenubi, α² Lib, HIP 72622)", (14, 50, 52.713), (-16, 2, 30.40), -105.68, -68.40, 43.03, -23.0),
    "antares": ("Cor Scorpii (Antares, α Sco, HIP 80763)", (16, 29, 24.460), (-26, 25, 55.21), -12.11, -23.30, 5.89, -3.4),
}
SHORT = {"regulus": "Cor Leonis (Regulus)", "spica": "Spica", "algol": "Caput Algol", "aldebaran": "Oculus Tauri (Aldebaran)",
         "pollux": "Hercules (Pollux)", "zubenelgenubi": "Lucida Lancis (Zubenelgenubi)", "antares": "Cor Scorpii (Antares)"}
# Lilly p.115 (key of the table row in kb/dignities.json) and p.616 (royal stars of honour)
LILLY_115 = {"regulus": "conj_cor_leonis", "spica": "conj_spica", "algol": "conj_caput_algol"}
ROYAL_616 = ("aldebaran", "pollux", "regulus", "spica", "zubenelgenubi", "antares")
ORB = 5.0   # Lilly p.616 'within distance of five degrees forward or backward'; p.115 gives the same for Caput Algol


@lru_cache(maxsize=None)
def _star(key: str) -> Star:
    _, ra, dec, pm_ra, pm_dec, plx, rv = CATALOG[key]
    d, m, s = dec
    sign = -1 if d < 0 else 1
    return Star(ra_hours=ra, dec_degrees=(abs(d) * sign, m * sign, s * sign), ra_mas_per_year=pm_ra, dec_mas_per_year=pm_dec,
                parallax_mas=plx, radial_km_per_s=rv)


def longitudes(t) -> dict[str, float]:
    """Apparent ecliptic longitude of date (degrees) of each star at Skyfield Time t."""
    e = E.earth().at(t)
    return {k: e.observe(_star(k)).apparent().frame_latlon(ecliptic_frame)[1].degrees % 360.0 for k in CATALOG}
