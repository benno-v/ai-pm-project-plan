# Changelog

All notable changes to this plugin are documented here.

## 1.1.0 (2026-10-11)

### Added

- **PDF output.** New `scripts/generate_pdf.py` renders the HTML page's print stylesheet to a print-quality PDF, A4 landscape by default (`--size`/`--orientation` flags support Letter and portrait). Tries WeasyPrint, then headless Chrome/Chromium (`--print-to-pdf`), then LibreOffice (converts the PPTX deck) in order, and fails with a clear message if none are available.
- **Milestones on the schedule.** The HTML SVG Gantt, the PPTX Timeline overview and Detail Gantt slides, and the XLSX Gantt sheet all now draw milestones as status-coloured diamonds directly on the timeline, with collision-aware date labels, instead of only on their own dedicated tracker.
- **`tests/test_generators.py`.** A stdlib `unittest` smoke-test suite that generates all four formats from the sample plan and checks that milestones render as markers on each schedule.
- **`CHANGELOG.md`.** This file.

### Changed

- **Dependency-free, responsive HTML.** The HTML output no longer loads Google Fonts or any other CDN by default; it uses a system font stack, with `brand.web_fonts: true` as an opt-in for Fraunces/Inter. The layout is responsive from about 600px wide up to full desktop, with the Gantt and milestone timeline scrolling horizontally rather than compressing into illegible text.
- **Compact PDF pagination.** The print layout packs the hero, snapshot cards, and status quote onto page one; scales the full Gantt to fit one landscape page, with every month visible and nothing clipped; and flows milestones and review-needed flags after, instead of stranding section headings alone on near-empty pages.
- **Fixed overlapping text in the Gantt.** Task name/owner captions and the TODAY marker label could overlap neighbouring text at certain dates; both are now spaced to never collide.
- Updated `SKILL.md` and the reference docs to describe four synchronised outputs instead of three, and to require confirming every requested format was actually generated before finishing.

## 1.0.0

- Initial release: premium-editorial project plan package (Gantt chart, milestone tracker, status snapshot) in three synchronised formats (Excel, interactive HTML, PowerPoint), driven by a single plan JSON and a shared brand palette module.
