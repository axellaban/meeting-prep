# Poner Meeting Prep OS a andar

De repo clonado a sistema corriendo solo: unos 15 minutos.

## Lo que necesitás antes de empezar

| Requisito | Por qué | ¿Obligatorio? |
|---|---|---|
| Cuenta de **Claude con Routines** (Claude Code en la web) | Es lo que despierta al agente cada mañana | **Sí** — sin esto no hay automatización |
| **Google Calendar** conectado en claude.ai | De ahí salen las reuniones | **Sí** |
| Cuenta de **GitHub** | Guarda los dashboards y las instrucciones del agente | **Sí** |
| **Vercel** (gratis) | Publica el sitio. Sin esto no podés abrir los dashboards del celular | **Sí, en la práctica** |
| **Firecrawl** conectado | Motor de research. Si falla, el sistema sigue con búsqueda web | Recomendado |

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

Esto **hay que hacerlo desde la interfaz**: el repositorio y los conectores solo se adjuntan ahí.

1. Andá a **claude.ai → Routines → nueva rutina**
2. **Elegí tu repositorio de GitHub como fuente/entorno de la rutina** (sin esto, la sesión despierta en una carpeta vacía y no encuentra `config.json` ni puede hacer `git push`)
3. Elegí la hora (la misma que pusiste en `config.json`)
4. Adjuntá los conectores: **Google Calendar** (obligatorio) y **Firecrawl** (recomendado)
5. Pegá este prompt:

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

> **Un consejo de horario:** elegí un minuto que no sea `:00` ni `:30`. Todo el
> mundo pide las horas en punto y esos minutos están congestionados. `06:03` anda
> mejor que `06:00`.

## 4. Publicar el sitio (opcional)

**vercel.com/new** → importá tu repo → **Deploy**. Vercel lo construye como Next.js
(lo fija `vercel.json`) y vuelve a desplegar en cada push del agente.

El sitio pide **login con Google** (Auth.js). Antes del primer deploy:

1. En **Google Cloud → APIs y servicios → Credenciales**, creá un cliente OAuth
   (aplicación web) con estas URLs de redirección autorizadas:
   `https://<tu-dominio>/api/auth/callback/google` y
   `http://localhost:3000/api/auth/callback/google`.
2. En **Vercel → Settings → Environment Variables**, cargá `AUTH_GOOGLE_ID`,
   `AUTH_GOOGLE_SECRET` y `AUTH_SECRET` (este último con `npx auth secret`).
   Los nombres están en `.env.example`.

Hoy entra cualquier cuenta de Google que complete el login.

---

## Usarlo todos los días

Poné la etiqueta en el título del evento:

```
Reunión con Juan García #prep
```

Y listo. A la mañana siguiente el dashboard está hecho.

**Los días sin reuniones etiquetadas, el agente no genera nada.** Sólo actualiza
`runs/last-run.md` con la fecha y el resultado, para que sepas que corrió. Si ese
archivo no cambió, la Routine no se ejecutó.

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

Y para chequear que el repo esté sano — configuración válida, registro coherente,
dashboards sin placeholders, assets en su lugar:

```bash
python3 tools/verify.py
```

Sale con código 1 si encuentra algún error, así que sirve para un hook o para CI.

---

## Adaptarlo

| Qué querés cambiar | Dónde |
|---|---|
| Nombre, calendario, hora, etiqueta, idioma | `config.json` |
| El guion de conversación del briefing | `config.json` → `pipeline.framework`, y los archivos de `frameworks/` |
| Cómo investiga y qué exige de densidad | `.claude/skills/meeting-prep-daily/SKILL.md` |
| El diseño de todos los dashboards | `templates/dashboard.html` |
| El portal | `public/index.html` |

Los frameworks incluidos son `generic` (default), `kona-4w` (discovery consultiva),
`spin` y `meddic`. Para escribir uno propio, copiá `frameworks/generic.md`.

---

## Actualizar tu repo con mejoras del template

Cuando `meeting-prep-OS` saca una nueva versión (mejoras en `templates/dashboard.html`,
`public/index.html`, skills o scripts), podés traer los cambios del motor **sin tocar tu
`config.json` ni tus reuniones en `public/meetings/`**:

```bash
python3 tools/sync_template.py --pull-upstream
```

Y si querés aplicar las mejoras visuales o de interactividad del nuevo template a los
dashboards que ya tenías generados:

```bash
python3 tools/generate_dashboard.py --upgrade-existing
```

---

## Problemas frecuentes

**La Routine falló diciendo que el directorio estaba vacío o sin repositorio git.**
Faltó seleccionar tu repositorio de GitHub como fuente/entorno dentro de la Routine
en claude.ai. Editala y asociá el repo.

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
