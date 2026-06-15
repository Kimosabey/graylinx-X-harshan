# Motion / Animation Revamp Brief — Harshan × Graylinx Work Tracker

> **Purpose:** hand this file to a Claude "design" agent to implement an **animation/motion-led
> UI revamp** of the existing dashboard. It is self-contained — it describes the current stack,
> the constraints, and an exact, component-by-component motion spec with acceptance criteria.

---

## 0. How to use this brief
You are revamping an **existing, working** single-file dashboard. Do **not** rebuild from
scratch and do **not** change the data, the data model, or the build pipeline. Layer motion on
top of the current neumorphic monochrome UI. Work through the phases in §10 and tick §11.

---

## 1. Project context (read before touching anything)

**Repo:** `git@github.com:Kimosabey/graylinx-X-harshan.git` (branch `main`).
**Stack:** plain **HTML + CSS + vanilla JS** in one file — no framework, no bundler. Opens by
double-click (`file://`) and deploys static to Netlify (`public/`).

**Key files**
- `index.html` — the whole app: inline `<style>`, inline `<script>`, plus an inline
  `<script id="seed-data" type="application/json">…</script>` data blob.
- `lenis.min.js` — **Lenis** smooth-scroll, already vendored & wired (RAF loop, scroll-progress
  bar, subtle parallax). Reuse it; don't duplicate scroll logic.
- `build_tracker.py` — regenerates data and **re-injects the seed JSON** into `index.html`
  between the exact markers `<script id="seed-data" type="application/json">` … `</script>`.
  ⚠️ **Never rename/remove that script tag or change its id** or the build breaks.
- `works.*`, `engagement.csv`, `public/`, `netlify.toml`, `README.md`.

**Current JS you must integrate with (names are stable):**
- `renderAll()` calls `renderStats, renderStatusLegend, renderGantt, renderCards,
  renderEngStats, renderCalendar, renderDayList`.
- `statCards()` + `countUp()` — stat number count-up already exists.
- A global **`animate`** flag and a CSS **`.reveal`** class already gate intro animation on
  first paint / tab-switch (set `false` on filter/keystroke so lists don't re-animate per keypress).
- A global **`RM`** = `matchMedia('(prefers-reduced-motion: reduce)').matches`. **Every** new
  animation MUST be a no-op when `RM` is true.
- Theme via `data-theme` on `<html>` (`auto`/`light`/`dark`); palette is CSS custom properties
  (`--ink`, `--bg`, `--s1..--s5`, neumorphic `--raise`/`--inset` shadows, `--ease`).

**Current motion already present (keep, then elevate):** Lenis smooth scroll, scroll-progress
bar, subtle parallax orbs, count-up stats, staggered `.reveal` fade-up, progress-bar width fill,
hover lifts, modal pop, button press (raised→inset).

---

## 2. Goals & non-goals

**Goal:** make **motion a first-class design language** — purposeful, premium, "alive" — so the
showcase feels modern and intentional, not decorative. Motion should *explain* (where did this
come from / where did it go), *guide attention*, and *reward interaction*.

**Non-goals:** no gratuitous spinning/bouncing; no motion that delays data; no parallax that
hurts readability; no dependency that breaks offline use; no change to data/contracts/WCAG.

---

## 3. Motion principles (the rubric for every decision)
1. **Purposeful** — every animation answers "what changed / where did it go / what can I do."
2. **Fast & interruptible** — UI motion 120–320ms; never block input; new input cancels in-flight.
3. **Spatial continuity** — elements enter from where they conceptually come from; shared-element
   transitions over hard cuts.
4. **Choreographed, not simultaneous** — stagger siblings 30–60ms; lead with the most important.
5. **Physical** — spring/eased easing, transform+opacity only (never animate layout props).
6. **Accessible** — full parity with `prefers-reduced-motion`; respect focus; keep AA contrast.
7. **Performant** — 60fps; GPU-friendly; no jank on a mid laptop.

---

## 4. Motion tokens (add to `:root`, reuse everywhere)
```css
--dur-1:120ms;  /* micro: hover, press */
--dur-2:200ms;  /* controls: tabs, chips */
--dur-3:320ms;  /* containers: cards, modal */
--dur-4:520ms;  /* hero/page choreography */
--stagger:45ms;
--ease-out:cubic-bezier(.2,.7,.2,1);     /* enter */
--ease-in:cubic-bezier(.5,0,.75,0);       /* exit */
--ease-spring:cubic-bezier(.34,1.56,.64,1); /* playful overshoot (use sparingly) */
```
Durations scale by element size (micro→hero). Enter = ease-out + fade-up; exit = ease-in + fade.

---

## 5. Library decision
**Recommended: [Motion One](https://motion.dev) (`motion`), vendored locally** as
`motion.min.js` (~18KB, fetch once like `lenis.min.js`). Rationale: tiny, uses the Web
Animations API, spring + stagger + scroll + **timeline** helpers, plays nicely with vanilla JS
and offline use. Wrap all calls so a load failure or `RM` degrades to instant/no-op.

- **Alt A — zero new deps:** Web Animations API (`el.animate(...)`) + CSS + `IntersectionObserver`.
  Choose this if you want no new file at all; slightly more code for stagger/springs.
- **Alt B — GSAP** (vendored): only if you need complex sequenced timelines (e.g. an intro
  "build the dashboard" reel). Heavier (~70KB); justify before adding.

**Constraint:** must work on `file://` offline and on Netlify → **vendor locally, no CDN at runtime**.
Add any new vendored lib to `build_tracker.py`'s `PUBLIC_FILES` so it ships in `public/`.

---

## 6. Component-by-component motion spec

**App-bar**
- On scroll: condense (already `.scrolled`) — also slightly reduce logo scale & blur-in shadow (200ms).
- Scroll-progress bar: animate width via `scaleX` (exists) — make it spring-eased.

**Stats band**
- Count-up (exists) — keep, but trigger when the band **scrolls into view** (IntersectionObserver),
  not just on load. Stagger the 5 cards by `--stagger`. Card entrance: fade + 10px up + 0.98→1 scale.

**Tabs (Projects ↔ Engagement)**
- Replace the hard `hidden` swap with a **shared transition**: outgoing view fades/slides 12px in
  the exit direction; incoming view fades/slides in from the opposite side (220ms). Prefer the
  **View Transitions API** (`document.startViewTransition`) with a CSS-animation fallback; degrade
  to instant under `RM`. Animate the selected-tab "pill" sliding between tabs.

**Project cards (`renderCards`)**
- Entrance: `IntersectionObserver` reveal with `--stagger` (only first paint / tab-switch; honor the
  `animate` flag so filtering/search doesn't re-stagger every keystroke — instant update instead).
- Hover: lift (exists) + raise the status dot slightly; keep ≤150ms.
- Progress bar: grow from 0 → value with `--ease-out` when card enters view (exists — make it
  view-triggered).
- Edit/delete: card removal animates out (fade + 8px down + height collapse) before DOM removal.

**Gantt timeline (`renderGantt`)**
- Bars **grow from their start edge** (`transform: scaleX(0→1)`, `transform-origin:left`) staggered
  by category, when the timeline scrolls into view. "today" marker fades in last.
- Hover bar: subtle scaleY (exists) + tooltip fade.

**Calendar (`renderCalendar`)**
- Month grids reveal on scroll; day cells **pop in** with a tiny stagger across the grid (cap total
  duration ~400ms so it never feels slow). Hover: scale (exists). Selected day: spring pulse.

**Daily log rows (`renderDayList`)**
- Stagger-in on view; row hover = inset press (exists). Filter change = cross-fade the list.

**Modal**
- Backdrop fade + dialog spring pop (exists) — refine timing; on close, reverse (don't just hide).
- Keep `data-lenis-prevent`; Lenis `.stop()/.start()` already handled — preserve it.

**Theme toggle**
- Animate the color-property transition (already a 0.3s transition on `body`); add an optional
  **circular reveal** (View Transitions / clip-path from the toggle button) light↔dark. `RM` = instant.

**Buttons / chips / inputs**
- Press: raised→inset (exists). Add a faint **ripple/scale** on `:active` (≤120ms). Focus ring stays
  the solid 2px (do NOT replace focus affordance with motion only).

**Empty/loading states**
- If a render is async or heavy, show a **neumorphic skeleton shimmer** (subtle, monochrome) instead
  of a blank flash.

---

## 7. Page-load choreography (first paint)
A short, premium intro (~600ms total, skip entirely under `RM`):
1. App-bar drops/fades in (logo plate scales 0.96→1).
2. Stats band counts up + staggers.
3. Active tab's content reveals (cards/gantt stagger).
Use one timeline; ensure content is **usable immediately** (don't gate interaction on the intro).

---

## 8. Scroll-driven motion (reuse Lenis)
- Subscribe to the **existing** `lenis.on('scroll', …)`; do not add a second smoothing layer.
- Reveal-on-scroll via `IntersectionObserver` (threshold ~0.15, `rootMargin:"0px 0px -10% 0px"`),
  add a `.in` class → CSS animation. Unobserve after first reveal.
- Keep parallax subtle (orbs + brand exist). Optionally add depth: stat band drifts a few px slower
  than cards. Cap parallax magnitude; disable under `RM`.
- Where supported, CSS **scroll-driven animations** (`animation-timeline:view()`) are a progressive
  enhancement over IO.

---

## 9. Accessibility & performance guardrails (hard requirements)
- **`prefers-reduced-motion: reduce`** → all entrance/scroll/parallax/intro motion OFF; show final
  state instantly; Lenis stays disabled (already does). The existing global `RM` and the
  `@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}`
  block must keep covering every new animation.
- Animate **only `transform` + `opacity` + `filter`** (and `clip-path` for theme reveal). Never
  animate width/height/top/left/margin (layout thrash) — the progress/gantt use `transform:scaleX`.
- Keep **60fps**; add `will-change` only on actively-animating elements, remove after.
- Don't animate on every keystroke (respect the `animate` flag pattern already in the code).
- Maintain WCAG AA: motion must not reduce text contrast; focus order/visibility unchanged.
- No content reflow / layout shift from animations (CLS ~0).

---

## 10. Implementation phases
1. **Tokens + lib**: add §4 tokens; vendor `motion.min.js` (or commit to WAAPI-only); add to
   `build_tracker.py` `PUBLIC_FILES`; create a tiny `anim(el, kf, opts)` wrapper that no-ops when
   `RM` or lib missing.
2. **Scroll reveal infra**: one `IntersectionObserver` util + `.reveal/.in` CSS; wire stats, cards,
   gantt, calendar, day rows (respect `animate` flag).
3. **View transitions**: tab switch + theme toggle (View Transitions API + fallback).
4. **Component polish**: gantt grow-in, calendar pop, card hover/exit, modal refine, button ripple.
5. **Page-load choreography** (§7).
6. **A11y/perf pass** (§9) + cross-browser + 320px responsive re-check.
7. Update `README.md` motion notes; `python build_tracker.py` to refresh `public/`; commit
   feature-wise; push.

---

## 11. Acceptance criteria (QA checklist)
- [ ] Offline `file://` open: all motion works, no console errors, no CDN calls.
- [ ] `prefers-reduced-motion: reduce`: zero non-essential motion; everything instantly usable.
- [ ] Tab switch animates with spatial continuity; no flash of unstyled/empty content.
- [ ] Cards/gantt/calendar reveal on scroll once, staggered; filtering/searching does **not** re-animate.
- [ ] Count-up triggers when stats enter view; numbers land on correct values.
- [ ] 60fps on a mid laptop (DevTools Performance: no long tasks > 50ms during scroll).
- [ ] No layout shift (CLS ≈ 0); only transform/opacity animated.
- [ ] Focus rings, keyboard nav, `Esc`-to-close, AA contrast all unchanged.
- [ ] `build_tracker.py` still injects seed (data intact: 18 projects / 48 engagement days); `public/` refreshed.
- [ ] Works in light, dark, and auto themes.

---

## 12. Reusable snippet patterns
```js
// RM-safe animation wrapper (works with Motion One OR WAAPI)
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
function anim(el, keyframes, opts){
  if (RM || !el) return;                  // reduced-motion → no-op (final state already in DOM)
  el.animate(keyframes, { duration:320, easing:'cubic-bezier(.2,.7,.2,1)', fill:'both', ...opts });
}

// Reveal-on-scroll (one observer for all)
const io = new IntersectionObserver((entries)=>{
  for (const e of entries) if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
}, { threshold:.15, rootMargin:'0px 0px -10% 0px' });
document.querySelectorAll('[data-reveal]').forEach(el=>RM?el.classList.add('in'):io.observe(el));
```
```css
[data-reveal]{opacity:0;transform:translateY(12px)}
[data-reveal].in{opacity:1;transform:none;transition:opacity var(--dur-3) var(--ease-out),transform var(--dur-3) var(--ease-out)}
@media (prefers-reduced-motion:reduce){[data-reveal]{opacity:1;transform:none;transition:none}}
```

---

**Definition of done:** the dashboard *feels* motion-designed — load, scroll, tab-switch, and
hover all have intentional, fast, accessible motion — with **no** regression to data, offline use,
WCAG, or the `build_tracker.py` seed contract.
