# AI for PM — Project Plan Starter Pack

A Claude plugin that turns a messy project — scattered tasks in Monday.com, ClickUp, Jira, Asana, Linear, or a spreadsheet — into a premium-editorial, client-ready project plan package in three synchronised formats.

Companion to the [Benjamin Vermeulen](https://benjaminvermeulen.substack.com) Substack, specifically the article *Using Claude Cowork to Generate a Client Project Plan From Your PM Tool*.

---

## What it produces

Given a structured project brief (or live data pulled via an MCP connector), the skill generates three artefacts that tell the same story across PowerPoint, HTML, and Excel:

| Artefact                | PMBOK domain           | Excel sheet     | HTML section                 | PowerPoint slide             |
|-------------------------|------------------------|-----------------|------------------------------|------------------------------|
| Cover + project identity| Planning               | Overview hero   | Hero                         | Cover                        |
| Executive snapshot      | Measurement            | Overview cards  | Snapshot cards + status quote| Executive snapshot           |
| Timeline overview       | Planning, Delivery     | Gantt (top)     | SVG Gantt (phase rows)       | Timeline overview            |
| Detail Gantt            | Planning, Measurement  | Gantt (tasks)   | SVG Gantt (task rows)        | Detail Gantt                 |
| Milestone tracker       | Measurement            | Milestones      | Milestone timeline + cards   | Milestones                   |
| Next 14 days            | Delivery               | —               | —                            | Next fortnight               |
| Review needed (flags)   | Delivery               | Review needed   | Review needed (conditional)  | Review needed (conditional)  |
| Handover / closing      | —                      | —               | Footer                       | Handover                     |

All three formats share the same data source, so the numbers never drift between views.

---

## What's new in this build

The package has been narrowed and sharpened:

- **Narrower scope.** WBS, RACI, and risk register are removed. The focus is Gantt + milestones + status — the "where is the project at?" story a client actually wants.
- **Premium editorial design.** Every artefact uses a shared visual language: one accent colour, Georgia/Calibri (or Fraunces/Inter for HTML), generous white space, desaturated status chips. Principles in `references/visual-design-principles.md`.
- **Per-client branding.** Supply a primary colour, an accent colour, and an optional logo in the plan JSON. The rest of the palette derives automatically. No design work required per client.
- **Shape-based PPTX.** Every visual is built from rectangles, rounded rectangles, lines, and text boxes — no PowerPoint tables, no auto-format surprises.
- **Inline SVG Gantt.** The HTML Gantt is vector-sharp at any size and prints cleanly.

---

## Install

Requires Claude Code or Claude Cowork with plugin support.

```bash
/plugin marketplace add benno-v/ai-pm-project-plan
/plugin install ai-pm-project-plan
```

Once installed, the `project-plan-generator` skill is available. Trigger it with:

> *"Generate a client-ready project plan from my Monday.com board."*
> *"Build a Gantt and milestone tracker for the Acme renovation."*
> *"Turn this project brief into a plan deck and workbook for the client."*

---

## How it works

1. **You describe the project** — from a brief, an MCP-connected tool, or a pasted task list.
2. **The skill builds a structured `plan` object** — project identity, brand, phases, tasks, milestones, and optional flags.
3. **It proposes the plan** — surfaces assumptions and review-needed flags before generating files.
4. **Three generators run** — `generate_xlsx.py`, `generate_html.py`, `generate_pptx.py`, all sharing one palette module (`brand.py`).
5. **You get three files in your workspace folder.** Open the Excel for the full dataset, the HTML for a browser view, the PowerPoint for the client meeting.

Validation checkpoints run before generation — every task has a matching phase, milestones pass the three-test rule, at-risk milestones have matching flag entries, nothing internal is marked client-visible.

---

## Sample output

The `assets/sample-outputs/` folder contains a fully-generated sample for a fictional *Acme HQ Office Renovation* project:

- `sample-plan.json` — the structured `plan` object that drives generation
- `sample-project-plan.xlsx` — Excel workbook (Overview, Gantt, Milestones, Review needed)
- `sample-project-plan.html` — self-contained HTML, opens offline
- `sample-project-plan.pptx` — 8-slide premium-editorial deck
- `acme-logo.png` — placeholder logo showing per-client branding

Open any of these files to see what the skill produces.

---

## Brand customisation

Everything is driven by two colours and an optional logo, specified in the plan JSON:

```json
"brand": {
  "primary":       "#0B2545",
  "accent":        "#C49A3A",
  "display_font":  "Georgia",
  "body_font":     "Calibri"
},
"project": {
  "logo_path": "acme-logo.png"
}
```

Only the two colours are needed. The rest of the palette — tints, shades, neutrals, status colours — is derived automatically by `scripts/brand.py`. Fonts are optional and format-specific (PPTX/XLSX default to Georgia + Calibri; HTML defaults to Fraunces + Inter via Google Fonts).

The logo is optional. If supplied, it appears in the PPTX footer on every slide, in the HTML hero + footer, and near cell F2 on the Excel Overview sheet. If no logo is supplied, the artefacts still render cleanly.

See `skills/project-plan-generator/references/brand-system.md` for the full derivation rules and per-format placement.

---

## Running the generators directly

Outside of Claude, you can run the generators against any plan JSON file:

```bash
python scripts/generate_xlsx.py --plan plan.json --out plan.xlsx
python scripts/generate_html.py --plan plan.json --out plan.html
python scripts/generate_pptx.py --plan plan.json --out plan.pptx
python scripts/recalc.py plan.xlsx   # optional — bakes cached formula values
```

Dependencies:

```bash
pip install openpyxl python-pptx Pillow
```

`recalc.py` additionally requires LibreOffice on your path. It is optional — Excel will recalculate formulas on first open.

---

## PMBOK 8th Edition alignment

The skill anchors to three PMBOK 8 performance domains: Planning, Measurement, and Delivery. The other five — Stakeholders, Team, Development approach, Project work, Uncertainty — are intentionally out of scope here; they belong in separate artefacts (stakeholder register, resource plan, charter, internal tools, risk register).

The mapping and rationale are documented in `skills/project-plan-generator/references/pmbok-mapping.md`. This skill produces **client-facing plan artefacts**, not an all-in-one governance bundle.

---

## What the skill deliberately does not do

- **Work breakdown structure.** The plan groups tasks into phases, not a multi-level WBS. If you need a formal WBS with charge codes, use a different artefact.
- **RACI matrix.** Tasks carry an `owner_role`, not a full responsibility map.
- **Risk register.** Issues that need client action surface as `flags`; the internal risk register is managed elsewhere.
- **Cost management.** No budgets, earned value, or cost tracking.
- **Dependency arrows on the Gantt.** `depends_on` is captured in the data but not visualised yet.

Ask for one of these and the skill will flag the gap rather than fake the output.

---

## File structure

```
ai-pm-project-plan/
├── .claude-plugin/
│   └── marketplace.json               # Plugin registry entry
├── skills/
│   └── project-plan-generator/
│       ├── SKILL.md                   # Skill entry point
│       ├── references/
│       │   ├── gantt-layout.md        # Plan JSON schema + Gantt rules
│       │   ├── milestone-tracker.md   # Milestone conventions
│       │   ├── pmbok-mapping.md       # Three-domain mapping
│       │   ├── brand-system.md        # Palette + font + logo derivation
│       │   └── visual-design-principles.md  # Editorial design principles
│       └── scripts/
│           ├── brand.py               # Shared palette + logo module
│           ├── generate_html.py       # Self-contained HTML
│           ├── generate_pptx.py       # Shape-based PPTX
│           ├── generate_xlsx.py       # Editorial Excel
│           └── recalc.py              # Optional formula bake
├── assets/
│   └── sample-outputs/                # Acme renovation sample
│       ├── sample-plan.json
│       ├── sample-project-plan.html
│       ├── sample-project-plan.pptx
│       ├── sample-project-plan.xlsx
│       └── acme-logo.png
├── LICENSE                            # MIT
└── README.md                          # This file
```

---

## Credits

Built by [Benjamin Vermeulen] — PMP.

Part of the *AI for Project Managers* content ecosystem. If you find this useful, the full walkthrough lives on Substack: [Benjamin Vermeulen](https://benjaminvermeulen.substack.com).

Issues, suggestions, and pull requests welcome.

---

## License

MIT — see [LICENSE](./LICENSE).
