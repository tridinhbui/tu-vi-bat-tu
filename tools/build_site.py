"""Regenerates the static content pages (engine/web/bai-viet, gioi-thieu, hoi-dap, xem-ngay, sitemap.xml, robots.txt) and the PWA icons
from the project's sourced data. Run after changing rule packs, claims_vi.json, glossary_vi.json or dignity_kb.json:
    .venv/bin/python tools/build_site.py [--origin https://example.com]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
from tvbt import icons, sitegen  # noqa: E402

if "--origin" in sys.argv:
    sitegen.ORIGIN = sys.argv[sys.argv.index("--origin") + 1].rstrip("/")
n = sitegen.write(sitegen.render())
k = icons.write()
print(f"{n} pages, {k} icons")
