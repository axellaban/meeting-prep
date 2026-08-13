# ⚡ Meeting Prep OS

Sistema automático de preparación de reuniones. Revisa Google Calendar cada mañana, investiga a cada persona con Firecrawl + búsqueda web, y genera un dashboard HTML interactivo con briefing, intel competitiva, quiz y flashcards.

## Cómo usar

### 1. Marcar una reunión para prep
Agregá `#prep` al título del evento en Google Calendar:
```
"Reunión con Juan García #prep"
"Discovery call - Empresa XYZ #prep"
"Follow up Pedro Ramirez #prep"
```

### 2. El sistema corre automáticamente
Todos los días a las **7:00 AM** (hora Argentina), el sistema:
1. Revisa Google Calendar buscando eventos del día con `#prep`
2. Investiga a la persona/empresa (web scraping + NotebookLM)
3. Genera el dashboard HTML completo
4. Hace commit y push a este repo
5. Vercel despliega automáticamente

### 3. Ver el dashboard
- **Vercel:** `https://meeting-prep-axellaban.vercel.app`
- **Local:** Abrí `index.html` directamente en el browser

---

## Setup inicial

```bash
# 1. Clonar / descargar este repo
# 2. Correr el setup script
chmod +x setup.sh
./setup.sh

# 3. Conectar con Vercel en https://vercel.com/new
```

---

## Estructura

```
meeting-prep/
├── index.html                          # Portal principal
├── meetings.json                       # Registro de todas las reuniones
├── vercel.json                         # Config Vercel
├── assets/
│   └── marked.min.js                   # Renderer de markdown (vendorizado)
├── templates/
│   └── dashboard.html                  # Template único de los dashboards
├── tools/
│   └── generate_dashboard.py           # Generador: spec JSON → dashboard + registro
├── meetings/
│   └── 2026-03-28-marcos-pueyrredon/
│       └── index.html                  # Dashboard por reunión
├── runs/                               # Logs de corridas con incidencias
├── .claude/skills/meeting-prep-daily/  # Instrucciones del pipeline automático
└── README.md
```

---

## Stack

- **Fuente de datos:** Google Calendar MCP
- **Research:** Firecrawl MCP + WebSearch
- **Frontend:** HTML/CSS/JS puro (sin build step)
- **Deploy:** Vercel (auto-deploy desde GitHub)
- **Automatización:** Routine diaria de Claude Code (sesión nueva cada mañana)

> **Nota sobre NotebookLM:** el diseño original preveía NotebookLM para el research,
> pero no existe como conector — no tiene API pública ni servidor MCP. El research
> corre con Firecrawl + búsqueda web, que sí están conectados. Los quiz y flashcards
> los genera el modelo directamente.

### Generar un dashboard a mano

```bash
python3 tools/generate_dashboard.py mi-spec.json
```

El formato del spec está documentado en `.claude/skills/meeting-prep-daily/SKILL.md`.

---

*Generado por Cowork OS · axellaban@gmail.com*
