"""engine/data/kinh_dich/zhouyi_han.json: rebuilt from the saved 周易 pages, structurally complete, every segment found on its page."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_kinh_dich_kb", ROOT / "tools" / "build_kinh_dich_kb.py")
kb_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kb_tool)
KB = json.loads((ROOT / "engine/data/kinh_dich/zhouyi_han.json").read_text("utf-8"))


def test_committed_file_is_up_to_date():
    assert kb_tool.build() == KB


def test_structure():
    assert kb_tool.problems(KB) == []
    assert [q["number"] for q in KB["hexagrams"]] == list(range(1, 65))


def test_every_segment_is_on_its_page():
    pages = {c["chapter"]: c["text"] for c in json.loads((ROOT / "engine/data/sources_web/zh_zhouyi.json").read_text("utf-8"))["chapters"]}
    for q in KB["hexagrams"]:
        page = "".join(kb_tool.clean(ln).lstrip("*#").strip() for ln in pages[q["page"]].splitlines())
        for s in q["segments"]:
            for part in s["text"].split("\n"):
                assert part in page, (q["han"], s["kind"], part[:20])


def test_trigram_quotes():
    tri = json.loads((ROOT / "engine/data/kinh_dich/trigrams.json").read_text("utf-8"))
    web = lambda f: {c["chapter"]: c["text"] for c in json.loads((ROOT / f"engine/data/sources_web/{f}.json").read_text("utf-8"))["chapters"]}
    ntt = web("vi_kinhdich_ntt")[tri["sources"]["ntt"]["chapter"]].replace("''", "")
    shuo = kb_tool.clean(web("zh_zhouyi")[tri["sources"]["shuogua"]["chapter"]])
    assert set(tri["trigrams"]) == {"Kiền", "Khôn", "Chấn", "Tốn", "Khảm", "Ly", "Cấn", "Đoài"}
    for name, t in tri["trigrams"].items():
        for f in ("image", "quality"):
            assert t[f]["ntt"] in ntt and t[f]["vi"] in t[f]["ntt"], (name, f)
        for f in ("quality", "animal", "body", "family", "direction"):
            if t[f]:
                assert t[f]["han"] in shuo, (name, f)


def test_chiem_words():
    by = {q["number"]: q for q in KB["hexagrams"]}
    thoan = lambda n: by[n]["segments"][0]
    assert [c["vi"] for c in thoan(12)["chiem"]] == ["bất lợi"]              # 否之匪人，不利君子貞
    hao2_kon = next(s for s in by[2]["segments"] if s.get("hao") == 2)
    assert [c["vi"] for c in hao2_kon["chiem"]] == ["vô bất lợi"]           # 不習无不利
    hao5_kon = next(s for s in by[2]["segments"] if s.get("hao") == 5)
    assert [c["vi"] for c in hao5_kon["chiem"]] == ["nguyên cát"]           # 黃裳，元吉
