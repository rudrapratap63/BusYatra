---
name: BusYatra
description: India's premier bus booking platform
colors:
  trust-teal: "#0d9488"
  ticket-gold: "#f59e0b"
  neutral-bg: "#fafaf9"
  neutral-fg: "#1c1917"
  seat-available: "#22c55e"
  seat-female: "#ec4899"
  seat-male: "#94a3b8"
  seat-blocked: "#ef4444"
typography:
  display:
    fontFamily: "'Outfit', sans-serif"
  body:
    fontFamily: "'Inter', sans-serif"
  mono:
    fontFamily: "'JetBrains Mono', monospace"
rounded:
  sm: "calc(0.75rem - 4px)"
  md: "calc(0.75rem - 2px)"
  lg: "0.75rem"
components:
  button-primary:
    backgroundColor: "{colors.trust-teal}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  button-secondary:
    backgroundColor: "#effcf9"
    textColor: "#065f56"
---

# Design System: BusYatra

## 1. Overview

**Creative North Star: "The Trusted Transit Terminal"**

This system is built for speed and reliability. It eschews generic SaaS decorations (like heavy glassmorphism and cluttered metric cards) in favor of clear, functional utility. The interface should feel robust, easy to parse, and entirely focused on getting the traveller to their destination with confidence. 

**Key Characteristics:**
- Utilitarian and direct
- High-contrast visual hierarchy
- Minimal and flush interactive elements

## 2. Colors

The palette is restrained, using trust-evoking teal for primary actions and gold for highlights or selections.

### Primary
- **Trust Teal** (#0d9488): The core brand color. Used for primary buttons, active states, and focus rings.

### Secondary
- **Ticket Gold** (#f59e0b): Used sparingly for seat selection, warnings, or highlighting special deals.

### Semantic
- **Seat Available** (#22c55e): Standard available seat.
- **Seat Female** (#ec4899): Seats reserved or booked by female passengers.
- **Seat Male** (#94a3b8): Seats booked by male passengers.
- **Seat Blocked** (#ef4444): Unavailable or blocked seats.

### Neutral
- **Background** (#fafaf9): Main canvas color in light mode.
- **Foreground** (#1c1917): Primary text color.
- **Border/Input** (#e7e5e4): Standard border for fields and cards.

**The Functional Color Rule.** Color is reserved for state and semantics. Do not use background gradients or decorative color washes.

## 3. Typography

**Display Font:** Outfit (with sans-serif fallback)
**Body Font:** Inter (with sans-serif fallback)
**Mono Font:** JetBrains Mono (with monospace fallback)

**Character:** Clean, legible, and optimized for dense data like timetables and pricing.

### Hierarchy
- **Display** (Bold): Major page headers.
- **Headline** (SemiBold): Section titles.
- **Body** (Regular): General UI text and descriptions. Cap line length at 65–75ch for readability.
- **Label** (Medium, small): Input labels, metadata, and data table headers.

## 4. Elevation

The system is flat by default, relying on structural borders (`#e7e5e4` in light mode) rather than shadows to define hierarchy. 

**The Flat-By-Default Rule.** Surfaces are flat at rest. Shadows appear only as a response to state (like hover, active, or dropdown menus). Avoid diffuse ambient shadows.

## 5. Components

Components are minimal and flush, prioritizing clarity over tactical realism.

### Buttons
- **Shape:** Softly rounded corners (md: calc(0.75rem - 2px)).
- **Primary:** Solid Trust Teal background with white text.
- **Hover / Focus:** Slightly darker teal (`#0a7c71`) on hover, with a crisp teal focus ring. Active state scales down slightly (`scale-[0.98]`).
- **Secondary:** Light teal background (`#effcf9`) with dark teal text.
- **Ghost:** Transparent background with neutral hover states.

### Inputs / Fields
- **Style:** Flush with a clear border (`#e7e5e4`), `0.75rem` radius.
- **Focus:** No shadows; uses a crisp 2px solid ring (`#0d9488`).

### Cards / Containers
- **Corner Style:** Large radius (`0.75rem`).
- **Background:** Solid white (`#ffffff`).
- **Border:** 1px solid border. No resting shadows.

## 6. Do's and Don'ts

### Do:
- **Do** rely on structural borders for layout division.
- **Do** use the established semantic seat colors (green, pink, gray, red, gold) exclusively for seat mapping to avoid confusion.
- **Do** ensure interactive elements feel "minimal and flush."

### Don't:
- **Don't** use overly complex, generic SaaS-heavy templates.
- **Don't** use decorative glassmorphism.
- **Don't** use cluttered metrics that distract from the core booking flow.
- **Don't** use `border-left` greater than 1px as a colored stripe on cards.
- **Don't** use gradient text.
