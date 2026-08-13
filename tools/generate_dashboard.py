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


def render(spec: dict) -> str:
    y, m, d = (int(x) for x in spec["date"].split("-"))
    dt = date(y, m, d)
    dia, mes = DIAS[dt.weekday()], MESES[m - 1]

    values = {
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
        "sources_count": spec.get("sources_count", 0),
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
    if len(sys.argv) != 2:
        raise SystemExit("uso: generate_dashboard.py <spec.json>")

    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for field in ("id", "date", "time", "person", "role_line",
                  "briefing_md", "intel_md", "research_md", "generated"):
        if not spec.get(field):
            raise SystemExit(f"ERROR: falta el campo obligatorio '{field}' en el spec")

    out_dir = ROOT / "meetings" / spec["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(render(spec), encoding="utf-8")

    total = upsert_registry(spec)
    sync_portal_fallback(json.loads(REGISTRY.read_text(encoding="utf-8"))["meetings"])

    print(f"✅ {out_dir.relative_to(ROOT)}/index.html")
    print(f"✅ meetings.json — {total} reuniones")
    print(f"✅ index.html — fallback inline sincronizado")


if __name__ == "__main__":
    main()
