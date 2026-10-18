"""Deep interpretation (synthesis) engine. Sits ON TOP of the existing rule engine; never replaces it.

Feature flag: environment variable TVBT_DEEP_INTERPRETATION=1 (default OFF). With the flag off nothing here is imported by the
production endpoints, and the new endpoint answers 404, so existing API output is byte-identical.
"""
from __future__ import annotations

import os


def enabled() -> bool:
    return os.environ.get("TVBT_DEEP_INTERPRETATION", "").strip().lower() in ("1", "true", "on", "yes")
