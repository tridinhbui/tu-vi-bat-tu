"""Personal Growth & Life Guidance layer. Sits ON TOP of the computed charts; never changes a calculation, a rule or another endpoint.

Every insight carries three explicitly separated layers:
  bieu_tuong  what the traditional symbol says (with a book page when one exists, otherwise marked 'phổ thông' or 'hệ thống'),
  tam_ly      a psychology concept placed NEXT TO the symbol as a hypothesis to test on oneself (the chart proves nothing about it),
  doi_song    what it looks like in ordinary life, with a reflection question, a situation and a 7–30 day practice.
No predictions, no decisions taken for the reader, no LLM. Journal data never reaches the server's storage (requests are stateless).

Feature flag: TVBT_GROWTH=1 (default OFF). With the flag off the /api/growth/* endpoints answer 404 and nothing here is imported elsewhere.
"""
from __future__ import annotations

import os


def enabled() -> bool:
    return os.environ.get("TVBT_GROWTH", "").strip().lower() in ("1", "true", "on", "yes")
