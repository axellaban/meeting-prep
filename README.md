# ⚡ Meeting Prep OS

Un agente que se despierta solo cada mañana, lee tu Google Calendar, investiga a
las personas con las que te vas a reunir y publica un dashboard con briefing,
inteligencia competitiva, guion de conversación, quiz y flashcards.

Vos ponés `#prep` en el título de un evento. A la mañana siguiente está listo.

**→ [Cómo ponerlo a andar](SETUP.md)** · unos 15 minutos

---

## Ponerlo a andar

Necesitás plan pago de Claude — el que incluye **Routines**.

1. **Creá tu repo desde el template** ([meeting-prep-OS](https://github.com/axellaban/meeting-prep-OS),
   botón «Use this template»). **Marcalo privado**: los briefings van a tener research
   sobre personas reales, con nombre y apellido.
2. **Conectá Google Calendar** en claude.ai → Connectors.
3. **Abrí tu repo en Claude Code** y escribí `/setup`. Te pregunta nombre, calendario,
   horario y método de venta, y deja todo configurado.
4. **Creá la Routine** en claude.ai → Routines, **adjuntando el conector de Google
   Calendar** y pegando el prompt que te da el `/setup`.
5. **Importá el repo en [vercel.com/new](https://vercel.com/new)** → Deploy, sin tocar
   nada. Sin esto los dashboards existen como archivos pero no podés abrirlos del
   celular, que es cuando los vas a querer.

*Opcional:* conectá **Firecrawl** — mejora el research, y si falla el sistema sigue igual.

> **Dos cosas que se confunden seguido.** Conectar un conector en tu cuenta **no** lo
> adjunta a la rutina: son dos pasos distintos, el 2 y el 4. Y el repo tiene que ser
> **tuyo** — si clonás este directamente no vas a poder pushear, y el agente va a fallar
> todas las mañanas al publicar.

Detalle completo en **[SETUP.md](SETUP.md)**.

---

## Cómo funciona

```
Routine diaria  →  sesión efímera  →  Google Calendar   →  research web
   (tu hora)         (sin memoria)      (eventos #prep)      (8-15 fuentes)
                            │
                            ↓
                  generate_dashboard.py  →  git push  →  Vercel
```

La sesión que corre el pipeline es **descartable**: nace a la hora configurada, no
recuerda nada de ayer y se destruye al terminar. Todo lo que la hace funcionar —
instrucciones, generador, historial — vive en este repo.

**El repo es a la vez el programa y la memoria.** Cambiar el comportamiento del
agente es hacer un commit, no reconfigurar nada.

---

## Qué trae cada dashboard

| Pestaña | Contenido |
|---|---|
| **Executive Briefing** | Perfil de la persona y la empresa, oportunidad de mercado, guion de conversación, manejo de objeciones, próximos pasos |
| **Competitive Intel** | Contra quién competís de verdad, números para soltar, quién más está en su órbita |
| **Deep Research** | Fuentes, evidencia y **limitaciones declaradas** del research |
| **Fuentes** | Cada URL usada, agrupada y con qué aportó — el research es auditable |
| **Knowledge Test** | Quiz de opción múltiple con corrección al toque |
| **Flashcards** | Tarjetas para repasar en los minutos previos |
| **Brief Post-Reunión** | Se completa después, con lo que realmente pasó |

Más botón de **Exportar PDF** y lectura del briefing **en voz alta**, para
escucharlo camino a la reunión.

---

## Privacidad

Todo corre en **tu** cuenta de Claude, con **tu** conector de Google Calendar, y
se guarda en **tu** repo. Los datos de tus reuniones y el research sobre las
personas no pasan por ningún servidor de terceros.

Por eso conviene que el repo sea **privado**.

---

## Estructura

```
meeting-prep/
├── config.json                         # Tu configuración — empezá por acá
├── SETUP.md                            # Guía de instalación
├── index.html                          # Portal
├── meetings.json                       # Registro de reuniones
├── frameworks/                         # Guiones de conversación enchufables
│   ├── generic.md · kona-4w.md · spin.md · meddic.md
├── templates/dashboard.html            # Diseño de todos los dashboards
├── tools/
│   ├── generate_dashboard.py           # Spec JSON → dashboard + registro
│   └── verify.py                       # Chequea que el repo esté sano
├── assets/marked.min.js                # Renderer de markdown (vendorizado)
├── meetings/<id>/index.html            # Un dashboard por reunión
├── docs/arquitectura.html              # Cómo se conectan las piezas
├── runs/                               # Bitácora de corridas con incidencias
└── .claude/skills/
    ├── setup/                          # /setup — configuración inicial
    └── meeting-prep-daily/             # El pipeline que corre cada día
```

---

## Personalizarlo

| Qué | Dónde |
|---|---|
| Nombre, calendario, hora, etiqueta, idioma | `config.json` |
| El guion de conversación | `pipeline.framework` + `frameworks/` |
| Cómo investiga y cuánta densidad exige | `.claude/skills/meeting-prep-daily/SKILL.md` |
| El diseño | `templates/dashboard.html` |

---

## Stack

- **Calendario:** conector de Google Calendar de Claude — sin OAuth propio ni verificación
- **Research:** Firecrawl con fallback automático a WebSearch + WebFetch
- **Generación:** Python sin dependencias, sobre un template único
- **Frontend:** HTML/CSS/JS puro, sin build step
- **Deploy:** Vercel, automático desde GitHub
- **Automatización:** Routines de Claude — una sesión nueva cada mañana

> **Sobre el research.** Firecrawl corre en cada preparación, pero **nunca es un punto
> único de falla**: cada llamada tiene su reemplazo con `WebSearch` / `WebFetch`, así que
> si el conector se cae o no lo configuraste, el pipeline sigue igual y lo anota en el
> reporte.
>
> **Descartados a propósito:** *NotebookLM* (sin API pública; la librería no oficial pide
> un volcado de tus cookies de Google, las mismas que abren Gmail y Drive), *Apollo*
> (sirve para prospectar, no para preparar una reunión ya agendada) y *Scrapling*
> (incompatible con proxies que terminan TLS). El motivo de cada uno está escrito en el
> skill del pipeline.

---

## Licencia

MIT. Cloná, adaptá y hacelo tuyo.
