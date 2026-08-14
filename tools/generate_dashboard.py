#!/usr/bin/env python3
"""
Meeting Prep OS — generador de dashboards.

Toma un spec JSON con el research ya hecho y produce:
  1. meetings/<id>/index.html   (a partir de templates/dashboard.html)
  2. la entrada correspondiente en meetings.json (upsert por id)
  3. el bloque INLINE_MEETINGS de index.html sincronizado

Uso:
    python3 tools/generate_dashboard.py spec.json

El spec se documenta en .claude/skills/meeting-prep-daily/SKILL.md
"""

import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "dashboard.html"
REGISTRY = ROOT / "meetings.json"
PORTAL = ROOT / "index.html"
CONFIG = ROOT / "config.json"

DEFAULT_BRAND = "Meeting Prep OS"


def load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: config.json no es JSON válido ({e})")

# Se muestra hasta que la reunión ocurre y alguien (o el pipeline post-reunión)
# completa el brief con lo que realmente pasó.
PLACEHOLDER_POSTBRIEF = """## Todavía sin completar

Esta sección se llena **después** de la reunión, con lo que realmente pasó:
decisiones tomadas, compromisos asumidos y próximos pasos concretos.

Mientras tanto, lo de acá arriba es la preparación — hipótesis, no hechos.
"""

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Los markdown se inyectan dentro de un template literal de JS: hay que
# neutralizar backtick, backslash y ${ o el HTML queda roto.
def js_template_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    letters = "".join(p[0] for p in parts[:2])
    return unicodedata.normalize("NFKD", letters).encode("ascii", "ignore").decode().upper() or "??"


def build_tags(tags) -> str:
    out = []
    for t in tags:
        icon = t.get("icon", "fas fa-tag")
        color = t.get("color", "blue")
        out.append(
            f'        <span class="tag tag-{color}"><i class="{icon}"></i> {t["text"]}</span>'
        )
    return "\n".join(out)


def build_stats(stats) -> str:
    out = []
    for s in stats:
        out.append(f"""    <div class="stat-card">
      <div class="stat-icon {s.get('color', 'blue')}"><i class="{s.get('icon', 'fas fa-chart-line')}"></i></div>
      <div>
        <div class="stat-value">{s['value']}</div>
        <div class="stat-label">{s['label']}</div>
      </div>
    </div>""")
    return "\n".join(out)


def build_sources_md(spec: dict) -> str:
    """Lista de fuentes con links, para que el research sea auditable.

    `sources` es una lista de {title, url, note?}, opcionalmente agrupada por
    `group`. Sin fuentes cargadas, deja un aviso honesto en vez de una tabla vacía.
    """
    sources = spec.get("sources") or []
    if not sources:
        return ("## Sin fuentes cargadas\n\n"
                "Este dashboard no registró las URLs del research. El detalle de la "
                "investigación está en la pestaña **Deep Research**.\n")

    grupos: dict = {}
    for s in sources:
        grupos.setdefault(s.get("group", "Fuentes consultadas"), []).append(s)

    out = [f"# Fuentes ({len(sources)})\n"]
    for grupo, items in grupos.items():
        out.append(f"\n## {grupo}\n")
        for s in items:
            title = s.get("title") or s.get("url", "sin título")
            url = s.get("url")
            note = s.get("note")
            line = f"- [{title}]({url})" if url else f"- {title}"
            if note:
                line += f" — {note}"
            out.append(line)
    out.append(
        "\n\n---\n\n*Cada afirmación del briefing tiene que poder rastrearse hasta "
        "alguna de estas fuentes. Lo que no sale de acá es interpretación, y como tal "
        "está marcado en Deep Research.*\n"
    )
    return "\n".join(out)


def rendered_text_len(html: str) -> int:
    """Caracteres de texto que realmente ve el lector, sin estilos ni etiquetas.

    Es la misma medida con la que se comparan los dashboards entre sí; contar el
    markdown fuente daría un número más chico y no comparable.
    """
    body = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return len(" ".join(body.split()))


def build_sidebar_link(spec: dict) -> str:
    """Botón de NotebookLM sólo si hay notebook real; si no, contador de fuentes."""
    url = spec.get("notebooklm_url")
    if url:
        return (f'    <a href="{url}" target="_blank" class="notebooklm-btn">\n'
                f'      <i class="fas fa-book-open"></i> Abrir en NotebookLM\n'
                f'    </a>')
    n = spec.get("sources_count", 0)
    return (f'    <div class="notebooklm-btn" style="cursor:default;opacity:.75">\n'
            f'      <i class="fas fa-search"></i> {n} fuentes · research web\n'
            f'    </div>')


def render(spec: dict, cfg: dict) -> str:
    y, m, d = (int(x) for x in spec["date"].split("-"))
    dt = date(y, m, d)
    dia, mes = DIAS[dt.weekday()], MESES[m - 1]

    brand = (cfg.get("branding") or {}).get("navbarBrand") or DEFAULT_BRAND

    values = {
        "BRAND": brand,
        "NAME": spec["person"],
        "INITIALS": initials(spec["person"]),
        "NAV_DATE": f"{dia} {d} de {mes}, {y}",
        "DATE_LONG": f"{dia} {d:02d}/{m:02d}/{y}",
        "TIME": f"{spec['time']} hs",
        "ROLE_LINE": spec["role_line"],
        "MEETING_TYPE": spec.get("meeting_type", "Reunión de Negocio"),
        "TAGS_HTML": build_tags(spec.get("tags", [])),
        "STATS_HTML": build_stats(spec.get("stats", [])),
        "SIDEBAR_LINK": build_sidebar_link(spec),
        "BRIEFING_MD": js_template_escape(spec["briefing_md"]),
        "INTEL_MD": js_template_escape(spec["intel_md"]),
        "RESEARCH_MD": js_template_escape(spec["research_md"]),
        "POSTBRIEF_MD": js_template_escape(spec.get("postbrief_md") or PLACEHOLDER_POSTBRIEF),
        "SOURCES_MD": js_template_escape(build_sources_md(spec)),
        "QUIZ_JSON": json.dumps(spec.get("quiz", []), ensure_ascii=False, indent=2),
        "FLASHCARDS_JSON": json.dumps(spec.get("flashcards", []), ensure_ascii=False, indent=2),
    }

    html = TEMPLATE.read_text(encoding="utf-8")
    for key, val in values.items():
        html = html.replace("{{" + key + "}}", val)

    missing = set(re.findall(r"\{\{(\w+)\}\}", html))
    if missing:
        raise SystemExit(f"ERROR: placeholders sin resolver: {sorted(missing)}")
    return html


def upsert_registry(spec: dict) -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = {
        "id": spec["id"],
        "date": spec["date"],
        "time": spec["time"],
        "person": spec["person"],
        "title": spec.get("title", ""),
        "company": spec.get("company", ""),
        "type": spec.get("meeting_type", "Reunión de Negocio"),
        "tags": spec.get("registry_tags", [t["text"] for t in spec.get("tags", [])]),
        "notebooklm_url": spec.get("notebooklm_url"),
        "sources_count": spec.get("sources_count") or len(spec.get("sources") or []),
        "path": f"meetings/{spec['id']}/index.html",
        "generated": spec["generated"],
    }
    meetings = [m for m in data["meetings"] if m["id"] != spec["id"]]
    meetings.append(entry)
    meetings.sort(key=lambda m: (m["date"], m.get("time", "")), reverse=True)
    data["meetings"] = meetings
    REGISTRY.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return len(meetings)


def sync_portal_fallback(meetings: list) -> None:
    """index.html trae una copia inline que se usa cuando se abre por file://."""
    html = PORTAL.read_text(encoding="utf-8")
    block = json.dumps(meetings, ensure_ascii=False, indent=4)
    block = "\n".join(("  " + ln) if ln.strip() else ln for ln in block.splitlines())
    new, n = re.subn(
        r"const INLINE_MEETINGS = \[.*?\n  \];",
        "const INLINE_MEETINGS = " + block.lstrip() + ";",
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        print("AVISO: no se pudo sincronizar INLINE_MEETINGS en index.html")
        return
    PORTAL.write_text(new, encoding="utf-8")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    if len(args) != 1:
        raise SystemExit("uso: generate_dashboard.py <spec.json> [--dry-run]")

    cfg = load_config()
    spec = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    for field in ("id", "date", "time", "person", "role_line",
                  "briefing_md", "intel_md", "research_md", "generated"):
        if not spec.get(field):
            raise SystemExit(f"ERROR: falta el campo obligatorio '{field}' en el spec")

    html = render(spec, cfg)

    if dry_run:
        chars = rendered_text_len(html)
        minimo = ((cfg.get("pipeline") or {}).get("research") or {}).get("minContentChars", 0)
        print("🔍 DRY RUN — no se escribió ningún archivo\n")
        print(f"   destino     meetings/{spec['id']}/index.html")
        print(f"   persona     {spec['person']}")
        print(f"   fecha       {spec['date']} {spec['time']}")
        print(f"   contenido   {chars:,} chars" + (f"  (mínimo {minimo:,})" if minimo else ""))
        print(f"   quiz        {len(spec.get('quiz', []))} preguntas")
        print(f"   flashcards  {len(spec.get('flashcards', []))}")
        print(f"   html        {len(html):,} bytes")
        if minimo and chars < minimo:
            print(f"\n⚠️  El contenido está por debajo del mínimo configurado.")
        print("\n   Quitá --dry-run para escribir de verdad.")
        return

    out_dir = ROOT / "meetings" / spec["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    total = upsert_registry(spec)
    sync_portal_fallback(json.loads(REGISTRY.read_text(encoding="utf-8"))["meetings"])

    print(f"✅ {out_dir.relative_to(ROOT)}/index.html")
    print(f"✅ meetings.json — {total} reuniones")
    print(f"✅ index.html — fallback inline sincronizado")


if __name__ == "__main__":
    main()
