# CLAUDE.md — Meeting Prep OS

This file provides context for AI assistants (Claude Code and others) working in this repository.

---

## Project Overview

**Meeting Prep OS** is a personal, automated meeting preparation system. It generates interactive HTML dashboards for upcoming meetings by researching people and companies via NotebookLM + web search, then deploying the result as a static site on Vercel.

- **Owner:** Axel Laban (axellaban@gmail.com)
- **Live URL:** https://meeting-prep-axellaban.vercel.app
- **Primary language:** Spanish (UI text, commit messages, README)
- **No build step required** — pure static HTML/CSS/JS

---

## Repository Structure

```
meeting-prep/
├── index.html                          # Main portal dashboard (lists all meetings)
├── meetings.json                       # Registry/manifest of all meetings
├── vercel.json                         # Vercel static hosting config
├── setup.sh                            # One-time Git init & remote setup script
├── README.md                           # User-facing documentation (Spanish)
├── CLAUDE.md                           # This file
└── meetings/
    └── YYYY-MM-DD-person-name/
        └── index.html                  # Individual meeting dashboard
```

### Key Files

| File | Role |
|---|---|
| `index.html` | Portal page: fetches `meetings.json`, renders meeting cards grouped by today/upcoming/past |
| `meetings.json` | Single source of truth for all meetings — read by the portal at runtime |
| `meetings/<id>/index.html` | Self-contained per-meeting dashboard with briefing, research, quiz, flashcards |
| `vercel.json` | Serves all `.html` and `.json` files statically; disables caching |

---

## How the System Works

### Automation Flow (external, not in this repo)

1. Daily at **7:00 AM Argentina time**, a scheduled task (Cowork OS) triggers
2. It reads Google Calendar looking for events tagged `#prep`
3. For each such event, it researches the person/company via NotebookLM MCP + web search
4. It generates a new `meetings/<id>/index.html` dashboard
5. It adds the meeting entry to `meetings.json`
6. It commits and pushes to this repo
7. Vercel auto-deploys within seconds

### Manual Flow (adding a meeting by hand)

1. Create directory: `meetings/YYYY-MM-DD-person-name/`
2. Create `meetings/YYYY-MM-DD-person-name/index.html` following the dashboard template (see below)
3. Add an entry to `meetings.json`
4. Commit and push — Vercel will deploy automatically

---

## meetings.json Schema

Each entry in the `meetings` array must follow this structure:

```json
{
  "id": "YYYY-MM-DD-person-name",          // kebab-case, must match directory name
  "date": "YYYY-MM-DD",
  "time": "HH:MM",                          // 24h format, local Argentina time
  "person": "Full Name",
  "title": "Job Title",
  "company": "Company Name",
  "type": "Business meeting",               // free text describing meeting type
  "tags": ["Tag1", "Tag2"],                 // array of short topic labels
  "notebooklm_url": "https://...",          // NotebookLM notebook URL (or null)
  "sources_count": 16,                      // number of research sources used
  "path": "meetings/YYYY-MM-DD-person-name/index.html",
  "generated": "YYYY-MM-DDTHH:MM:SSZ"      // ISO 8601 UTC timestamp of generation
}
```

---

## Individual Meeting Dashboard — Structure & Template

Each `meetings/<id>/index.html` is a **self-contained single file** (no external assets besides CDN). It follows a fixed layout:

### CDN Dependencies (always include in `<head>`)

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
```

### Layout Structure

```
Fixed Navbar (60px height)
  └── Brand logo | Person name + company | Date badge | Export button
Page Layout (flex row, padding-top: 60px)
  ├── Sidebar (240px, fixed)
  │     └── Nav items linking to each section via anchor IDs
  └── Main content (flex-grow)
        ├── #briefing    — Executive summary, key facts
        ├── #research    — Deep research notes (markdown rendered via marked.js)
        ├── #intel       — Competitive / strategic intelligence
        ├── #quiz        — Quiz cards for preparation practice
        └── #flashcards  — Flashcard-style key facts
```

### CSS Design System (use these variables consistently)

```css
:root {
  --bg: #08080c;                          /* page background */
  --gold: #f0b429;                        /* primary accent */
  --gold-soft: #fcd34d;                   /* lighter gold */
  --blue: #3b82f6;                        /* secondary accent */
  --blue-light: #60a5fa;
  --blue-deep: #1d4ed8;
  --glass: rgba(255,255,255,0.05);        /* card background */
  --glass-border: rgba(255,255,255,0.08); /* card border */
  --glass-hover: rgba(255,255,255,0.08);
  --text: #f1f5f9;                        /* primary text */
  --text-muted: #94a3b8;                  /* secondary text */
  --sidebar-w: 240px;
}
```

### Visual Conventions

- **Theme:** Dark (near-black `#08080c`) with glassmorphic cards
- **Glassmorphic cards:** `background: var(--glass); border: 1px solid var(--glass-border); backdrop-filter: blur(12px); border-radius: 12px;`
- **Body radial gradients:** Blue top-left, gold bottom-right (subtle, `pointer-events: none; z-index: 0`)
- **Mobile breakpoint:** `640px` — sidebar collapses, layout shifts to single column
- **Spacing scale:** 4, 8, 12, 16, 20, 24, 32, 40, 48px
- **Border radius:** 8px (small), 10–14px (cards), 999px (pills/badges)
- **Typography:** Inter font, weights 300/400/500/600/700/800

### Standard Component Patterns

**Badge/pill:**
```css
background: rgba(240,180,41,0.12);
border: 1px solid rgba(240,180,41,0.3);
color: var(--gold);
padding: 4px 12px; border-radius: 999px;
font-size: 12px; font-weight: 600;
```

**Export button:**
```css
background: linear-gradient(135deg, var(--blue-deep), var(--blue));
border: none; color: white;
padding: 7px 16px; border-radius: 8px;
font-size: 13px; font-weight: 600; cursor: pointer;
```

**Section header colors:** Use `var(--gold)` for briefing/flashcards, `var(--blue)` for research/intel sections.

---

## Portal Dashboard (index.html)

The portal (`index.html`) is the main entry point. It:

1. **Fetches `meetings.json`** via `fetch('meetings.json')` on page load
2. Falls back to an inline `INLINE_MEETINGS` array if the fetch fails (offline support)
3. **Categorizes meetings** into: today, upcoming (future), past
4. Renders responsive grid cards with avatar (initials-based), tags, company, and link to the meeting dashboard
5. Shows statistics: total meetings, unique companies, total research sources

### Avatar color generation

Avatars use deterministic color generation from initials — consistent across page loads:
```js
function getInitialsColor(name) {
  let hash = 0;
  for (let c of name) hash = ((hash << 5) - hash) + c.charCodeAt(0);
  const hue = Math.abs(hash) % 360;
  return `hsl(${hue}, 60%, 40%)`;
}
```

---

## Git Conventions

- **Commit language:** Spanish
- **Commit prefix style:** `feat:`, `fix:`, `chore:`, etc.
- **Branch naming for AI work:** `claude/<description>-<id>` (e.g., `claude/add-claude-documentation-j9X5O`)
- **Main branch:** `main` (auto-deploys to Vercel)
- **Never commit:** `.DS_Store`, `.env`, `node_modules/`, `.vercel/`, `pixel-agents/`
- The `pixel-agents/` directory is a nested repo — do not touch it

### Deployment

- Pushing to `main` triggers an automatic Vercel deploy (no build step)
- `vercel.json` serves all `*.html` and `*.json` files statically
- Caching is disabled (`no-cache, no-store`) so new meetings appear immediately

---

## Development Workflow

### Adding a new meeting manually

```bash
# 1. Create the meeting directory
mkdir -p meetings/YYYY-MM-DD-person-name

# 2. Create the dashboard (follow the template above)
# meetings/YYYY-MM-DD-person-name/index.html

# 3. Add entry to meetings.json (follow schema above)

# 4. Commit and push
git add meetings/YYYY-MM-DD-person-name/index.html meetings.json
git commit -m "feat: agregar reunión con Person Name - Company"
git push origin main
```

### Viewing locally

No server required. Open directly in browser:
```bash
open index.html
# or
open meetings/YYYY-MM-DD-person-name/index.html
```

---

## What NOT to do

- Do not add a build system, bundler, or package manager — this is intentionally zero-dependency
- Do not add a backend or server-side code
- Do not introduce CSS frameworks (Tailwind, Bootstrap) — maintain the existing custom CSS
- Do not change the `meetings.json` schema without updating all consumers (`index.html` and any automation scripts)
- Do not add React, Vue, or any JS framework — vanilla JS only
- Do not remove the CDN fallback (`INLINE_MEETINGS`) from `index.html` — it enables offline viewing
- Do not modify `vercel.json` routing without testing locally first
