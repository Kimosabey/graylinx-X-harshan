# Harshan × Graylinx — Work Tracker & Showcase

A self-contained dashboard + spreadsheets to **track and showcase** all of Harshan's work at
Graylinx, from **22 Apr 2026** to today. Two linked stories:

- **Projects & Timeline** — *what was built* (from git history + filesystem dates)
- **Engagement & Deployment** — *how the engagement ran* (from the day-by-day attendance log)

Design: **accessible monochrome neumorphism** (soft-UI, black-and-white shades), with the
Graylinx logo in brand blue, **Lucide** icons, **Lenis** smooth scroll, a hidden scrollbar +
scroll-progress bar, subtle parallax, micro-animations, and a fully responsive layout.

## Files

| File | What it is |
|---|---|
| **`index.html`** | The dashboard. **Double-click to open** (offline; loads only `lenis.min.js`). |
| `lenis.min.js` | Vendored [Lenis](https://lenis.studiofreight.com/) smooth-scroll library (offline-safe). |
| `works.csv` | Projects + milestones spreadsheet — opens in Excel / Google Sheets. |
| `engagement.csv` | Day-by-day engagement log (ISO dates). |
| `works.json` | Full dataset (both tables) — machine-readable backup / re-import. |
| `works.xlsx` | Styled workbook: **Projects** + **Engagement** sheets. |
| `build_tracker.py` | Regenerator — re-reads git/files + the attendance CSV and rebuilds everything. |
| `netlify.toml` + `public/` | Static deploy config + the assembled deploy directory. |

### Source inputs (read-only)
`graylinxLogo.png`, `IMG-20230616-WA0000.jpg` (header avatar),
`Harshan X Graylinx Deployment Tracker 2026(Deployment Attendance).csv` (engagement source).

## Use it

### View & showcase
Open `index.html`. Switch between **Projects & Timeline** and **Engagement & Deployment**.
**Print** for a clean PDF; toggle **light / dark / auto** theme (button cycles all three).

### Keep it updated
1. **In the browser (live):** **＋ Add**, or click any project card / calendar day to edit.
   Saves to this device (`localStorage`). **Export** CSV/JSON, **Import** to restore, **Reset**
   to reload the seed.
2. **From source (regenerate):** `python build_tracker.py` — re-pulls real dates, rebuilds the
   datasets, re-injects the seed into `index.html`, and refreshes `public/`.

> Dates: **git** (exact, 4 repos) · **filesystem mtimes** (`approx`, non-git projects) ·
> the **attendance CSV** (22-Apr→25-May) · then **carried forward** to today — git-active days
> are `derived`, the rest flagged **`needs-fill`** (hatched on the calendar) to complete.

### Finish the engagement log
Engagement → **Show: Needs filling** → click each hatched day and add work type / location / notes.

## Deploy to Netlify (continuous deploy from GitHub)

The site is static — no build step (data is embedded in `index.html`); Netlify just serves `public/`.

1. Push this repo to GitHub (`Kimosabey/graylinx-X-harshan`, branch `main`).
2. In Netlify → **Add new site → Import an existing project → GitHub** → pick the repo.
3. Build command: *(leave empty)* · Publish directory: **`public`** (already set in `netlify.toml`).
4. Deploy. Every push to `main` auto-redeploys.

*CLI alternative:* `netlify login` then `netlify deploy --prod --dir=public`.

> Privacy: the deployed site and repo show **full** engagement detail (hotels, travel, notes).
> Make the GitHub repo **private** if you want it internal-only.

## Design & accessibility

Monochrome neumorphism on a neutral base (`#ECECEC` light / `#1C1C1C` dark); depth from dual
soft shadows. Status & work-type are shown by **grayscale + glyph + label** (never colour
alone). Solid 2px focus rings (neumorphism done accessibly), ≥44px targets, keyboard + `Esc`,
honours `prefers-reduced-motion` (disables Lenis/animations) and `prefers-color-scheme`.

### Verified contrast (WCAG 2.1)

| Pair | Ratio | Grade |
|---|---|---|
| Body ink `#171717` on `#ECECEC` | 15.2:1 | AAA |
| Secondary `#4B4B4B` on `#ECECEC` | 7.4:1 | AAA |
| Tertiary `#5C5C5C` on `#ECECEC` | 5.7:1 | AA |
| Dark ink `#F2F2F2` on `#1C1C1C` | 15.2:1 | AAA |
| Dark secondary `#B2B2B2` on `#1C1C1C` | 8.0:1 | AAA |
| Dark tertiary `#8C8C8C` on `#1C1C1C` | 5.1:1 | AA |
| WFH chip `#171717` on `#ABABAB` | 7.8:1 | AAA |
| Discussion chip `#F2F2F2` on `#5C5C5C` | 6.0:1 | AA |

## Data model

**Projects** (`type` = `project` | `milestone`; milestones link via `parent_id`):
`id, name, category, description, role, tech, start, end, date_source, status, progress,
commits, location, highlights`. Categories: HVAC Platform · Graylinx Core · SelfAware Suite ·
Voice AI · Client Apps · Infra & Tooling. Statuses: Active · Ongoing · Done · Paused · Planned · At-risk.

**Engagement** (one row per day): `date, day, work_type (Office/Discussion/WFH/Leave),
location, hotel, check_in, check_out, travel, notes, linked_project,
source (csv/derived/manual/needs-fill)`.
