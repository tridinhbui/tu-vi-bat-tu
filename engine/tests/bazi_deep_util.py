import json
from pathlib import Path

from tvbt.bazi_deep.model import ChartView

ROOT = Path(__file__).resolve().parent.parent
EX = json.loads((ROOT / "data/bazi_deep/examples.json").read_text("utf-8"))["charts"]
# constructed charts used where the EX set has no instance
HOA1 = "Mậu Ngọ / Kỷ Mùi / Giáp Thìn / Tân Mùi"        # Giáp–Kỷ hợp, all seven hóa conditions met
TONG1 = "Mậu Tuất / Tân Dậu / Ất Dậu / Bính Tuất"      # Ất with no Mộc/Thủy anywhere
SAVED = "Tân Sửu / Đinh Dậu / Giáp Thìn / Quý Dậu"     # Thương kiến Quan with Ấn (Quý) present


def view(name_or_text: str, days=None) -> ChartView:
    return ChartView.from_names(EX.get(name_or_text, name_or_text), days_into_month=days)

THUC_SAT = "Bính Tý / Canh Dần / Giáp Tuất / Giáp Tý"       # Bính (Thực Thần) kề Canh (Thất Sát)
TAI_AN = "Kỷ Hợi / Nhâm Thân / Giáp Tý / Bính Dần"        # Kỷ (Chính Tài) kề Nhâm (Thiên Ấn)
