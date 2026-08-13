# Frameworks de conversación

Cada archivo de esta carpeta define **cómo se escribe la sección 4 del briefing**
(el guion de conversación) y **cómo se llena la tabla de objeciones**.

Elegí uno en `config.json`:

```json
"pipeline": { "framework": "kona-4w" }
```

| Archivo | Para quién |
|---|---|
| `generic.md` | Default. No asume método de venta. Sirve para cualquier reunión. |
| `kona-4w.md` | Discovery consultiva: diagnosticar antes de presentar. |
| `spin.md` | Venta consultiva B2B clásica (Situación, Problema, Implicación, Necesidad). |
| `meddic.md` | Ventas enterprise con ciclo largo y comité de compra. |

## Escribir uno propio

Copiá `generic.md`, renombralo y apuntá `config.json` al nombre nuevo (sin `.md`).
Un framework tiene que responder tres cosas:

1. **Qué estructura** tiene la sección 4.
2. **Qué se anticipa** — objeciones, riesgos, señales.
3. **Cómo se conecta** con la tabla de objeciones de la sección 5.

Mantenelo en una página. El agente lo lee entero en cada corrida.
