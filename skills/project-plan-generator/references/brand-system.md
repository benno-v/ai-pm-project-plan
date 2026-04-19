# Brand system — colours, fonts, logo

The whole plan package can be rebranded from two colour values and, optionally, a logo file. Everything else in the palette — tints, shades, status colours, neutrals — is derived automatically so you don't have to design a full system for every client.

## What the user supplies

Inside the plan JSON:

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

All four brand fields and `logo_path` are optional. Leave them out and the deck falls back to an editorial default: deep navy primary, warm muted gold accent, Georgia and Calibri.

## The derived palette

`scripts/brand.py` derives the rest of the palette from the two input colours. A single `Palette` object carries every colour used across the three generators:

| Role           | How it's derived                                   | Used for                                 |
|----------------|----------------------------------------------------|------------------------------------------|
| `primary`      | User input, or `#0B2545` default.                  | Headlines, phase bars, primary chrome.   |
| `primary_dark` | Primary blended 30% toward black.                  | Hover / pressed states, depth tints.     |
| `primary_soft` | Primary blended 90% toward white.                  | Task bar backgrounds, section washes.    |
| `accent`       | User input, or `#C49A3A` default.                  | Progress fills, today marker, key numbers. |
| `accent_soft`  | Accent blended 82% toward white.                   | Callout backgrounds, subtle highlights.  |
| `ink`          | Fixed `#1A1A1A`.                                   | Body copy.                               |
| `ink_soft`     | Fixed `#4A4A4A`.                                   | Secondary copy.                          |
| `ink_faint`    | Fixed `#8A8A8A`.                                   | Captions, eyebrows, footer text.         |
| `ink_mute`     | Fixed `#BFBFBF`.                                   | Watermark-level notes.                   |
| `rule`         | Fixed `#D9D9D9`.                                   | Visible borders.                         |
| `hairline`     | Fixed `#EFEFEF`.                                   | Subtle dividers.                         |
| `page`         | Fixed `#FFFFFF`.                                   | Page background.                         |
| `card`         | Fixed `#FAFAF7`.                                   | Cards and callouts.                      |
| `wash`         | Fixed `#F3F1EC`.                                   | Phase bands, section washes.             |
| `ok`           | Fixed desaturated green `#3F7A52`.                 | Achieved, on-track chips.                |
| `ok_soft`      | Fixed `#E9F1EC`.                                   | Background for ok chips.                 |
| `warn`         | Fixed desaturated amber `#AE7A2A`.                 | At-risk chips, warn bars.                |
| `warn_soft`    | Fixed `#F7EFDF`.                                   | Background for warn chips.               |
| `risk`         | Fixed desaturated red `#8E2F2F`.                   | Blocked, delayed chips.                  |
| `risk_soft`    | Fixed `#F1E3E3`.                                   | Background for risk chips.               |

The status colours (ok / warn / risk) stay fixed so the plan reads the same across any brand. A client with a red primary doesn't get a red "on track" chip.

## Font handling

Fonts are set per-format so the same plan still looks right in each tool:

| Format | Display default | Body default | Notes                                                     |
|--------|-----------------|--------------|-----------------------------------------------------------|
| PPTX   | Georgia         | Calibri      | Both ship with Windows and Mac.                           |
| HTML   | Fraunces        | Inter        | Loaded from Google Fonts via CDN link in the HTML head.   |
| XLSX   | Calibri         | Calibri      | Excel-safe. Display fields use 22pt+ Calibri bold.        |

If `brand.display_font` or `brand.body_font` are set in the plan, they override the PPTX and (in theory) HTML defaults — but only if the font is available on the rendering machine. For bulletproof portability, leave them unset unless you have a reason.

## Logo handling

`project.logo_path` is resolved in three stages:

1. Absolute path — used directly if it exists on disk.
2. Relative path — resolved against the folder containing the plan JSON.
3. Relative path — resolved against the current working directory.

If none of these find the file, the logo is silently skipped and the generators still run. This is deliberate: a missing logo should never break the build.

**File format.** PNG with transparency is recommended. Aim for a horizontal wordmark no larger than 800×240 pixels — the generators will scale it down to fit a 35-pixel-tall footer band.

**Placement per format.**

- **PowerPoint.** Appears in the footer of every slide, bottom-left, next to the project signature line.
- **HTML.** Appears in the hero section (top right of the title block) and in the footer.
- **Excel.** Added to the Overview sheet near cell F2. Other sheets don't carry a logo — Excel doesn't have a concept of page footers that's useful here.

## Accessibility

The derived palette keeps body copy at 4.5:1 contrast against the page background and at 3:1 for large display type. If you supply a very pale primary colour, headlines may look thin — consider using a deeper shade. The fixed ink values are chosen to work with any primary that is at least mid-tone.

## Customising further

If the derived palette isn't working for a specific brand, edit `scripts/brand.py` — it's 200 lines, fully commented, and the only file that holds palette maths. The three generators import from it, so one change propagates to all three formats.
