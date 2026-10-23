"""Finer concepts for the seven thin palaces (plan 2026-10-23 P1 'tách các khái niệm quá thô'): what Nô Bộc, Thiên Di, Phúc Đức, Phụ Mẫu, Tử Tức,
Huynh Đệ and Tật Ách books distinguish, so that different book lines do not all fall on the same few concepts. Adds them to
engine/data/kg/concepts.json (KG-only concepts) and their reader cards to src/interpret/content/prose/concepts_palaces.json, and relinks
existing rules whose reading names exactly one of them (rule_concepts.manual.json). Idempotent. Cards carry no illustration (behave) line:
a minh họa needs its own review (illustration policy); health cards carry only the book words (no soft form, value or advice)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "engine" / "data" / "kg"
CARDS = ROOT / "src" / "interpret" / "content" / "prose" / "concepts_palaces.json"

# id, facet, pol, kind, opp, np, short, card fields
C = [
 ("ally.helpful", "relationships.allies", "+", "outcome", "ally.weak", "bạn bè, người giúp việc được việc", "người giúp được việc",
  {"pred": ["có bạn bè, người giúp việc được việc", "có người dưới làm được việc"], "soft": ["có người giúp được việc, dù không nhiều"], "value": ["những người làm được việc bên cạnh"]}),
 ("ally.overstep", "relationships.allies", "-", "tendency", None, "người dưới dễ lạm quyền, lấn quyền", "sự lấn quyền của người dưới",
  {"turn": ["gặp người dưới lạm quyền", "để người dưới lấn quyền"], "soft": ["đôi khi để người dưới lấn quyền"], "mature": ["giao việc kèm giới hạn rõ ràng"]}),
 ("ally.fickle", "relationships.allies", "-", "tendency", None, "người giúp việc hay đổi, ít ai ở lâu", "sự đổi thay của người giúp việc",
  {"turn": ["có người giúp việc hay đổi, ít ai ở lâu"], "soft": ["có lúc người giúp việc không ở lâu"], "mature": ["giữ người bằng sự rõ ràng hơn là lời hứa"]}),
 ("ally.resent", "relationships.allies", "-", "tendency", None, "sự oán trách từ bạn bè, người dưới", "sự oán trách của người dưới",
  {"turn": ["bị bạn bè, người dưới oán trách", "làm ơn mà nên oán"], "soft": ["đôi khi bị người dưới oán trách"], "mature": ["giữ ân oán rạch ròi, giúp người có chừng mực"]}),
 ("ally.dispute", "relationships.allies", "-", "outcome", None, "cãi vã, kiện tụng với bạn bè, người dưới", "sự va chạm với người dưới",
  {"turn": ["vướng cãi vã, kiện tụng với bạn bè, người dưới"], "soft": ["có lúc va chạm với người dưới"], "mature": ["giao kèo với người cùng làm cho rõ từ đầu"]}),
 ("ally.few", "relationships.allies", "-", "outcome", "ally.many", "sự ít bạn bè", "sự ít bạn",
  {"turn": ["ít bạn bè", "không có nhiều người quen thân"], "soft": ["bạn bè không đông"], "mature": ["giữ kỹ vài người bạn thật"]}),
 ("ally.powerful", "relationships.allies", "+", "outcome", None, "bạn bè có thế lực", "bạn bè có thế lực",
  {"pred": ["có bạn bè có uy quyền, thế lực"], "soft": ["có vài người quen có thế lực"], "value": ["những người bạn có thế lực"]}),
 ("ally.slander", "relationships.allies", "-", "outcome", None, "người dưới nói xấu chủ", "lời nói xấu của người dưới",
  {"turn": ["bị người dưới nói xấu sau lưng"], "soft": ["có lúc bị người dưới nói ra nói vào"], "mature": ["để việc mình làm tự nói thay mình"]}),
 ("ally.greedy", "relationships.allies", "-", "tendency", None, "bạn bè tham lam", "lòng tham của bạn bè",
  {"turn": ["gặp bạn bè tham lam"], "soft": ["có người bạn hay tính phần lợi"], "mature": ["tách bạch chuyện tiền với chuyện tình bạn"]}),
 ("ally.drain", "relationships.allies", "-", "outcome", None, "người dưới chỉ tốn kém, ăn hại", "người ăn hại",
  {"turn": ["có người dưới chỉ ăn hại"], "soft": ["có người dưới tốn kém hơn được việc"], "mature": ["chọn người theo việc chứ không theo cảm tình"]}),
 ("travel.helped", "life.outside", "+", "outcome", None, "sự được kính nể, giúp đỡ khi ra ngoài", "sự được giúp khi ra ngoài",
  {"pred": ["ra ngoài được người kính nể, giúp đỡ", "ra ngoài gặp quý nhân"], "soft": ["ra ngoài có lúc được người giúp"], "value": ["những người giúp mình ở bên ngoài"]}),
 ("travel.gain", "life.outside", "+", "outcome", None, "cái lợi khi đi xa, ra ngoài", "cái lợi nơi xa",
  {"pred": ["đi xa làm ăn tốt hơn ở nhà", "ra ngoài dễ kiếm tiền"], "soft": ["đi xa có phần lợi hơn"], "value": ["cái lợi của việc đi xa"]}),
 ("travel.dispute", "life.outside", "-", "outcome", None, "khẩu thiệt, cãi vã khi ra ngoài", "khẩu thiệt bên ngoài",
  {"turn": ["ra ngoài hay vướng khẩu thiệt, cãi vã"], "soft": ["ra ngoài đôi khi vướng điều tiếng"], "mature": ["nói ít hơn ở nơi lạ"]}),
 ("travel.toil", "life.outside", "-", "outcome", None, "sự long đong khi ra ngoài", "sự long đong",
  {"turn": ["ra ngoài long đong vất vả", "ra ngoài lang thang, không ổn định"], "soft": ["ra ngoài có lúc vất vả"], "mature": ["có một chỗ dựa cố định trước khi đi xa"]}),
 ("travel.mixed", "life.outside", "~", "outcome", None, "sự may rủi đi liền nhau khi ra ngoài", "may rủi nơi xa",
  {"pred": ["ra ngoài may rủi đi liền nhau"]}),
 ("travel.costly", "life.outside", "-", "outcome", None, "sự tốn kém khi ra ngoài", "sự tốn kém khi ra ngoài",
  {"turn": ["ra ngoài tốn tiền"], "soft": ["ra ngoài hay tốn hơn dự tính"], "mature": ["định trước khoản chi cho mỗi chuyến đi"]}),
 ("fortune.away", "life.fortune", "~", "outcome", None, "việc phải rời quê mới khá lên", "sự rời quê lập nghiệp",
  {"pred": ["phải rời quê lập nghiệp mới khá lên"]}),
 ("fortune.clan_scattered", "life.fortune", "-", "outcome", None, "sự ly tán của họ hàng", "họ hàng ly tán",
  {"turn": ["có họ hàng ly tán"], "soft": ["họ hàng không gần gũi"], "mature": ["giữ liên lạc với những người thân còn gần"]}),
 ("fortune.clan_decline", "life.fortune", "-", "outcome", "fortune.clan_prosper", "sự sa sút của dòng họ", "họ hàng sa sút",
  {"turn": ["có dòng họ sa sút"], "soft": ["dòng họ không còn thịnh như trước"], "mature": ["tự gây nền cho mình thay vì trông vào gốc họ"]}),
 ("fortune.clan_prosper", "life.fortune", "+", "outcome", "fortune.clan_decline", "sự hiển đạt trong dòng họ", "dòng họ hiển đạt",
  {"pred": ["có người hiển đạt trong họ", "có dòng họ thịnh vượng"], "soft": ["trong họ có người khá giả"], "value": ["chỗ dựa của dòng họ"]}),
 ("fortune.clan_military", "life.fortune", "~", "outcome", None, "truyền thống võ nghiệp trong họ", "võ nghiệp trong họ",
  {"pred": ["có người trong họ theo nghiệp võ"]}),
 ("fortune.clan_few", "life.fortune", "-", "outcome", None, "dòng họ ít người nối dõi", "họ ít người",
  {"turn": ["có dòng họ ít người nối dõi"]}),
 ("fortune.mishap", "life.fortune", "-", "outcome", None, "những rắc rối bất ngờ", "rắc rối bất ngờ",
  {"turn": ["hay gặp chuyện rắc rối bất ngờ"], "soft": ["đôi khi gặp chuyện bất ngờ"], "mature": ["giữ một phần dự phòng cho việc không lường trước"]}),
 ("fortune.protected", "life.fortune", "+", "outcome", None, "sự được che chở", "sự che chở",
  {"pred": ["được che chở, mong gì được nấy"], "soft": ["có lúc được che chở"], "value": ["sự che chở của phúc phần"]}),
 ("fortune.reputation", "life.fortune", "-", "outcome", None, "những lúc mang tai tiếng", "tai tiếng",
  {"turn": ["có lúc mang tai tiếng"], "soft": ["đôi khi vướng điều tiếng"], "mature": ["giữ mình ở những chỗ dễ sinh điều tiếng"]}),
 ("parents.prosper", "relationships.parents", "+", "outcome", "parents.poor", "sự khá giả của cha mẹ", "cha mẹ khá giả",
  {"pred": ["có cha mẹ khá giả"], "soft": ["có cha mẹ đủ đầy ở mức vừa"], "value": ["nền nhà của cha mẹ"]}),
 ("parents.poor", "relationships.parents", "-", "outcome", "parents.prosper", "sự vất vả, thiếu thốn của cha mẹ", "cha mẹ vất vả",
  {"turn": ["có cha mẹ vất vả, chẳng giàu"], "mature": ["tự đứng vững sớm để đỡ đần cha mẹ"]}),
 ("parents.strain", "relationships.parents", "-", "outcome", None, "sự bất hòa của cha mẹ", "cha mẹ bất hòa",
  {"turn": ["có cha mẹ bất hòa"], "soft": ["cha mẹ đôi khi không hợp ý nhau"], "mature": ["giữ mình đứng ngoài những bất hòa của cha mẹ"]}),
 ("parents.apart", "relationships.parents", "-", "outcome", None, "sự xa cách giữa cha mẹ", "cha mẹ xa cách",
  {"turn": ["có cha mẹ xa cách nhau"]}),
 ("parents.burden", "relationships.parents", "-", "outcome", None, "gánh phần của cha mẹ để lại", "gánh của cha mẹ",
  {"turn": ["không nhờ được cha mẹ, lại phải gánh phần để lại"], "mature": ["tách bạch phần mình gánh được với phần không"]}),
 ("kin.talented", "relationships.kin", "+", "outcome", None, "người con, người anh em có tài, hiển đạt", "người thân hiển đạt",
  {"pred": ["có người thân hiển đạt", "có con hay anh em thành danh"], "soft": ["có người thân khá thành đạt"], "value": ["những người thân thành đạt"]}),
 ("kin.prosper", "relationships.kin", "+", "outcome", None, "sự khá giả của con cái, anh em", "người thân khá giả",
  {"pred": ["có con cái, anh em khá giả"], "soft": ["người thân đủ đầy ở mức vừa"], "value": ["sự khá giả của người thân"]}),
 ("kin.wayward", "relationships.kin", "-", "tendency", None, "tính ngỗ ngược, phá tán ở người thân", "sự ngỗ ngược",
  {"turn": ["có người thân ngỗ ngược, hay phá tán"], "soft": ["có người thân khó bảo"], "mature": ["đặt giới hạn rõ ràng với người thân hay phá"]}),
 ("kin.filial", "relationships.kin", "+", "tendency", None, "lòng hiếu thảo của con cái", "con cái hiếu thảo",
  {"pred": ["có con cái hiếu thảo"], "soft": ["con cái biết nghĩ cho cha mẹ"], "value": ["lòng hiếu thảo của con cái"]}),
 ("kin.good", "relationships.kin", "+", "outcome", "kin.adverse", "đường con cái thuận", "đường con cái thuận",
  {"pred": ["có đường con cái tốt"], "soft": ["đường con cái khá thuận"], "value": ["đường con cái"]}),
 ("kin.adverse", "relationships.kin", "-", "outcome", "kin.good", "đường con cái kém thuận", "đường con cái kém thuận",
  {"turn": ["có đường con cái kém thuận"], "mature": ["kiên nhẫn với chuyện con cái"]}),
 ("health.shielded", "wellbeing.health", "+", "outcome", "health.exposed", "sao cứu giải ở cung Tật Ách", "sao cứu giải",
  {"pred": ["có sao cứu giải ở cung Tật Ách"], "note": "health (owner review 2026-10-22): only the book words, no soft form, no illustration, no value or advice line"}),
 ("health.exposed", "wellbeing.health", "-", "outcome", "health.shielded", "sao mà sách bảo là tối kỵ ở cung Tật Ách", "sao tối kỵ ở Tật Ách",
  {"turn": ["có sao mà sách bảo là tối kỵ ở cung Tật Ách"], "note": "health (owner review 2026-10-22): only the book words, no soft form, no illustration, no value or advice line"}),
]
RELINK = {
 "TV_TH_P2_NO_BOC_NN_HAM": ["ally.fickle"], "TV_TH_P2_NO_BOC_QUYEN_CU": ["ally.resent", "ally.overstep"],
 "TV_TT_PAL_NO_BOC_TU_VI_BASE_P": ["ally.helpful", "fin.abundance"], "TV_TT_PAL_NO_BOC_THIEN_CO_HAM_M": ["ally.resent"],
 "TV_TT_PAL_NO_BOC_THIEN_CO_WITH_THAI_AM_M": ["ally.weak"], "TV_TT_PAL_NO_BOC_THAI_DUONG_WITH_CU_MON_M": ["ally.resent"],
 "TV_TT_PAL_NO_BOC_VU_KHUC_WITH_THAM_LANG_M": ["ally.weak"], "TV_TT_PAL_NO_BOC_THIEN_DONG_BASE_P": ["ally.helpful"],
 "TV_TT_PAL_NO_BOC_THAI_AM_WITH_THIEN_CO_M": ["ally.weak"], "TV_TT_PAL_NO_BOC_PHA_QUAN_MIEU_P": ["ally.helpful"],
 "TV_TT_PAL_NO_BOC_VAN_KHUC_MIEU_P": ["ally.helpful"], "TV_TT_PAL_NO_BOC_DA_LA_BASE_M": ["ally.resent"], "TV_TT_PAL_NO_BOC_HOA_TINH_BASE_M": ["ally.resent"],
 "TV_TL_NO_A_SANG_BN_HAM": ["ally.resent", "ally.weak"], "TV_TL_NO_A_HAM_BN_SANG": ["ally.helpful", "ally.overstep"], "TV_TL_NO_B_HAM_BN_SANG": ["ally.helpful"],
 "TV_TL_NO_BOC_SPT_DAC_MENH_A": ["ally.helpful", "ally.loyal"], "TV_KL_CUNG_NO_BOC_PHA_VU": ["ally.resent", "ally.fickle"],
 "TV_KL_CUNG_PHU_MAU_TU_VI": ["career.status", "parents.prosper"], "TV_KL_CUNG_PHU_MAU_TU_VI_SPLT": ["parents.prosper", "kin.strain"],
 "TV_KL_CUNG_PHU_MAU_SAO_TOT": ["parents.prosper", "kin.harmony"], "TV_KL_CUNG_PHU_MAU_HUNG": ["parents.poor"],
 "TV_KL_STAR_PHU_MAU_TV_THAT_SAT": ["parents.strain"], "TV_TL_PHU_MAU_TU_SAT": ["parents.strain"],
 "TV_TH_AUX2_PHUC_DUC_SUY": ["fortune.clan_decline", "fortune.clan_scattered"], "TV_TH_P2_PHUC_DUC_TS_DV": ["fortune.clan_prosper"],
 "TV_TH_P2_TU_TUC_TU_PHU": ["kin.talented"], "TV_TT_PHU_TU_TUC_TU_VU": ["kin.talented", "kin.many"], "TV_TH_P2_TU_TUC_KHOI_VIET": ["kin.talented"],
 "TV_TH_P2_HUYNH_DE_TUONG_LOC_MA": ["kin.talented"],
}

cf = json.loads((KG / "concepts.json").read_text("utf-8"))
have = {c["id"] for c in cf["concepts"]}
for cid, facet, pol, kind, opp, np, short, _ in C:
    e = {"id": cid, "facet": facet, "pol": pol, "kind": kind, "np": np, "short": short, **({"opp": opp} if opp else {})}
    if cid in have:
        cf["concepts"] = [e if c["id"] == cid else c for c in cf["concepts"]]
    else:
        cf["concepts"].append(e)
(KG / "concepts.json").write_text(json.dumps(cf, ensure_ascii=False, indent=1) + "\n", "utf-8")

cards = json.loads(CARDS.read_text("utf-8"))
byid = {c["id"]: i for i, c in enumerate(cards["cards"])}
for cid, facet, pol, kind, opp, np, short, fields in C:
    card = {"id": cid, "status": "draft", "np": np, "pron": f"{short} ấy", **fields}
    if cid in byid:
        cards["cards"][byid[cid]] = card
    else:
        cards["cards"].append(card)
CARDS.write_text(json.dumps(cards, ensure_ascii=False, indent=1) + "\n", "utf-8")

man = json.loads((KG / "rule_concepts.manual.json").read_text("utf-8"))
for rid, cs in RELINK.items():
    man["entries"][rid] = {**man["entries"].get(rid, {}), "asserts": [{"concept": c, "stance": "affirms"} for c in cs]}
    man["entries"][rid].pop("src", None); man["entries"][rid].pop("review", None)
    man["entries"][rid] = {"asserts": man["entries"][rid]["asserts"], **{k: v for k, v in man["entries"][rid].items() if k != "asserts"}, "src": "manual", "review": "draft"}
(KG / "rule_concepts.manual.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", "utf-8")
print(len(C), "concepts,", len(RELINK), "relinked")
