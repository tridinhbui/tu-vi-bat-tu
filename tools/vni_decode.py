"""Decode VNI-Windows legacy-encoded Vietnamese text (as extracted from old PDFs) to Unicode."""
import sys


def build_map():
    m = {}
    plain = {"ù": 0, "ø": 1, "û": 2, "õ": 3, "ï": 4}      # tone chars after plain vowels / ơ / ư
    marks = ["́", "̀", "̉", "̃", "̣"]
    import unicodedata as u
    comp = lambda s: u.normalize("NFC", s)
    circ = {"á": 0, "à": 1, "å": 2, "ã": 3, "ä": 4}      # tone chars after â ê ô (circumflex absorbed)
    breve = {"é": 0, "è": 1, "ú": 2, "ü": 3, "ë": 4}      # tone chars after ă
    for up in (False, True):
        c = (lambda s: s.upper()) if up else (lambda s: s)
        for v in "aeiouy":
            base = c(v)
            for t, i in plain.items():
                m[base + t] = comp(base + marks[i])
        for v, hat in (("a", "̂"), ("e", "̂"), ("o", "̂")):
            base = c(v)
            m[base + "â"] = comp(base + hat)
            for t, i in circ.items():
                m[base + t] = comp(base + hat + marks[i])
        base = c("a")
        m[base + "ê"] = comp(base + "̆")
        for t, i in breve.items():
            m[base + t] = comp(base + "̆" + marks[i])
        # ơ (ô) and ư (ö)
        horn_o, horn_u = c("ơ"), c("ư")
        m[c("ô")] = horn_o
        m[c("ö")] = horn_u
        for t, i in plain.items():
            m[c("ô") + t] = comp(horn_o + marks[i])
            m[c("ö") + t] = comp(horn_u + marks[i])
        for ch, tone in (("í", 0), ("ì", 1), ("æ", 2), ("ó", 3), ("ò", 4)):
            ch = ch.upper() if up else ch
            m[ch] = comp(c("i") + marks[tone])
    m["ñ"], m["Ñ"] = "đ", "Đ"
    m["î"], m["Î"] = "ỵ", "Ỵ"
    # uppercase text uses uppercase tone characters as well: duplicate every key with an upper-cased tail
    for k, v in list(m.items()):
        if len(k) == 2 and k[0].isupper():
            m[k[0] + k[1].upper()] = v
        if len(k) == 2 and k[0].lower() in "aeiouy":
            m.setdefault(k[0].upper() + k[1].upper(), v.upper() if k[0].islower() else v)
    return m


MAP = build_map()
KEYS = sorted(MAP, key=len, reverse=True)


def decode(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        for k in KEYS:
            if s.startswith(k, i):
                out.append(MAP[k]); i += len(k); break
        else:
            out.append(s[i]); i += 1
    return "".join(out)


if __name__ == "__main__":
    sys.stdout.write(decode(sys.stdin.read()))
