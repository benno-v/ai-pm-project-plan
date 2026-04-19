---
name: project-plan-generator
description: Generate a premium-editorial, client-ready project plan package — Gantt chart, milestone tracker, and status snapshot — in three synchronised formats (Excel .xlsx, interactive HTML, PowerPoint .pptx). Use this skill whenever a project manager asks for a project plan, Gantt chart, milestone tracker, client-ready schedule, or a "where is the project at?" update artefact. Trigger when the user wants to turn a brief, a Monday.com / ClickUp / Jira / Asana / Linear board, or an unstructured list of tasks into a clean, client-facing project plan. Trigger when the user mentions "project plan starter pack", "client project plan", or references the T11 article on using Claude Cowork to generate a client project plan.
license: MIT. LICENSE in plugin root has complete terms.
---

# Project Plan Generator

## Purpose

Produce a premium-editorial project plan package from a structured brief or live PM-tool data. One skill, three artefacts, one consistent visual language across every format. Built so a project manager can go from a Monday.com board (or a written brief) to a client-ready status update in under fifteen minutes, with validation built in.

This skill is opinionated. It enforces a single project plan structure anchored to three PMBOK 8th Edition performance domains — Planning, Measurement, Delivery — so every plan tells the same kind of story: where we are, where we're going, and what needs a decision. Change the project, not the structure.

## When to use

Trigger this skill when the user says any of the following (non-exhaustive):

- "Create a project plan for [project]"
- "Generate a Gantt chart for this work"
- "Pull the current data from my Monday.com board and produce a client project plan"
- "Make me a project plan in Excel / HTML / PowerPoint"
- "I need a client-ready version of this schedule"
- "Use the Project Plan Starter Pack"
- "Turn this brief into a full project plan package"
- "Give the client an update on where the project is at"

A request for "a project plan" defaults to the full package — all three formats, generated in parallel, driven by a single plan JSON.

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

**Output scope.** Which formats to produce. Default: all three (xlsx, HTML, pptx). Honour the user's scoping if they narrow it to one format.

## Outputs

Three synchronised artefacts, all driven by the same plan JSON:

**PowerPoint (.pptx).** 16:9 premium-editorial deck. Slides: Cover, Executive snapshot, Timeline overview, Detail Gantt, Milestones, Next 14 days, Review needed (only if `flags` has entries), Handover. Every slide carries a muted footer with optional logo, project signature, and page counter. All visuals are shape-based (no tables) for pixel control.

**HTML (single-file).** Self-contained, print-friendly, interactive-ready page. Sections: hero + snapshot cards, status pull-quote, SVG Gantt, milestone timeline + cards, review needed (conditional), footer. Loads Google Fonts via CDN; logo embedded as base64. Opens directly in any browser.

**Excel (.xlsx).** Editorial-quality workbook for PMs who want to dig into the data. Sheets: Overview (hero + snapshot cards), Gantt (weekly Monday-aligned columns with progress fills and TODAY marker), Milestones (status-chipped table), Review needed (only if `flags` has entries). Gridlines off, generous row heights, Calibri body.

All three are driven by `assets/sample-outputs/sample-plan.json`, which is also the authoritative schema reference — see `references/gantt-layout.md`.

## How to run

The three generators live in `scripts/` and share the `brand.py` palette module:

```bash
python scripts/generate_pptx.py --plan plan.json --out plan.pptx
python scripts/generate_html.py --plan plan.json --out plan.html
python scripts/generate_xlsx.py --plan plan.json --out plan.xlsx
```

Each generator is independently runnable — pass the same `plan.json` to all three and you get three views of the same plan.

Dependencies:

```bash
pip install python-pptx>=0.6.21 openpyxl>=3.1 Pillow>=10
```

No other third-party packages are needed — the HTML generator is pure Python string templating with an inline SVG Gantt.

## Workflow

1. **Gather inputs.** Confirm project identity, task data source, scope rules, brand inputs.
2. **Build the plan JSON.** Either hand-authored or pulled from an MCP-connected board. Validate against the schema in `references/gantt-layout.md`.
3. **Assign owners as roles.** Use "Architect", "Contractor", "PM" — not named people. Keeps the plan portable across staffing changes.
4. **Review milestones.** Every milestone must pass the three-test rule in `references/milestone-tracker.md`: zero-duration, externally observable, decision-worthy. Aim for 6–10 per project.
5. **Set flags.** For any at-risk milestone or task, add a `flags` entry naming the decision the client needs to take.
6. **Run all three generators.** Pass the plan JSON to `generate_pptx.py`, `generate_html.py`, and `generate_xlsx.py`.
7. **Deliver.** Put the three files in the client workspace and link via `computer://` URLs.

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

## References

- `references/gantt-layout.md` — the plan JSON schema and Gantt rendering rules.
- `references/milestone-tracker.md` — what qualifies as a milestone and how they render.
- `references/pmbok-mapping.md` — the three-domain mapping and what's intentionally out of scope.
- `references/brand-system.md` — how colours, fonts, and the logo flow through the three formats.
- `references/visual-design-principles.md` — the premium-editorial principles the artefacts obey.

## AI limitations to flag

When using this skill, the following caveats apply and should be flagged honestly to the user:

- **The generators do not draw dependency arrows** yet. `depends_on` is stored in the plan but not visualised — the Gantt shows sequence through dates, not explicit arrows.
- **Progress is not recalculated from dates.** The `progress` field is taken verbatim from the plan. If you pull data from a PM tool, make sure the tool's progress field is accurate before generating.
- **Fonts are rendered as-installed.** If the display font you specify is not available on the reader's machine, the format will substitute. For bulletproof portability across clients, stick to the defaults (Georgia / Calibri / Fraunces / Inter).
- **The logo is never validated.** If the supplied file is too large or off-brand, the artefacts won't notice — that check is on the PM.
- **Human oversight is required on status.** Claude can generate the plan, but the status values, progress fractions, and flag reasons need a human PM's judgement before they ship to a client.

Never present a generated plan as final without a PM review pass.
