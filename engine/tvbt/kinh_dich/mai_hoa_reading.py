"""The Mai Hoa reading of a cast, from the rules of 梅花易數 only (engine/data/mai_hoa/rules_extract.json: each rule an exact Hán quote of its
section with Thiên Bàn's Vietnamese). No Kinh Dịch commentary and no modern interpretation is mixed in: a Tiên thiên cast is judged by the
quái alone, a Hậu thiên cast also shows the moving line's text, as 先天後天論 says.

Order: the cast → thể and dụng and how dụng stands to thể (體用總訣) → the strength of thể in the month (衰旺) → the course: hỗ of thể,
then biến (體用互變之訣, 用吉變凶…) → which quái sinh / khắc thể and what each brings (生體 / 克體 per quái) → the topic chapter asked about
→ Đọc sâu: đảng of thể and dụng, the points the book leaves open and how they were settled."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from .reading import P, S, finish
from .tables import TIEN_THIEN_NUMBER, TRIGRAM_HAN

DATA = Path(os.environ.get("TVBT_MH_DATA_DIR") or Path(__file__).resolve().parents[2] / "data" / "mai_hoa")
# the user's topic -> the chapter of 體用生克篇之二 that answers it (人事 for a general question)
TOPIC_RULE = {None: "p.nhan_su", "su_nghiep": "p.cau_danh", "tai_chinh": "p.cau_tai", "kinh_doanh": "p.giao_dich",
              "hoc_tap": "p.cau_danh", "tinh_cam": "p.hon_nhan", "gia_dinh": "p.gia_trach", "lua_chon": "p.cau_muu"}
TOPIC_NOTE = {"hoc_tap": "Sách không có thiên riêng cho học tập; việc học được đọc theo thiên Cầu danh (求名占).",
              "lua_chon": "Lựa chọn cá nhân được đọc theo thiên Cầu mưu (求謀占): dụng là việc mình định làm.",
              "su_nghiep": "Sự nghiệp được đọc theo thiên Cầu danh (求名占).", "kinh_doanh": "Kinh doanh được đọc theo thiên Giao dịch (交易占).",
              "tinh_cam": "Tình cảm được đọc theo thiên Hôn nhân (婚姻占).", "gia_dinh": "Gia đình được đọc theo thiên Gia trạch (家宅占).",
              "tai_chinh": "Tài chính được đọc theo thiên Cầu tài (求財占).", None: "Câu hỏi chung được đọc theo thiên Nhân sự (人事占)."}
# how the dụng stands to the thể (mai_hoa.relation) -> the book's key
REL_KEY = {"khac_the": "dung_khac_the", "the_khac": "the_khac_dung", "sinh_the": "dung_sinh_the", "the_sinh": "the_sinh_dung", "ty_hoa": "ty_hoa"}
REL_VI = {"khac_the": "khắc thể", "the_khac": "bị thể khắc", "sinh_the": "sinh thể", "the_sinh": "được thể sinh (thể bị tiết khí)", "ty_hoa": "cùng hành với thể"}
GOOD = {"sinh_the", "ty_hoa", "the_khac"}
PART_VI = {"dung": "dụng", "ho_upper": "hỗ trên", "ho_lower": "hỗ dưới", "bien": "biến"}
POS_VI = ("Đầu", "Hai", "Ba", "Tư", "Năm", "Trên")


@lru_cache(maxsize=None)
def rules() -> dict:
    d = json.loads((DATA / "rules_extract.json").read_text("utf-8"))
    return {r["id"]: r for r in d["rules"]}


def frm(rule_id: str, part: str | None = None) -> list[dict]:
    r = rules()[rule_id]
    q = (r.get("han_by_relation") or {}).get(part) if part else None
    return [{"rule": rule_id, "book": "WEB:zh_meihua", "path": r["path"], "quote": q or r["han_quote"]}]


def rel_vi(rule_id: str, key: str) -> str | None:
    return (rules()[rule_id].get("vi_by_relation") or {}).get(key)


class MaiHoaReader:
    def __init__(self, cast: dict, topic: str | None):
        self.c = cast
        self.topic = topic if topic in TOPIC_RULE else None
        self.the = cast["the"]["trigram"]
        self.dung = cast["dung"]["trigram"]
        self.rel = cast["relations"]

    def lap_que(self) -> dict:
        c = self.c
        out = [S(f"Quẻ lập được là {c['ban']['full_name']} ({c['ban']['han']}), hào {POS_VI[c['moving'] - 1]} động, biến sang {c['bien']['full_name']} "
                 f"({c['bien']['han']}); quẻ hỗ là {c['ho']['full_name']}", "tinh_toan",
                 [{"cast": [s["expr"] for s in c["steps"]]}])]
        return {"id": "lap_que", "title": "Quẻ đã lập", "paragraphs": [P(out)]}

    def the_dung(self) -> dict:
        c, r = self.c, self.rel["dung"]
        pos = {"upper": "trên", "lower": "dưới"}
        out = [S(f"Hào động nằm ở quái {pos[c['dung']['position']]}, nên {self.dung} ({c['dung']['element']}) là dụng, "
                 f"{self.the} ({c['the']['element']}) ở quái {pos[c['the']['position']]} là thể: thể là mình, dụng là việc", "kinh",
                 frm("t.assign") + frm("t.roles"))]
        verdict = rel_vi("t.five_relations", REL_KEY[r])
        if verdict:
            out.append(S(verdict, "kinh", frm("t.five_relations", REL_KEY[r])))     # the book's clause already names the relation
        else:
            out.append(S(f"Dụng {REL_VI[r]}. {rules()['t.five_relations']['vi']}", "kinh", frm("t.five_relations")))
        if r == "the_sinh":
            out.append(S(rules()["t.tiet_khi"]["vi"], "kinh", frm("t.tiet_khi")))
        return {"id": "the_dung", "title": "Thể và dụng", "paragraphs": [P(out)]}

    def vuong_suy(self) -> dict | None:
        st = self.c.get("strength")
        if not st:
            return None
        s = st["the"]
        word = {"vuong": "đang vượng", "suy": "đang suy", "binh": "không vượng không suy"}[s]
        out = [S(f"Thể {self.the} {word} trong {self.c['season_vi']} (tháng {self.c['month']} âm lịch)", "tinh_toan",
                 frm("v.vuong") + frm("v.suy"))]
        khac = [k for k, v in self.rel.items() if v == "khac_the"]
        if s == "vuong" and khac:
            out.append(S(rules()["v.dac_lenh"]["vi"], "kinh", frm("v.dac_lenh")))
        elif s == "suy" and khac:
            out.append(S(rules()["v.the_suy_khac_vuong"]["vi"] if any(st.get(k) == "vuong" for k in khac) else rules()["v.suy_vuong_luan"]["vi"],
                         "kinh", frm("v.the_suy_khac_vuong" if any(st.get(k) == "vuong" for k in khac) else "v.suy_vuong_luan")))
        else:
            out.append(S(rules()["t.thinh_suy"]["vi"], "kinh", frm("t.thinh_suy")))
        return {"id": "vuong_suy", "title": "Thể mạnh hay yếu", "paragraphs": [P(out)]}

    def dien_tien(self) -> dict:
        c = self.c
        side = c["the"]["position"]
        ho_the = c["ho"][side]
        r_ho = self.rel["ho_upper" if side == "upper" else "ho_lower"]
        r_bien = self.rel["bien"]
        out = [S(f"Giữa chừng, hỗ của thể là {ho_the}, {REL_VI[r_ho]}; về sau, dụng biến thành {c['bien_dung']['trigram']}, {REL_VI[r_bien]}",
                 "tinh_toan", frm("t.hu_of_the") + frm("t.roles"))]
        start_good, end_good = self.rel["dung"] in GOOD, r_bien in GOOD
        if start_good != end_good:
            out.append(S(rules()["t.cat_hung_course"]["vi"], "kinh", frm("t.cat_hung_course"),
                         note=("Dụng thuận mà biến nghịch: trước thuận sau trở." if start_good else "Dụng nghịch mà biến thuận: trước trở sau thuận.")))
        out.append(S(rules()["t.bian_end"]["vi"], "kinh", frm("t.bian_end")))
        return {"id": "dien_tien", "title": "Diễn tiến", "paragraphs": [P(out)]}

    def sinh_khac(self) -> dict | None:
        """What each quái that sinh / khắc the thể brings (生體 / 克體 per quái), once per quái."""
        out, seen = [], set()
        parts = {"dung": self.dung, "ho_upper": self.c["ho"]["upper"], "ho_lower": self.c["ho"]["lower"], "bien": self.c["bien_dung"]["trigram"]}
        for k, tri in parts.items():
            r = self.rel[k]
            if r not in ("sinh_the", "khac_the") or (tri, r) in seen:
                continue
            seen.add((tri, r))
            rid = f"t.{'sinh' if r == 'sinh_the' else 'khac'}_the.{TIEN_THIEN_NUMBER[tri]}"
            if rid in rules() and "các điềm" not in rules()[rid]["vi"]:
                out.append(S(f"{tri} {'sinh' if r == 'sinh_the' else 'khắc'} thể: {rules()[rid]['vi']}", "kinh", frm(rid)))
        if not out:
            return None
        return {"id": "sinh_khac", "title": "Quái nào sinh, quái nào khắc thể", "paragraphs": [P(out, depth="sau")]}

    def chu_de(self) -> dict:
        rid = TOPIC_RULE[self.topic]
        key = REL_KEY[self.rel["dung"]]
        v = rel_vi(rid, key)
        text = v if v else rules()[rid]["vi"]
        out = [S(text, "kinh", frm(rid, key if v else None), note=TOPIC_NOTE[self.topic])]
        return {"id": "chu_de", "title": "Việc đang hỏi", "paragraphs": [P(out)]}

    def hao_text(self) -> dict | None:
        if not self.c.get("use_hao_text"):
            return None
        from .reading import first_lines
        from .texts import quẻ_texts
        n, m = self.c["ban"]["number"], self.c["moving"]
        t = quẻ_texts(n)["segments"].get(f"hao{m}", {})
        nghia = first_lines(t.get("layers", {}).get("nghia", ""))
        line = nghia or t.get("han", "")
        out = [S(f"Quẻ Hậu thiên dùng cả lời hào: hào {POS_VI[m - 1]} của quẻ {self.c['ban']['name']} nói «{line.rstrip('.')}»", "kinh",
                 frm("t.xian_tian_gua_only") + [{"hexagram": n, "seg": f"hao{m}", "layer": "nghia" if nghia else "han"}])]
        return {"id": "hao_text", "title": "Lời hào", "paragraphs": [P(out)]}

    def doc_sau(self) -> dict:
        c = self.c
        out = []
        if c["party_the"]:
            out.append(S(f"Phe của thể (cùng hành {c['the']['element']}): {', '.join(PART_VI[x] for x in c['party_the'])}", "tinh_toan", frm("t.dang")))
        if c["party_dung"]:
            out.append(S(f"Phe của dụng (cùng hành {c['dung']['element']}): {', '.join(PART_VI[x] for x in c['party_dung'])}", "tinh_toan", frm("t.dang")))
        for n in c["notes"]:
            out.append(S(n, "he_thong"))
        if c["ho_from"] == "bien":
            out.append(S("Kiền và Khôn không có hỗ, nên lấy hỗ của quẻ biến", "kinh", frm("x.qian_kun_no_hu") if "x.qian_kun_no_hu" in rules() else None))
        return {"id": "doc_sau", "title": "Phe thể, phe dụng và chỗ sách để ngỏ", "paragraphs": [P([s for s in out if s], depth="sau")]}

    def read(self) -> dict:
        secs = [self.lap_que(), self.the_dung(), self.vuong_suy(), self.dien_tien(), self.chu_de(), self.hao_text(), self.sinh_khac(), self.doc_sau()]
        secs = [s for s in secs if s and any(p["sentences"] for p in s["paragraphs"])]
        return {"system": "mai_hoa", "topic": self.topic, "sections": secs, "status": "draft",
                "translation": "Bản dịch Mai Hoa Dịch Số của Thiên Bàn (bản nháp)"}


def read(cast: dict, topic: str | None = None) -> dict:
    return MaiHoaReader(cast, topic).read()


__all__ = ["read", "TRIGRAM_HAN", "finish"]
