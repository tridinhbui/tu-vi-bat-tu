"""POST /api/phi-hoa — opt-in, DRAFT Phi Hóa graph + rule results with full trace. Separate module so api.py needs two lines."""

import dataclasses


def register(app, BirthReq, compute):
    @app.post("/api/phi-hoa")
    def phi_hoa(req: BirthReq):
        from .phi_hoa.run import run_phi_hoa
        from .reasoning.engine import Finding  # noqa: F401
        nb, bz, tv = compute(req)
        r = run_phi_hoa(tv)
        g, res = r["graph"], r["result"]
        why = lambda f: res.why(f.id)           # noqa: E731
        return {
            "status": "draft", "school": "phi_tinh_draft",
            "warning": "Phi Hóa là trường phái riêng; bảng Tứ Hóa theo can dùng lại bảng tam hợp và CHƯA đối chiếu tài liệu Phi Tinh. Chỉ mô tả cấu trúc, không dự báo.",
            "table": {"id": g.table_id, "status": g.table_status},
            "edges": [{"from": e.src, "to": e.dst, "hoa": e.hoa, "star": e.star, "stem": e.src_stem, "kinds": e.kinds, "trace": e.trace} for e in g.edges],
            "findings": [{**dataclasses.asdict(f), "why": why(f)} for f in r["findings"]],
            "blocked": r["blocked"], "conflicts": r["conflicts"], "problems": r["problems"],
        }
