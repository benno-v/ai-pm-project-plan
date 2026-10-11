#!/usr/bin/env python3
"""
Generate the self-contained HTML output for a project plan.

The HTML is premium editorial — large serif display type, generous white
space, muted off-white background, restrained accent colour, and a single
SVG-based Gantt chart so the artefact stays vector-sharp at any zoom.

The file is fully self-contained and dependency-free: one .html that opens
offline in any modern browser, with no reliance on Google Fonts or any other
CDN (system font stack only, by default). It is also responsive from ~600px
up and carries a @media print stylesheet, which ``generate_pdf.py`` reuses
to render a print-quality PDF of the same page. Set ``brand.web_fonts: true``
in the plan JSON to opt into loading Fraunces/Inter from Google Fonts.

Usage
-----
    python generate_html.py --plan plan.json --out plan.html
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from brand import (  # noqa: E402
    derive_palette,
    resolve_logo,
    Palette,
    DEFAULT_DISPLAY_FONT_HTML,
    DEFAULT_BODY_FONT_HTML,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _days_between(a: date, b: date) -> int:
    return (b - a).days


def _fmt_long(d: date) -> str:
    return d.strftime("%d %B %Y")


def _fmt_short(d: date) -> str:
    return d.strftime("%d %b")


def _fmt_month(d: date) -> str:
    return d.strftime("%B %Y")


def _img_to_data_uri(path: Path) -> str | None:
    """Embed an image as a base64 data URI so the HTML stays self-contained."""
    try:
        mime, _ = mimetypes.guess_type(str(path))
        if mime is None:
            mime = "image/png"
        data = path.read_bytes()
        return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")
    except Exception:
        return None


def _status_meta(status: str) -> tuple[str, str]:
    """Return (display label, css class) for a task status."""
    return {
        "done":        ("Done",        "status-done"),
        "in_progress": ("In progress", "status-in-progress"),
        "at_risk":     ("At risk",     "status-at-risk"),
        "on_hold":     ("On hold",     "status-hold"),
        "not_started": ("Upcoming",    "status-upcoming"),
    }.get(status, ("—", "status-upcoming"))


def _milestone_meta(status: str) -> tuple[str, str]:
    return {
        "achieved": ("Achieved", "ms-achieved"),
        "on_track": ("On track", "ms-on-track"),
        "at_risk":  ("At risk",  "ms-at-risk"),
        "slipping": ("Slipping", "ms-at-risk"),
        "slipped":  ("Slipped",  "ms-slipped"),
        "delayed":  ("Delayed",  "ms-slipped"),
        "blocked":  ("Blocked",  "ms-slipped"),
    }.get(status, ("—", "ms-on-track"))


def _milestone_fill(status: str, pal: Palette) -> str:
    """Diamond/dot fill colour for a milestone status — shared by the Gantt row
    and the milestone timeline so the two read as one system."""
    return {
        "achieved": pal.ok,
        "on_track": pal.primary,
        "at_risk":  pal.warn,
        "slipping": pal.warn,
        "slipped":  pal.risk,
        "delayed":  pal.risk,
        "blocked":  pal.risk,
    }.get(status, pal.primary)


# ---------------------------------------------------------------------------
# CSS (editorial)
# ---------------------------------------------------------------------------

CSS_TEMPLATE = """
:root {{
  --primary: {primary};
  --primary-dark: {primary_dark};
  --primary-soft: {primary_soft};
  --accent: {accent};
  --accent-soft: {accent_soft};
  --ink: {ink};
  --ink-soft: {ink_soft};
  --ink-faint: {ink_faint};
  --ink-mute: {ink_mute};
  --rule: {rule};
  --hairline: {hairline};
  --page: {page};
  --card: {card};
  --wash: {wash};
  --ok: {ok};
  --ok-soft: {ok_soft};
  --warn: {warn};
  --warn-soft: {warn_soft};
  --risk: {risk};
  --risk-soft: {risk_soft};
  --font-display: {display_font_stack};
  --font-body: {body_font_stack};
}}

* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  font-family: var(--font-body);
  color: var(--ink);
  background: var(--wash);
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

.page {{
  max-width: 1120px;
  margin: 0 auto;
  padding: 80px 56px 120px;
  background: var(--page);
  box-shadow: 0 1px 0 var(--hairline), 0 40px 120px -60px rgba(0,0,0,0.12);
}}

/* --- Hero --- */
.hero {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 48px;
  padding-bottom: 40px;
  border-bottom: 1px solid var(--rule);
}}
.hero .meta {{ flex: 1; }}
.eyebrow {{
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 20px;
}}
.project-title {{
  font-family: var(--font-display);
  font-size: 56px;
  line-height: 1.04;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--ink);
  margin: 0 0 20px;
}}
.hero-sub {{
  font-family: var(--font-display);
  font-size: 18px;
  font-style: italic;
  color: var(--ink-soft);
  font-weight: 400;
  margin: 0;
}}
.hero .logo img {{
  max-height: 60px;
  max-width: 160px;
  opacity: 0.9;
}}

/* --- Snapshot cards --- */
.snapshot {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  margin: 56px 0 48px;
  border-top: 1px solid var(--hairline);
  border-bottom: 1px solid var(--hairline);
}}
.card {{
  padding: 28px 24px 24px;
  border-right: 1px solid var(--hairline);
}}
.card:last-child {{ border-right: 0; }}
.card .label {{
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 12px;
}}
.card .value {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 38px;
  letter-spacing: -0.02em;
  line-height: 1;
  color: var(--ink);
}}
.card.accent .value {{ color: var(--accent); }}
.card.primary .value {{ color: var(--primary); }}
.card .foot {{
  margin-top: 12px;
  font-size: 12px;
  color: var(--ink-faint);
}}

.health-pill {{
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.02em;
}}
.health-on-track {{ background: var(--ok-soft); color: var(--ok); }}
.health-at-risk  {{ background: var(--warn-soft); color: var(--warn); }}
.health-off-track {{ background: var(--risk-soft); color: var(--risk); }}

/* --- Status summary --- */
.summary {{
  margin: 48px 0 72px;
  padding: 40px 48px 40px 40px;
  background: var(--card);
  border-left: 3px solid var(--accent);
}}
.summary p {{
  font-family: var(--font-display);
  font-size: 22px;
  line-height: 1.5;
  font-style: italic;
  color: var(--ink);
  margin: 0;
  font-weight: 400;
}}

/* --- Section heading --- */
.section {{ margin: 72px 0; }}
.section-head {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 28px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--rule);
}}
.section-head h2 {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 28px;
  letter-spacing: -0.01em;
  color: var(--ink);
  margin: 0;
}}
.section-head .count {{
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-faint);
}}

/* --- SVG Gantt --- */
.gantt-wrap {{
  margin: 0 -8px;
  padding: 0 8px;
  overflow-x: auto;
}}
.gantt {{
  min-width: {gantt_min_width}px;
}}
.gantt svg {{ display: block; width: 100%; height: auto; }}
.gantt text.month {{
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 10px;
  letter-spacing: 0.14em;
  fill: var(--ink-soft);
  text-transform: uppercase;
}}
.gantt text.week {{
  font-family: var(--font-body);
  font-size: 9px;
  fill: var(--ink-mute);
}}
.gantt text.phase {{
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 10px;
  letter-spacing: 0.14em;
  fill: var(--primary-dark);
  text-transform: uppercase;
}}
.gantt text.task {{
  font-family: var(--font-body);
  font-size: 12px;
  fill: var(--ink);
}}
.gantt text.owner {{
  font-family: var(--font-body);
  font-size: 10px;
  fill: var(--ink-faint);
}}
.gantt text.today-label {{
  font-family: var(--font-body);
  font-weight: 700;
  font-size: 9px;
  letter-spacing: 0.14em;
  fill: var(--accent);
  text-transform: uppercase;
}}
.gantt text.ms-row-label {{
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 10px;
  letter-spacing: 0.14em;
  fill: var(--primary-dark);
  text-transform: uppercase;
}}
.gantt text.ms-label {{
  font-family: var(--font-body);
  font-size: 9px;
  fill: var(--ink-soft);
}}
.gantt .ms-diamond {{
  stroke: var(--page);
  stroke-width: 1;
}}

/* --- Milestones --- */
.milestones-timeline {{
  position: relative;
  overflow-x: auto;
  padding: 32px 4px 40px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--hairline);
}}
.timeline-dots {{
  position: relative;
  display: flex;
  gap: 4px;
  min-width: max-content;
}}
.timeline-dots::before {{
  content: "";
  position: absolute;
  left: 0; right: 0; top: 50%;
  height: 1px;
  background: var(--hairline);
}}
.dot {{
  position: relative;
  flex: 0 0 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}}
.dot .mark {{
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid var(--page);
  box-shadow: 0 0 0 1px var(--rule);
  margin: 8px 0;
}}
.dot.ms-achieved .mark {{ background: var(--ok); box-shadow: 0 0 0 1px var(--ok); }}
.dot.ms-on-track .mark {{ background: var(--primary); box-shadow: 0 0 0 1px var(--primary); }}
.dot.ms-at-risk .mark {{ background: var(--warn); box-shadow: 0 0 0 1px var(--warn); }}
.dot.ms-slipped .mark {{ background: var(--risk); box-shadow: 0 0 0 1px var(--risk); }}
.dot .date {{
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ink-faint);
}}
.dot .name {{
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--ink);
  margin-top: 4px;
  max-width: 112px;
  line-height: 1.25;
}}

.milestone-list {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 32px;
}}
.milestone-card {{
  padding: 20px 24px;
  border: 1px solid var(--hairline);
  background: var(--page);
}}
.milestone-card .row {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 8px;
}}
.milestone-card .title {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 18px;
  color: var(--ink);
}}
.milestone-card .when {{
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ink-faint);
}}
.milestone-card .desc {{
  font-size: 14px;
  color: var(--ink-soft);
  margin: 10px 0 14px;
}}
.chip {{
  display: inline-block;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  border-radius: 999px;
}}
.chip.ms-achieved {{ background: var(--ok-soft); color: var(--ok); }}
.chip.ms-on-track {{ background: var(--primary-soft); color: var(--primary-dark); }}
.chip.ms-at-risk  {{ background: var(--warn-soft); color: var(--warn); }}
.chip.ms-slipped  {{ background: var(--risk-soft); color: var(--risk); }}

/* --- Review needed --- */
.review {{
  padding: 28px 32px;
  border: 1px solid var(--warn);
  background: var(--warn-soft);
  margin-top: 48px;
}}
.review h3 {{
  font-family: var(--font-display);
  font-size: 20px;
  margin: 0 0 16px;
  color: var(--warn);
}}
.review ul {{ margin: 0; padding: 0; list-style: none; }}
.review li {{
  padding: 12px 0;
  border-top: 1px solid rgba(0,0,0,0.08);
  font-size: 14px;
  color: var(--ink);
}}
.review li:first-child {{ border-top: 0; }}
.review li .ref {{
  font-weight: 600;
  color: var(--warn);
  margin-right: 12px;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.12em;
}}

/* --- Footer --- */
footer {{
  margin-top: 96px;
  padding-top: 32px;
  border-top: 1px solid var(--rule);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  font-size: 12px;
  color: var(--ink-faint);
}}
footer .brand {{
  display: flex;
  align-items: center;
  gap: 16px;
}}
footer img {{
  max-height: 32px;
  max-width: 120px;
  opacity: 0.85;
}}

/* --- Responsive (down to ~600px) --- */
@media (max-width: 760px) {{
  .page {{ padding: 40px 20px 72px; }}
  .hero {{ flex-direction: column; gap: 20px; }}
  .project-title {{ font-size: 34px; }}
  .hero-sub {{ font-size: 15px; }}
  .snapshot {{ grid-template-columns: repeat(2, 1fr); }}
  .card {{ border-right: 1px solid var(--hairline); border-bottom: 1px solid var(--hairline); }}
  .card:nth-child(2n) {{ border-right: 0; }}
  .card .value {{ font-size: 28px; }}
  .summary {{ padding: 24px; }}
  .summary p {{ font-size: 17px; }}
  .section-head {{ flex-direction: column; align-items: flex-start; gap: 4px; }}
  .milestone-list {{ grid-template-columns: 1fr; }}
  footer {{ flex-direction: column; align-items: flex-start; gap: 8px; }}
}}

/* --- Print --- */
@media print {{
  body {{ background: var(--page); }}
  .page {{ box-shadow: none; max-width: 100%; padding: 10px 16px; }}

  /* Keep short, self-contained blocks from splitting across a page
     boundary — but don't force whole (possibly page-plus-tall) sections
     to avoid breaking, which strands headings alone on an otherwise
     empty page. */
  .card, .summary, .milestone-card, .dot, .review li {{
    break-inside: avoid;
  }}
  .hero, .snapshot {{ break-inside: avoid; }}

  /* One deliberate break before the schedule, so the Gantt always starts
     flush at the top of its own page instead of drifting part-way down
     whatever page it happened to land on. */
  .schedule-section {{ break-before: page; }}
  .milestones-section {{ break-before: page; }}

  .section {{ margin: 16px 0; }}
  .section-head {{ margin-bottom: 14px; padding-bottom: 8px; }}
  .summary {{ margin: 16px 0; padding: 20px 28px 20px 24px; }}
  .snapshot {{ margin: 24px 0; }}
  .review {{ margin-top: 12px; padding: 16px 24px; }}
  .review h3 {{ margin: 0 0 8px; }}
  footer {{ margin-top: 10px; padding-top: 8px; }}

  .gantt-wrap, .milestones-timeline {{ overflow: visible; }}
  .gantt {{ min-width: 0; }}
  /* Scale the whole Gantt — heading included — to fit one landscape page
     tall, so it's never clipped and never pushed to share a page with
     only part of itself visible. Width stays 100% (no horizontal
     clipping, every month stays visible); only the height is capped, and
     the SVG's own viewBox keeps everything in proportion. */
  .gantt svg {{ max-height: 64vh; width: auto; max-width: 100%; margin: 0 auto; }}

  .timeline-dots {{ min-width: 0; flex-wrap: wrap; }}
  @page {{ size: A4 landscape; margin: 10mm; }}
}}
"""


# ---------------------------------------------------------------------------
# SVG Gantt
# ---------------------------------------------------------------------------

# Layout constants for the SVG Gantt chart — all in user units (1:1 px).
SVG_WIDTH = 1008
LEFT_COL_W = 260
RIGHT_PAD = 16
TODAY_FLAG_H = 16  # dedicated strip above the month row for the TODAY pill,
                    # so it never collides with a month label
HEADER_MONTH_H = 22
HEADER_WEEK_H = 16
HEADER_TOTAL_H = TODAY_FLAG_H + HEADER_MONTH_H + HEADER_WEEK_H + 12
PHASE_ROW_H = 30
TASK_ROW_H = 34
BAR_H = 12
MS_ROW_H = 42
MS_DIAMOND = 6  # half-diagonal, in px
MS_LABEL_GAP = 10  # minimum horizontal gap between two labels in the same tier

# Minimum pixel width the Gantt is allowed to shrink to before the page's
# horizontal-scroll container kicks in, so text never has to compress below
# a readable size on narrow (e.g. 600px) viewports.
GANTT_MIN_WIDTH = SVG_WIDTH


def _layout_milestone_markers(
    milestones: list[dict[str, Any]], start: date, end: date, x_for,
) -> list[tuple[float, date, dict[str, Any], int | None]]:
    """Return (x, date, milestone, tier) for every in-range milestone.

    ``tier`` is 0 (label below the diamond), 1 (label above), or ``None`` —
    every milestone always gets its diamond, but if a cluster is so dense
    that neither tier has room for its date label without colliding with a
    neighbour, the label is dropped rather than left to overlap (the full
    name/date is still available via the diamond's tooltip, and in the
    milestone cards below).
    """
    points: list[tuple[float, date, dict[str, Any]]] = []
    for m in milestones:
        md = _parse_date(m["date"])
        if not (start <= md <= end):
            continue
        points.append((x_for(md), md, m))
    points.sort(key=lambda p: p[0])

    tier_right = [float("-inf"), float("-inf")]
    out: list[tuple[float, date, dict[str, Any], int | None]] = []
    for x, md, m in points:
        label_w = 10 + len(_fmt_short(md)) * 7.5
        half = label_w / 2
        if x - half >= tier_right[0] + MS_LABEL_GAP:
            tier = 0
        elif x - half >= tier_right[1] + MS_LABEL_GAP:
            tier = 1
        else:
            tier = None
        if tier is not None:
            tier_right[tier] = x + half
        out.append((x, md, m, tier))
    return out


def _fmt_svg(plan: dict[str, Any], pal: Palette) -> str:
    proj = plan["project"]
    tasks = plan.get("tasks", [])
    phases = plan.get("phases", [])
    milestones = plan.get("milestones", [])

    start = _parse_date(proj["start"])
    end = _parse_date(proj["end"])
    today = _parse_date(proj["status_as_of"])
    total_days = max(1, _days_between(start, end) + 1)

    ms_row_h = MS_ROW_H if milestones else 0

    chart_w = SVG_WIDTH - LEFT_COL_W - RIGHT_PAD

    # Precise height: header + optional milestones row + phase/task rows
    precise_h = HEADER_TOTAL_H + ms_row_h
    for ph in phases:
        precise_h += PHASE_ROW_H
        precise_h += TASK_ROW_H * sum(1 for t in tasks if t.get("phase_id") == ph["id"])
    svg_h = precise_h + 12

    def x_for(d: date) -> float:
        return LEFT_COL_W + (_days_between(start, d) / total_days) * chart_w

    def w_for(a: date, b: date) -> float:
        return max(2.0, (_days_between(a, b) + 1) / total_days * chart_w)

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {svg_h}" '
        f'preserveAspectRatio="xMidYMin meet" role="img" aria-label="Project Gantt chart">'
    )

    # Month + week axis
    month_cursor = date(start.year, start.month, 1)
    axis_y_month = TODAY_FLAG_H
    axis_y_week = TODAY_FLAG_H + HEADER_MONTH_H
    parts.append(
        f'<line x1="{LEFT_COL_W}" y1="{HEADER_TOTAL_H - 1}" '
        f'x2="{SVG_WIDTH - RIGHT_PAD}" y2="{HEADER_TOTAL_H - 1}" '
        f'stroke="{pal.rule}" stroke-width="1"/>'
    )

    while month_cursor <= end:
        next_month_start = (
            date(month_cursor.year + 1, 1, 1)
            if month_cursor.month == 12
            else date(month_cursor.year, month_cursor.month + 1, 1)
        )
        seg_start = max(month_cursor, start)
        seg_end = min(next_month_start - timedelta(days=1), end)
        if seg_end >= seg_start:
            x1 = x_for(seg_start)
            x2 = x_for(seg_end) + (w_for(seg_end, seg_end))  # include last day
            # Month label at x1, shortened (or dropped) when the visible
            # segment is too narrow, so it never runs past the chart edge.
            avail = min(x2, SVG_WIDTH - RIGHT_PAD) - x1 - 6
            label = _fmt_month(month_cursor).upper()
            if len(label) * 8.6 > avail:
                label = month_cursor.strftime("%b %y").upper()
            if len(label) * 8.6 > avail:
                label = month_cursor.strftime("%b").upper()
            if len(label) * 8.6 <= avail:
                parts.append(
                    f'<text x="{x1 + 4}" y="{axis_y_month + 14}" class="month">'
                    f'{escape(label)}</text>'
                )
            # Thin divider between months
            parts.append(
                f'<line x1="{x1}" y1="{axis_y_month + 2}" '
                f'x2="{x1}" y2="{HEADER_TOTAL_H - 1}" '
                f'stroke="{pal.hairline}" stroke-width="1"/>'
            )
        month_cursor = next_month_start

    # Weekly tick marks (Mondays)
    cur = start - timedelta(days=start.weekday())  # Monday of start's week
    while cur <= end:
        if cur >= start:
            x = x_for(cur)
            parts.append(
                f'<line x1="{x}" y1="{HEADER_TOTAL_H - 6}" x2="{x}" y2="{HEADER_TOTAL_H - 1}" '
                f'stroke="{pal.hairline}" stroke-width="1"/>'
            )
            # Only label every 2nd week to reduce clutter
            weeks_from_start = _days_between(start, cur) // 7
            if weeks_from_start % 2 == 0:
                parts.append(
                    f'<text x="{x + 2}" y="{HEADER_TOTAL_H - 6}" class="week">'
                    f'{cur.strftime("%d")}</text>'
                )
        cur += timedelta(days=7)

    # Milestones row — diamonds on their own dedicated row, drawn ON the
    # schedule rather than only in the separate milestone timeline below.
    y = HEADER_TOTAL_H
    if milestones:
        parts.append(
            f'<rect x="0" y="{y}" width="{SVG_WIDTH}" height="{ms_row_h}" fill="{pal.card}"/>'
        )
        parts.append(
            f'<text x="12" y="{y + ms_row_h - 10}" class="ms-row-label">MILESTONES</text>'
        )
        mid_y = y + ms_row_h / 2
        parts.append(
            f'<line x1="{LEFT_COL_W}" y1="{mid_y}" x2="{SVG_WIDTH - RIGHT_PAD}" y2="{mid_y}" '
            f'stroke="{pal.hairline}" stroke-width="1"/>'
        )
        for mx, md, m, tier in _layout_milestone_markers(milestones, start, end, x_for):
            fill = _milestone_fill(m.get("status", "on_track"), pal)
            points = (
                f"{mx},{mid_y - MS_DIAMOND} "
                f"{mx + MS_DIAMOND},{mid_y} "
                f"{mx},{mid_y + MS_DIAMOND} "
                f"{mx - MS_DIAMOND},{mid_y}"
            )
            label_svg = ""
            if tier is not None:
                label_y = mid_y + MS_DIAMOND + 13 if tier == 0 else mid_y - MS_DIAMOND - 7
                half_w = (10 + len(_fmt_short(md)) * 7.5) / 2
                lx = min(max(mx, LEFT_COL_W + half_w), SVG_WIDTH - RIGHT_PAD - half_w)
                label_svg = (
                    f'<text x="{lx}" y="{label_y}" text-anchor="middle" class="ms-label">'
                    f'{escape(_fmt_short(md))}</text>'
                )
            parts.append(
                f'<g><title>{escape(m.get("name", ""))} — {escape(_fmt_long(md))} '
                f'({escape(m.get("status", "on_track"))})</title>'
                f'<polygon class="ms-diamond" points="{points}" fill="{fill}"/>'
                f'{label_svg}</g>'
            )
        parts.append(
            f'<line x1="0" y1="{y + ms_row_h}" x2="{SVG_WIDTH}" y2="{y + ms_row_h}" '
            f'stroke="{pal.hairline}" stroke-width="1"/>'
        )
        y += ms_row_h

    # Rows
    for ph in phases:
        p_start = _parse_date(ph["start"])
        p_end = _parse_date(ph["end"])

        # Phase row — wash band
        parts.append(
            f'<rect x="0" y="{y}" width="{SVG_WIDTH}" height="{PHASE_ROW_H}" '
            f'fill="{pal.wash}"/>'
        )
        parts.append(
            f'<text x="12" y="{y + PHASE_ROW_H - 10}" class="phase">'
            f'{escape(ph["name"].upper())}</text>'
        )
        # Phase bar
        px = x_for(p_start)
        pw = w_for(p_start, p_end)
        parts.append(
            f'<rect x="{px}" y="{y + 8}" width="{pw}" height="{PHASE_ROW_H - 16}" '
            f'rx="2" ry="2" fill="{pal.primary_soft}" '
            f'stroke="{pal.primary}" stroke-opacity="0.45" stroke-width="1"/>'
        )
        y += PHASE_ROW_H

        phase_tasks = [t for t in tasks if t.get("phase_id") == ph["id"]]
        for t in phase_tasks:
            t_start = _parse_date(t["start"])
            t_end = _parse_date(t["end"])
            progress = float(t.get("progress", 0.0))
            status = t.get("status", "not_started")

            # Row hairline
            parts.append(
                f'<line x1="0" y1="{y + TASK_ROW_H}" x2="{SVG_WIDTH}" y2="{y + TASK_ROW_H}" '
                f'stroke="{pal.hairline}" stroke-width="1"/>'
            )

            # Task name + owner
            parts.append(
                f'<text x="24" y="{y + 15}" class="task">{escape(t["name"])}</text>'
            )
            parts.append(
                f'<text x="24" y="{y + TASK_ROW_H - 6}" class="owner">'
                f'{escape(t.get("owner_role", ""))}</text>'
            )

            # Bar background (rest) + progress fill
            bx = x_for(t_start)
            bw = w_for(t_start, t_end)
            bar_y = y + (TASK_ROW_H - BAR_H) / 2

            if status == "at_risk":
                rest_colour = pal.warn_soft
                done_colour = pal.warn
            elif status == "done":
                rest_colour = pal.ink_soft
                done_colour = pal.ink_soft
            else:
                rest_colour = pal.primary_soft
                done_colour = pal.accent

            parts.append(
                f'<rect x="{bx}" y="{bar_y}" width="{bw}" height="{BAR_H}" '
                f'rx="3" ry="3" fill="{rest_colour}"/>'
            )
            if progress > 0:
                done_w = max(1.0, bw * progress)
                parts.append(
                    f'<rect x="{bx}" y="{bar_y}" width="{done_w}" height="{BAR_H}" '
                    f'rx="3" ry="3" fill="{done_colour}"/>'
                )

            y += TASK_ROW_H

    # Today marker — the pill lives in its own strip above the month row so
    # it never overlaps a month label, and is horizontally clamped so it
    # never clips off the left/right edge of the chart.
    if start <= today <= end:
        tx = x_for(today)
        parts.append(
            f'<line x1="{tx}" y1="{TODAY_FLAG_H - 2}" x2="{tx}" y2="{svg_h - 6}" '
            f'stroke="{pal.accent}" stroke-width="1.5" stroke-dasharray="2 3"/>'
        )
        pill_w, pill_h = 46, 14
        cx = min(
            max(tx, LEFT_COL_W + pill_w / 2 + 2),
            SVG_WIDTH - RIGHT_PAD - pill_w / 2 - 2,
        )
        parts.append(
            f'<rect x="{cx - pill_w / 2}" y="1" width="{pill_w}" height="{pill_h}" '
            f'rx="7" ry="7" fill="{pal.accent_soft}"/>'
        )
        parts.append(
            f'<text x="{cx}" y="{pill_h - 2}" text-anchor="middle" class="today-label">TODAY</text>'
        )

    # Column divider between left pane and chart
    parts.append(
        f'<line x1="{LEFT_COL_W}" y1="0" x2="{LEFT_COL_W}" y2="{svg_h}" '
        f'stroke="{pal.hairline}" stroke-width="1"/>'
    )

    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

def _font_stack(display: str, body: str, web_fonts: bool) -> tuple[str, str]:
    """Return CSS font stacks for display + body fonts.

    No Google Fonts dependency by default — these are pure system-font
    stacks, so the page renders identically offline or inside a sandboxed
    preview iframe that blocks external requests. If ``web_fonts`` is
    explicitly enabled in ``brand``, "Fraunces"/"Inter" are added ahead of
    the system fallback (see the optional ``<link>`` tags in the page head).
    """
    display_lead = ['"Fraunces"'] if web_fonts else []
    body_lead = ['"Inter"'] if web_fonts else []
    display_stack = ", ".join(
        [f'"{display}"'] + display_lead + ['Georgia', '"Times New Roman"', "serif"]
    )
    body_stack = ", ".join(
        [f'"{body}"'] + body_lead +
        ["-apple-system", "BlinkMacSystemFont", '"Segoe UI"', "Helvetica", "Arial", "sans-serif"]
    )
    return display_stack, body_stack


def generate_html(plan: dict[str, Any], plan_path: Path, pal: Palette) -> str:
    proj = plan["project"]
    tasks = plan.get("tasks", [])
    milestones = plan.get("milestones", [])
    flags = plan.get("flags", [])

    # Aggregates
    total_progress = sum(float(t.get("progress", 0.0)) for t in tasks)
    pct_complete = round((total_progress / max(1, len(tasks))) * 100) if tasks else 0
    achieved = sum(1 for m in milestones if m.get("status") == "achieved")
    total_ms = len(milestones)
    at_risk_ms = sum(1 for m in milestones if m.get("status") == "at_risk")
    slipped_ms = sum(1 for m in milestones if m.get("status") == "slipped")

    if slipped_ms:
        health_label, health_class = "Off track", "health-off-track"
    elif at_risk_ms:
        health_label, health_class = "At risk", "health-at-risk"
    else:
        health_label, health_class = "On track", "health-on-track"

    brand = plan.get("brand", {})
    display_font = brand.get("display_font") or DEFAULT_DISPLAY_FONT_HTML
    body_font = brand.get("body_font") or DEFAULT_BODY_FONT_HTML
    web_fonts = bool(brand.get("web_fonts"))
    display_stack, body_stack = _font_stack(display_font, body_font, web_fonts)

    logo_path = resolve_logo(proj.get("logo_path"), plan_path)
    logo_uri = _img_to_data_uri(logo_path) if logo_path else None

    css = CSS_TEMPLATE.format(
        primary=pal.primary, primary_dark=pal.primary_dark, primary_soft=pal.primary_soft,
        accent=pal.accent, accent_soft=pal.accent_soft,
        ink=pal.ink, ink_soft=pal.ink_soft, ink_faint=pal.ink_faint, ink_mute=pal.ink_mute,
        rule=pal.rule, hairline=pal.hairline,
        page=pal.page, card=pal.card, wash=pal.wash,
        ok=pal.ok, ok_soft=pal.ok_soft,
        warn=pal.warn, warn_soft=pal.warn_soft,
        risk=pal.risk, risk_soft=pal.risk_soft,
        display_font_stack=display_stack,
        body_font_stack=body_stack,
        gantt_min_width=GANTT_MIN_WIDTH,
    )

    # Google Fonts are opt-in only (``brand.web_fonts: true``) — by default
    # the page depends on nothing outside the file itself, so it renders
    # correctly offline and inside sandboxed preview iframes that block
    # third-party requests.
    web_fonts_html = ""
    if web_fonts:
        web_fonts_html = (
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;'
            '9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap" '
            'rel="stylesheet">'
        )

    # Snapshot cards
    cards_html = f"""
      <div class="card accent">
        <div class="label">Overall complete</div>
        <div class="value">{pct_complete}%</div>
        <div class="foot">Across {len(tasks)} tasks</div>
      </div>
      <div class="card primary">
        <div class="label">Milestones</div>
        <div class="value">{achieved}<span style="font-size:24px;color:var(--ink-faint);"> / {total_ms}</span></div>
        <div class="foot">Achieved</div>
      </div>
      <div class="card">
        <div class="label">Schedule health</div>
        <div class="value"><span class="health-pill {health_class}">{health_label}</span></div>
        <div class="foot">{at_risk_ms} at risk • {slipped_ms} slipped</div>
      </div>
      <div class="card">
        <div class="label">Target handover</div>
        <div class="value">{_parse_date(proj['end']).strftime('%d %b')}</div>
        <div class="foot">{_parse_date(proj['end']).year}</div>
      </div>
    """

    # Hero + logo slot
    logo_hero_html = (
        f'<div class="logo"><img src="{logo_uri}" alt="{escape(proj.get("client", ""))} logo"/></div>'
        if logo_uri else ''
    )

    hero_html = f"""
    <section class="hero">
      <div class="meta">
        <div class="eyebrow">{escape(proj.get('client', ''))} — Project status</div>
        <h1 class="project-title">{escape(proj['name'])}</h1>
        <p class="hero-sub">Status as of {_fmt_long(_parse_date(proj['status_as_of']))}</p>
      </div>
      {logo_hero_html}
    </section>
    """

    # Status summary
    summary_html = f"""
    <section class="summary">
      <p>{escape(plan.get('status_summary', ''))}</p>
    </section>
    """

    # Schedule / Gantt
    svg = _fmt_svg(plan, pal)
    schedule_html = f"""
    <section class="section schedule-section">
      <div class="section-head">
        <h2>Schedule</h2>
        <span class="count">{len(tasks)} tasks · {len(plan.get('phases', []))} phases</span>
      </div>
      <div class="gantt-wrap"><div class="gantt">{svg}</div></div>
    </section>
    """

    # Milestone timeline
    timeline_dots = ""
    for m in milestones:
        label, css_class = _milestone_meta(m.get("status", "on_track"))
        timeline_dots += f"""
          <div class="dot {css_class}">
            <div class="date">{_parse_date(m['date']).strftime('%d %b')}</div>
            <div class="mark"></div>
            <div class="name">{escape(m['name'])}</div>
          </div>
        """

    milestone_cards = ""
    for m in milestones:
        label, css_class = _milestone_meta(m.get("status", "on_track"))
        milestone_cards += f"""
          <div class="milestone-card">
            <div class="row">
              <div class="title">{escape(m['name'])}</div>
              <div class="when">{_parse_date(m['date']).strftime('%d %b %Y')}</div>
            </div>
            <div class="desc">{escape(m.get('description', ''))}</div>
            <span class="chip {css_class}">{label}</span>
            <span style="margin-left:8px;font-size:12px;color:var(--ink-faint);">{escape(m.get('owner_role', ''))}</span>
          </div>
        """

    milestones_html = f"""
    <section class="section milestones-section">
      <div class="section-head">
        <h2>Milestones</h2>
        <span class="count">{achieved} achieved · {total_ms - achieved} ahead</span>
      </div>
      <div class="milestones-timeline">
        <div class="timeline-dots">{timeline_dots}</div>
      </div>
      <div class="milestone-list">{milestone_cards}</div>
    </section>
    """

    # Review needed
    review_html = ""
    if flags:
        items = "".join(
            f'<li><span class="ref">{escape(f.get("scope", ""))} · {escape(f.get("ref", ""))}</span>'
            f'{escape(f.get("reason", ""))}</li>'
            for f in flags
        )
        review_html = f"""
        <section class="review">
          <h3>Review needed before sending</h3>
          <ul>{items}</ul>
        </section>
        """

    # Footer
    footer_logo = (
        f'<img src="{logo_uri}" alt="{escape(proj.get("client", ""))} logo"/>'
        if logo_uri else ''
    )
    footer_html = f"""
    <footer>
      <div class="brand">
        {footer_logo}
        <span>Prepared by {escape(proj.get('pm', ''))}</span>
      </div>
      <div>Generated {escape(proj.get('generated', ''))}</div>
    </footer>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{escape(proj['name'])} — Project status</title>
{web_fonts_html}
<style>{css}</style>
</head>
<body>
<main class="page">
  {hero_html}
  <div class="snapshot">
    {cards_html}
  </div>
  {summary_html}
  {schedule_html}
  {milestones_html}
  {review_html}
  {footer_html}
</main>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate the project-plan HTML file.")
    p.add_argument("--plan", required=True, help="Path to the plan JSON file")
    p.add_argument("--out", required=True, help="Path to the output .html file")
    args = p.parse_args(argv)

    plan_path = Path(args.plan)
    out_path = Path(args.out)
    with open(plan_path, "r") as f:
        plan = json.load(f)

    brand = plan.get("brand", {})
    pal = derive_palette(
        primary=brand.get("primary"),
        accent=brand.get("accent"),
        display_font=brand.get("display_font"),
        body_font=brand.get("body_font"),
    )

    html = generate_html(plan, plan_path, pal)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
