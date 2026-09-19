---
name: CompliScan LM Authentication System
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#45474c'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#545f73'
  primary: '#091426'
  on-primary: '#ffffff'
  primary-container: '#1e293b'
  on-primary-container: '#8590a6'
  inverse-primary: '#bcc7de'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#051426'
  on-tertiary: '#ffffff'
  tertiary-container: '#1b293b'
  on-tertiary-container: '#8290a6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e3fb'
  primary-fixed-dim: '#bcc7de'
  on-primary-fixed: '#111c2d'
  on-primary-fixed-variant: '#3c475a'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#d5e3fc'
  tertiary-fixed-dim: '#b9c7df'
  on-tertiary-fixed: '#0d1c2e'
  on-tertiary-fixed-variant: '#3a485b'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: 2.25rem
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: 2rem
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '600'
    lineHeight: 1.5rem
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
  body-md:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.375rem
  body-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1.125rem
  label-lg:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '500'
    lineHeight: 1.25rem
  label-md:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: '500'
    lineHeight: 1.125rem
  label-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '500'
    lineHeight: 1rem
    letterSpacing: 0.02em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system embodies institutional maturity, precision, and quiet confidence for high-stakes regulatory and legal metrology operations. The visual atmosphere is strictly utilitarian, clear, and unembellished—built to instill legal confidence and eliminate cognitive fatigue during mission-critical identity and access workflows.

Drawing from modern enterprise minimalism and high-legibility legal workstations, the aesthetic explicitly rejects trend-driven gradients, neon focus states, skeuomorphic textures, and floating blurs. Structure, contrast, calibrated whitespace, and crisp 1-pixel architectural borders convey security and operational stability.

## Colors

The system is calibrated strictly for light mode to maintain document-grade readability and parity with physical legal records.

- **Canvas & Surface:** `#f8fafc` (slate-50) serves as the structural application backdrop, while pure `#ffffff` is reserved strictly for interactive authentication containers, modal sheets, and card surfaces.
- **Typography & Hierarchies:** Primary textual data, headings, and high-impact values use `#0f172a` (slate-900). Informational copy, field hints, and subtext utilize `#475569` (slate-600), while timestamps, placeholders, and passive micro-copy fall back to `#64748b` (slate-500).
- **Structural Borders:** Subtle 1px structural framing uses `#e2e8f0` (slate-200) for card perimeters, dividers, and passive rules. Input borders leverage `#cbd5e1` (slate-300) to ensure clear edge definition against pure white surfaces.
- **Interaction & Feedback:** High-intent actions utilize `#1e293b` (slate-800), darkening to `#0f172a` (slate-900) on hover. Keyboard accessibility focus outlines and explicit link interactions rely on `#2563eb` (blue-600). Critical validation errors and unfulfilled legal checks resolve to `#dc2626` (red-600).

## Typography

Inter is utilized throughout all responsive breakpoints to guarantee structural clarity, predictable vertical metrics, and optical legibility in high-density compliance environments.

Headings strictly employ weight `600` (Semi-Bold) with negative letter-spacing to ground identity views without decorative weight. Body text utilizes weight `400` (Regular) paired with relaxed line heights to promote effortless reading of disclaimers, dual-factor instructions, and session terms. All UI labels, metadata tags, and form titles rely on weight `500` (Medium) to ensure fast visual scanning across dense credential inputs.

## Layout & Spacing

The workspace uses a fixed, centered authentication canvas capped at `440px` width for standard single-pane authentication flows (login, magic link, password reset, MFA verification), expandable to `880px` for split-pane SSO verification or compliance disclosures.

- **Grid & Margins:** Fluid page framing with fixed margins (`1.5rem` on desktop, `1rem` on mobile). Outer viewport padding centers the active authentication surface horizontally and vertically.
- **Rhythm & Padding:** Strict 4px base increment rhythm. Micro gaps (`space-xs`, `space-sm`) align form field labels, helper descriptions, and input containers. Macro spacing (`space-md`, `space-lg`, `space-xl`) standardizes vertical separation between card headers, form groups, and legal compliance footers.
- **Breakpoints:**
  - Mobile (`< 640px`): Cards stretch edge-to-edge minus outer margins; minimal vertical offsets.
  - Tablet (`640px - 1024px`): Centered card geometry with default paddings.
  - Desktop (`> 1024px`): Centered card with structured baseline alignment or split layout against slate-50 canvas.

## Elevation & Depth

This design system uses a low-contrast outlined model to avoid the theatricality of deep shadows and heavy elevations. Spatial separation is achieved through color contrast and crisp borders rather than physical layering.

- **Base Canvas:** `#f8fafc` surface without decoration.
- **Containers & Cards:** Pure `#ffffff` surface delineated by a flat, continuous 1px border of `#e2e8f0`.
- **Shadow Metric:** Strictly minimal ambient anchoring: `0 1px 2px 0 rgba(15, 23, 42, 0.05)`. Floating or dramatic elevation tiers are prohibited.
- **Interactive Layers & Popovers:** Dropdowns and tooltips share the flat white ground, bound by a 1px `#cbd5e1` outline and a restrained grounding shadow `0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05)`.

## Shapes

The geometric vernacular communicates sobriety and institutional permanence. Corner radiuses are restrained to subtle soft curvetures:

- Base interactive inputs, standard buttons, and small containers employ an exact `0.25rem` (4px) to `0.375rem` (6px) radius.
- Primary authentication cards and modal containers limit radius to `0.5rem` (8px).
- Pill shapes, circular action buttons, and oversized border radiuses are prohibited to maintain a clean, architectural silhouette.

## Components

### Buttons
- **Primary:** Background `#1e293b`, text `#ffffff`, border none, border-radius `4px` (`0.25rem`), font `label-lg`. Height `40px`. Hover transitions to `#0f172a`. Active state deepens to `#020617`. Focus displays a clean 2px offset ring in `#2563eb`.
- **Secondary / Outline:** Background `#ffffff`, text `#0f172a`, border 1px solid `#cbd5e1`. Hover shifts background to `#f8fafc`.
- **Text / Link:** Background transparent, text `#2563eb`, weight `500`. Underlined only on hover.

### Form Fields & Inputs
- **Text Inputs:** Height `40px`, background `#ffffff`, border 1px solid `#cbd5e1`, border-radius `4px`. Internal text uses `body-md` (`#0f172a`), placeholder uses `#64748b`.
- **Focus State:** 1px solid `#2563eb` with a sharp `0 0 0 1px #2563eb` ring outline. No soft diffuse glows.
- **Error State:** Border shifts to 1px solid `#dc2626`. Error message beneath input displays in `body-sm` with `#dc2626`.

### Checkboxes & Radios
- **Checkboxes:** Size `16px x 16px`, 1px solid border `#cbd5e1`, radius `3px`. Checked state fills `#1e293b` with a white checkmark icon. Focus produces a 2px `#2563eb` offset ring.
- **Selection Labels:** Styled in `body-md` (`#0f172a`) positioned `0.5rem` to the right, baseline-aligned.

### Cards & Panels
- **Auth Card:** Background `#ffffff`, border 1px solid `#e2e8f0`, border-radius `6px`, padding `space-xl` (`2rem`). Houses security badge, header block, forms, and secondary action links.

### Badges & Compliance Status Chips
- **Status Indicator:** Height `24px`, padding `0 8px`, border 1px solid `#e2e8f0`, background `#f8fafc`, font `label-sm` (`#475569`). For official legal metrology seal/stamp indicators, utilize neutral slate tones rather than decorative fills.

### One-Time Password (OTP) / MFA Pin Inputs
- **Digit Box:** Width `44px`, height `48px`, centered text alignment, font `headline-md`, border 1px solid `#cbd5e1`, border-radius `4px`. Active cell immediately draws the 1px `#2563eb` focus border.
