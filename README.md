# ⚡ Meeting Prep OS

Un agente que se despierta solo cada mañana, lee tu Google Calendar, investiga a
las personas con las que te vas a reunir y publica un dashboard con briefing,
inteligencia competitiva, guion de conversación, quiz y flashcards.

Vos ponés `#prep` en el título de un evento. A la mañana siguiente está listo.

**→ [Cómo ponerlo a andar](SETUP.md)** · unos 15 minutos

> **Empezá con el botón verde «Use this template»**, arriba a la derecha. Te crea tu
> propio repo. Hacelo **privado**: los briefings van a contener research sobre personas
> reales con nombre y apellido.

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
├── meetings/<id>/index.html            # Un dashboard por reunión (vacío al empezar)
├── runs/last-run.md                    # Prueba de vida: cuándo corrió y qué hizo
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
- **Research:** WebSearch + WebFetch, con Firecrawl para páginas que no rinden
- **Generación:** Python sin dependencias, sobre un template único
- **Frontend:** HTML/CSS/JS puro, sin build step
- **Deploy:** Vercel, automático desde GitHub
- **Automatización:** Routines de Claude — una sesión nueva cada mañana

> **Motores de research descartados, y por qué.** *NotebookLM*: no tiene API pública, y
> la librería no oficial autentica con un volcado de las cookies de Google del usuario —
> las mismas que abren Gmail, Drive y Cloud Console. *Apollo*: sirve para prospectar, no
> para preparar; cuando la reunión ya está agendada, ya sabés quién es. *Scrapling*: su
> vía rápida falsifica la huella TLS y no atraviesa proxies corporativos; su vía con
> navegador descarga ~600 MB por corrida. `WebSearch` + `WebFetch` resolvieron cada caso
> que probamos, sin secretos y sin instalar nada.

---

## Estado

Funciona y está en uso diario. Nació de un sistema personal, así que las decisiones
de diseño están tomadas y documentadas — incluidas las de **no** usar ciertas
herramientas, con el motivo escrito en el skill del pipeline.

Si lo adaptás y algo te resulta confuso, abrí un issue: probablemente la documentación
esté asumiendo contexto que sólo tenía el autor.

## Licencia

MIT. Cloná, adaptá y hacelo tuyo.
