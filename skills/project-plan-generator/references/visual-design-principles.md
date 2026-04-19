# Visual design principles

The three artefacts (PPTX, HTML, XLSX) share a visual language we call "premium editorial". The reference points are McKinsey client decks, Stripe's annual reports, and serious long-form magazines — not SaaS dashboards. Five principles carry the whole system.

## 1. One accent, used sparingly

Everything that isn't structural is ink (black), ink-soft (grey), or accent (the single brand colour the user supplied). That's it. The accent appears on:

- Progress fills on task bars.
- The today marker line.
- The eyebrow labels above section titles.
- Key numbers on snapshot cards.
- Milestone date labels on the next-14-days slide.

Nothing else gets the accent. Status chips use their own desaturated palette (ok / warn / risk). Phase bars use primary_soft, not accent. This discipline is what makes the accent feel like a brand signature rather than a highlighter.

## 2. Display type wants space around it

Headlines in this system are big. The cover slide title is 54pt. Section titles on content slides are 26pt. The HTML hero is 56px. These sizes only work when the type has room to breathe — so the layout gives them at least 20% of the available vertical space and never sets them closer than 32 pixels to any other element.

If a headline is fighting for space, it's a symptom that the slide is doing too much. Split it into two.

## 3. Italic is for voice, not decoration

Italic is reserved for:

- The status summary pull-quote.
- Secondary lines on snapshot cards ("Duration-weighted average").
- The project signature in the footer ("Acme Corp · Project plan · Status as of 19 April 2026").

Each of those is a direct voice — words from the PM to the client. Everything else — headlines, labels, body copy — is roman. This mirrors editorial convention, where italic carries meaning (speech, foreign terms, quoted voice) rather than being stylistic texture.

## 4. White space is a feature, not a failure

The page margins are generous by design — 0.6 inches on every side of a 13.33-inch slide is about 9% of the width. That's more than most business decks. The payoff is that every element on the slide has room, and the cumulative effect is calm.

The urge to fill white space should be resisted. A slide that shows three things well is worth more than a slide that shows six things poorly.

## 5. Status is a grammar, not a palette

Status colours (ok / warn / risk) are not used to *decorate* — they communicate a specific claim about the state of work. A green chip on a milestone card means "achieved or tracking to deliver". A warm chip means "needs attention". A red chip means "something is broken and we need to decide what to do about it".

Because the colours are claims, they are used consistently across all three artefacts — a milestone that's `at_risk` gets the same warm treatment in PPTX, HTML, and XLSX. And because they're claims, status chips never appear without a specific status — we don't use the ok colour just to make a neutral element look positive.

## How the principles show up per format

### PowerPoint

- 16:9 aspect ratio; every slide uses the blank master.
- Footer is a 0.35-inch band with a hairline above; holds logo (if supplied), signature line, and page counter.
- Every slide has an eyebrow + section title stack in the top-left, anchoring the reader.
- No tables. All visuals are composed from rectangles, rounded rectangles, lines, and text boxes — which means pixel-level control and zero PowerPoint "auto-formatting" surprises.
- Shadows are disabled on every shape.

### HTML

- Single-page, scroll-to-read, print-friendly.
- Self-contained: no external CSS, no JavaScript, no assets except the (optional) logo embedded as a base64 data URI and the Google Fonts CDN link.
- SVG Gantt renders inline — vector-sharp at any size, prints cleanly, and never breaks layout.
- The page takes the same editorial constraints as the PPTX: one accent, display type, italic for voice.
- `@media print` removes the drop shadow on the hero card and tightens the side padding.

### Excel

- Gridlines off on every sheet.
- Generous row heights — display titles sit in 34-point rows, body content in 18-point rows.
- Display type uses Georgia or Calibri at 22pt+; body uses Calibri at 10–11pt.
- The Gantt sheet's bars are built from cell fills with a `DataBarRule` on the progress column. The today marker is a medium-weight left border in the accent colour.
- Logo, when supplied, sits near cell F2 on the Overview sheet only.

## What good looks like

A plan that follows these principles feels calm to read. The eye lands on the headline first, then the status summary, then the snapshot numbers, then the Gantt. At no point does the reader feel they're being shouted at by colour or crowded by density. The brand — whoever the client is — reads as a confident signature, not as a template dressed up in someone else's colours.

A plan that doesn't follow these principles feels like a typical PM dashboard: every possible colour in use, every cell filled, everything equally important. The reader has to work to find the signal.

The principles are what separate a plan that clients screenshot and circulate from a plan they file and forget.
