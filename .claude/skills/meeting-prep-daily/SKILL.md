---
name: meeting-prep-daily
description: Pipeline diario de Meeting Prep OS. Lee Google Calendar, detecta los eventos etiquetados para preparar, investiga a cada persona con búsqueda web, genera el dashboard HTML y publica vía git push. Se dispara por Routine a la hora configurada en config.json, o manualmente cuando el usuario pide "corré el meeting prep".
---

# Meeting Prep OS — Pipeline diario

Preparás al dueño de este repo para sus reuniones antes de que empiecen. Corrés sin
supervisión: nadie va a contestar preguntas a mitad de la ejecución. Ante una
decisión ambigua, tomá la opción razonable, seguí, y dejala anotada en el reporte.

## Paso 0 — Leé la configuración

**Antes que nada, leé `config.json`.** De ahí sale todo lo que cambia entre usuarios:

| Campo | Para qué |
|---|---|
| `owner.calendarId` | Qué calendario consultar |
| `owner.timezone` / `utcOffset` | Cómo interpretar «hoy» y «mañana» |
| `owner.name` / `shortName` | A quién estás preparando |
| `pipeline.detection.tag` | La etiqueta a buscar (default `#prep`) |
| `pipeline.detection.lookaheadDays` | Cuántos días hacia adelante mirar |
| `pipeline.language` | Idioma de todo el contenido generado |
| `pipeline.research.minSources` / `maxSources` | Cuántas fuentes buscar |
| `pipeline.research.minContentChars` | Piso de densidad del dashboard |
| `pipeline.framework` | Qué archivo de `frameworks/` usar en la sección 4 |
| `publish.branch` | A qué rama pushear |

Si `config.json` no existe, usá los defaults (`#prep`, 1 día, español, `main`) y
decilo en el reporte final. **No inventes un calendario**: sin `calendarId` usá el
primario del conector.

En este documento, donde diga `#prep` leé «la etiqueta configurada», y donde diga
`main` leé «la rama configurada».

## Contexto de herramientas

| Necesidad | Herramienta | Estado |
|---|---|---|
| Calendario | `mcp__Google_Calendar__list_events` | ✅ **sin esto no hay pipeline** |
| Research primario | `WebSearch` + `WebFetch` | ✅ siempre disponibles |
| Páginas difíciles | `mcp__Firecrawl__*` | ⚙️ opcional, sólo cuando hace falta |

**`WebSearch` es el motor, no el respaldo.** Medido sobre un mismo target devolvió
historial laboral y registro corporativo que el scraping especializado no trajo, y
sintetiza en prosa en vez de devolver links crudos. `WebFetch` extrajo el mismo
contenido que un scraper dedicado sobre la misma página, incluidos precios.

**Firecrawl entra sólo cuando `WebFetch` falla o vuelve vacío:** sitios que renderizan
todo con JS, extracción estructurada con schema (`jsonOptions`), o páginas que
bloquean el fetch simple (probá `proxy: "stealth"`). Si no está disponible, no es un
bloqueante: seguí y anotalo en el reporte.

**LinkedIn está cerrado y así se queda.** Ni el scraper dedicado ni el fetch simple
pasan. El headline y los títulos de publicaciones salen de los *snippets* de búsqueda,
que sí los exponen. No pierdas intentos, y no intentes saltear su protección
anti-bot: va contra sus términos y expone la cuenta.

**Descartados a propósito**, para que nadie los vuelva a proponer:
- **NotebookLM** — no tiene API pública; la librería no oficial autentica con un volcado
  de las cookies de Google del usuario, que da acceso a Gmail, Drive y Cloud Console.
  El costo de seguridad no justifica lo que aporta.
- **Apollo** — sirve para prospectar, no para preparar: cuando la reunión ya está
  agendada, ya sabés quién es. Además sus endpoints de personas están fuera del plan
  Free y cada llamada exige confirmación humana, que en una corrida desatendida no existe.
- **Scrapling** — su vía rápida falsifica la huella TLS y es incompatible con proxies
  que terminan TLS; su vía con navegador necesita descargar ~600 MB por corrida.

## Paso 1 — Detectar

Buscá en el calendario de `owner.calendarId` los eventos de **hoy y mañana** cuyo
título contenga `#prep`:

```
mcp__Google_Calendar__list_events(
  calendarId=<owner.calendarId>,
  startTime=<hoy 00:00 -03:00>, endTime=<mañana 23:59 -03:00>,
  fullText="#prep", orderBy="startTime")
```

Reglas:
- **Solo `#prep`.** No prepares eventos sin la etiqueta, aunque tengan invitados externos. Es una decisión explícita del usuario.
- Google indexa duplicados de Cal.com; quedate con el evento que tiene `attendees` poblado.
- Saltá los que ya existen en `meetings.json` con el mismo `id`, salvo que el usuario pida regenerarlos.
- **Si no hay eventos con `#prep`: no generes ningún dashboard.** Escribí igual el heartbeat del paso 4.5, commitealo y terminá informando "sin reuniones para preparar". Es el resultado esperado la mayoría de los días, no una falla.

Del evento sacás: nombre del invitado, email, empresa (del dominio del mail), hora,
plataforma y la descripción de Cal.com (trae nombre + email + timezone del invitado).

## Paso 2 — Investigar

Objetivo: 8–15 fuentes por persona. Buscá siempre el nombre **entre comillas**: sin
comillas los resultados se van a homónimos y a ruido genérico del rubro.

1. `WebSearch` con `"Nombre Apellido" <empresa>` → headline, cargo y empleadores previos.
2. `WebSearch` con `"Nombre Apellido"` + término del rubro → actividad y contenido reciente.
3. `WebFetch` sobre el sitio de la empresa → modelo de negocio, precios y posicionamiento.
   Si vuelve vacío y tenés Firecrawl, reintentá con `firecrawl_scrape`.
4. `WebSearch` de mercado: tamaño, CAGR, tendencias del sector — son los números que
   alimentan los `stats` del encabezado y la sección de oportunidad.

Cargá cada URL usada en el campo `sources` del spec: es lo que hace auditable el research.

Reglas de honestidad, importantes:
- **No inventes datos.** Si no encontraste el rol, escribí "rol a confirmar al inicio del call".
- Distinguí siempre **hecho verificado** de **interpretación estratégica**. La sección de research lleva un apartado explícito de limitaciones.
- Si el research sale flaco (menos de 5 fuentes útiles), generá igual el dashboard pero decilo en la sección de research y bajá `sources_count`.

## Paso 3 — Armar el spec

Escribí un JSON en el scratchpad con esta forma (los `*_md` son markdown, y son
lo que más valor aporta: escribilos con densidad real, no con relleno):

```jsonc
{
  "id": "YYYY-MM-DD-nombre-apellido",      // slug ASCII, en minúsculas
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "person": "Nombre Apellido",
  "role_line": "Cargo · Empresa",          // subtítulo del header
  "title": "Cargo",                        // para meetings.json
  "company": "Empresa",
  "meeting_type": "Reunión de 30 min (Cal.com)",
  "tags": [{"text":"...", "icon":"fas fa-robot", "color":"blue"}],   // colores: blue|purple|gold|green
  "registry_tags": ["...", "..."],
  "stats": [{"value":"$131B", "label":"...", "icon":"fas fa-dollar-sign", "color":"gold"}],  // exactamente 3
  "briefing_md": "...",   // secciones 1-6, ver abajo
  "intel_md": "...",      // cheat sheet competitivo
  "research_md": "...",   // fuentes, evidencia y limitaciones
  "quiz": [{"q":"...", "options":["A) ...","B) ...","C) ...","D) ..."], "answer":"B"}],  // 8
  "flashcards": [{"q":"...", "a":"..."}],  // 10
  "sources": [                             // pobla la pestaña Fuentes — ver abajo
    {"group":"Identidad profesional", "title":"...", "url":"https://...", "note":"qué aportó"}
  ],
  "notebooklm_url": null,                  // NotebookLM está descartado, ver arriba
  "generated": "<ISO 8601 con el offset de owner.utcOffset>"
}
```

### El campo `sources` no es opcional

Cargá **todas** las URLs que usaste, agrupadas por `group` (por ejemplo: *Identidad
profesional*, *La empresa*, *Producción de contenido*, *Mercado*). En `note` poné
en media línea **qué aportó esa fuente**, no de qué se trata.

Es lo que hace auditable el research: cualquier afirmación del briefing tiene que
poder rastrearse hasta una de esas fuentes. `sources_count` se calcula solo a partir
de la lista, no hace falta escribirlo.

`briefing_md` lleva seis secciones numeradas:

1. **Perfil de la persona**
2. **Perfil de la empresa**
3. **Oportunidad de mercado** — con números concretos, no adjetivos.
4. **Guion de conversación** — ver abajo, es la sección que más importa.
5. **Manejo de objeciones** — tabla de dos columnas.
6. **Próximos pasos** — tres acciones concretas.

### Cómo se escribe (esto define la calidad)

El briefing se lee **cinco minutos antes de entrar a la reunión**, muchas veces desde
el celular. Tiene que ser escaneable, no literario. Usá **campos etiquetados en
negrita**, no párrafos corridos:

```markdown
**Background:** Argentino, radicado en Montevideo. 25+ años en comercio digital.
**Formación:** MBA (USAL), MBA (SUNY), posgrado en eBusiness Management.
**Roles actuales:**
- Co-Founder & Global Executive SVP — **VTEX (NYSE: VTEX)**
- Presidente & Co-Founder — **eCommerce Institute**
**Logros clave:** Autor de 25 libros. El eCommerce Day Tour llegó a 71.400 asistentes en 13 países.
**Contexto de la reunión:** Te reunís con un arquitecto fundacional de la economía
digital de LATAM, justo cuando lanza la edición 200 del eCommerce Day Tour.
```

Reglas de densidad, medidas sobre el texto **renderizado** del dashboard (lo que
`tools/generate_dashboard.py --dry-run` reporta como «contenido»):

- **Apuntá a 25.000+ caracteres de contenido** entre las tres secciones de texto.
  Por debajo de ~20.000 el dashboard se siente flaco.
- Cada afirmación lleva un dato: fecha, cifra, nombre propio o cargo. Si una línea
  no tiene ninguno de los cuatro, sobra.
- Negrita para el nombre de empresas, cifras y cargos — es lo que el ojo engancha.
- Nada de relleno de consultor: «es importante destacar», «en un mundo cada vez más
  digital», «sin duda un actor clave». Si la frase sobreviviría intacta en el
  briefing de otra persona, borrala.
- El **contexto de la reunión** cierra siempre la sección 1 y responde: por qué
  esta conversación, por qué ahora.

### La sección 4 la define el framework

**Leé `frameworks/<pipeline.framework>.md` y seguí lo que diga.** Ese archivo
define la estructura de la sección 4, qué se anticipa y cómo se conecta con la
tabla de objeciones de la sección 5.

Los que vienen incluidos:

| Framework | Cuándo |
|---|---|
| `generic` | Default. Cinco puntos de conversación. Sirve para cualquier reunión. |
| `kona-4w` | Discovery consultiva: diagnosticar antes de presentar. |
| `spin` | Venta consultiva B2B (Situación, Problema, Implicación, Necesidad). |
| `meddic` | Enterprise con comité de compra: checklist de calificación. |

Si el archivo configurado no existe, usá `generic.md` y anotalo en el reporte.

**Aplicá el framework de venta sólo cuando la reunión lo amerite** — un prospecto,
una discovery, una primera conversación comercial. Para un partner, un proveedor,
una institución o alguien que ya conocés, usá `generic` aunque haya otro configurado:
un guion de venta contra un socio de años queda fuera de lugar.

## Paso 4 — Generar y publicar

```bash
python3 tools/generate_dashboard.py <spec.json>
```

El script escribe `meetings/<id>/index.html`, hace upsert en `meetings.json` y
sincroniza el fallback `INLINE_MEETINGS` de `index.html`. Falla ruidosamente si
queda algún placeholder sin resolver.

Verificá antes de publicar:
```bash
python3 -c "import json;json.load(open('meetings.json'))"   # registry válido
grep -c '{{' meetings/<id>/index.html                       # tiene que dar 0
```

Después:
```bash
git add -A
git commit -m "feat: meeting prep <Nombre> - <YYYY-MM-DD>"
git push -u origin main     # Vercel despliega solo
```

Si el push falla por red, reintentá hasta 4 veces con backoff de 2s, 4s, 8s, 16s.

## Paso 4.5 — Dejar constancia (siempre)

**Corras o no corras algo, escribí `runs/last-run.md`** con este formato exacto:

```markdown
# Última corrida

- **Cuándo:** 2026-08-14 06:03 (America/Argentina/Buenos_Aires)
- **Resultado:** sin reuniones para preparar | 2 preps generados | error
- **Research:** web
- **Detectados:** 1 evento con #prep
- **Preparados:** 0 — «Nombre Apellido» ya existía en meetings.json
- **Notas:** cualquier decisión ambigua que hayas tomado
```

Es una sola línea de diff por día y hace **demostrable** que el sistema está vivo.
Sin esto, un día de silencio es indistinguible de una Routine que dejó de dispararse.

Commiteá ese archivo aunque no haya preps: es la única excepción a la regla de
«no commitear si no hay nada». El mensaje en ese caso es
`chore: heartbeat <fecha> — sin reuniones`.

## Paso 5 — Reportar

Terminá con un resumen corto: a quién preparaste, cuántas fuentes, qué quedó flojo
y la URL. Si algo falló, decilo derecho — no reportes éxito si el push no salió.

## Notas de mantenimiento

- El look de los dashboards vive en `templates/dashboard.html`. Tocá ahí, no en cada reunión.
- `assets/marked.min.js` está vendorizado a propósito: el CDN se caía y dejaba las
  pestañas en blanco. No lo vuelvas a apuntar a cdnjs.
- Las corridas con incidencias se documentan en `runs/YYYY-MM-DD-status.md`.
