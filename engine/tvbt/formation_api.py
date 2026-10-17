"""Opt-in endpoint for the draft cách-cục explanations (never part of the production reading)."""

from fastapi import HTTPException

WARNING = "Cấu trúc thử nghiệm, chưa đối chiếu sách; không thuộc kết quả luận giải chính thức. Điều kiện thành, phá, cứu do người xây dựng hệ thống đặt ra từ kiến thức chung."


def register(app, birth_model, compute):
    @app.post("/api/formations")
    def formations(req: birth_model):  # type: ignore[valid-type]
        from .formation_explain import analyse
        from .knowledge.loader import load_experimental
        try:
            nb, bz, tv = compute(req)
        except HTTPException:
            raise
        _, xf, _ = load_experimental()
        return {"status": "draft", "warning": WARNING, "formations": analyse(tv, xf)}
