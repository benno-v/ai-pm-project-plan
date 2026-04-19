"""
Shared brand utilities for the project-plan-generator skill.

Purpose
-------
One source of truth for the editorial palette and logo handling so that
the Excel, HTML, and PowerPoint generators always speak the same visual
language. The plan JSON ships two colour inputs — primary and accent —
and an optional display + body font. Everything else (tints, shades,
status colours, ink, rules, backgrounds) is derived here.

Design language
---------------
Premium editorial. Muted off-white background, large display type,
generous white space, and accent colour used sparingly — progress fills,
today marker, key numbers, nothing else. Status tones (ok / warn / risk)
are desaturated so the deck does not read like a traffic light.

Public API
----------
- ``Palette``              : NamedTuple bundling every colour + font.
- ``derive_palette(...)``  : primary + accent + (fonts) -> Palette.
- ``resolve_logo(...)``    : absolute path to a logo file if it exists,
                             otherwise None (so generators just skip it).
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple, Optional


class Palette(NamedTuple):
    # Brand
    primary: str
    primary_dark: str
    primary_soft: str
    accent: str
    accent_soft: str

    # Typography tones
    ink: str          # body headings / primary text
    ink_soft: str     # secondary text
    ink_faint: str    # muted / captions
    ink_mute: str     # extremely muted (watermark-level)

    # Structure
    rule: str         # visible borders
    hairline: str     # subtle dividers
    page: str         # page background
    card: str         # card / callout background
    wash: str         # subtle section wash

    # Status
    ok: str
    ok_soft: str
    warn: str
    warn_soft: str
    risk: str
    risk_soft: str

    # Typography
    display_font: str
    body_font: str


# ---------------------------------------------------------------------------
# Colour maths
# ---------------------------------------------------------------------------

def _normalise_hex(value: str | None, fallback: str) -> str:
    """Return a string in the form ``#RRGGBB``.

    Accepts input with or without leading ``#``. Collapses 3-digit shorthand.
    Falls back to ``fallback`` if ``value`` is None/empty/invalid.
    """
    if not value:
        return fallback.upper() if fallback.startswith("#") else f"#{fallback.upper()}"
    s = str(value).strip().lstrip("#")
    if len(s) == 3 and all(c in "0123456789abcdefABCDEF" for c in s):
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6 or not all(c in "0123456789abcdefABCDEF" for c in s):
        return fallback.upper() if fallback.startswith("#") else f"#{fallback.upper()}"
    return f"#{s.upper()}"


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = rgb
    return "#{:02X}{:02X}{:02X}".format(
        max(0, min(255, int(round(r)))),
        max(0, min(255, int(round(g)))),
        max(0, min(255, int(round(b)))),
    )


def _blend(hex_a: str, hex_b: str, t: float) -> str:
    """Linear blend ``t`` from ``hex_a`` toward ``hex_b``."""
    ra, ga, ba = _hex_to_rgb(hex_a)
    rb, gb, bb = _hex_to_rgb(hex_b)
    return _rgb_to_hex((ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t))


def _darken(hex_str: str, t: float) -> str:
    return _blend(hex_str, "#000000", t)


def _lighten(hex_str: str, t: float) -> str:
    return _blend(hex_str, "#FFFFFF", t)


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

DEFAULT_PRIMARY = "#0B2545"   # deep navy — the editorial default
DEFAULT_ACCENT = "#C49A3A"    # warm muted gold

DEFAULT_DISPLAY_FONT_PPTX = "Georgia"             # serif, widely installed
DEFAULT_BODY_FONT_PPTX = "Calibri"                # sans, default on Windows/Mac

DEFAULT_DISPLAY_FONT_HTML = "Fraunces"            # Google serif, editorial
DEFAULT_BODY_FONT_HTML = "Inter"                  # Google sans

DEFAULT_FONT_XLSX = "Calibri"                     # Excel-safe


def derive_palette(
    primary: str | None = None,
    accent: str | None = None,
    display_font: str | None = None,
    body_font: str | None = None,
) -> Palette:
    """Turn primary + accent (hex) into a full editorial palette.

    ``display_font`` and ``body_font`` are pass-through strings — each
    generator chooses sensible defaults if they are None.
    """
    primary_hex = _normalise_hex(primary, DEFAULT_PRIMARY)
    accent_hex = _normalise_hex(accent, DEFAULT_ACCENT)

    return Palette(
        primary=primary_hex,
        primary_dark=_darken(primary_hex, 0.30),
        primary_soft=_lighten(primary_hex, 0.90),
        accent=accent_hex,
        accent_soft=_lighten(accent_hex, 0.82),
        ink="#1A1A1A",
        ink_soft="#4A4A4A",
        ink_faint="#8A8A8A",
        ink_mute="#BFBFBF",
        rule="#D9D9D9",
        hairline="#EFEFEF",
        page="#FFFFFF",
        card="#FAFAF7",
        wash="#F3F1EC",
        ok="#3F7A52",
        ok_soft="#E9F1EC",
        warn="#AE7A2A",
        warn_soft="#F7EFDF",
        risk="#8E2F2F",
        risk_soft="#F1E3E3",
        display_font=display_font or DEFAULT_DISPLAY_FONT_PPTX,
        body_font=body_font or DEFAULT_BODY_FONT_PPTX,
    )


def resolve_logo(logo_path: str | None, plan_file: Path | None = None) -> Optional[Path]:
    """Resolve a logo path from the plan JSON.

    Lookup order:
    1. Absolute path — used directly if it exists.
    2. Relative to the plan JSON file's directory (most common case).
    3. Relative to the current working directory.

    Returns ``None`` if no logo is configured or the file cannot be found —
    generators should treat None as "skip the logo".
    """
    if not logo_path:
        return None

    p = Path(str(logo_path)).expanduser()
    if p.is_absolute() and p.exists():
        return p.resolve()

    if plan_file is not None:
        candidate = (Path(plan_file).parent / p).resolve()
        if candidate.exists():
            return candidate

    cwd_candidate = (Path.cwd() / p).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    return None
