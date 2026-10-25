"""Build the birthplace gazetteer for the Western chart from GeoNames (CC BY 4.0, https://www.geonames.org/).

Input: cities15000.txt (every place with >= 15,000 people), cities1000.txt (used for Vietnam only, >= 1,000 people),
admin1CodesASCII.txt and countryInfo.txt from https://download.geonames.org/export/dump/.
Output: engine/data/western/places.json.gz, rows [name, ascii, alt_names_vi, country, admin1, lat, lon, tz, population].

Time zones: GeoNames' own column, except Vietnam: north of the 17th parallel (the 1954-1975 dividing line, Bến Hải river)
uses tzdb's backzone Asia/Hanoi and the south Asia/Ho_Chi_Minh, exactly as the Tử Vi birth form does (web/js/util.js placeTz).

    python tools/west/build_places.py /path/to/geonames/dump
"""
from __future__ import annotations

import gzip
import json
import pathlib
import re
import sys
from zoneinfo import ZoneInfo

OUT = pathlib.Path(__file__).resolve().parents[2] / "engine" / "data" / "western" / "places.json.gz"
VI_CHARS = re.compile("[ăâđêôơưàảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵ]", re.I)
COUNTRY_VI = {"VN": "Việt Nam"}
# everyday names GeoNames does not carry for the two big cities
ALIASES_VN = {"1566083": ["Sài Gòn", "Saigon", "TP HCM", "TPHCM", "TP Hồ Chí Minh", "Thành phố Hồ Chí Minh"], "1581130": ["Hà Nội", "TP Hà Nội"]}
# Vietnamese names of a few foreign cities that GeoNames lacks (common usage, added as search keys only)
EXONYMS_VI = {"2643743": ["Luân Đôn"], "1816670": ["Bắc Kinh"], "1796236": ["Thượng Hải"], "524901": ["Mát-xcơ-va", "Mạc Tư Khoa"],
              "2950159": ["Béc-lin", "Bá Linh"], "1668341": ["Đài Bắc"], "1819729": ["Hồng Kông"], "1835848": ["Hán Thành", "Xơ-un"],
              "2988507": ["Pa-ri", "Ba Lê"], "1609350": ["Băng Cốc", "Vọng Các"], "1821306": ["Ma Cao"], "1880252": ["Tân Gia Ba"],
              "1850147": ["Đông Kinh"], "1642911": ["Gia-các-ta"], "1871859": ["Bình Nhưỡng"]}


def main(src: pathlib.Path):
    countries = {}
    for line in (src / "countryInfo.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            f = line.split("\t")
            countries[f[0]] = COUNTRY_VI.get(f[0], f[4])
    admin1 = {}
    for line in (src / "admin1CodesASCII.txt").read_text(encoding="utf-8").splitlines():
        code, name, *_ = line.split("\t")
        admin1[code] = name
    rows, seen, bad_tz = [], set(), set()

    def take(path: pathlib.Path, only_vn: bool):
        for line in path.read_text(encoding="utf-8").splitlines():
            f = line.split("\t")
            gid, name, ascii_, alts, lat, lon, cc, a1, pop, tz = f[0], f[1], f[2], f[3], float(f[4]), float(f[5]), f[8], f[10], int(f[14] or 0), f[17]
            if gid in seen or (only_vn and cc != "VN"):
                continue
            if cc == "VN":
                tz = "Asia/Hanoi" if lat >= 17.0 else "Asia/Ho_Chi_Minh"
                al = {a for a in alts.split(",") if a and a != name}
                alt_vi = (sorted(a for a in al if VI_CHARS.search(a))[:10] + sorted(a for a in al if not VI_CHARS.search(a) and len(a) <= 20)[:6]
                          + ALIASES_VN.get(gid, []))
            else:
                alt_vi = sorted({a for a in alts.split(",") if VI_CHARS.search(a) and a != name})[:2] + EXONYMS_VI.get(gid, [])
                try:
                    ZoneInfo(tz)
                except Exception:  # noqa: BLE001
                    bad_tz.add(tz)
                    continue
            seen.add(gid)
            rows.append([name, ascii_, alt_vi, countries.get(cc, cc), admin1.get(f"{cc}.{a1}", ""), round(lat, 5), round(lon, 5), tz, pop])

    take(src / "cities15000.txt", False)
    take(src / "cities1000.txt", True)
    rows.sort(key=lambda r: -r[8])
    OUT.write_bytes(gzip.compress(json.dumps({"source": "GeoNames (CC BY 4.0), https://www.geonames.org/", "rows": rows},
                                             ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    print(len(rows), "places,", sum(r[3] == "Việt Nam" for r in rows), "in Việt Nam; skipped zones:", sorted(bad_tz), "->", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]))
