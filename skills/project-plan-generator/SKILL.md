---
name: project-plan-generator
description: Generate a premium-editorial, client-ready project plan package — Gantt chart, milestone tracker, and status snapshot — in four synchronised formats (Excel .xlsx, interactive HTML, PowerPoint .pptx, PDF). Use this skill whenever a project manager asks for a project plan, Gantt chart, milestone tracker, client-ready schedule, or a "where is the project at?" update artefact. Trigger when the user wants to turn a brief, a Monday.com / ClickUp / Jira / Asana / Linear board, or an unstructured list of tasks into a clean, client-facing project plan. Trigger when the user mentions "project plan starter pack", "client project plan", or references the T11 article on using Claude Cowork to generate a client project plan.
license: MIT. LICENSE in plugin root has complete terms.
---

# Project Plan Generator

## Purpose

Produce a premium-editorial project plan package from a structured brief or live PM-tool data. One skill, four artefacts, one consistent visual language across every format. Built so a project manager can go from a Monday.com board (or a written brief) to a client-ready status update in under fifteen minutes, with validation built in.

This skill is opinionated. It enforces a single project plan structure anchored to three PMBOK 8th Edition performance domains — Planning, Measurement, Delivery — so every plan tells the same kind of story: where we are, where we're going, and what needs a decision. Change the project, not the structure.

## When to use

Trigger this skill when the user says any of the following (non-exhaustive):

- "Create a project plan for [project]"
- "Generate a Gantt chart for this work"
- "Pull the current data from my Monday.com board and produce a client project plan"
- "Make me a project plan in Excel / HTML / PowerPoint / PDF"
- "I need a client-ready version of this schedule"
- "Use the Project Plan Starter Pack"
- "Turn this brief into a full project plan package"
- "Give the client an update on where the project is at"

A request for "a project plan" defaults to the full package — all four formats, generated in parallel, driven by a single plan JSON. A request that explicitly asks for PDF always includes `generate_pdf.py` in that run.

Do not trigger for general project-management advice, status reports, programme governance, RACI matrices, WBS hierarchies, risk registers, or stakeholder communications. Those live in other skills or artefacts. This skill produces **client-facing plan artefacts**: a Gantt-led story of the schedule, the milestones, and anything that needs a decision.

## Required inputs

Before generating anything, confirm the following are available. If any are missing, ask the user for them before producing a single artefact.

**Project identity.** Project name, client name (if client-facing), project manager name, start date, planned end date, and the status-as-of date for the TODAY marker.

**Task data.** One of:

- A Monday.com / ClickUp / Jira / Asana / Linear board or project, accessed via its MCP connector.
- A structured list of tasks the user provides (with names, durations, dependencies, owners).
- A brief the user wants you to decompose into phases and tasks — in which case, propose the phase structure first and get approval before generating any other artefact.

**Scope rules (for client-facing plans).** What the client should see and what must be excluded (internal names, time estimates, internal comments, items tagged "Internal Only", etc.). If the user has not supplied these, ask. Set `client_visible: false` on any task or milestone that must not ship to the client.

**Brand inputs (optional but recommended).** A primary hex colour, an accent hex colour, a logo file path, and optional display/body font names. If nothing is supplied, fall back to the editorial default (deep navy `#0B2545`, warm gold `#C49A3A`, Georgia + Calibri). Note the absence in your summary to the user.

**Output scope.** Which formats to produce. Default: all four (xlsx, HTML, pptx, PDF). Honour the user's scoping if they narrow it to one format — but if they ask for PDF, always produce PDF, never substitute HTML or PPTX for it.

## Outputs

Four synchronised artefacts, all driven by the same plan JSON:

**PowerPoint (.pptx).** 16:9 premium-editorial deck. Slides: Cover, Executive snapshot, Timeline overview, Detail Gantt, Milestones, Next 14 days, Review needed (only if `flags` has entries), Handover. Every slide carries a muted footer with optional logo, project signature, and page counter. All visuals are shape-based (no tables) for pixel control. The Timeline overview and Detail Gantt slides both carry a dedicated milestones row — every milestone renders as a status-coloured diamond directly on the schedule, not just on its own slide.

**HTML (single-file).** Self-contained, dependency-free page — no Google Fonts or other CDN by default (pure system font stack; set `brand.web_fonts: true` to opt into Fraunces/Inter), so it renders identically offline and inside sandboxed preview iframes that block external requests. Responsive from ~600px wide up to full desktop: the SVG Gantt and milestone timeline scroll horizontally rather than compressing text into illegibility, snapshot cards and milestone cards reflow at narrow widths, and labels sit outside short bars so nothing overlaps. Sections: hero + snapshot cards, status pull-quote, SVG Gantt (with its own milestones row — diamonds on the schedule, coloured by status, with collision-avoided date labels), milestone timeline + cards, review needed (conditional), footer. Carries a `@media print` stylesheet (A4 landscape by default) that `generate_pdf.py` reuses. Logo embedded as base64. Opens directly in any browser.

**Excel (.xlsx).** Editorial-quality workbook for PMs who want to dig into the data. Sheets: Overview (hero + snapshot cards), Gantt (weekly Monday-aligned columns with progress fills, TODAY marker, and a "Milestones" block at the top of the schedule — one row per milestone with a ◆ marker dropped into its week column, plus a cell comment with the full name/date), Milestones (status-chipped table), Review needed (only if `flags` has entries). Gridlines off, generous row heights, Calibri body.

**PDF (.pdf).** Print-quality render of the HTML page's `@media print` stylesheet — same Gantt, same milestones, same brand — defaulting to A4 landscape (`--size`/`--orientation` flags support Letter/portrait). Tries WeasyPrint first, falls back to headless Chrome/Chromium `--print-to-pdf`, then to LibreOffice converting the PPTX deck (lower-fidelity: 16:9, not A4/Letter) if neither is available. Fails loudly with install instructions if none of the three are present — it never silently skips the PDF.

All four are driven by `assets/sample-outputs/sample-plan.json`, which is also the authoritative schema reference — see `references/gantt-layout.md`.

**If the user asks for PDF in any form, always run `generate_pdf.py`** — do not substitute HTML or PPTX and call it done. Before finishing, explicitly confirm every format the user actually asked for was generated and written to disk (not just that the command exited 0).

## How to run

The four generators live in `scripts/` and share the `brand.py` palette module:

```bash
python scripts/generate_pptx.py --plan plan.json --out plan.pptx
python scripts/generate_html.py --plan plan.json --out plan.html
python scripts/generate_xlsx.py --plan plan.json --out plan.xlsx
python scripts/generate_pdf.py  --plan plan.json --out plan.pdf   # --size A4|Letter --orientation landscape|portrait
```

Each generator is independently runnable — pass the same `plan.json` to all four and you get four views of the same plan. `generate_pdf.py` internally renders the same HTML that `generate_html.py` produces, so there's nothing extra to regenerate first.

Dependencies:

```bash
pip install python-pptx>=0.6.21 openpyxl>=3.1 Pillow>=10 weasyprint>=60
```

`weasyprint` is the preferred PDF renderer and the only dependency with a native-library footprint (Pango/Cairo). If it can't be installed in the environment, `generate_pdf.py` falls back automatically to a Chrome/Chromium binary already on PATH, then to a LibreOffice (`soffice`) binary — install whichever is available. No other third-party packages are needed for HTML — it's pure Python string templating with an inline SVG Gantt.

## Workflow

1. **Gather inputs.** Confirm project identity, task data source, scope rules, brand inputs.
2. **Build the plan JSON.** Either hand-authored or pulled from an MCP-connected board. Validate against the schema in `references/gantt-layout.md`.
3. **Assign owners as roles.** Use "Architect", "Contractor", "PM" — not named people. Keeps the plan portable across staffing changes.
4. **Review milestones.** Every milestone must pass the three-test rule in `references/milestone-tracker.md`: zero-duration, externally observable, decision-worthy. Aim for 6–10 per project.
5. **Set flags.** For any at-risk milestone or task, add a `flags` entry naming the decision the client needs to take.
6. **Run the requested generators.** Default is all four (`generate_pptx.py`, `generate_html.py`, `generate_xlsx.py`, `generate_pdf.py`) against the same plan JSON; honour the user's scoping if they narrow it. If PDF was requested in any form, run `generate_pdf.py` — never substitute another format for it.
7. **Confirm delivery.** Before telling the user you're done, check that every format they asked for actually exists on disk (non-zero size) — not just that the generator command exited without error. Put the files in the client workspace and link via `computer://` URLs.

## PMBOK alignment

The narrowed scope maps cleanly to three PMBOK 8th Edition performance domains: Planning (phases + dependency data), Measurement (progress fills + today marker + snapshot cards), and Delivery (phase rollups + next 14 days + flags). The other five domains — Stakeholders, Team, Development approach, Project work, Uncertainty — are intentionally out of scope; they belong in other artefacts. See `references/pmbok-mapping.md` for the full breakdown.

## Validation checkpoints

Before delivering to a client, check:

- **Phase coverage.** Every task has a `phase_id` that matches a phase in `phases`.
- **Date sanity.** No task ends before it starts; no phase contains tasks outside its span.
- **Progress realism.** Progress values align with where TODAY sits on each bar. A task that's 50% of the way through in time should not be at 5% progress without a corresponding flag.
- **Milestone discipline.** Every milestone passes the three-test rule; at-risk milestones have matching flag entries.
- **Client visibility.** Nothing internal is marked `client_visible: true`.
- **Brand sanity.** Primary and accent colours have enough contrast; display font is installed on the rendering machine (or one of the fonts bundled by the format).
- **Format delivery.** Every format the user asked for was actually generated and written to disk — check file existence, not just a clean exit code. If PDF was requested, confirm `generate_pdf.py` ran (not a substitute format) and note which renderer it used (WeasyPrint / Chrome / LibreOffice fallback).

## References

- `references/gantt-layout.md` — the plan JSON schema and Gantt rendering rules.
- `references/milestone-tracker.md` — what qualifies as a milestone and how they render.
- `references/pmbok-mapping.md` — the three-domain mapping and what's intentionally out of scope.
- `references/brand-system.md` — how colours, fonts, and the logo flow through all four formats.
- `references/visual-design-principles.md` — the premium-editorial principles the artefacts obey.

## AI limitations to flag

When using this skill, the following caveats apply and should be flagged honestly to the user:

- **The generators do not draw dependency arrows** yet. `depends_on` is stored in the plan but not visualised — the Gantt shows sequence through dates, not explicit arrows.
- **Progress is not recalculated from dates.** The `progress` field is taken verbatim from the plan. If you pull data from a PM tool, make sure the tool's progress field is accurate before generating.
- **Fonts are rendered as-installed.** If the display font you specify is not available on the reader's machine, the format will substitute. HTML defaults to a system font stack (no webfont download) for portability; set `brand.web_fonts: true` if you want Fraunces/Inter loaded from Google Fonts instead, at the cost of an external dependency.
- **The logo is never validated.** If the supplied file is too large or off-brand, the artefacts won't notice — that check is on the PM.
- **Human oversight is required on status.** Claude can generate the plan, but the status values, progress fractions, and flag reasons need a human PM's judgement before they ship to a client.

Never present a generated plan as final without a PM review pass.
