# PMBOK 8th Edition — performance-domain mapping

This skill anchors its artefacts to PMBOK 8th Edition performance domains. The mapping is what makes the output defensible in professional PM contexts — a PMP-certified PM receiving the plan can see the discipline behind the structure.

The narrowed scope (Gantt + milestones + flags) maps to three of the eight performance domains cleanly. The others are still relevant to the project but are addressed elsewhere — in separate artefacts, the status report, or the stakeholder plan.

## The three in-scope domains

### Planning

PMBOK defines the planning domain as "activities and functions associated with the initial, ongoing, and evolving organisation and co-ordination necessary for delivering the project's deliverables and outcomes." This skill addresses planning in two concrete ways:

- **Phases.** The `phases` array is the high-level planning structure — the chunks of work the project team has agreed to deliver in sequence. It is not a WBS, and it does not need to be exhaustive. Its job is to give the client a clear mental model of where the project is in its arc.
- **Tasks with dependencies.** The task schema includes `depends_on` so the dependency network is captured even if the current generators don't visualise it. The dependency data lives in the plan and is preserved across updates.

Planning questions this artefact answers: *What order are we doing things in? When does each chunk start and end? What depends on what?*

### Measurement

PMBOK frames measurement as "activities and functions associated with assessing project performance and taking appropriate actions to maintain acceptable performance." Every visual in this skill serves measurement:

- **Progress fill.** Each task bar's accent-coloured fill shows duration-weighted progress at a glance.
- **Overall complete.** The snapshot card aggregates duration-weighted progress into one headline number.
- **Today marker.** The vertical rule on the Gantt lets the reader see schedule performance without maths — anything to the left of the line that isn't filled is slipping.
- **Milestone achievement ratio.** The "Milestones achieved" snapshot card communicates delivery cadence against the plan.

These four signals together give a client what PMBOK calls a *performance measurement baseline* read-out without requiring any formal variance reporting.

### Delivery

PMBOK's delivery domain is about "the requirements, scope, and quality required to produce the project deliverables." This skill addresses the delivery domain through:

- **Phase progress rollup.** Each phase bar on the timeline-overview slide carries an aggregated completion percentage so the client can see delivery health per phase.
- **Next 14 days slide.** Surfaces what the client should expect to land in the upcoming fortnight — a rolling delivery commitment window.
- **Flags.** The "Review needed" section is how delivery risks escalate into the conversation. Each flag names a decision the client or sponsor needs to take to keep the deliverable on track.

## The five out-of-scope domains

| Domain          | Why it's out of scope here                                                       | Where it should live                                                                     |
|-----------------|----------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Stakeholders    | Plan is client-facing, not stakeholder management data.                          | Separate stakeholder register and engagement plan.                                       |
| Team            | The plan uses `owner_role`, not named resources, by design.                      | RACI / resource plan lives in a separate document.                                       |
| Development approach & life cycle | Plan assumes a predictive or hybrid approach; the skill does not enforce it.    | Project charter.                                                                         |
| Project work    | Day-to-day work management is the PM's concern, not the client's.                | Monday.com / ClickUp / Jira — wherever operational tracking lives.                       |
| Uncertainty     | Risks are intentionally not in the client-facing plan — they surface only as flags. | Risk register managed internally, with summaries reported via the status report narrative. |

This separation is deliberate. Client plans that try to do everything — schedule, RACI, risks, stakeholder analysis — end up communicating nothing. This skill picks three domains, does them well, and trusts other artefacts to cover the rest.

## How to use the mapping in practice

When a stakeholder asks *"where's the RACI?"* or *"where are the risks?"*, the answer is not "we removed those" — it's "those live in the internal governance pack, not in the client artefact." The client plan's job is to tell a story about schedule, progress, and the decisions needed next. PMBOK supports exactly that separation through the concept of tailoring: the same performance domains are addressed, but via the artefact most fit for the audience.

## Validation checkpoint

Before shipping a plan:

- The three in-scope domains (Planning, Measurement, Delivery) should each be visibly addressed in at least one slide or section.
- The five out-of-scope domains should not be forced into the artefact — their absence is intentional and defensible.
- If a flag exists, it should name the specific decision the client needs to take, not just describe the issue.

This alignment is what separates a one-off Gantt from a client-ready plan built on a defensible methodology.
