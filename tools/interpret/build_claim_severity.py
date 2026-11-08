"""Claim severity (plan THIEN-BAN-33 G1, owner decision Q2 2026-11-07): which verified Tử Vi rules state a grave or over-specific outcome.

severity is its own axis, independent of confidence: a rule whose conditions hold exactly may still be too heavy to show as a conclusion.
Classes (engine/data/kg/claim_severity.json `classes`):
  suc_khoe, tho_yeu, sinh_san      never in a main paragraph, a chapter close or the Tổng luận; in Đọc sâu only as a neutral line
  vat_chat_nang, hon_nhan_vo, tat_xau, phap_ly   the same (the owner's Q2 answer covers every grave outcome)
  moc_tuoi                          a fixed age: kept, said as the book's mark and set beside the chart's đại hạn
The match runs on the CLAIM part of the rule's description (after "cung X:", before the condition in brackets), so palace names such as
Tật Ách never match. Hand corrections live in MANUAL below (False = not grave although a keyword matched).
  python3 tools/interpret/build_claim_severity.py
"""
import glob, json, re, sys, unicodedata

CLASSES = {
    # "tai họa / tai ương" alone is general misfortune in these books, not a health outcome: not matched
    "suc_khoe": {"topic": "bệnh tật, tai ách", "re": r"bệnh|đau ốm|ốm đau|tai nạn|tai ách|thương tật|tàn tật|mổ xẻ|\bmù\b|\bđiếc\b|\bcâm\b|\bquè\b|huyết quang|ung nhọt|tật nguyền|có tật|mang tật|thương tích"},
    "tho_yeu": {"topic": "thọ yểu", "re": r"\bthọ\b|yểu|\bchết\b|tử vong|mất sớm|đoản mệnh|mạng vong|chết non|sống lâu|qua đời|tuổi thọ|nguy đến tính mạng"},
    "sinh_san": {"topic": "đường con cái", "re": r"đông con|nhiều con|hiếm con|muộn con|chậm con|không con|vô tự|tuyệt tự|sát con|khó nuôi con|con khó nuôi|ít con|sẩy thai|hư thai|khó có con|hiếm muộn|không có con"},
    "hon_nhan_vo": {"topic": "đổ vỡ hôn nhân", "re": r"ly hôn|ly dị|góa|goá|tái giá|bỏ nhau|đổ vỡ|dang dở|sinh ly tử biệt|khắc vợ|khắc chồng|sát phu|sát thê|lập gia đình hai lần|hai lần lập gia đình|nhiều đời chồng"},
    "vat_chat_nang": {"topic": "hao tổn tài sản lớn", "re": r"phá sản|chiếm đoạt|tán gia|khuynh gia|bại sản|mất hết|trắng tay|tan cửa nát nhà"},
    "tat_xau": {"topic": "thói ham vui, sa đà", "re": r"cờ bạc|phóng đãng|trộm|\bdâm\b|nghiện|rượu chè|gian xảo|gian manh|gian dối|lừa đảo|bất lương|trác táng|đàng điếm"},
    "phap_ly": {"topic": "chuyện tù tội", "re": r"\btù\b|\bngục\b|tù tội|hình ngục|tội vạ"},
    "moc_tuoi": {"topic": "mốc tuổi", "re": r"\b\d{2}\s*tuổi"},
}
GRAVE = [c for c in CLASSES if c != "moc_tuoi"]
# hand review of the keyword matches (2026-11-08): a match that is not the grave outcome itself
MANUAL: dict[str, object] = {
    "TV_KL_STAR_MENH_NHAT_HAM_TT": False,     # "như người tài được thả khỏi tù": a simile for Tuần/Triệt lifting a hãm Thái Dương
    "TV_KL_PHU2_TUONG_TA_HUU_Y": False,       # "hợp nghề thầy thuốc, chữa bệnh": a calling, not an illness
    "TV_D3_KL204_VCD_KHONG_KIEP": False,      # "tìm đường sống trong chỗ chết": an idiom for daring
    # cách: the Cách cục chapter tells the formation itself (G5 decides its wording), not the severity pass
    "TV_D3_KL47_DE_NGO_HUNG_DO": False,
    "TV_D3_TT142_HINH_TU_HIEP_AN": False,
    "TV_KL_STAR_MENH_LOC_MA_KHONG_KIEP": False,  # "sự nghiệp dễ đổ vỡ": a career setback, not a marriage outcome
    "TV_PB_TT_DIEN_TRACH_TT_DIEN_TRACH_SAT_HINH": "vat_chat_nang",  # "gia nghiệp đổ vỡ": the estate, not the marriage
}

def parse(desc: str):
    """claim / condition / cite of a rule description "<book> … (paraphrased), cung P: <claim> (<condition>) [<cite>]" (the "cung P" part may be
    missing). The condition is the last balanced bracket before the cite; a cách's condition may carry its meaning after a colon, which counts
    as claim text."""
    m = re.search(r"\[([^\]]+)\]\s*$", desc or "")
    if not m:
        return None
    cite, body = m.group(1).strip(), desc[:m.start()].rstrip()
    cond = ""
    if body.endswith(")"):
        depth, i = 0, len(body) - 1
        while i >= 0:
            depth += {")": 1, "(": -1}.get(body[i], 0)
            if depth == 0:
                break
            i -= 1
        cond, body = body[i + 1:-1].strip(), body[:i].rstrip()
    if ": " not in body:
        return None
    head, claim = body.rsplit(": ", 1)
    pm = re.search(r"cung ([^,:()]+)$", head)
    meaning = cond.split(": ", 1)[1] if ": " in cond else ""
    return {"palace": pm.group(1).strip() if pm else "", "claim": claim.strip(), "cond": cond.split(": ", 1)[0].strip(), "cite": cite, "meaning": meaning}


def main() -> None:
    rules, seen = {}, 0
    for fn in sorted(glob.glob("engine/data/pack_*.json")):
        d = json.load(open(fn))
        for r in (d.get("rules", d) if isinstance(d, dict) else d):
            if r.get("system") != "tu_vi" or r.get("reviewStatus") != "verified":
                continue
            seen += 1
            p = parse(unicodedata.normalize("NFC", r.get("description", "")))
            if not p:
                continue
            low = (p["claim"] + " | " + p["meaning"]).lower()
            hit = [c for c, v in CLASSES.items() if re.search(v["re"], low)]
            if r["id"] in MANUAL:
                hit = [] if MANUAL[r["id"]] is False else [MANUAL[r["id"]]]
            if not hit:
                continue
            cls = next((c for c in GRAVE if c in hit), hit[0])
            eff = next((c.get("effect") for c in r.get("consequences", []) if c.get("effect")), None)
            rules[r["id"]] = {"class": cls, "pol": "-" if eff == "limit" else "+" if eff == "support" else "~", "palace": p["palace"], "cond": p["cond"], "cite": p["cite"], "claim": p["claim"]}
    out = {"version": "claim-severity-1", "date": "2026-11-08", "basis": "he_thong",
           "note": "Severity of a verified rule's stated outcome (plan THIEN-BAN-33 G1, owner Q2 2026-11-07). Independent of confidence. Built by tools/interpret/build_claim_severity.py from the claim part of each rule's description; MANUAL in the builder holds the hand review.",
           "grave": GRAVE, "classes": {c: {"topic": v["topic"], "re": v["re"]} for c, v in CLASSES.items()}, "rules": dict(sorted(rules.items()))}
    json.dump(out, open("engine/data/kg/claim_severity.json", "w"), ensure_ascii=False, indent=1)
    by = {}
    for v in rules.values():
        by[v["class"]] = by.get(v["class"], 0) + 1
    print(seen, "verified Tử Vi rules;", len(rules), "classed", by)
    if "-v" in sys.argv:
        for k, v in rules.items():
            print(v["class"], k, "|", v["claim"][:90], "|", v["cond"][:60])


main()
