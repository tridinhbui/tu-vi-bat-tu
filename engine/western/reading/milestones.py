"""Which transits are worth naming: a score whose every part is written down, so a reader can see why a contact was picked.

The parts come from the books where the books say something, and are Thiên Bàn's convention where they do not:
  moving planet  Jupiter, Saturn, Uranus 3: Alan Leo's main transiting planets (The Progressed Horoscope p.193); Mars is on Leo's
                 list too but each of its contacts lasts only days, so it counts 1 (convention);
                 Neptune, Pluto, Chiron 1 (slow, but Leo gives them no rule); Sun, Mercury, Venus 0, except 1 for the ruler
                 of the chart (Leo p.201: Venus and Mercury count little 'except when one of them is the ruling planet')
  natal point    the lord of the year +3 (Valens IV.11 confirms the year by the stars passing over its places; Lilly
                 pp.726-727 judges the year from its lord); the Sun, Moon, Ascendant, MC +2 (the lights and angles every school
                 reads first); the chart ruler +1; any other planet +1
  aspect         conjunction 3, opposition and square 2, trine and sextile 1 (convention: the strength order Lilly and
                 Ptolemy give the aspects, turned into numbers by Thiên Bàn)
  timing         +1 if it is exact inside the window, +1 if one retrograde loop brings it back over the point (it lasts)
No score adds techniques together: profection, transits, progressions and the solar return are reported side by side.
"""
from __future__ import annotations

from .. import dignity

MOVER = {"jupiter": 3, "saturn": 3, "uranus": 3, "mars": 1, "neptune": 1, "pluto": 1, "chiron": 1}
NOTABLE = 7                     # the score from which a contact is called notable (the timeline filter and Thời vận)
ASPECT = {"conjunction": 3, "opposition": 2, "square": 2, "trine": 1, "sextile": 1}
LIGHTS_ANGLES = ("sun", "moon", "asc", "mc")
WHY = {"mover": "hành tinh đi qua", "lord": "chạm chủ năm", "light": "chạm sao sáng hoặc trục chính", "ruler": "chạm chủ lá số",
       "planet": "chạm một hành tinh gốc", "aspect": "loại góc", "exact": "chính xác trong khung", "loop": "lặp lại trong một vòng nghịch hành"}


def chart_ruler(natal: dict) -> str | None:
    return dignity.domicile_lord(natal["angles"]["asc"]["sign"]) if "angles" in natal else None


def score(ev: dict, natal: dict, lord: str | None, ruler: str | None) -> tuple[int, list[tuple[str, int]]]:
    parts: list[tuple[str, int]] = []
    mv = MOVER.get(ev["transiting"], 1 if ev["transiting"] == ruler and ruler in ("sun", "mercury", "venus") else 0)
    if not mv:
        return 0, []
    parts.append(("mover", mv))
    na = ev["natal"]
    if lord and na == lord:
        parts.append(("lord", 3))
    elif na in LIGHTS_ANGLES:
        parts.append(("light", 2))
    elif ruler and na == ruler:
        parts.append(("ruler", 1))
    elif na in natal["bodies"]:
        parts.append(("planet", 1))
    parts.append(("aspect", ASPECT.get(ev["aspect"], 0)))
    if ev.get("exact"):
        parts.append(("exact", 1))
    if ev.get("spans", 1) > 1 or len(ev.get("exact", [])) > 1:
        parts.append(("loop", 1))
    return sum(v for _, v in parts), parts


def merge_cycles(events: list[dict]) -> list[dict]:
    """One item per retrograde loop (western.transits gives one event per in-orb span, sharing a `cycle` id)."""
    by: dict[str, dict] = {}
    for e in events:
        k = e.get("cycle") or f"{e['transiting']}-{e['aspect']}-{e['natal']}-{e['start']}"
        m = by.get(k)
        if m is None:
            by[k] = {**e, "exact": list(e["exact"]), "retro_at_exact": list(e["retro_at_exact"]), "spans": 1}
        else:
            m["exact"] += e["exact"]
            m["retro_at_exact"] += e["retro_at_exact"]
            m["spans"] += 1
            m["end"] = e["end"]
            m["min_orb"] = min(m["min_orb"], e["min_orb"])
    return list(by.values())


def rank(events: list[dict], natal: dict, lord: str | None, n: int | None = None) -> list[dict]:
    ruler = chart_ruler(natal)
    out = []
    for e in merge_cycles(events):
        s, parts = score(e, natal, lord, ruler)
        if s:
            out.append({**e, "score": s, "score_parts": parts})
    out.sort(key=lambda e: (-e["score"], e["exact"][0] if e["exact"] else e["start"] or ""))
    return out[:n] if n else out
