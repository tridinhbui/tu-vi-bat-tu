"""The Kinh Dịch reading of a cast: no model, no randomness. Same cast + same topic = same text.

What each sentence rests on is in its `basis` and `from`:
  kinh       a line of the classic (Ngô Tất Tố's dịch nghĩa of the Hán)
  chu_giai   the traditional commentary (Trình Di, Chu Hy), quoted
  tinh_toan  what the cast computes (which quẻ, which hào move, positions)
  he_thong   how the reading is put together (Chu Hy's rule on moving lines named in plain words)
  dien_giai  the system's modern interpretation (draft), each tied to quoted lines
  loi_khuyen practical advice, kept apart from the traditional reading

Order of the main reading: tình thế (quẻ chủ) → lời chính (the text Chu Hy's rule picks, with the traditional reading of it) → the moving
hào → hướng chuyển (quẻ biến) → the topic asked about → what can change the outcome → practical advice. Đọc sâu (depth 'sau'): the build of
the quẻ, the position of each moving hào, quẻ hỗ, the original texts, other schools' rule for the same moving lines."""
from __future__ import annotations

import re

from . import dien_giai as dg
from .doc_hao import CITES as RULE_CITES
from .tables import TRIGRAM_HAN, cite
from .texts import quẻ_texts

TRIGRAMS = None


def _tri() -> dict:
    global TRIGRAMS
    if TRIGRAMS is None:
        import json

        from .texts import DATA
        TRIGRAMS = json.loads((DATA / "trigrams.json").read_text("utf-8"))["trigrams"]
    return TRIGRAMS


def S(text: str, basis: str, frm: list | None = None, note: str | None = None) -> dict:
    s = {"text": finish(text), "basis": basis}
    if frm:
        s["from"] = frm
    if note:
        s["note"] = note
    return s


def finish(t: str) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    if t and t[-1] not in ".!?":
        t += "."
    return t[:1].upper() + t[1:]


def P(sentences: list[dict], depth: str = "nhanh", lead: str | None = None) -> dict:
    p = {"depth": depth, "sentences": [s for s in sentences if s]}
    if lead:
        p["lead"] = lead
    return p


def strip_label(t: str) -> str:
    """'Hào Chín Hai: Ở trong quân…' / 'Lời Tượng nói rằng: Trong đất…' -> the text itself."""
    t = re.sub(r"^\s*Hào [^:：.]{2,20}[:：.]\s*", "", t)
    t = re.sub(r"^\s*Lời (Tượng|Thoán) nói rằng[:：]\s*", "", t)
    return t.strip()


def first_lines(t: str) -> str:
    return strip_label(t.split("\n")[0])


def quote(t: str) -> str:
    return f"«{t.rstrip('.')}»"


def ref(n: int, seg: str, layer: str, q: str | None = None) -> dict:
    r = {"hexagram": n, "seg": seg, "layer": layer}
    if q:
        r["quote"] = q
    return r


def tied(n: int, item: dict) -> list[dict]:
    return [ref(n, f["seg"], f["layer"], f["quote"]) for f in item.get("from", [])]


def seg_key_of(textref: dict) -> str:
    k = textref["kind"]
    return f"hao{textref['hao']}" if k == "hao" else ("dung" if k == "dung" else "thoan")


def hao_vi(h: dict) -> str:
    return f"hào {h['vi']}"


TOPIC_LEAD = dg.TOPICS


class Reader:
    def __init__(self, cast: dict, topic: str | None):
        self.c = cast
        self.topic = topic if topic in dg.TOPICS else None
        self.ban = cast["ban"]
        self.bien = cast["bien"]
        self.n = self.ban["number"]
        self.tx = quẻ_texts(self.n)
        self.d = dg.load(self.n)
        self.bt = quẻ_texts(self.bien["number"]) if self.bien else None
        self.bd = dg.load(self.bien["number"]) if self.bien else None
        self.rule = cast["reading_rule"]
        self.missing: list[str] = []

    # ---- helpers over the texts
    def layer(self, tx: dict, seg: str, layer: str) -> str:
        s = tx["segments"].get(seg)
        return (s or {}).get("layers", {}).get(layer, "") if s else ""

    def nghia(self, tx: dict, seg: str) -> str:
        return first_lines(self.layer(tx, seg, "nghia"))

    def name(self, h: dict) -> str:
        return f"{h['full_name']} ({h['han']})"

    # ---- sections
    def tinh_the(self) -> dict:
        b, tri = self.ban, _tri()
        up, lo = tri[b["upper"]], tri[b["lower"]]
        out = [S(f"Quẻ gieo được là {self.name(b)}: {b['upper']} ({up['image']['vi']}) ở trên, {b['lower']} ({lo['image']['vi']}) ở dưới",
                 "tinh_toan", [ref(self.n, "thoan", "han")],
                 note=f"Tính của hai quái: {b['lower']} {lo['quality']['vi']}, {b['upper']} {up['quality']['vi']} (Ngô Tất Tố, Những điều nên biết)."),
               ]
        image = self.nghia(self.tx, "dai_tuong")
        if image:
            out.append(S(f"Lời Tượng: {quote(image)}", "kinh", [ref(self.n, "dai_tuong", "nghia", image)]))
        if self.d:
            q = self.d["que"]
            out.append(S(q["core"]["text"], "dien_giai", tied(self.n, q["core"])))
            if q.get("image"):
                out.append(S(q["image"]["text"], "dien_giai", tied(self.n, q["image"])))
        else:
            self.missing.append(f"diễn giải quẻ {self.ban['name']}")
        return {"id": "tinh_the", "title": "Tình thế", "paragraphs": [P(out)]}

    def loi_chinh(self) -> dict:
        r = self.rule
        main, also = r["main"], r["also"]
        n_moving = r["moving_count"]
        why = {0: "Không có hào nào động, nên lời quẻ là lời chính.",
               1: "Có một hào động, nên lời của hào ấy là lời chính.",
               2: "Có hai hào động: lời hào trên là lời chính, lời hào dưới đọc kèm.",
               4: "Có bốn hào động: lời chính nằm ở hai hào không động của quẻ biến, hào dưới làm chủ.",
               5: "Năm hào cùng động: lời chính là hào duy nhất không động, đọc ở quẻ biến."}
        if n_moving == 3:
            why_t = ("Ba hào động, trong đó có hào Đầu: đọc lời của cả quẻ chủ lẫn quẻ biến, lời quẻ chủ nặng hơn." if 1 in self.c["moving"]
                     else "Ba hào động, không có hào Đầu: đọc lời của cả quẻ chủ lẫn quẻ biến, lời quẻ biến nặng hơn.")
        elif n_moving == 6:
            why_t = ("Sáu hào cùng động ở quẻ " + self.ban["name"] + ": đọc lời 'dùng " + ("Chín" if self.n == 1 else "Sáu") + "'."
                     if self.n in (1, 2) else "Sáu hào cùng động: lời quẻ biến là lời chính.")
        else:
            why_t = why[n_moving]
        out = [S(why_t, "he_thong", [{"rule": r["school"], "cites": RULE_CITES[n_moving]}],
                 note="Phép đọc hào động của Chu Hy (Dịch học khải mông), các phái khác đọc khác: xem Đọc sâu.")]
        for i, t in enumerate([main] + also):
            tx = self.tx if t["hexagram"] == self.n else self.bt
            dd = self.d if t["hexagram"] == self.n else self.bd
            seg = seg_key_of(t)
            text = self.nghia(tx, seg)
            if not text:
                self.missing.append(f"bản dịch {seg} quẻ {tx['han']}")
                continue
            who = ("lời quẻ " + (self.ban["name"] if t["hexagram"] == self.n else self.bien["name"]) if t["kind"] == "thoan"
                   else ("lời 'dùng Chín'" if self.n == 1 else "lời 'dùng Sáu'") if t["kind"] == "dung"
                   else f"lời hào {self.hao_label(t)}")
            lead = "Lời chính là " if i == 0 else "Đọc kèm "
            out.append(S(f"{lead}{who}: {quote(text)}", "kinh", [ref(t["hexagram"], seg, "nghia", text)]))
            trad = None
            if dd:
                trad = (dd["que"].get("traditional") if t["kind"] in ("thoan",) else dd.get("hao", {}).get(str(t.get("hao")), {}).get("traditional"))
                if t["kind"] == "dung":
                    trad = dd.get("dung", {}).get("traditional")
            if trad and trad["layer"] in ("chu_hy", "trinh_di"):
                who_c = "Chu Hy" if trad["layer"] == "chu_hy" else "Trình Di"
                out.append(S(f"Lời bàn của {who_c}: {quote(trad['quote'])}", "chu_giai", [ref(t["hexagram"], trad["seg"], trad["layer"], trad["quote"])]))
            if dd and t["kind"] == "hao":
                g = dd.get("hao", {}).get(str(t["hao"]), {}).get("gist")
                if g:
                    out.append(S(g["text"], "dien_giai", tied(t["hexagram"], g)))
        return {"id": "loi_chinh", "title": "Lời chính", "paragraphs": [P(out)]}

    def hao_label(self, t: dict) -> str:
        h = t["hao"]
        lines = self.ban["lines"] if t["hexagram"] == self.n else self.bien["lines"]
        from .core import hao_name
        return hao_name(h, bool(lines[h - 1]))["vi"]

    def hao_dong(self) -> dict | None:
        """The moving hào not already read as the main text: what each says, briefly (Chu Hy reads only some of them; the others are the
        change itself and are shown so the reader sees every moving line)."""
        named = {(t["hexagram"], t.get("hao")) for t in [self.rule["main"], *self.rule["also"]] if t["kind"] == "hao"}
        rest = [h for h in self.c["hao"] if h["moving"] and (self.n, h["position"]) not in named]
        if not rest:
            return None
        out = []
        for h in rest:
            seg = f"hao{h['position']}"
            text = self.nghia(self.tx, seg)
            if not text:
                continue
            out.append(S(f"Hào {h['vi']} cũng động: {quote(text)}", "kinh", [ref(self.n, seg, "nghia", text)]))
            g = (self.d or {}).get("hao", {}).get(str(h["position"]), {}).get("gist")
            if g:
                out.append(S(g["text"], "dien_giai", tied(self.n, g)))
        return {"id": "hao_dong", "title": "Các hào động khác", "paragraphs": [P(out, depth="sau")]} if out else None

    def huong_chuyen(self) -> dict | None:
        if not self.bien:
            return None
        b = self.bien
        tri = _tri()
        names = [f"hào {h['vi']}" for h in self.c["hao"] if h["moving"]]
        moving = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " và " + names[-1]
        out = [S(f"{moving[:1].upper() + moving[1:]} đổi chiều, quẻ chuyển sang {self.name(b)}: {b['upper']} ({tri[b['upper']]['image']['vi']}) trên, "
                 f"{b['lower']} ({tri[b['lower']]['image']['vi']}) dưới", "tinh_toan", [ref(b["number"], "thoan", "han")])]
        image = self.nghia(self.bt, "dai_tuong")
        if image:
            out.append(S(f"Lời Tượng của quẻ biến: {quote(image)}", "kinh", [ref(b["number"], "dai_tuong", "nghia", image)]))
        if self.bd:
            out.append(S(self.bd["que"]["core"]["text"], "dien_giai", tied(b["number"], self.bd["que"]["core"]),
                         note="Quẻ biến cho thấy chiều việc đang chuyển tới, không phải một kết cục đã định."))
        else:
            self.missing.append(f"diễn giải quẻ {b['name']}")
        return {"id": "huong_chuyen", "title": "Hướng chuyển", "paragraphs": [P(out)]}

    def chu_de(self) -> dict | None:
        if not self.topic or not self.d:
            return None
        t = self.topic
        out = []
        q = self.d["que"]["topics"].get(t)
        if q:
            out.append(S(q["text"], "dien_giai", tied(self.n, q)))
        main = self.rule["main"]
        if main["kind"] == "hao":
            dd = self.d if main["hexagram"] == self.n else self.bd
            h = (dd or {}).get("hao", {}).get(str(main["hao"]), {})
            if h.get("topics", {}).get(t):
                out.append(S(h["topics"][t]["text"], "dien_giai", tied(main["hexagram"], h["topics"][t])))
        if self.bd and self.bd["que"]["topics"].get(t):
            bq = self.bd["que"]["topics"][t]
            out.append(S(f"Về chiều chuyển sang quẻ {self.bien['name']}: {lower_first(bq['text'])}", "dien_giai", tied(self.bien["number"], bq)))
        return {"id": "chu_de", "title": dg.TOPICS[t], "paragraphs": [P(out)]} if out else None

    def dieu_kien(self) -> dict | None:
        if not self.d or not self.d["que"].get("conditions"):
            return None
        out = [S(c["text"], "dien_giai", tied(self.n, c)) for c in self.d["que"]["conditions"]]
        return {"id": "dieu_kien", "title": "Điều có thể làm khác đi", "paragraphs": [P(out)]}

    def loi_khuyen(self) -> dict | None:
        if not self.d or not self.d["que"].get("advice"):
            return None
        a = self.d["que"]["advice"]
        return {"id": "loi_khuyen", "title": "Lời khuyên thực tế",
                "paragraphs": [P([S(a["text"], "loi_khuyen", tied(self.n, a),
                                    note="Lời khuyên đời thường rút từ ý của quẻ, không phải lời của kinh văn.")])]}

    # ---- Đọc sâu
    def cau_truc(self) -> dict:
        b, tri = self.ban, _tri()
        lo, up = tri[b["lower"]], tri[b["upper"]]
        out = [S(f"Nội quái {b['lower']} có tính {lo['quality']['vi']}, ngoại quái {b['upper']} có tính {up['quality']['vi']}: "
                 f"bên trong là {lo['image']['vi']}, bên ngoài là {up['image']['vi']}", "tinh_toan",
                 [cite("WEB:vi_kinhdich_ntt", "Kinh Dịch/Những điều nên biết", lo["quality"]["ntt"]),
                  cite("WEB:vi_kinhdich_ntt", "Kinh Dịch/Những điều nên biết", up["quality"]["ntt"])])]
        if self.d and self.d["que"].get("structure"):
            out.append(S(self.d["que"]["structure"]["text"], "dien_giai", tied(self.n, self.d["que"]["structure"])))
        for h in self.c["hao"]:
            if not h["moving"]:
                continue
            facts = [("đúng ngôi" if h["chinh"] else "không đúng ngôi"), ("ở giữa quái" if h["trung"] else None),
                     (f"có ứng với hào {self.c['hao'][h['ung_with'] - 1]['vi']}" if h["ung"] else f"không ứng với hào {self.c['hao'][h['ung_with'] - 1]['vi']}")]
            out.append(S(f"Hào {h['vi']} ({h['han']}) là hào {'dương' if h['yang'] else 'âm'}, " + ", ".join(f for f in facts if f),
                         "tinh_toan", [cite("WEB:vi_kinhdich_ntt", "Kinh Dịch/Những điều nên biết", "Hào Dương mà ở ngôi lẻ")],
                         note="Ngôi, giữa, ứng theo lệ chung; Ngô Tất Tố nhắc đây là 'nói đại khái', lời bàn của từng hào mới là chính."))
            pos = (self.d or {}).get("hao", {}).get(str(h["position"]), {}).get("position")
            if pos:
                out.append(S(pos["text"], "dien_giai", tied(self.n, pos)))
        return {"id": "cau_truc", "title": "Cấu trúc quẻ", "paragraphs": [P(out, depth="sau")]}

    def que_ho(self) -> dict:
        h = self.c["ho"]
        tri = _tri()
        out = [S(f"Lấy hào Hai đến hào Tư làm quái dưới, hào Ba đến hào Năm làm quái trên, được quẻ hỗ {self.name(h)}: "
                 f"{h['upper']} ({tri[h['upper']]['image']['vi']}) trên, {h['lower']} ({tri[h['lower']]['image']['vi']}) dưới", "tinh_toan",
                 [ref(h["number"], "thoan", "han")],
                 note="Quẻ hỗ (hỗ thể) là phép của các nhà chú giải đời Hán; phép đoán của Chu Hy không dùng nó, nên ở đây chỉ để xem cấu trúc bên trong.")]
        hd = dg.load(h["number"])
        if hd:
            out.append(S(hd["que"]["core"]["text"], "dien_giai", tied(h["number"], hd["que"]["core"])))
        return {"id": "que_ho", "title": "Quẻ hỗ", "paragraphs": [P(out, depth="sau")]}

    def nguyen_van(self) -> dict:
        out = []
        for t in [self.rule["main"], *self.rule["also"]]:
            tx = self.tx if t["hexagram"] == self.n else self.bt
            seg = seg_key_of(t)
            s = tx["segments"].get(seg, {})
            am = first_lines(s.get("layers", {}).get("am", ""))
            line = f"{s.get('han', '')}" + (f" — {am}" if am else "")
            out.append(S(line, "kinh", [ref(t["hexagram"], seg, "han")]))
            td = s.get("layers", {}).get("trinh_di")
            if td:
                first = re.split(r"(?<=[.!?])\s+", td.strip())
                excerpt = " ".join(first[:3])
                out.append(S(f"Trình Di: {quote(excerpt)}", "chu_giai", [ref(t["hexagram"], seg, "trinh_di", excerpt)]))
        return {"id": "nguyen_van", "title": "Nguyên văn và lời bàn", "paragraphs": [P(out, depth="sau")]}

    def read(self) -> dict:
        sections = [self.tinh_the(), self.loi_chinh(), self.hao_dong(), self.huong_chuyen(), self.chu_de(), self.dieu_kien(),
                    self.loi_khuyen(), self.cau_truc(), self.que_ho(), self.nguyen_van()]
        sections = [s for s in sections if s and any(p["sentences"] for p in s["paragraphs"])]
        return {"system": "kinh_dich", "topic": self.topic, "hexagram": self.ban, "bien": self.bien, "ho": self.c["ho"],
                "moving": self.c["moving"], "rule": self.rule, "sections": sections, "missing": sorted(set(self.missing)),
                "status": "draft"}


def lower_first(s: str) -> str:
    return s[:1].lower() + s[1:]


def read(cast: dict, topic: str | None = None) -> dict:
    return Reader(cast, topic).read()


__all__ = ["read", "TRIGRAM_HAN"]
