# Design plan — professional website for Maurizio Dècina

## Subject, audience, job

- Subject: Maurizio Dècina, Professor of Telecommunications at Politecnico di Milano, IEEE Fellow (1986), pioneer of PCM hierarchies, ISDN standards, fast packet switching and ATM, founder of CEFRIEL, President of the IEEE Communications Society 1994–1995.
- Audience: colleagues and institutions, students and former students looking for course material, journalists and historians of telecommunications.
- Job of the site: present the career credibly in one page, and give one-click access to the full CV (English and Italian), the complete publication list and the 483-file teaching archive.
- Content rule: every fact on the new pages comes from the captured source (CV 4/2012, publication list, teaching archive). Nothing from the PDF's example copy is used. The PDF supplied structure only.

## Tokens

Color

| Token | Hex | Use |
| --- | --- | --- |
| ink | #0f1f33 | headings, body text |
| navy | #173352 | footer, dark band, primary button |
| slate | #51627a | secondary text, metadata |
| mist | #eef2f6 | portrait panel, tinted sections |
| rule | #d7dfe8 | hairlines |
| gold | #a98740 | rules, timeline spine, large accents |
| gold-deep | #86682a | small gold text on white (5.3:1) |
| brass | #d2b36f | gold on navy |

Type

- Literata (variable, optical sizes): display name, headings, body, quotations. Chosen for its book-like scholarly voice and strong italics; the site reads like a well-set academic monograph rather than a start-up page.
- IBM Plex Sans: navigation, buttons, years, file sizes, labels. Engineering heritage fits a standards-body career.
- Scale (px at desktop): 14, 15, 17, 19 body, 22, 27, 34, 44, 56, display clamp(60–120).
- Line length ≤ 68ch for serif body; line-height 1.6 body, 1.05–1.15 display.

Layout

- Left-aligned editorial grid, max 1360px, gutters clamp(20px, 5vw, 80px).
- Hero: 7/5 split. Text left; portrait panel right on mist with one gold hairline on its edge.
- Every content section uses the same split: heading column left (sticky on desktop), content right. Lists are separated by hairlines, never boxed in cards.
- One memorable element: the career timeline, a gold spine with years in Plex Sans and roles in Literata. Everything else stays quiet.

```
┌──────────────────────────────────────────────────────────────┐
│ Maurizio Dècina      Career Research Publications Teaching Contact  [Biography] │
├──────────────────────────────────────┬───────────────────────┤
│ Professor of Telecommunications,     │                       │
│ Politecnico di Milano                │      portrait         │
│                                      │      on mist          │
│ Maurizio                             │   │ gold hairline      │
│ Dècina                               │                       │
│ “For contributions to digital        │                       │
│  communications and to voice/data    │                       │
│  packet switching.” IEEE Fellow 1986 │                       │
│ [Read the biography] [Publications]  │                       │
├──────────────────────────────────────┴───────────────────────┤
│ Politecnico | IEEE ComSoc | CEFRIEL | Italtel | Bell Labs | FUB │
├──────────────┬───────────────────────────────────────────────┤
│ Career       │ 1966 ●── Dott. Ing., University of Rome        │
│ (sticky)     │ 1967 ●── Ugo Bordoni Foundation …              │
│              │ …                                              │
├──────────────┼───────────────────────────────────────────────┤
│ Research     │ 2 × 2 areas separated by hairlines             │
├──────────────┼───────────────────────────────────────────────┤
│ Recognition  │ year | award | citation rows                   │
├──────────────┼───────────────────────────────────────────────┤
│ Publications │ category table (A–H, counts) + selected list   │
├──────────────┴───────────────────────────────────────────────┤
│ lecture-hall photograph, full width                           │
│ Teaching     │ courses + archive index (10 years) + downloads │
├──────────────┼───────────────────────────────────────────────┤
│ Contact      │ address, emails                                │
├──────────────┴───────────────────────────────────────────────┤
│ footer (navy)                                                 │
└──────────────────────────────────────────────────────────────┘
```

Motion: one hero reveal on load (name, rule, portrait). Scroll-spy on the archive year rail and publication categories answers the reader's scrolling. Reduced motion disables all of it.

## Review against the generic default

A default academic site from me would be: cream background, high-contrast serif, terracotta accent, ALL-CAPS eyebrow labels, three identical shadowed cards per section, 01/02/03 markers, arrows after links. Checked and changed:

- Palette follows the brief (navy and gold from the PDF and approved mockups) but on white and mist, with gold used as a rule, not a wash.
- No eyebrows, no all-caps labels, no middle dots, no arrows. Section titles are plain nouns.
- Numbers appear only where the content is a sequence (career years, the archive's academic years, the original publication IDs).
- Hairline grids instead of cards; one border radius (2px) used only on buttons.
- The hero headline device is a real IEEE citation rather than an invented tagline.

## Pages

- index.html — English home page built from the CV, the publication list and the archive.
- teaching.html — the complete original "Attività didattica" page, Italian, all 493 original anchors, with the sticky year rail.
- stuff/decinabiography.htm, stuff/decinabiografia.htm, stuff/decinapublications.htm — complete original documents restyled, with a category navigation on Publications.
