"""POST /api/phi-hoa — opt-in, DRAFT. Two clearly separated parts:
  computation    the Phi Hóa graph (48 edges with trace): pure geometry + the Tứ Hóa-by-stem table. No reading of any kind.
  interpretation draft rules over that graph (school phi_tinh_draft): structure-only statements, unverified.
Separate module so api.py needs two lines. No `from __future__ import annotations` here: FastAPI must see the BirthReq type object."""
import dataclasses


def register(app, BirthReq, compute):
    @app.post("/api/phi-hoa")
    def phi_hoa(req: BirthReq):
        from .phi_hoa.run import run_phi_hoa
        from .phi_hoa.tables import TABLES
        nb, bz, tv = compute(req)
        r = run_phi_hoa(tv)
        g, res = r["graph"], r["result"]
        t = TABLES[g.table_id]
        edges = [{"from": e.src, "to": e.dst, "hoa": e.hoa, "star": e.star, "stem": e.src_stem, "kinds": e.kinds, "trace": e.trace} for e in g.edges]
        findings = [{**dataclasses.asdict(f), "why": res.why(f.id)} for f in r["findings"]]
        return {
            # v1 top-level keys, kept so clients written against the first release of this endpoint keep working (same names, same shapes).
            # The same data lives under computation / interpretation, which is where new code should read it.
            "table": {"id": g.table_id, "status": g.table_status}, "edges": edges, "findings": findings,
            "blocked": r["blocked"], "conflicts": r["conflicts"], "problems": r["problems"],
            "status": "draft", "school": "phi_tinh_draft",
            "warning": "Chế độ thử nghiệm. Phi Hóa là trường phái riêng; bảng Tứ Hóa theo can đang dùng là bảng của hệ Tam Hợp, CHƯA được xác minh là bảng của Phi Tinh. Chỉ mô tả cấu trúc, không dự báo.",
            "computation": {
                "level": "computed",
                "table": {"id": g.table_id, "school": t["school"], "status": g.table_status, "verified_for": t["verified_for"], "note": t["note"]},
                "edges": edges,
            },
            "interpretation": {
                "level": "experimental", "reviewStatus": "draft", "rules": [x.id for x in r["rules"]],
                "findings": findings,
                "blocked": r["blocked"], "conflicts": r["conflicts"], "problems": r["problems"],
            },
        }
