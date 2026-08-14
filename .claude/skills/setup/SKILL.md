---
name: setup
description: Configura Meeting Prep OS para un usuario nuevo que acaba de clonar el repo. Pregunta los datos, detecta el calendario, escribe config.json, limpia las reuniones de demo y deja lista la Routine diaria. Disparadores - "configurá esto", "setup", "recién cloné el repo", "cómo lo pongo a andar", "adaptalo a mí".
---

# Setup de Meeting Prep OS

Alguien acaba de clonar este repo y lo quiere andando con **su** calendario, **su**
marca y **su** método de venta. Tu trabajo es dejarlo listo en una sola conversación.

Sé breve. Preguntá de a poco, no tires un formulario de doce campos.

## Antes de preguntar nada, mirá qué hay

1. ¿Está el conector de Google Calendar en esta sesión? Probá
   `mcp__Google_Calendar__list_calendars`. Si responde, ya tenés los calendarios
   disponibles y el mail del usuario — **no se los preguntes, ofrecéselos**.
2. Leé `config.json` si existe. Si ya está configurado con datos de otra persona
   (el default trae los del autor original), avisá que vas a reemplazarlos.

Si el conector **no** está, no te frenes: seguí con el resto y al final decile que
lo conecte en claude.ai → Connectors, porque sin eso el pipeline no puede detectar
reuniones.

## Lo que hay que averiguar

Preguntá en dos o tres tandas cortas, no todo junto:

**Tanda 1 — quién es**
- Nombre completo (va en el portal y en los briefings)
- Cuál de sus calendarios usar (ofrecé la lista que trajo el conector)
- Zona horaria (deducila del calendario; confirmá, no preguntes desde cero)

**Tanda 2 — cómo trabaja**
- ¿A qué hora quiere que corra? Sugerí una hora temprana, y **evitá los minutos
  en punto**: `06:03` en vez de `06:00`, así no compite con todos los cron del mundo.
- ¿Qué etiqueta usa para marcar reuniones? Default `#prep`.
- ¿Qué framework de conversación? Mostrale las opciones de `frameworks/` con una
  línea cada una y recomendá `generic` si no vende de forma consultiva.

**Tanda 3 — marca (opcional)**
- Nombre del producto para el portal. Default: *Meeting Prep OS*.
- Si no le importa, no insistas: los defaults funcionan.

## Escribí `config.json`

Con eso armá el archivo. Campos: `owner` (name, shortName, email, calendarId,
timezone, utcOffset), `branding` (productName, navbarBrand, tagline, footerNote),
`pipeline` (language, detection.mode/tag/lookaheadDays, research.minSources/
maxSources/minContentChars, framework, cronLocal) y `publish` (branch, siteUrl).

Tomá el archivo existente como referencia de forma. `utcOffset` tiene que ser
coherente con `timezone`.

## Limpiá la demo

El repo viene con reuniones de ejemplo del autor original. Preguntá si las quiere
borrar. Si dice que sí:

- borrá los directorios de `meetings/`
- dejá `meetings.json` como `{"meetings": []}`
- corré cualquier generación posterior para que el portal se sincronice

Si dice que no, dejalas: sirven para ver cómo queda un dashboard terminado.

## Verificá antes de cantar victoria

```bash
python3 -c "import json;json.load(open('config.json'))"          # config válida
python3 tools/generate_dashboard.py <un-spec.json> --dry-run     # el generador corre
```

Si borraron la demo no vas a tener spec a mano; alcanza con validar el JSON y
confirmar que `templates/dashboard.html` y `tools/generate_dashboard.py` existen.

## Dejá andando la Routine

Esto **no lo podés hacer vos**: los conectores se adjuntan sólo desde la interfaz.
Dale el paso a paso exacto, con la hora ya convertida a UTC:

> 1. Andá a **claude.ai → Routines → nueva rutina**
> 2. Horario: `<la hora que eligió>` en su zona
> 3. Conectores: **Google Calendar** (obligatorio) y **Firecrawl** (recomendado)
> 4. Pegá este prompt:

```
Corré el pipeline diario de Meeting Prep OS.

1. Leé primero las instrucciones completas en `.claude/skills/meeting-prep-daily/SKILL.md`
   y la configuración del usuario en `config.json`.
2. Ejecutá todos los pasos que documenta ese archivo, del 0 al 5.
3. Si no hay eventos con la etiqueta configurada hoy ni mañana: no generes ningún
   dashboard, pero **escribí igual `runs/last-run.md` y commiteálo**. Es lo que hace
   demostrable que el sistema corrió. Reportá "sin reuniones para preparar" y terminá.
4. Corrés sin supervisión: ante una decisión ambigua elegí la opción razonable, seguí,
   y anotala en el reporte final.
5. Nunca inventes datos sobre una persona. Si no encontraste el rol, escribí
   "a confirmar al inicio del call". No reportes éxito si el push falló.
```

Recordale que **el cron de la interfaz se define en su hora local**, y que si quiere
publicar el sitio tiene que importar el repo en vercel.com/new (deploy sin cambiar
nada).

## Cerrá con el resumen

Tres líneas: qué quedó configurado, qué tiene que hacer él (crear la Routine, y
conectar Vercel si quiere el sitio público), y cómo se usa a diario — poner la
etiqueta en el título del evento y nada más.
