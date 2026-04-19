#!/usr/bin/env python3
"""
Recalculate formulas inside a .xlsx file by opening it in headless LibreOffice.

Why this exists
---------------
`openpyxl` writes formulas as strings into the file. When Excel (or the online
Excel viewer used in Cowork) opens the file, it evaluates them on load — but
if a tool or script reads the .xlsx straight after generation using a pure
Python parser, the cached values will be empty.

For deliverables handed straight to a client, we recalc once so every cell
has a cached value baked in. This also guarantees that the conditional
formatting kicks off correctly on first open without a manual re-save.

Usage
-----
    python recalc.py path/to/file.xlsx

Requires a LibreOffice install on the PATH (soffice or libreoffice).
Falls back to a no-op (and exits 0) if LibreOffice is not available — Excel
will recalculate on open, so the file is still valid, just without cached
values.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _find_soffice() -> str | None:
    for candidate in ("soffice", "libreoffice"):
        path = shutil.which(candidate)
        if path:
            return path
    # Common macOS install path
    mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if Path(mac_path).exists():
        return mac_path
    return None


def recalc(xlsx_path: Path) -> int:
    if not xlsx_path.exists():
        print(f"File not found: {xlsx_path}", file=sys.stderr)
        return 2

    soffice = _find_soffice()
    if not soffice:
        print(
            "LibreOffice not found — skipping recalc. "
            "Excel will evaluate formulas on first open.",
            file=sys.stderr,
        )
        return 0

    with tempfile.TemporaryDirectory() as tmpdir:
        # Convert to xlsx in-place via headless LibreOffice. The --convert-to
        # xlsx flag re-saves and forces formula evaluation.
        cmd = [
            soffice,
            "--headless",
            "--calc",
            "--convert-to", "xlsx",
            "--outdir", tmpdir,
            str(xlsx_path),
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            print("LibreOffice recalc timed out after 120s.", file=sys.stderr)
            return 3

        if result.returncode != 0:
            print(
                f"LibreOffice exited {result.returncode}.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}",
                file=sys.stderr,
            )
            return result.returncode

        converted = Path(tmpdir) / xlsx_path.name
        if not converted.exists():
            print(
                f"LibreOffice did not produce the expected output: {converted}",
                file=sys.stderr,
            )
            return 4

        # Overwrite the original with the recalculated file
        shutil.copy2(converted, xlsx_path)
        print(f"Recalculated: {xlsx_path}")
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Recalculate .xlsx formulas via headless LibreOffice.")
    parser.add_argument("xlsx", help="Path to the .xlsx file to recalculate")
    args = parser.parse_args(argv)

    return recalc(Path(args.xlsx))


if __name__ == "__main__":
    raise SystemExit(main())
