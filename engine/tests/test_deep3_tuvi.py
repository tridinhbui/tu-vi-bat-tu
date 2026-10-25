"""DEEP-3 Tử Vi mining (2026-10-24): the raw entries (engine/data/kg/mined/deep3_*.json, tools/mining/deep3), the rule packs built from them
(pack_toan_thu_ca.json, pack_khao_luan_cach.json, pack_toan_thu_han_van.json; tools/build_deep3_tuvi_pack.py), the new knowledge structures
(kg/che_hoa.json, kg/combos.json, kg/schools.json; tools/build_deep3_kg.py), the Thực Hành additions to star_nature.json and van_han_books.json,
the 紫微斗數全書 snapshot and the 'WEB:' / 'SCAN:' quote check. Book quotes are re-checked when the PDFs are present; snapshot quotes always."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

from phase1_helpers import base_facts
from tvbt.knowledge.loader import load_all
from tvbt.reasoning import engine

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import book_text  # noqa: E402

D = ROOT / "engine" / "data"
MINED = {e["id"]: e for f in sorted((D / "kg" / "mined").glob("deep3_*.json")) for e in json.loads(f.read_text("utf-8"))["entries"]}
PACKS = {n: json.loads((D / n).read_text("utf-8"))["rules"] for n in ("pack_toan_thu_ca.json", "pack_khao_luan_cach.json", "pack_toan_thu_han_van.json")}
Q = json.loads((D / "quotes_deep3_tuvi.json").read_text("utf-8"))
KG = {n: json.loads((D / "kg" / f"{n}.json").read_text("utf-8")) for n in ("che_hoa", "combos", "schools", "star_nature", "van_han_books")}
RULES, SOURCES = load_all()
RULE_IDS = {r.id for r in RULES}
FV = {f["id"] for f in json.loads((D / "formations_verified.json").read_text("utf-8"))["formations"]}
BOOKS = all(book_text.available(b) for b in ("KL", "TH", "TT"))


def checkable(book):
    return book.startswith(("WEB:", "SCAN:")) or BOOKS


def test_snapshots_are_the_saved_ones():
    idx = json.loads((D / "sources_web" / "index.json").read_text("utf-8"))["sources"]
    for sid, s in idx.items():
        if s.get("url") is None and not s.get("chapters"):
            continue                                     # TBCT: no public-domain snapshot could be saved, an empty placeholder (draft only)
        data = (D / "sources_web" / s["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == s["sha256"], sid
        # wikitext snapshots carry their revision; the Bát Tự JSON snapshots (chapters fetched one by one) carry the fetch date
        assert s["url"].startswith("https://zh.wikisource.org/") and s["fetched"] and (s.get("revid") or s["file"].endswith(".json"))
    assert book_text.available("WEB:zwds_quanshu_2") and book_text.available("SCAN:tvnl_scan")
    # a section is searched on its own: a line of 八奴仆 is not found under 四子女
    assert book_text.quote_on_page("WEB:zwds_quanshu_2", "八奴仆", "天府得力一呼百诺")
    assert not book_text.quote_on_page("WEB:zwds_quanshu_2", "四子女", "天府得力一呼百诺")
    assert book_text.quote_on_page("SCAN:tvnl_scan", 15, "Sát Phá Tham gặp Tuần Triệt cũng mất tính cách hung hãn")
    assert not book_text.quote_on_page("SCAN:tvnl_scan", 13, "Sát Phá Tham gặp Tuần Triệt cũng mất tính cách hung hãn")


def test_mined_entries_shape():
    assert len(MINED) > 500
    for k, e in MINED.items():
        assert e["quote_checked"] is True, k
        assert e["skip"] or e.get("duplicate_of") or e.get("target") or e["reading_vi"], k
        if e.get("duplicate_of"):
            d = e["duplicate_of"]
            assert d in RULE_IDS or d in FV or d in MINED, (k, d)


def test_mined_quotes_on_their_page():
    bad = [(k, e["book"], e["page"], e["quote"]) for k, e in MINED.items() if checkable(e["book"]) and not book_text.quote_on_page(e["book"], e["page"], e["quote"])]
    assert not bad, bad


def test_every_rule_has_its_mined_quote():
    rules = [r for rs in PACKS.values() for r in rs]
    assert len(rules) == len({r["id"] for r in rules}) >= 175
    by_rule = {}
    for x in Q["quotes"]:
        by_rule.setdefault(x["rule"], []).append(x)
        e = MINED[x["mined"]]
        assert (e["book"], e["page"], e["quote"]) == (x["book"], x["page"], x["quote"]), x["rule"]
    for r in rules:
        assert r["reviewStatus"] == "verified" and r["id"] in RULE_IDS, r["id"]
        main = MINED[r["id"][len("TV_D3_"):].lower()]
        assert not main["skip"] and not main.get("duplicate_of"), r["id"]
        assert by_rule[r["id"]][0]["mined"] == main["id"]
        page = f"TTH {main['book'].rsplit('_', 1)[1]} {main['page']}" if main["book"].startswith("WEB:") else f"{main['book']} p.{main['page']}"
        assert f"[{page}]" in r["description"], r["id"]
    for k, why in Q["skipped"].items():
        assert MINED[k]["skip"] == why and why, k
    assert not Q["not_rules"]


@pytest.mark.skipif(not BOOKS, reason="Tử Vi Khảo Luận / Thực Hành / Toàn Thư PDF not present")
def test_rule_quotes_on_page():
    bad = [x for x in Q["quotes"] if not book_text.quote_on_page(x["book"], x["page"], x["quote"])]
    assert not bad, bad


def fired(ops, menh="Tý", chart=None, palace="Mệnh"):
    f = base_facts(ops, menh)
    f["chart"].update(chart or {})
    res = engine.run(RULES, SOURCES, f, system="tu_vi")
    return {x.rule_id for x in res.findings if x.subject == f"palace:{palace}" or palace is None}


S = lambda star, where="Mệnh": ("star", star, where)  # noqa: E731
H = lambda hoa, where="Mệnh": ("hoa", hoa, where)     # noqa: E731
NAM, NU = {"chart.gender": "nam"}, {"chart.gender": "nữ"}


def test_toan_thu_conditions():
    # Nam Mệnh ca are for men (TT p.64), nữ mệnh ca for women; TT p.148 splits one phá cách by sex
    assert "TV_D3_TT148_PHA_THAN_NAM" in fired([S("Cự Môn")], menh="Thân", chart=NAM)
    assert "TV_D3_TT148_PHA_THAN_NAM" not in fired([S("Cự Môn")], menh="Thân", chart=NU)
    assert "TV_D3_TT148_PHA_THAN_NU" in fired([S("Cự Môn")], menh="Thân", chart=NU)
    assert "TV_D3_TT118_CO_CU_NU" in fired([S("Thiên Cơ"), S("Cự Môn")], menh="Mão", chart=NU)
    assert "TV_D3_TT118_CO_CU_NU" not in fired([S("Thiên Cơ"), S("Cự Môn")], menh="Mão", chart=NAM)
    # one-star traits dropped after review keep their reason
    assert "Barnum" in Q["skipped"]["tt69_tuong_ca_quyet"]
    # a group of sát ('Hỏa Linh Dương Đà') needs two of them in the tam phương
    assert "TV_D3_TT67_PHU_BON_SAT" not in fired([S("Thiên Phủ"), S("Kình Dương", "Thiên Di")], chart=NAM)
    assert "TV_D3_TT67_PHU_BON_SAT" in fired([S("Thiên Phủ"), S("Kình Dương", "Thiên Di"), S("Hỏa Tinh", "Quan Lộc")], chart=NAM)
    # brightness in Toàn Thư's own table: Thái Dương is hãm at Tý, miếu at Ngọ
    assert "TV_D3_TT66_NHAT_HAM_KY" in fired([S("Thái Dương"), H("Hóa Kỵ", "Quan Lộc")], menh="Tý", chart=NAM)
    assert "TV_D3_TT66_NHAT_HAM_KY" not in fired([S("Thái Dương"), H("Hóa Kỵ", "Quan Lộc")], menh="Ngọ", chart=NAM)
    # the stem that puts the Hóa on the star
    assert "TV_D3_TT65_CO_HOA_KY_TY" in fired([S("Thiên Cơ"), H("Hóa Kỵ")], menh="Tỵ", chart={**NAM, "chart.year_stem": "Mậu"})
    assert "TV_D3_TT65_CO_HOA_KY_TY" not in fired([S("Thiên Cơ"), H("Hóa Kỵ")], menh="Tỵ", chart={**NAM, "chart.year_stem": "Ất"})
    # phá cách by Mệnh branch: the verse's Tý Ngọ, not the translation's Tị
    assert "TV_D3_TT147_PHA_CO_TY_NGO_CU_LINH" in fired([S("Thiên Cơ")], menh="Ngọ")
    assert "TV_D3_TT147_PHA_CO_TY_NGO_CU_LINH" not in fired([S("Thiên Cơ")], menh="Tỵ")
    # phú nôm Tử Tức / Huynh Đệ (Tử Tức and Huynh Đệ of a synthetic chart are named palaces)
    assert "TV_D3_TT93_TU_QUYEN_LOC" in fired([H("Hóa Quyền", "Tử Tức"), H("Hóa Lộc", "Tử Tức")], palace="Tử Tức")
    assert "TV_D3_TT93_TU_QUYEN_LOC" not in fired([H("Hóa Quyền", "Tử Tức")], palace="Tử Tức")
    assert "TV_D3_TT92_BAO_PHA_HINH_KY" in fired([S("Phá Quân", "Huynh Đệ"), S("Thiên Hình", "Huynh Đệ"), H("Hóa Kỵ", "Huynh Đệ")], palace="Huynh Đệ")
    # cách cục as formation rules: Quân thần khánh hội needs Tả Hữu in Mệnh and Vũ Tướng in the tam phương
    qt = [S("Tử Vi"), S("Tả Phụ"), S("Hữu Bật"), S("Vũ Khúc", "Quan Lộc"), S("Thiên Tướng", "Tài Bạch")]
    assert "TV_D3_TT142_QUAN_THAN_KHANH_HOI" in fired(qt)
    assert "TV_D3_TT142_QUAN_THAN_KHANH_HOI" not in fired(qt[:2] + qt[3:])


def test_khao_luan_conditions():
    # Song Hao: Đại Hao and Tiểu Hao always face each other, one of them in the palace
    assert "TV_D3_KL203_SONG_HAO_DAN_THAN_MAO_DAU" in fired([S("Đại Hao"), S("Tiểu Hao", "Thiên Di")], menh="Mão")
    assert "TV_D3_KL203_SONG_HAO_MENH" in fired([S("Tiểu Hao"), S("Đại Hao", "Thiên Di")], menh="Tý")
    assert "TV_D3_KL203_SONG_HAO_MENH" not in fired([S("Tiểu Hao"), S("Đại Hao", "Thiên Di")], menh="Dậu")
    # Liên Giáp: Kình Đà giáp Mệnh
    assert "TV_D3_KL205_GIAP_KINH_DA" in fired([S("Lộc Tồn"), S("Kình Dương", "Phụ Mẫu"), S("Đà La", "Huynh Đệ")])
    # Mệnh vô chính diệu with Không Kiếp at the four sinh places
    vcd = [S("Địa Không", "Thiên Di"), S("Địa Kiếp", "Thiên Di")]
    assert "TV_D3_KL204_VCD_KHONG_KIEP" in fired(vcd, menh="Dần")
    assert "TV_D3_KL204_VCD_KHONG_KIEP" not in fired(vcd, menh="Tý")
    assert "TV_D3_KL204_VCD_KHONG_KIEP" not in fired(vcd + [S("Thiên Cơ")], menh="Dần")
    # Đào hoa Thiên không: the pair together, in Mệnh or one tam hợp palace
    assert "TV_D3_KL47_DAO_HOA_THIEN_KHONG" in fired([S("Thiên Không", "Quan Lộc"), S("Đào Hoa", "Quan Lộc")])
    assert "TV_D3_KL47_DAO_HOA_THIEN_KHONG" not in fired([S("Thiên Không", "Quan Lộc"), S("Đào Hoa", "Tài Bạch")])


def test_toan_thu_han_van_conditions():
    assert "TV_D3_W2_NO_TU_VI" in fired([S("Tử Vi", "Nô Bộc")], palace="Nô Bộc")
    got = fired([S("Tử Vi", "Nô Bộc"), S("Kình Dương", "Nô Bộc")], palace="Nô Bộc")
    assert {"TV_D3_W2_NO_TU_VI", "TV_D3_W2_NO_TU_VI_SAT"} <= got
    rel = json.loads((D / "kg" / "relations.manual.json").read_text("utf-8"))["relations"]
    assert any(x["from"] == "TV_D3_W2_NO_TU_VI_SAT" and "TV_D3_W2_NO_TU_VI" in x["to"] and x["type"] == "qualifies" for x in rel)
    # 独守 = the palace has no chính tinh
    assert "TV_D3_W2_NO_TA_DOC" in fired([S("Tả Phụ", "Nô Bộc")], palace="Nô Bộc")
    assert "TV_D3_W2_NO_TA_DOC" not in fired([S("Tả Phụ", "Nô Bộc"), S("Thiên Lương", "Nô Bộc")], palace="Nô Bộc")
    assert "TV_D3_W2_TU_LIEM_PHU" in fired([S("Liêm Trinh", "Tử Tức"), S("Thiên Phủ", "Tử Tức")], palace="Tử Tức")
    assert "TV_D3_W2_PM_KHOI_VIET" in fired([S("Thiên Việt", "Phụ Mẫu")], palace="Phụ Mẫu")
    for r in PACKS["pack_toan_thu_han_van.json"]:
        assert r["sourceIds"] == ["SRC_TOAN_THU_HAN"] and "[TTH 2 " in r["description"], r["id"]


STARS = set(json.loads((D / "dignity_kb.json").read_text("utf-8"))["stars"]) | {
    "Tuần", "Triệt", "Thiên Không", "Đại Hao", "Tiểu Hao", "Thiên Giải", "Địa Giải", "Thiên Quan", "Thiên Phúc", "Thiên Khốc", "Thiên Hư", "Đào Hoa",
    "Hồng Loan", "Thiếu Dương", "Cô Thần", "Phá Toái", "Thiên Hình", "Đẩu Quân", "Thiên Mã", "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ", "Lộc Tồn",
    "Thiên Khôi", "Thiên Việt", "Văn Xương", "Văn Khúc", "Tả Phụ", "Hữu Bật"}


def test_kg_sources_are_mined_entries():
    def check(srcs, where):
        assert srcs, where
        for s in srcs:
            e = MINED[s["mined"]]
            assert (e["book"], e["page"], e["quote"]) == (s["book"], s["page"], s["quote"]), where
    ch = KG["che_hoa"]
    assert len(ch["entries"]) >= 50 and len({x["id"] for x in ch["entries"]}) == len(ch["entries"])
    for x in ch["entries"]:
        assert x["effect"] in ch["effects"] and x["tamer"] and x["tamed"] and x["text"], x["id"]
        for s in x["tamer"] + x["tamed"]:
            assert s in STARS or s in ch["groups"], (x["id"], s)
        check(x["sources"], x["id"])
        if x.get("star_nature"):
            assert any(e["id"] == x["star_nature"] for e in KG["star_nature"]["entries"]), x["id"]
    cb = KG["combos"]
    for k in ("groups", "kinds", "layouts", "pairs", "modifiers"):
        for x in cb[k]:
            check(x["sources"], x["id"])
    assert {b for x in cb["layouts"] for b in x["tu_vi_branch"]} == {"Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"}
    for pair, by_pal in cb["per_palace"].items():
        for pal, xs in by_pal.items():
            assert all(x["rule"] in RULE_IDS for x in xs), (pair, pal)
    sc = KG["schools"]
    assert len(sc["topics"]) >= 25
    for t in sc["topics"]:
        assert t["sides"] and t["note"], t["id"]
        assert len(t["sides"]) >= 2 or t["subkind"] == "y_kien", t["id"]
        assert t["kind"] in ("dignity", "hoa", "cach", "reading"), t["id"]
        for s in t["sides"]:
            assert s["school"] in sc["schools"] and s["statement"], t["id"]
            check([s], t["id"])


def test_reader_shapes():
    """che_hoa.relations / combos.combos / schools in the field names reason/argue.ts reads; each quote is its mined entry's"""
    ch, cb = KG["che_hoa"], KG["combos"]
    assert all(KG[n]["version"] == "1.0.0" for n in ("che_hoa", "combos", "schools"))
    ids = {x["id"] for x in ch["entries"]}
    assert set(ch["relations_left_out"]) <= ids
    assert len(ch["relations"]) == len(ch["entries"]) - len(ch["relations_left_out"])
    by_entry = {x["id"]: x for x in ch["entries"]}
    for r in ch["relations"]:
        assert r["scope"] in ("dong_cung", "tam_phuong", "any") and r["effect"] in ("giam", "hoa_giai", "dao_nguoc", "che", "tang"), r["id"]
        assert r["tamer"] and r["tamed"] and r["text"] and r["reviewStatus"] == "verified", r["id"]
        assert all(s in STARS or s == "*" or s.startswith("@") for s in r["tamer"] + r["tamed"]), r["id"]
        src0 = by_entry[r["entry"]]["sources"][0]
        assert (r["book"], r["page"], r["quote"]) == (src0["book"], src0["page"], src0["quote"]), r["id"]
    used = {s["mined"] for x in ch["entries"] for s in x["sources"]}  # every Tuần / Triệt line of KL p.204
    assert {"kl204_menh_triet", "kl204_menh_tuan", "kl204_tuan_triet_cung_cho", "kl204_chinh_tinh_ham_can_tt", "kl204_dac_dia_tt_pha_hu",
            "kl204_dai_van_tt_thao_go"} <= used
    for c in cb["combos"]:
        assert c["scope"] in ("dong_cung", "xung", "tam_phuong") and c["pol"] in ("+", "-", "±") and c["dignity"] in (None, "bright", "ham"), c["id"]
        assert c["stars"] and all(s in STARS for s in c["stars"]) and c["reading"], c["id"]
        assert any(c["quote"] == MINED[k]["quote"] and MINED[k]["page"] == c["page"] for k in MINED), c["id"]
        for m in c["modifiers"]:
            assert m["pol"] in ("+", "-") and any(m["quote"] == MINED[k]["quote"] for k in MINED), c["id"]
    assert set(KG["schools"]["schools"]) == {"KL", "TH", "TT", "ZWDS_HAN", "TVNL"}


def test_th_additions():
    th = [e for e in KG["star_nature"]["entries"] if e.get("deep3")]
    assert len(th) >= 20 and all(e["book"] == "TH" and not e["explains"] and e["kind"] == "hanh" for e in th)
    vh = [e for e in KG["van_han_books"]["entries"] if e["kind"] == "th"]
    # the condition vocabulary src/interpret/prose/vanhan_books.ts understands
    vocab = {"major", "star", "dig", "not_dig", "with_any", "tp_any", "tp_any2", "tp_all", "tp_sat", "tp_sat2", "tp_cat", "no_cat", "no_sat_tp", "hoa", "hoa_any",
             "hoa3", "hoa_star_dig", "opp_major", "branch", "tuoi", "tp_major_dig"}
    assert len(vh) >= 25
    for e in vh:
        assert set(e["cond"]) <= vocab and e["tone"] in ("", "pos", "neg") and e["text"].startswith("hạn có "), e["id"]
        assert MINED[e["id"]]["quote"] == e["quote"]
