"""Python reference for src/interpret/reason/structures.ts (plan quirky-tinkering-rabin R2): for every chart of corpus1000.json.gz, the
verdict of each experimental cách cục (formation_eval.evaluate_formation + render_vi, on base facts at the anchor palace, as
engine.run_formations does before the rule loop) and every special structure (synthesis.structures.detect_all). Written gzipped to
src/interpret/test/fixtures/structures_parity.json.gz; the menh_cu_tuat worked example is included under "example".
    .venv/bin/python tools/interpret/make_structure_parity.py
Reads the corpus facts as stored (no chart is recomputed), so the fixture follows the corpus. Nothing is marked verified."""
import gzip
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine"))
from tvbt.knowledge.formation import load_formations  # noqa: E402
from tvbt.reasoning.formation_eval import evaluate_formation, render_vi  # noqa: E402
from tvbt.synthesis.structures import detect_all  # noqa: E402

FIX = ROOT / "src" / "interpret" / "test" / "fixtures"
FORMATIONS = load_formations(ROOT / "engine" / "data" / "experimental" / "formations_experimental.json")


def one(facts):
    base = facts["base"]

    def facts_of(subj):
        d = dict(base.get("chart", {}))
        d.update(base[subj])
        return d

    def world(name):
        return facts_of(f"palace:{name}") if f"palace:{name}" in base else None

    forms = []
    for f in FORMATIONS:
        subj = f"palace:{f.anchor}"
        if subj not in base:
            continue
        d = evaluate_formation(f, facts_of(subj), world)
        d["text"] = render_vi(f, d)
        forms.append(d)
    return {"formations": forms, "structures": [asdict(s) for s in detect_all(facts["palaces"], facts["tu_hoa"])]}


def main():
    corpus = json.loads(gzip.decompress((FIX / "corpus1000.json.gz").read_bytes()))
    ex = json.loads((FIX / "menh_cu_tuat.json").read_text(encoding="utf-8"))
    out = {"charts": [one(c["facts"]) for c in corpus], "example": one(ex["facts"])}
    dst = FIX / "structures_parity.json.gz"
    dst.write_bytes(gzip.compress(json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    print(dst, dst.stat().st_size, "bytes,", len(out["charts"]), "charts")
    states = Counter((d["id"], d["state"]) for c in out["charts"] for d in c["formations"])
    for f in FORMATIONS:
        print(f"  {f.id:32s}", ", ".join(f"{s}={states[(f.id, s)]}" for s in
                                          ("khong_hien", "hinh_thuc", "thanh", "thanh_thuong", "bi_pha", "pha_duoc_cuu", "chua_du_du_kien") if states[(f.id, s)]))
    present = Counter(s["id"] for c in out["charts"] for s in c["structures"] if s["present"])
    print("  structures present:", dict(sorted(present.items())))


if __name__ == "__main__":
    main()
