"""Vietnamese surface lexicon. Maps claim ids -> phrasing. A claim with no entry is rendered
as a neutral 'chưa có mô tả' line — the generator never invents wording for unknown claims."""
CLAIMS: dict[str, dict[str, str]] = {}   # filled by rule packs / fixtures: {claim: {"label": ..., "gloss": ...}}

STATUS_VI = {
    "supported": "được các quy tắc đã khớp hỗ trợ",
    "qualified": "được hỗ trợ nhưng có điều kiện hạn chế",
    "limited": "bị giới hạn bởi quy tắc đối lập",
    "unresolved": "chưa thể kết luận vì có quy tắc đối lập mà nguồn chưa xác định thứ tự ưu tiên",
}
BASIS_VI = {"draft": "dựa trên quy tắc nháp, chưa xác minh nguồn", "verified": "dựa trên quy tắc đã xác minh nguồn"}
EFFECT_VI = {"support": "gắn với", "limit": "thuộc điều kiện hạn chế:", "neutral": "liên quan đến"}

DISCLAIMER = ("Đây là diễn giải theo hệ biểu tượng truyền thống, không phải dự báo hay chẩn đoán, "
              "và không phải bằng chứng khoa học về số phận.")
PHILOSOPHY = [
    "Sinh khắc chỉ là quan hệ nền; lợi hay hại còn tùy thời, thế và vai trò của yếu tố trong toàn cục.",
    "Một dấu hiệu chỉ có nghĩa trong điều kiện áp dụng của quy tắc sinh ra nó, không phải chân lý chung.",
]
