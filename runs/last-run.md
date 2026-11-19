# Última corrida

- **Cuándo:** 2026-11-19 09:26 (America/Argentina/Buenos_Aires)
- **Resultado:** 2 preps generados
- **Research:** Firecrawl (search, map, scrape) + WebSearch/WebFetch + contexto interno (Gmail, Drive, Calendar, repo del proyecto)
- **Detectados:** 2 eventos con #prep — «Matías mindlin #prep» (16:45) y «Mariano Bocca #prep» (17:45)
- **Preparados:** 2 — Matías Mindlin (29 fuentes) y Mariano Bocca (21 fuentes)
- **Notas:** ver abajo

## Notas

- **La Routine de las 06:03 no corrió el pipeline:** la sesión arrancó sin el repo clonado
  (directorio de trabajo vacío). Esta corrida es la re-ejecución manual pedida por Axel,
  clonando `axellaban/meeting-prep` a mano. Para que no vuelva a pasar, la Routine tiene
  que tener este repo como *source* del entorno.
- **Framework:** `config.json` pide `kona-4w`, pero se usó `generic` en los dos: Mindlin es
  cliente activo y Bocca es alumno de mentoría. La regla del skill dice no aplicar un guion
  de venta a relaciones existentes.
- **Eventos sin invitados ni descripción** (creados a mano esta mañana): la identidad salió
  de Gmail (hilo de la mentoría con Bocca, notificaciones del proyecto Mindlin), Drive y el
  calendario.
- **Confidencialidad:** los dashboards se publican en una URL abierta. Se dejaron afuera a
  propósito los precios de la propuesta a Mindlin y los datos internos que Bocca contó en la
  mentoría (proveedores, sellers, números de su operación e incidentes de seguridad).
- **Firecrawl:** el conector no cargó en esta sesión. Se usó la API REST de Firecrawl con una key
  autorizada por Axel durante la corrida; la key quedó fuera del repo. Firecrawl sumó lo que
  WebSearch no trajo: la entrevista de Infobae/Movant a Mindlin, que conduce el Jutzpá Podcast,
  y la trayectoria previa de Bocca (Frávega, Bimbo do Brasil, UTN).
- **Template:** se agregó un bloque responsive a `templates/dashboard.html`. Los dashboards
  desbordaban horizontalmente en el celular (también los anteriores, que no se regeneraron).
