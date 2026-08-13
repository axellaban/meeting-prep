# Poner Meeting Prep OS a andar

De repo clonado a sistema corriendo solo: unos 15 minutos.

## Lo que necesitás antes de empezar

| Requisito | Por qué | ¿Obligatorio? |
|---|---|---|
| Cuenta de **Claude con Routines** (Claude Code en la web) | Es lo que despierta al agente cada mañana | **Sí** — sin esto no hay automatización |
| **Google Calendar** conectado en claude.ai | De ahí salen las reuniones | **Sí** |
| Cuenta de **GitHub** | Guarda los dashboards y las instrucciones del agente | **Sí** |
| **Vercel** (gratis) | Publica el sitio para abrirlo del celular | Opcional |
| **Firecrawl** conectado | Mejora el research en sitios pesados | Opcional |

> **El punto importante:** el calendario se conecta a través del conector de Claude,
> que ya está verificado por Google. No tenés que crear ninguna app, ni pedir
> permisos, ni configurar OAuth.

---

## 1. Clonar el repo

Usá el botón **Use this template** en GitHub, o cloná y subilo a un repo propio.
Conviene que sea **privado**: los briefings van a tener research sobre personas reales.

## 2. Configurarlo

Abrí el repo en Claude Code y escribí:

```
/setup
```

El agente te va a preguntar tu nombre, cuál de tus calendarios usar, a qué hora
querés que corra y qué framework de conversación preferís. Escribe `config.json`
solo y te ofrece borrar las reuniones de ejemplo.

Si preferís hacerlo a mano, editá `config.json` directamente — está comentado.

## 3. Crear la Routine

Esto **hay que hacerlo desde la interfaz**: los conectores solo se adjuntan ahí.

1. Andá a **claude.ai → Routines → nueva rutina**
2. Elegí la hora (la misma que pusiste en `config.json`)
3. Adjuntá los conectores: **Google Calendar** (obligatorio) y **Firecrawl** (opcional)
4. Pegá este prompt:

```
Corré el pipeline diario de Meeting Prep OS.

Leé las instrucciones completas en `.claude/skills/meeting-prep-daily/SKILL.md`
y ejecutá los 5 pasos. La configuración del usuario está en `config.json`.

Si no hay ningún evento con la etiqueta configurada hoy o mañana: no generes nada,
no hagas commit. Reportá "sin reuniones para preparar" y terminá.

Corrés sin supervisión: ante una decisión ambigua elegí la opción razonable y
anotala en el reporte. Nunca inventes datos sobre una persona. No reportes éxito
si el push falló.
```

> **Un consejo de horario:** elegí un minuto que no sea `:00` ni `:30`. Todo el
> mundo pide las horas en punto y esos minutos están congestionados. `06:03` anda
> mejor que `06:00`.

## 4. Publicar el sitio (opcional)

**vercel.com/new** → importá tu repo → **Deploy**, sin cambiar nada. Vercel vuelve
a desplegar en cada push del agente.

Si el repo es privado, el sitio también nace privado. Revisá la configuración de
Vercel si querés compartirlo.

---

## Usarlo todos los días

Poné la etiqueta en el título del evento:

```
Reunión con Juan García #prep
```

Y listo. A la mañana siguiente el dashboard está hecho.

**Los días sin reuniones etiquetadas, el agente no hace nada.** No commitea, no
avisa. El silencio es el comportamiento correcto.

---

## Probar sin esperar a mañana

En Claude Code, sobre el repo:

```
Corré el pipeline de meeting prep para hoy y mañana
```

Para ver qué generaría sin escribir archivos:

```bash
python3 tools/generate_dashboard.py <spec.json> --dry-run
```

---

## Adaptarlo

| Qué querés cambiar | Dónde |
|---|---|
| Nombre, calendario, hora, etiqueta, idioma | `config.json` |
| El guion de conversación del briefing | `config.json` → `pipeline.framework`, y los archivos de `frameworks/` |
| Cómo investiga y qué exige de densidad | `.claude/skills/meeting-prep-daily/SKILL.md` |
| El diseño de todos los dashboards | `templates/dashboard.html` |
| El portal | `index.html` |

Los frameworks incluidos son `generic` (default), `kona-4w` (discovery consultiva),
`spin` y `meddic`. Para escribir uno propio, copiá `frameworks/generic.md`.

---

## Problemas frecuentes

**El agente dice que no encuentra Google Calendar.**
El conector no quedó adjunto a la Routine. Editala en claude.ai y agregalo — no
alcanza con tenerlo conectado en tu cuenta.

**Corrió pero no preparó nada.**
Casi siempre es que el evento no tiene la etiqueta, o que la etiqueta de
`config.json` no coincide con la que usás.

**El dashboard sale corto o genérico.**
El piso está en `pipeline.research.minContentChars`. Si la persona tiene poca
huella pública, el agente lo declara en la sección de fuentes en vez de rellenar.

**El sitio no se actualiza.**
Verificá que Vercel esté escuchando la rama de `publish.branch`, y que el push
del agente haya salido.
