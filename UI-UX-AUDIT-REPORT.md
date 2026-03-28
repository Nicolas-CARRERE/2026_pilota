# Pilota UI/UX Audit Report

**Date:** 2026-03-27  
**Auditor:** orchestrator (subagent)  
**Project:** `/home/nco-bot-helper/.openclaw/workspace/pilota/frontend`

---

## Executive Summary

The Pilota frontend is a functional Angular application with a coherent visual theme (Basque flag: green, red, white). However, several UI/UX issues impact usability, accessibility, and polish. This report lists **23 actionable improvements** prioritized by impact and effort.

---

## Priority Legend

| Priority | Meaning |
|----------|---------|
| **High** | Blocks usability, accessibility violation, or major friction |
| **Medium** | Noticeable friction, inconsistent UX, or missing best practice |
| **Low** | Nice-to-have polish or enhancement |

## Effort Legend

| Effort | Meaning |
|--------|---------|
| **S** (Small) | < 2 hours, single-file change |
| **M** (Medium) | 2-8 hours, multiple files or new component |
| **L** (Large) | > 8 hours, new system or significant refactor |

---

## Findings

### 1. Navigation & Layout

#### #1: No Mobile Navigation Menu
- **Issue:** Header nav links wrap awkwardly on small screens; no hamburger menu
- **Current:** Nav links use `flex-wrap: wrap` in `.nav`
- **Fix:** Implement collapsible mobile nav with hamburger toggle
- **Priority:** High
- **Effort:** M
- **Files:** `src/app/layout/header/header.component.*`
- **Status:** ✅ COMPLETED — Added hamburger button, mobile nav with slide-down animation, aria-expanded attributes

#### #2: No Breadcrumb Navigation
- **Issue:** Detail pages only have "Retour" links; users lose context
- **Current:** `<a routerLink="/players" class="back-link">← Retour</a>`
- **Fix:** Add breadcrumb component: `Accueil > Joueurs > Jean Dupont`
- **Priority:** Medium
- **Effort:** M
- **Files:** New component `src/app/shared/components/breadcrumb/`
- **Status:** ✅ COMPLETED — BreadcrumbComponent added, integrated on all detail pages (players, teams, games, championships)

#### #3: Inconsistent Back Links
- **Issue:** Some pages use `btn btn--outline`, others use `.back-link` class
- **Current:** Mixed patterns across detail pages
- **Fix:** Standardize on one pattern (recommend styled link, not button)
- **Priority:** Low
- **Effort:** S
- **Files:** All detail page templates
- **Status:** ✅ COMPLETED — All back links now have aria-labels, consistent pattern across pages

#### #4: No Skip-to-Content Link
- **Issue:** Keyboard users must tab through nav on every page
- **Current:** No skip link in `index.html` or `app.component.html`
- **Fix:** Add skip link: `<a href="#main" class="skip-link">Skip to content</a>`
- **Priority:** High
- **Effort:** S
- **Files:** `src/app/app.component.html`, `src/styles.scss`
- **Status:** ✅ COMPLETED — Added "Aller au contenu principal" skip link, hidden until focused

---

### 2. Forms & Validation

#### #5: No Form Validation Feedback
- **Issue:** Filter inputs show no error states or validation messages
- **Current:** Inputs have `:focus` styles but no error styling
- **Fix:** Add `.is-invalid` class with red border + error text below field
- **Priority:** Medium
- **Effort:** M
- **Files:** `src/app/shared/components/filter/filter.component.*`
- **Status:** ✅ COMPLETED — Added .is-invalid class, error-text display, aria-invalid and aria-describedby attributes

#### #6: No Loading State on Filter Changes
- **Issue:** Filters emit immediately; no feedback during API calls
- **Current:** `(filtersChange)="applyFilters($event)"` with no loading indicator
- **Fix:** Show spinner or disable form during filter fetch
- **Priority:** Medium
- **Effort:** S
- **Files:** Filter component + parent list components
- **Status:** ✅ COMPLETED — Added loading spinner with aria-live status during competition fetch

#### #7: No Confirmation on Filter Reset
- **Issue:** "Réinitialiser" button clears filters without warning
- **Current:** `resetFilters()` emits immediately
- **Fix:** Add toast confirmation or undo snackbar
- **Priority:** Low
- **Effort:** M
- **Files:** Filter component + notification service
- **Status:** ✅ COMPLETED — Toast notification shows "Filtres réinitialisés" on reset

#### #8: No Search Functionality
- **Issue:** Player/team lists have no search box
- **Current:** Only filter by competition/phase/status
- **Status:** ✅ COMPLETED — Added search input with debounced filtering on player and team lists
- **Fix:** Add text search input with debounced filtering
- **Priority:** High
- **Effort:** M
- **Files:** Player/team list components + services

---

### 3. Flash Messages & Notifications

#### #9: No Flash/Toast System
- **Issue:** No feedback for actions (success, error, info)
- **Current:** Errors shown inline with `.error-message` div
- **Fix:** Implement toast notification service (success/error/info/warning)
- **Priority:** High
- **Effort:** L
- **Files:** New service + component `src/app/shared/components/toast/`
- **Status:** ✅ COMPLETED — ToastService + ToastComponent with success/error/info/warning types, auto-dismiss, close button

#### #10: Error Messages Lack Visibility
- **Issue:** `.error-message` blends in; users may miss errors
- **Current:** Light red background `#ffebee` with red text
- **Fix:** Increase contrast, add icon, make sticky at top of page
- **Priority:** Medium
- **Effort:** S
- **Files:** `src/styles.scss`, update error templates
- **Status:** ✅ COMPLETED — Added warning icon, sticky positioning, improved contrast and shadow

---

### 4. Responsive Design

#### #11: Game Cards Don't Adapt to Mobile
- **Issue:** Game cards use fixed grid columns that break on small screens
- **Current:** `grid-template-columns: auto 1fr auto auto` in `.game-card-link`
- **Fix:** Add media query to stack elements vertically on mobile
- **Priority:** High
- **Effort:** S
- **Files:** `src/app/features/games/game-list/game-list.component.scss`
- **Status:** ✅ COMPLETED — Stacks vertically on screens < 600px, increased touch targets

#### #12: Filter Panel Overflows on Small Screens
- **Issue:** Filter inputs wrap poorly below 400px width
- **Current:** Basic responsive at 768px breakpoint only
- **Fix:** Add breakpoint at 400px, reduce input widths, stack labels
- **Priority:** Medium
- **Effort:** S
- **Files:** `src/app/shared/components/filter/filter.component.scss`
- **Status:** ✅ COMPLETED — Added 400px breakpoint with full-width inputs and smaller fonts

#### #13: Dashboard Sidebar Not Collapsible on Mobile
- **Issue:** `sidebarCollapsed` button exists but sidebar takes full width on mobile
- **Current:** Toggle button shows "Show/Hide Filters" but layout doesn't adapt
- **Fix:** Make sidebar slide out or become modal on mobile
- **Priority:** Medium
- **Effort:** M
- **Files:** `src/app/dashboard/dashboard.component.*`
- **Status:** ✅ COMPLETED — Sidebar slides out as modal on mobile with overlay backdrop, closes on main click

---

### 5. Accessibility (a11y)

#### #14: Missing ARIA Labels
- **Issue:** Only 2 ARIA attributes found in entire codebase
- **Current:** `aria-live` on loading, `aria-label` on nav
- **Fix:** Add `aria-label`, `aria-describedby`, `role` attributes throughout
- **Priority:** High
- **Effort:** M
- **Files:** All component templates
- **Status:** ✅ COMPLETED — Added ARIA labels to lists, detail pages, buttons, navigation, error messages, pagination

#### #15: No Focus States Defined
- **Issue:** Keyboard navigation has no visible focus indicators
- **Current:** Only `:focus` on filter inputs
- **Fix:** Add global `:focus-visible` styles with outline
- **Priority:** High
- **Effort:** S
- **Files:** `src/styles.scss`
- **Status:** ✅ COMPLETED — Added 3px green outline on all interactive elements (buttons, links, inputs)

#### #16: Color Contrast Issues (Potential)
- **Issue:** Green `#008C45` on white may fail WCAG AA for small text
- **Current:** Links use green, status badges use green/red
- **Fix:** Run contrast checker; darken green if needed
- **Priority:** Medium
- **Effort:** S
- **Files:** `src/styles.scss` (update `--pelota-green`)
- **Status:** ✅ COMPLETED — Darkened green to #007A3D and red to #C40210 for better WCAG AA compliance

#### #17: No Alt Text on Images
- **Issue:** No images currently, but future images will need alt text
- **Current:** N/A
- **Fix:** Document alt text requirement in component templates
- **Priority:** Low
- **Effort:** S
- **Files:** Team guidelines (add to README)
- **Status:** ✅ COMPLETED — Added accessibility guidelines section to README.md with alt text requirements

---

### 6. Loading States & Error Handling

#### #18: Loading Component Is Text-Only
- **Issue:** `<app-loading>` shows "Chargement…" with no spinner
- **Current:** Template: `<div class="loading-spinner">Chargement…</div>`
- **Fix:** Add CSS spinner or SVG animation
- **Priority:** Medium
- **Effort:** S
- **Files:** `src/app/shared/components/loading/loading.component.ts`
- **Status:** ✅ COMPLETED — Added CSS spinner with smooth rotation animation (0.8s)

#### #19: No Skeleton Screens
- **Issue:** Content jumps when loading completes
- **Current:** Loading component blocks entire view
- **Fix:** Implement skeleton placeholders for cards/lists
- **Priority:** Medium
- **Effort:** M
- **Files:** New component `src/app/shared/components/skeleton/`
- **Status:** ✅ COMPLETED — SkeletonComponent with card/list/text/avatar variants and shimmer animation

#### #20: No Retry Mechanism on Error
- **Issue:** Error state shows message but no way to retry
- **Current:** `<div class="error-message">{{ error }}</div>`
- **Fix:** Add "Retry" button that re-triggers data fetch
- **Priority:** Medium
- **Effort:** S
- **Files:** All list/detail components
- **Status:** ✅ COMPLETED — Added "Réessayer" button to game, player, team, championship lists

---

### 7. User Flow & Information Architecture

#### #21: No Pagination on Player List
- **Issue:** Games have pagination; players don't (will break at scale)
- **Current:** Player list shows all players with no limit
- **Fix:** Add same pagination pattern as game list
- **Priority:** Medium
- **Effort:** M
- **Files:** `src/app/features/players/player-list/player-list.component.*`
- **Status:** ✅ COMPLETED — Added pagination with Prev/Next buttons, page info display, 20 items per page

#### #22: No Sorting Options
- **Issue:** Lists have no sort controls (by name, date, wins, etc.)
- **Current:** Default order from API
- **Fix:** Add sort dropdown with common options per list type
- **Priority:** Medium
- **Effort:** M
- **Files:** All list components + services
- **Status:** ✅ COMPLETED — Added sort dropdown (name, games played, wins) with ascending/descending toggle on player list

#### #23: No Empty State Illustrations
- **Issue:** "Aucun joueur trouvé" is plain text
- **Current:** Simple `<p>` tags for empty states
- **Fix:** Add friendly illustrations or icons with helpful text
- **Priority:** Low
- **Effort:** M
- **Files:** All list components
- **Status:** ✅ COMPLETED — Added .empty-state class with centered styling, icon placeholder, and helpful text

---

## Quick Wins (S Effort, High Impact)

✅ **1. #4: Skip-to-content link** — COMPLETED (2026-03-27)
✅ **2. #15: Focus states** — COMPLETED (2026-03-27)
✅ **3. #18: Loading spinner** — COMPLETED (2026-03-27)
✅ **4. #11: Mobile game cards** — COMPLETED (2026-03-27)
✅ **5. #20: Retry button on errors** — COMPLETED (2026-03-27)

---

## QA Recommendations Implementation

### ✅ Recommendation 1: Visual Skip-Link Enhancement (COMPLETED 2026-03-27)
**Status:** ✅ IMPLEMENTED  
**Files Modified:** `frontend/src/styles.scss`  
**Changes:**
- Increased border thickness (3px white border)
- Added background color change on focus (darker green → green)
- Set z-index to 9999 to appear above all content
- Added smooth transition with transform effect
- Added box-shadow for depth on focus-visible
- Increased padding and font-weight for better visibility

**Test Results:** All 15 accessibility tests pass

### ✅ Recommendation 2: Unit Tests for Accessibility Features (COMPLETED 2026-03-27)
**Status:** ✅ IMPLEMENTED  
**Files Created:** `frontend/src/app/accessibility.spec.ts`  
**Tests Added:**
- ✅ Test skip-link exists and is clickable
- ✅ Test skip-link has correct href (`#main`)
- ✅ Test skip-link has French text "Aller au contenu principal"
- ✅ Test focus-visible states apply on keyboard navigation
- ✅ Test loading spinner availability
- ✅ Test mobile breakpoint triggers card stacking (600px)
- ✅ Test retry button calls reload function
- ✅ Test component integration with template structure

**Test Results:** 15/15 tests passing (Chrome Headless)

---

## Recommended Implementation Order

**Phase 1 (Critical):** #1, #4, #9, #11, #14, #15  
**Phase 2 (Important):** #2, #5, #6, #10, #16, #18, #20  
**Phase 3 (Polish):** #3, #7, #8, #12, #13, #19, #21, #22, #23

---

## Notes for coding-agent

- All CSS variables are defined in `src/styles.scss` — use them consistently
- Angular 18+ syntax is used (`@if`, `@for`, etc.) — maintain this pattern
- French language is used throughout — keep consistency
- No external UI library is in use — build custom components or consider adding Angular Material/PrimeNG if scope grows

---

**End of Report**
