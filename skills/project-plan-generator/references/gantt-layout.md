# Gantt layout and plan schema

This skill produces three synchronised views of the same plan: a PowerPoint deck, an interactive HTML page, and an Excel workbook. All three are driven by one JSON object — the `plan` — so the schema below is the source of truth. If a field is missing the generators fall back to sensible defaults rather than error out, but you should aim to supply everything.

## Top-level shape

```json
{
  "project":        { ... },
  "brand":          { ... },
  "status_summary": "...",
  "phases":         [ ... ],
  "tasks":          [ ... ],
  "milestones":     [ ... ],
  "flags":          [ ... ]
}
```

Every top-level key except `project`, `phases`, `tasks`, and `milestones` is optional.

## `project`

```json
{
  "name":          "Acme HQ Office Renovation",
  "client":        "Acme Corp",
  "pm":            "Benjamin Vermeulen",
  "start":         "2026-03-02",
  "end":           "2026-09-25",
  "status_as_of":  "2026-04-19",
  "generated":     "2026-04-19",
  "logo_path":     "acme-logo.png"
}
```

| Field          | Notes                                                                   |
|----------------|-------------------------------------------------------------------------|
| `name`         | Appears on the cover slide, HTML hero, and every Excel sheet title.     |
| `client`       | Used in the eyebrow above the project name and in the footer.           |
| `pm`           | Printed on the cover and the closing slide's contact card.              |
| `start`, `end` | ISO dates (`YYYY-MM-DD`). Define the outer Gantt span.                  |
| `status_as_of` | ISO date. Drives the TODAY marker on every Gantt and the 14-day window. |
| `generated`    | Optional. Printed in the HTML and Excel footer as "generated on".       |
| `logo_path`    | Optional. Relative to the plan JSON file, or an absolute path.          |

## `brand`

```json
{
  "primary":       "#0B2545",
  "accent":        "#C49A3A",
  "display_font":  "Georgia",
  "body_font":     "Calibri"
}
```

Only two colours are needed. The rest of the palette — tints, shades, status colours, neutrals — is derived automatically from these two. Fonts are optional and per-format (see `references/brand-system.md`).

## `phases`

Phases group tasks. Keep them at a level the client will recognise — typically 3 to 6 per project.

```json
[
  { "id": "P1", "name": "Design & Permits",       "start": "2026-03-02", "end": "2026-05-01" },
  { "id": "P2", "name": "Demolition & Structural","start": "2026-05-04", "end": "2026-06-19" }
]
```

| Field          | Notes                                                        |
|----------------|--------------------------------------------------------------|
| `id`           | Short stable handle. Referenced by tasks via `phase_id`.     |
| `name`         | Displayed on the timeline-overview slide and in Excel.       |
| `start`, `end` | ISO dates. Normally the min/max of the child tasks.          |

## `tasks`

```json
{
  "id":           "T04",
  "name":         "Permit applications",
  "phase_id":     "P1",
  "owner_role":   "Permit Consultant",
  "start":        "2026-04-06",
  "end":          "2026-04-30",
  "duration_days": 19,
  "status":       "at_risk",
  "progress":     0.55,
  "is_milestone": false,
  "client_visible": true,
  "depends_on":   ["T03"]
}
```

| Field            | Notes                                                                 |
|------------------|-----------------------------------------------------------------------|
| `id`             | Short stable handle.                                                  |
| `name`           | Plain English — no acronyms the client wouldn't recognise.            |
| `phase_id`       | Must match an `id` in `phases`. Drives grouping and sort order.       |
| `owner_role`     | Role, not person (e.g. "Architect", "Contractor", "PM"). Keeps the plan portable across staffing changes. |
| `start`, `end`   | ISO dates.                                                            |
| `duration_days`  | Working days. Used to weight the overall progress calculation.        |
| `status`         | See status vocabulary below.                                          |
| `progress`       | Float 0.0 to 1.0.                                                     |
| `is_milestone`   | Reserve for zero-duration markers. Full milestones go in the `milestones` array — this flag only exists so you can mark a task like "Client approval" that collapses to a diamond on the Gantt. |
| `client_visible` | When false the task is dropped from client artefacts (but still counted in progress maths). |
| `depends_on`     | Array of task `id`s. Currently read-only — the generators don't draw dependency arrows yet. |

### Status vocabulary

The generators colour bars and chips from a small controlled vocabulary:

| Status        | Used for                                             | Visual                       |
|---------------|------------------------------------------------------|------------------------------|
| `done`        | Completed tasks.                                     | Accent fill, faded label.    |
| `in_progress` | Active work, on track.                               | Primary fill.                |
| `not_started` | Future work.                                         | Neutral fill, no progress.   |
| `at_risk`     | Slipping but recoverable.                            | Warm soft fill.              |
| `slipping`    | Same treatment as `at_risk`.                         | Warm soft fill.              |
| `delayed`     | Missed its window.                                   | Risk soft fill.              |
| `blocked`     | Waiting on a dependency.                             | Risk soft fill.              |
| `cancelled`   | Descoped.                                            | Muted / faint.               |

## `milestones`

```json
{
  "id":            "M03",
  "name":          "Permits approved",
  "date":          "2026-04-30",
  "status":        "at_risk",
  "owner_role":    "Permit Consultant",
  "description":   "City sign-off on building and mechanical permits.",
  "client_visible": true
}
```

Milestones have their own slide, their own HTML timeline dots, and their own Excel sheet. They use the same status vocabulary as tasks — achieved milestones get the ok (green) chip; pending ones get on-track or at-risk.

## `flags`

```json
[
  {
    "scope":  "milestones",
    "ref":    "M03",
    "reason": "Permit sign-off is trending five working days behind..."
  }
]
```

Flags surface as a "Review needed" section — an extra slide in PPTX and a warning card in HTML. The slide is omitted entirely if the `flags` array is empty. Use flags sparingly: each one should be a genuine decision the client needs to make.

| Field    | Notes                                                                 |
|----------|-----------------------------------------------------------------------|
| `scope`  | Either `"tasks"` or `"milestones"` — which array the `ref` points at. |
| `ref`    | The `id` of the task or milestone the flag is attached to.            |
| `reason` | Short paragraph. Written directly to the client — no jargon.          |

## Generator behaviours

All three generators share these behaviours:

**Weekly Monday alignment.** Gantt grids align to Monday of the project's first week and run through Monday on or after the last task's end. This keeps weeks readable across long projects.

**Today marker.** A vertical rule in the accent colour is drawn at `status_as_of`. If `status_as_of` falls outside the project span it is clamped to the edge.

**Progress fill.** The completed portion of each task bar is filled in the accent colour; the remainder uses a soft neutral or, for at-risk work, a warm soft fill. The progress fraction is taken from the `progress` field verbatim — it is not recalculated from dates.

**Duration-weighted overall progress.** The "overall complete" headline is the sum of `duration_days × progress` divided by the sum of `duration_days`. Zero-duration tasks and milestones are excluded.

**Next milestone.** The snapshot card picks the first milestone on or after `status_as_of` that has not been achieved. If every remaining milestone is in the past it falls back to the earliest non-achieved one.

**Graceful degradation.** If `phases` is empty, the timeline-overview slide renders a short notice instead of crashing. The same applies to empty `tasks` and empty `milestones`.
