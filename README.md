# ⚡ Meeting Prep OS

Sistema automático de preparación de reuniones. Revisa Google Calendar, investiga a cada persona/empresa con **Firecrawl** (search + scrape + deep research agent), y genera un dashboard HTML interactivo con briefing ejecutivo, intel competitiva, quiz y flashcards.

> **v2 — Claude Code + Firecrawl.** Esta versión migró de Cowork OS + NotebookLM a **Claude Code** (cloud) con el **MCP de Firecrawl** como motor de research. El pipeline completo está definido en [`CLAUDE.md`](CLAUDE.md).

## Cómo usar

### 1. Marcar una reunión para prep
Agregá `#prep` al título del evento en Google Calendar:
```
"Reunión con Juan García #prep"
"Discovery call - Empresa XYZ #prep"
"Follow up Pedro Ramirez #prep"
```

### 2. Correr el pipeline
Abrí una sesión de Claude Code (web o CLI) sobre este repo con los MCP de **Google Calendar** y **Firecrawl** conectados, y pedile:

> "Corré el pipeline de meeting prep"

Claude lee `CLAUDE.md`, busca los eventos `#prep` de hoy/mañana, investiga con Firecrawl, genera el dashboard y pushea al repo.

### 3. Ver el dashboard
- **Vercel:** `https://meeting-prep-axellaban.vercel.app` (auto-deploy desde GitHub)
- **Local:** abrí `index.html` directamente en el browser

---

## Estructura

```
meeting-prep/
├── CLAUDE.md                           # Pipeline del agente (Claude Code + Firecrawl)
├── index.html                          # Portal principal
├── meetings.json                       # Registro de todas las reuniones
├── vercel.json                         # Config Vercel
├── meetings/
│   └── YYYY-MM-DD-nombre-apellido/
│       └── index.html                  # Dashboard por reunión (offline-ready)
├── runs/                               # Logs de cada corrida
└── .github/workflows/
    └── daily-meeting-prep.yml          # Scaffold de automatización diaria (Fase 2)
```

---

## Stack

- **Fuente de datos:** Google Calendar MCP
- **Research:** Firecrawl MCP (`firecrawl_search`, `firecrawl_scrape`, `firecrawl_agent`)
- **Síntesis:** Claude (briefing, intel, deep research, quiz, flashcards)
- **Frontend:** HTML/CSS/JS puro, sin build step (Inter + Font Awesome + marked.js por CDN)
- **Deploy:** Vercel (auto-deploy desde GitHub)
- **Runtime:** Claude Code en la nube

---

## Roadmap

### ✅ Fase 1 — Migración a Claude Code + Firecrawl (actual)
- Pipeline en `CLAUDE.md`, research 100% Firecrawl (sin NotebookLM)
- Dashboards con tab "Fuentes" (URLs del research) en lugar del link a NotebookLM
- Repo en la nube, corrida manual/on-demand desde Claude Code

### 🔜 Fase 2 — Corrida diaria automática
- GitHub Actions con cron (7:00 AM ART) usando `claude-code-action` — ver scaffold en `.github/workflows/daily-meeting-prep.yml`
- Secrets necesarios: `ANTHROPIC_API_KEY`, `FIRECRAWL_API_KEY`, credenciales OAuth de Google Calendar (refresh token)

### 🔮 Fase 3 — SaaS multi-tenant para clientes
- **Auth:** login de clientes (Supabase Auth o Clerk)
- **Onboarding:** cada cliente conecta su Google Calendar (OAuth) y opcionalmente su API key de Firecrawl
- **Worker diario:** job programado por cliente que corre el pipeline con el **Claude Agent SDK** (mismo prompt de `CLAUDE.md`, credenciales del tenant)
- **Storage:** dashboards y meetings.json por tenant (DB + object storage en lugar de un repo git)
- **Frontend:** portal con login donde cada cliente ve solo sus reuniones
- **Billing:** Stripe (suscripción mensual)

---

*Meeting Prep OS · axellaban@gmail.com*
