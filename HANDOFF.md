# HANDOFF — Harshan × Graylinx Work Tracker

> Paste this into a new chat to continue seamlessly. It captures the full state, decisions,
> gotchas, and what's queued. Last commit at handoff: **`e0beba4`** on `main`.

## 1. What this is
A self-contained dashboard + spreadsheets that **track and showcase all of Harshan's work at
Graylinx** (projects, timeline, day-by-day engagement, analytics). Built iteratively; live and deployed.

- **Working dir:** `D:\Harshan\Graylinx X Harshan\`
- **GitHub:** `git@github.com:Kimosabey/graylinx-X-harshan.git` (branch `main`); SSH key wired via
  repo `core.sshCommand` → `D:/Harshan/kimo-ssh-keys/graylinx-ssh-laptop`. `gh` CLI authed as **Kimosabey**.
- **Live:** https://graylinxxharshan.netlify.app (auto-deploys on push from GitHub).
- **Commit identity:** `Harshan Aiyappa <harshan.aiyappa@gmail.com>`; commit trailer
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

## 2. Architecture
- **`index.html`** — the whole app (inline CSS + JS). Loads sibling `lenis.min.js` + `echarts.min.js`.
  Data is embedded in `<script id="seed-data" type="application/json">…</script>` (⚠ **never rename
  that tag/id** — the build injects into it). `load()` keeps localStorage edits only when
  `stored.meta.build === SEED.meta.build`, else reloads fresh seed (anti-stale).
- **`build_tracker.py`** — source-of-truth generator. Reads a curated `PROJECTS` catalogue + live
  **git** (incl. nested repos) + **filesystem mtimes** + the **attendance CSV** + per-day commit
  subjects; writes `works.csv`, `engagement.csv`, `works.json`, styled `works.xlsx`; injects the seed
  into `index.html`; builds the **`public/`** deploy dir. Run: `python build_tracker.py`.
- **Vendored (offline-safe, no runtime CDN):** `lenis.min.js` (smooth scroll), `echarts.min.js`
  (analytics), `SpaceGrotesk.woff2` (display font — vendored but **not yet wired**, for the queued redesign).
- **`netlify.toml`** publishes `public/` (no build step; seed is embedded). `PUBLIC_FILES` in
  build_tracker.py controls what lands in `public/`.
- **`.gitignore`** excludes `.claude/`, `_handoff/`, `graylinx-X-harshan-handoff/`, `_drop/`, `*.zip`, `__pycache__/`.

## 3. Data (current numbers)
**22 projects · 900 commits · 55 engagement days (0 needs-fill) · span Oct 2025 → Jun 2026.**

- **Date reconciliation (RESOLVED — important):** Harshan has **two GitHub accounts**:
  `harshan-aiyappa` (original — HVAC pipeline v1/v2, genuinely **Nov 2025**, matches his emails) and
  `Kimosabey` (the **2026** rebuilds: clima-stream, thermynx, omnyx, nesso, SelfAware×6, etc.).
  GitHub server `created_at` timestamps are authoritative (can't be clock-faked) → **2026 is real**;
  the 2025 emails are the earlier POC phase. **Do NOT apply a −1-year shift.**
- **date_source tags:** `git` (local) / `github` (gh/zip-confirmed) / `approx` (filesystem mtimes,
  ~9 non-git projects like gl-pulse, Docs, VOXARA, konva) / `email` / `manual`.
- **Engagement** = attendance CSV (Apr–May 2026, real on-site/WFH/hotel/travel) + git-derived days
  (with real commit-subject notes) + 8 **gap days** filled as **Lingotran task + RAPL/Examic
  recruitment interviews** (see memory).
- **Collaborators:** J. Suryanarayanan, Satish Krishna, Raghunandan Srinath (`@graylinx.ai`).
- `harshan-aiyappa` repos are private to that account → `Kimosabey`'s `gh` token 404s; pulled HVAC
  v1/v2 from user-provided ZIPs (extracted to gitignored `_drop/`, now locked but harmless).

## 4. UI features shipped
- **4 tabs:** **Projects** (cards + filters/sort/density) · **Timeline** (own tab: category-coloured
  gantt bars, status dot by name, ◆ milestone diamonds, own filters, today line) · **Engagement**
  (calendar w/ work-type glyphs O/D/W/L + today ring + daily log) · **Analytics** (ECharts: calendar
  heatmap, cumulative-commits area, category/work-type donuts, weekday + project/status bars).
- **Command palette** (Ctrl/⌘K) — search projects/days/actions. **Theme** light/dark/auto (button shows
  current). **Accent** = cobalt `#0123B4` (from logo). **Per-category accents** on cards + gantt.
- **Animated aurora-gradient bg** + drifting orbs + scroll-progress bar (Lenis). **Add/Edit/Delete**
  in-browser (localStorage), **Export/Import CSV/JSON**, **Print/PDF**, **Reset**.
- **Accessibility:** WCAG-AA validated (contrast script in chat history); solid focus rings; keyboard +
  Esc; `prefers-reduced-motion` disables all motion; `prefers-color-scheme`.

## 5. Gotchas / conventions
- After `python build_tracker.py` rewrites `index.html` (seed), **re-Read it before Edit** (harness
  file-state). `node --check` the extracted last `<script>` after JS edits.
- `works.xlsx` is made **byte-deterministic** (`_normalize_xlsx` rewrites zip + normalizes
  `docProps/core.xml` timestamp) so rebuilds don't churn git.
- LF→CRLF git warnings on Windows are harmless.
- Commit **feature-wise**; `public/` is regenerated each build (commit it — Netlify serves it).

## 6. Queued work (approved, not yet built) — the 2026 "statement" redesign
Plan file: `C:\Users\Harshan Aiyappa\.claude\plans\i-need-track-my-mutable-star.md`. User approved all 4:
1. **Expressive identity** — wire the vendored variable font (`--font-display`), **OLED theme**
   (light→dark→oled→auto), glass app-bar, **accent-color picker**, subtle grain.
2. **Bento Overview tab** (new default landing: hero stat + sparkline + tiles) + **Dev-Wrapped 2026**
   recap overlay with PNG export (SVG→canvas, no new lib).
3. **Data-viz centerpieces** — force-directed **project↔tech graph**, **Bangalore↔Mysore travel map**
   (ECharts scatter+lines), self-drawing gantt on scroll.
4. **Motion** — View Transitions API tab morphs, card tilt, magnetic buttons, digit-roll numerals.
Phased + each shippable; keep all guardrails in §5 and AA/reduced-motion.

Optional refinements discussed: Timeline group-by toggle (category↔status↔flat); pull more
`harshan-aiyappa` repos if its `gh` auth is added; trim ECharts weight (lazy-load) if needed.

## 7. Persistent memory (auto-loaded in new sessions here)
`C:\Users\Harshan Aiyappa\.claude\projects\d--Harshan-Graylinx-X-Harshan\memory\`
- `gap-days-lingotran-recruitment.md` — gap days = Lingotran + RAPL/Examic interviews.
- `collaborators-and-email-works.md` — teammates + 2025/2026 date resolution + two-accounts fact.

## 8. Verify / run
```
python build_tracker.py          # regenerate data + inject seed + build public/
# double-click index.html (offline) — 4 tabs, all features
git add … && git commit && git push origin main   # → Netlify auto-deploys
```
End state: data-complete for everything provided; IA clean; live. Next: start the §6 redesign (Phase 1).
