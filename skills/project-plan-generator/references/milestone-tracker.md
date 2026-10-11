# Milestones — rules and conventions

Milestones are the drumbeat of the project. They anchor the Gantt, they drive the client conversation, and they are the measurement layer of the plan. Get them right and the plan tells a story; get them wrong and the plan is just a list of tasks.

## What qualifies as a milestone

Three tests, and a milestone needs to pass all three:

1. **Zero-duration marker.** A milestone is a moment, not a piece of work. If it has a duration, it is a task. "Permits approved" is a milestone. "Prepare permit application" is a task.
2. **Externally observable.** Someone outside the delivery team should be able to verify it happened. Signed contract. Site handed over. Client approval received. Internal to-dos don't make the cut.
3. **Decision-worthy.** The milestone should represent a point where the project can be reviewed, paused, accelerated, or killed. If nothing would change on the basis of the milestone, it is not a milestone — it is just a date.

A practical rule of thumb: aim for one milestone per phase, plus start and finish. For a six-month project that's usually 6 to 10 milestones total. More than that and the tracker becomes noise; fewer than that and the plan looks empty.

## PMBOK alignment

PMBOK 8th Edition treats milestones as part of the *Measurement* performance domain — they are the mechanism by which the project is known to be on track. That alignment shapes two conventions:

- **Name milestones as outcomes, not activities.** "Concept design approved" over "Approve concept design". The name is a state, not a verb.
- **Status reflects the approval state, not the activity state.** A milestone is either `achieved` or it isn't. Pending milestones can be `on_track` or `at_risk` based on the state of the work feeding into them.

## Status vocabulary

Milestones use the same status vocabulary as tasks, with two caveats:

- `achieved` is the completion terminal state (tasks use `done`).
- `at_risk` is the critical one to flag — it means the milestone is trending to be missed unless something changes. If a milestone is `at_risk`, it should also appear in `flags` so it surfaces on the "Review needed" slide.

Valid statuses: `achieved`, `on_track`, `at_risk`, `slipping`, `delayed`, `blocked`, `cancelled`.

## How milestones render

Each format shows milestones twice: once drawn directly on the schedule (so the Gantt alone tells the milestone story), and once in a dedicated milestone view with full names, descriptions, and status chips.

**PowerPoint** — the Timeline overview and Detail Gantt slides both carry a "Milestones" row with every in-range milestone drawn as a diamond coloured by status; date labels stagger above/below to avoid collisions, and a label is dropped (diamond only) rather than overlapping a neighbour in a dense cluster. There's also a dedicated "Milestone tracker" slide: a horizontal track plots every milestone as a dot coloured by status, with up to six feature cards below showing name, date, description, and status chip. The latest achieved milestone anchors the feature set, with upcoming milestones filling the rest.

**HTML** — the SVG Gantt has its own "Milestones" row at the top, diamonds at scale coloured by status with the same collision-avoidance as PowerPoint (a `<title>` tooltip always carries the full name/date/status, even when the label is dropped). Below the Gantt, the milestone timeline track runs across the full width (horizontally scrollable on narrow viewports) with dots at scale; each milestone also appears as a card in a grid below, with the same status chip and description.

**Excel** — the "Gantt" sheet opens with a "Milestones" block: one row per milestone, with a ◆ marker dropped into its week column (plus a cell comment carrying the full name/date/status) so milestones read on the same weekly grid as the tasks. There's also a dedicated "Milestones" sheet: a six-column table — ID, name, date, status (as a coloured chip cell), owner role, description — sorted chronologically.

## Writing good milestone descriptions

A milestone description should give the client enough context to know what is being signed off — no more than two sentences. Write it assuming the reader won't remember the preceding conversation.

Good: *"City sign-off on building and mechanical permits. Currently five working days behind the target date."*

Bad: *"Permits signed off per schedule."* (No content, no context.)

Bad: *"The City of Cape Town, after reviewing the submissions made under application reference 2026/B/0342, will issue the formal permit documents to the Permit Consultant by close of business..."* (Too long — this goes in the status report, not the milestone description.)

## The flag rule

If a milestone is `at_risk`, `slipping`, `delayed`, or `blocked`, it should have a matching entry in `flags`. The flag reason is the plain-English explanation of what needs to change and when.

Rationale: the milestone field alone tells the client *that* something is wrong. The flag tells them *what to do about it*. Separate fields, separate jobs.

## Validation checkpoint

Before handing a plan to a client, check:

- Every milestone passes all three qualifying tests above.
- Every milestone name is an outcome, not an activity.
- No milestone is more than one sentence of description.
- Every at-risk milestone has a matching flag entry.
- The number of milestones is within the 6–10 band for a typical project.

Milestones are the one part of the plan the client will actually remember between reviews. Treat them accordingly.
