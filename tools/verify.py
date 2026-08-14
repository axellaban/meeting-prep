#!/usr/bin/env python3
"""
Meeting Prep OS — verificación del repo.

Chequea que todo esté sano antes de publicar: configuración válida, registro
coherente con los archivos en disco, dashboards sin placeholders, el renderer
de markdown servido localmente y sin rastros de datos de otra persona.

    python3 tools/verify.py

Sale con código 1 si hay algún error, para poder usarlo en CI o en un hook.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

errores: list[str] = []
avisos: list[str] = []


def error(msg: str) -> None:
    errores.append(msg)


def aviso(msg: str) -> None:
    avisos.append(msg)


def check_config() -> dict:
    p = ROOT / "config.json"
    if not p.exists():
        aviso("config.json no existe — el pipeline va a usar los defaults")
        return {}
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        error(f"config.json no es JSON válido: {e}")
        return {}

    owner = cfg.get("owner") or {}
    for campo in ("name", "calendarId", "timezone"):
        if not owner.get(campo):
            error(f"config.json: falta owner.{campo}")

    tz, off = owner.get("timezone", ""), owner.get("utcOffset", "")
    if tz and off and not re.fullmatch(r"[+-]\d{2}:\d{2}", off):
        error(f"config.json: utcOffset '{off}' no tiene el formato +HH:MM")

    fw = (cfg.get("pipeline") or {}).get("framework")
    if fw and not (ROOT / "frameworks" / f"{fw}.md").exists():
        error(f"config.json: el framework '{fw}' no existe en frameworks/")

    return cfg


def check_registry() -> list:
    p = ROOT / "meetings.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        error(f"meetings.json ilegible: {e}")
        return []

    meetings = data.get("meetings", [])
    vistos = set()
    for m in meetings:
        mid = m.get("id", "<sin id>")
        if mid in vistos:
            error(f"meetings.json: id duplicado '{mid}'")
        vistos.add(mid)
        for campo in ("id", "date", "person", "path"):
            if not m.get(campo):
                error(f"meetings.json: '{mid}' no tiene {campo}")
        if m.get("path") and not (ROOT / m["path"]).exists():
            error(f"meetings.json: '{mid}' apunta a {m['path']}, que no existe")

    # Al revés: dashboards en disco que el registro no conoce
    for d in sorted((ROOT / "meetings").glob("*/index.html")):
        rel = str(d.relative_to(ROOT))
        if not any(m.get("path") == rel for m in meetings):
            aviso(f"{rel} existe en disco pero no está en meetings.json")

    return meetings


def check_dashboards() -> int:
    archivos = sorted((ROOT / "meetings").glob("*/index.html"))
    if not archivos:
        aviso("no hay dashboards generados todavía")
        return 0

    for f in archivos:
        nombre = f.parent.name
        html = f.read_text(encoding="utf-8")

        sin_resolver = set(re.findall(r"\{\{(\w+)\}\}", html))
        if sin_resolver:
            error(f"{nombre}: placeholders sin resolver {sorted(sin_resolver)}")

        local = html.find('src="../../assets/marked.min.js"')
        if local == -1:
            error(f"{nombre}: no sirve marked.min.js desde assets/ (depende del CDN)")
        else:
            cdn = html.find("cdnjs.cloudflare.com/ajax/libs/marked")
            jsd = html.find("cdn.jsdelivr.net/npm/marked")
            primer_cdn = min([x for x in (cdn, jsd) if x != -1], default=-1)
            if primer_cdn != -1 and primer_cdn < local:
                error(f"{nombre}: el CDN de marked carga antes que la copia local")

        if "marked.parse(" in html and "md2html" not in html:
            aviso(f"{nombre}: sin degradación elegante si marked no carga")

    return len(archivos)


def check_assets() -> None:
    marked = ROOT / "assets" / "marked.min.js"
    if not marked.exists():
        error("falta assets/marked.min.js — los dashboards quedarían en blanco sin CDN")
    elif marked.stat().st_size < 10_000:
        error("assets/marked.min.js parece truncado")

    vercel = ROOT / "vercel.json"
    if vercel.exists():
        try:
            v = json.loads(vercel.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            error(f"vercel.json no es JSON válido: {e}")
            return
        srcs = [b.get("src", "") for b in v.get("builds", [])]
        if not any("assets" in s or s == "**" for s in srcs):
            error("vercel.json no despliega assets/ — marked.min.js daría 404 en producción")

    for req in ("templates/dashboard.html", "tools/generate_dashboard.py",
                ".claude/skills/meeting-prep-daily/SKILL.md"):
        if not (ROOT / req).exists():
            error(f"falta {req}")


def check_personal_leaks(cfg: dict) -> None:
    """El código del sistema no debería tener datos de ninguna persona en particular."""
    owner = cfg.get("owner") or {}
    marcas = {v.lower() for v in (owner.get("email"), owner.get("name")) if v}
    if not marcas:
        return

    for f in [ROOT / "templates" / "dashboard.html",
              ROOT / "tools" / "generate_dashboard.py",
              *(ROOT / "frameworks").glob("*.md"),
              *(ROOT / ".claude" / "skills").glob("*/SKILL.md")]:
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8").lower()
        for marca in marcas:
            if marca in txt:
                error(f"{f.relative_to(ROOT)} tiene datos personales hardcodeados ('{marca}')")


def main() -> None:
    cfg = check_config()
    meetings = check_registry()
    n = check_dashboards()
    check_assets()
    check_personal_leaks(cfg)

    print(f"config.json      {'ok' if cfg else 'ausente'}")
    print(f"meetings.json    {len(meetings)} reuniones")
    print(f"dashboards       {n} archivos")
    print(f"frameworks       {len(list((ROOT / 'frameworks').glob('*.md'))) - 1} disponibles")
    print()

    for a in avisos:
        print(f"  aviso   {a}")
    for e in errores:
        print(f"  ERROR   {e}")

    if errores:
        print(f"\n❌ {len(errores)} error(es)")
        sys.exit(1)
    print(f"✅ todo en orden{f' ({len(avisos)} aviso(s))' if avisos else ''}")


if __name__ == "__main__":
    main()
