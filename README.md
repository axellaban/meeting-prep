# ⚡ Meeting Prep OS

Sistema automático de preparación de reuniones. Revisa Google Calendar cada mañana, investiga a cada persona con NotebookLM + web research, y genera un dashboard HTML interactivo con briefing, intel competitiva, quiz y flashcards.

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
├── meetings/
│   └── 2026-03-28-marcos-pueyrredon/
│       └── index.html                  # Dashboard por reunión
└── README.md
```

---

## Stack

- **Fuente de datos:** Google Calendar MCP
- **Research:** NotebookLM MCP + web search
- **Frontend:** HTML/CSS/JS puro (sin build step)
- **Deploy:** Vercel (auto-deploy desde GitHub)
- **Automatización:** Cowork OS scheduled tasks

---

*Generado por Cowork OS · axellaban@gmail.com*
