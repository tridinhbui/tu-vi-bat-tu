"""Save public-domain Wikisource texts for the Kinh Dịch / Mai Hoa module as engine/data/sources_web/<id>.json (owner decision 2026-10-25).

Each snapshot is {chapters: [{chapter, text, revid, revision_timestamp, sha256}]}: one chapter per Wikisource page, the chapter name is the page
title, the text is the raw wikitext. tools/book_text.py reads it as 'WEB:<id>' with the page title as the 'page'. The index entry in
engine/data/sources_web/index.json is written alongside.

  .venv/bin/python -I tools/snapshot_wikisource.py zh_zhouyi zh_meihua vi_kinhdich_ntt
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "engine" / "data" / "sources_web"
UA = {"User-Agent": "tvbt-sources/1.0 (Thiên Bàn; public-domain snapshot)"}

# King Wen order, as the 周易 page lists them
ZHOUYI_64 = ("乾 坤 屯 蒙 需 訟 師 比 小畜 履 泰 否 同人 大有 謙 豫 隨 蠱 臨 觀 噬嗑 賁 剝 復 无妄 大畜 頤 大過 坎 離 "
             "咸 恒 遯 大壯 晉 明夷 家人 睽 蹇 解 損 益 夬 姤 萃 升 困 井 革 鼎 震 艮 漸 歸妹 豐 旅 巽 兌 渙 節 中孚 小過 既濟 未濟").split()
ZHOUYI_TEN_WINGS = ["彖", "大象", "小象", "文言", "繫辭上", "繫辭下", "說卦", "序卦", "雜卦"]

SETS = {
    "zh_zhouyi": {
        "site": "zh.wikisource.org",
        "pages": ["周易"] + [f"周易/{n}" for n in ZHOUYI_64] + [f"周易/{n}" for n in ZHOUYI_TEN_WINGS],
        "title": "周易",
        "label_vi": "Chu Dịch (Hán văn): lời quẻ, lời hào, Thoán, Tượng, Văn ngôn, Hệ từ, Thuyết quái, Tự quái, Tạp quái",
        "cite": "Chu Dịch",
        "status": "public-domain classical text; Wikisource transcription",
    },
    "zh_meihua": {
        "site": "zh.wikisource.org",
        "pages": ["梅花易數", "梅花易數/卷一", "梅花易數/卷二", "梅花易數/卷三"],
        "title": "梅花易數",
        "label_vi": "Mai Hoa Dịch Số (Hán văn), tương truyền của Thiệu Ung (邵雍)",
        "cite": "Mai Hoa",
        "status": "public-domain classical text; Wikisource transcription (3 quyển)",
    },
    "vi_kinhdich_ntt": {
        "site": "vi.wikisource.org",
        "list_prefix": "Kinh Dịch/",
        "pages": ["Kinh Dịch"],
        "title": "Kinh Dịch (Ngô Tất Tố dịch và chú giải)",
        "label_vi": "Kinh Dịch, bản dịch và chú giải của Ngô Tất Tố (Wikisource, chưa đủ 64 quẻ)",
        "cite": "Kinh Dịch NTT (Wikisource)",
        "status": "public domain in Viet Nam (translator died 1954); Wikisource transcription, 9 of 64 quẻ",
    },
    # Chu Hy's rule for reading moving lines (易學啟蒙 · 考變占) is not on Wikisource and ctext needs an API key: it is read where two later books
    # quote it — 胡煦 周易函書 約存卷七 (each 啟蒙 clause, then 煦按, plus 程迥 考古占例, 王氏 and 豐南禺 methods) and 韓邦奇 啓蒙意見 卷四 (七占:
    # which clauses he keeps 仍舊 and which he changes 新定). The 3-coin method (以錢代蓍畫法) is 卜筮全書 as printed in 古今圖書集成 卷544;
    # that page is a transclusion of the scanned volume, so its rendered text is saved (machine punctuation, see the page's own notice).
    "zh_iching_methods": {
        "site": "zh.wikisource.org",
        "pages": ["周易函書 (四庫全書本)/約存卷07", "啓蒙意見 (四庫全書本)/卷4"],
        "rendered": ["欽定古今圖書集成/博物彙編/藝術典/第544卷"],
        "title": "Phép đọc hào động và phép gieo tiền",
        "label_vi": "Các phép đọc hào động (Chu Hy Khải mông qua Hồ Húc, Hàn Bang Kỳ; Trình Hồi, Vương thị, Phong Nam Ngung) và phép gieo ba đồng tiền (Bốc phệ toàn thư)",
        "cite": "Phép bói",
        "status": "public-domain classical texts; Wikisource transcriptions (四庫全書本; 古今圖書集成 with machine punctuation)",
    },
}


def get(url: str) -> str:
    for attempt in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if attempt == 3 or e.code not in (429, 503):
                raise
            time.sleep(int(e.headers.get("Retry-After") or 30) + 5)
    raise AssertionError


def api(site: str, **params) -> dict:
    params = {"format": "json", "formatversion": "2", **params}
    return json.loads(get(f"https://{site}/w/api.php?" + urllib.parse.urlencode(params)))


def list_prefix(site: str, prefix: str) -> list[str]:
    pages = api(site, action="query", list="allpages", apprefix=prefix, aplimit="500")["query"]["allpages"]
    return [p["title"] for p in pages]


def fetch(site: str, titles: list[str]) -> list[dict]:
    """Up to 50 titles per request (the API limit for revision content), in the order asked."""
    out, chapters = {}, []
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        res = api(site, action="query", prop="revisions", titles="|".join(batch), rvprop="ids|timestamp|content", rvslots="main", redirects="1")
        norm = {n["from"]: n["to"] for n in res["query"].get("normalized", [])}
        redir = {r["from"]: r["to"] for r in res["query"].get("redirects", [])}
        for page in res["query"]["pages"]:
            if page.get("missing"):
                raise SystemExit(f"missing page: {site} {page['title']}")
            rev = page["revisions"][0]
            out[page["title"]] = (rev, rev["slots"]["main"]["content"])
        for t in batch:
            # the chapter keeps the title asked for (e.g. 周易/說卦); a redirect target (易傳/說卦) is recorded as source_title
            target = redir.get(norm.get(t, t), norm.get(t, t))
            rev, text = out[target]
            ch = {"chapter": t, "text": text, "revid": rev["revid"], "revision_timestamp": rev["timestamp"],
                  "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
            if target != t:
                ch["source_title"] = target
            chapters.append(ch)
        time.sleep(3)
    return chapters


def rendered(site: str, title: str) -> dict:
    """A page whose wikitext only transcludes scanned pages: keep the rendered text (tags stripped, '[编辑]' links dropped)."""
    res = api(site, action="parse", page=title, prop="text|revid")["parse"]
    text = html.unescape(re.sub(r"<[^>]+>", "", res["text"])).replace("[编辑]", "")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    time.sleep(3)
    return {"chapter": title, "text": text, "revid": res["revid"], "rendered": True, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


def snapshot(sid: str) -> None:
    spec = SETS[sid]
    titles = list(spec["pages"])
    if "list_prefix" in spec:
        titles += [t for t in list_prefix(spec["site"], spec["list_prefix"]) if t not in titles]
    chapters = fetch(spec["site"], titles) + [rendered(spec["site"], t) for t in spec.get("rendered", [])]
    body = {"source": spec["title"], "site": spec["site"], "fetched": date.today().isoformat(), "chapters": chapters}
    raw = json.dumps(body, ensure_ascii=False, indent=1)
    (OUT / f"{sid}.json").write_text(raw + "\n", "utf-8")
    idx_file = OUT / "index.json"
    idx = json.loads(idx_file.read_text("utf-8"))
    idx["sources"][sid] = {
        "file": f"{sid}.json", "title": spec["title"], "label_vi": spec["label_vi"], "cite": spec["cite"],
        "url": f"https://{spec['site']}/wiki/" + urllib.parse.quote(spec["pages"][0]), "pages": len(chapters),
        "fetched": body["fetched"], "sha256": hashlib.sha256((raw + "\n").encode("utf-8")).hexdigest(), "status": spec["status"],
    }
    idx_file.write_text(json.dumps(idx, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(sid, len(chapters), "pages")


if __name__ == "__main__":
    for s in sys.argv[1:] or list(SETS):
        snapshot(s)
