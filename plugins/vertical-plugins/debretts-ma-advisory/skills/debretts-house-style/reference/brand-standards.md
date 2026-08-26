# Debrett's brand standards — applied reference

Applies to every document, deck, spreadsheet and visual, internal or external.

## Page

| Property | Value |
|---|---|
| Format | A4 landscape |
| Dimensions | 297 x 210mm (11.69 x 8.27in) |
| Margins | 9.5mm all sides |
| Aspect | Never 16:9 |

In `python-pptx`: `prs.slide_width = Mm(297)`, `prs.slide_height = Mm(210)`.
In Word: A4, landscape, 9.5mm margins.

## Type

| Use | Typeface | Notes |
|---|---|---|
| Chart headings, subtitles, callouts, quotes | Playfair Display | Serif, editorial voice |
| Slide titles, sub-headers, body, labels, footers | Albert Sans | Arial the only fallback |

Never Calibri. Never a third family. Set an explicit fallback stack in any generated file.

## Colour

| Role | Name | Hex |
|---|---|---|
| Primary | Oxford Blue | `#16243C` |
| Primary | Corn Silk | `#E7D3AE` |
| Content page background | Off-White | `#F4F3EE` |
| Cover / divider / thank-you background | Oxford Blue | `#16243C` |
| Titles and sub-headers | Teal | `#3E92AC` |

Rules: maximum two background colours per document. No gradients. No drop shadows. No
tints or opacity variants outside the palette above.

## Footer

One line, 10pt Albert Sans Medium, capitals:

```
[DOCUMENT TITLE]            [crown mark]            DEBRETTS.COM / [page]
```

Left: document title. Centre: crown mark. Right: `DEBRETTS.COM / [page]`.

## Logo and crown mark

Never stretch, recolour, crop or rotate. Clear space of at least the height of the crown
on all sides. On navy use the Corn Silk lockup; on Off-White use the Oxford Blue lockup.

## Charts

- Native, editable charts. Never a pasted image of a chart.
- Series colours drawn from the palette only, in this order: Oxford Blue, Teal,
  Corn Silk, then Oxford Blue at a documented palette step.
- Playfair Display for the chart heading; Albert Sans for axis labels and data labels.
- Source line beneath every chart: `Source: [name], [date accessed]`. Never omit it.
- No 3D, no gridline clutter, no legend where direct labelling works.
