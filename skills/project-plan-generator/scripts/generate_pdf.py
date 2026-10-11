#!/usr/bin/env python3
"""
Generate a print-quality PDF of the project plan from a ``plan`` JSON file.

Approach
--------
The PDF is a print render of the same self-contained HTML page produced by
``generate_html.py`` — same Gantt, same milestones, same brand — using its
``@media print`` stylesheet (A4 landscape by default). Three renderers are
tried in order, so the PDF works on whatever happens to be installed:

  1. **WeasyPrint** (``pip install weasyprint``) — pure-Python, no browser
     needed, the preferred path.
  2. **Headless Chrome/Chromium** (``--print-to-pdf``) — used if WeasyPrint
     isn't installed but a Chrome-family browser is on PATH.
  3. **LibreOffice** (``soffice --convert-to pdf``) — last resort, converts
     the PPTX deck instead of the HTML page, so the result is the 16:9 deck
     layout rather than A4/Letter.

If none of the three are available, the script fails with a clear message
naming what's missing and how to install it — it never silently skips the
PDF.

Usage
-----
    python generate_pdf.py --plan plan.json --out plan.pdf
    python generate_pdf.py --plan plan.json --out plan.pdf --size letter --orientation portrait
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from brand import derive_palette  # noqa: E402
import generate_html  # noqa: E402

# The default @page rule baked into generate_html's print stylesheet — we
# swap it out verbatim when the caller asks for a different size/orientation
# rather than threading new parameters through generate_html's own API.
_DEFAULT_PAGE_RULE = "@page { size: A4 landscape; margin: 12mm; }"

_CHROME_CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
]


def _build_html(plan: dict[str, Any], plan_path: Path, size: str, orientation: str) -> str:
    brand = plan.get("brand", {})
    pal = derive_palette(
        primary=brand.get("primary"),
        accent=brand.get("accent"),
        display_font=brand.get("display_font"),
        body_font=brand.get("body_font"),
    )
    html = generate_html.generate_html(plan, plan_path, pal)
    page_rule = f"@page {{ size: {size.upper()} {orientation}; margin: 12mm; }}"
    return html.replace(_DEFAULT_PAGE_RULE, page_rule)


def _render_via_weasyprint(html: str, out_path: Path) -> None:
    import weasyprint  # type: ignore

    weasyprint.HTML(string=html).write_pdf(str(out_path))


def _find_chrome() -> str | None:
    for name in _CHROME_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    return None


def _render_via_chrome(html: str, out_path: Path) -> None:
    chrome = _find_chrome()
    if not chrome:
        raise RuntimeError("no Chrome/Chromium binary found on PATH")
    with tempfile.TemporaryDirectory() as td:
        html_path = Path(td) / "plan.html"
        html_path.write_text(html, encoding="utf-8")
        pdf_path = Path(td) / "plan.pdf"
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            "--virtual-time-budget=10000",
            f"file://{html_path}",
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode != 0 or not pdf_path.exists():
            raise RuntimeError(
                f"chrome --print-to-pdf failed (exit {result.returncode}): "
                f"{result.stderr.decode(errors='replace')[:500]}"
            )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(pdf_path, out_path)


def _render_via_libreoffice(plan: dict[str, Any], plan_path: Path, out_path: Path) -> None:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("no LibreOffice (soffice) binary found on PATH")

    import generate_pptx  # noqa: E402  (imported lazily — only needed on this fallback path)

    with tempfile.TemporaryDirectory() as td:
        pptx_path = Path(td) / "plan.pptx"
        generate_pptx.build_deck(plan, plan_path, pptx_path)

        cmd = [soffice, "--headless", "--convert-to", "pdf", "--outdir", td, str(pptx_path)]
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        converted = Path(td) / "plan.pdf"
        if result.returncode != 0 or not converted.exists():
            raise RuntimeError(
                f"soffice --convert-to pdf failed (exit {result.returncode}): "
                f"{result.stderr.decode(errors='replace')[:500]}"
            )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(converted, out_path)


def build_pdf(plan: dict[str, Any], plan_path: Path, out_path: Path,
              size: str = "A4", orientation: str = "landscape") -> str:
    """Render the PDF, returning the name of the renderer that succeeded.

    Raises ``RuntimeError`` with a message listing every renderer tried and
    why each one failed, plus install instructions, if all three fail.
    """
    html = _build_html(plan, plan_path, size, orientation)
    errors: list[str] = []

    for name, fn in (
        ("weasyprint", lambda: _render_via_weasyprint(html, out_path)),
        ("chrome", lambda: _render_via_chrome(html, out_path)),
    ):
        try:
            fn()
            return name
        except Exception as e:  # noqa: BLE001 — collect and try the next renderer
            errors.append(f"  - {name}: {e}")

    try:
        _render_via_libreoffice(plan, plan_path, out_path)
        return "libreoffice (converted from the PPTX deck — 16:9, not A4/Letter)"
    except Exception as e:  # noqa: BLE001
        errors.append(f"  - libreoffice: {e}")

    raise RuntimeError(
        "Could not generate a PDF — none of the supported renderers are available:\n"
        + "\n".join(errors)
        + "\n\nInstall one of:\n"
        "  pip install weasyprint\n"
        "  (or install Google Chrome / Chromium)\n"
        "  (or install LibreOffice — lower-fidelity fallback, converts the PPTX)"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate the project-plan PDF.")
    p.add_argument("--plan", required=True, help="Path to the plan JSON file")
    p.add_argument("--out", required=True, help="Path to the output .pdf file")
    p.add_argument("--size", default="A4", choices=["A4", "Letter", "a4", "letter"],
                   help="Page size (default: A4)")
    p.add_argument("--orientation", default="landscape",
                   choices=["landscape", "portrait"],
                   help="Page orientation (default: landscape)")
    args = p.parse_args(argv)

    plan_path = Path(args.plan)
    out_path = Path(args.out)
    with open(plan_path, "r") as f:
        plan = json.load(f)

    try:
        renderer = build_pdf(plan, plan_path, out_path, args.size, args.orientation)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1

    print(f"Wrote {out_path} (via {renderer})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
