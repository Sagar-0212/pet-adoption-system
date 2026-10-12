# Happy Paws  UI/UX Design System

This document outlines the official design tokens, typography, and component guidelines implemented in the newly upgraded Pet Adoption & Management System. This ensures consistent, accessible, and inclusive design handoffs for future developers.

## 1. Design Tokens & Color Palette

We are utilizing a Tailwind-based SaaS color palette optimized for accessibility (WCAG AA contrast) and a modern, friendly aesthetic.

### Brand Colors (Emerald/Teal gradient)
The primary brand communicates trust, nature, and successful adoptions.
- **Brand Primary:** `#16a34a` (Tailwind `green-600`) - Used for primary buttons and active states.
- **Brand Hover:** `#15803d` (Tailwind `green-700`) - Used for interaction feedback.
- **Brand Light:** `#dcfce7` (Tailwind `green-100`) - Used for soft backgrounds, like the 'Available' badge.

### Interface Neutral Colors (Slate)
Slate provides a cool, professional contrast that reduces eye strain compared to pure black and white.
- **Background:** `#f8fafc` (Tailwind `slate-50`)
- **Card Background:** `#ffffff` (White)
- **Primary Text:** `#1e293b` (Tailwind `slate-800`) - High contrast body text.
- **Secondary Text:** `#64748b` (Tailwind `slate-500`) - Used for timestamps and metadata.
- **Borders/Dividers:** `#e2e8f0` (Tailwind `slate-200`)

---

## 2. Typography

To give the application a modern, startup-grade feel, we have implemented **Plus Jakarta Sans**, a highly legible geometric sans-serif typeface.

- **Font Family:** `'Plus Jakarta Sans', system-ui, sans-serif`
- **Hero Headings (h1):** `font-extrabold`, `text-4xl` to `text-5xl`, tracking tight (`tracking-tight`).
- **Section Headings (h2):** `font-semibold`, `text-xl`, text color `slate-800`.
- **Body Text:** `font-normal`, `text-base`, line-height `relaxed`.
- **Micro-copy / Badges:** `font-medium`, `text-xs`, uppercase styling with wide letter spacing.

---

## 3. UI Component Architecture

### The Pet Catalog Card
The primary interactive component of the public portal. Designed for scanning and emotional connection.
- **Visuals:** Uses a 16:9 aspect ratio placeholder image (e.g., Unsplash) with a soft hover scale effect (`hover:scale-105 duration-300`) to invite interaction.
- **Information Hierarchy:**
  1. Name (Largest, bold)
  2. Status Badge (Top right, color-coded)
  3. Breed / Age (Subdued metadata)
  4. Adoption Button (Full width at bottom to create a massive click target).
- **Shadows:** `shadow-sm` resting state, transitioning to `shadow-md` on hover to indicate interactivity.

### Accessibility (A11y) & Inclusivity
- **Zero Emojis:** All decorative emojis have been systematically replaced with clean, semantic SVG icons equipped with `aria-hidden="true"`.
- **Color Independence:** Statuses like "Adopted" and "Available" rely on both text and color, not color alone, ensuring color-blind users can navigate the system easily.
- **Focus States:** All interactive elements (`<button>`, `<a>`, `<input>`) must have clear focus rings for keyboard navigators.

---

## 4. Animation & Micro-Interactions
- **Tab Switching:** `tabFadeIn 0.25s ease-out`  A subtle fade and 4px upward translation to make navigation feel physical and snappy.
- **Toasts:** Cubic-bezier transitions (`cubic-bezier(0.16, 1, 0.3, 1)`) to create a satisfying, spring-like entrance for success/error messages.
- **Loaders:** A minimalist CSS spinner on buttons to provide instant visual feedback when the user submits an adoption application.

> **Next Steps:** If we want to further improve conversion rates, we should look into mapping the **Adoption User Journey** to reduce the number of fields in the application form.
