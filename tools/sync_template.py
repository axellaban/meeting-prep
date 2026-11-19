#!/usr/bin/env python3
"""
Meeting Prep OS — sincronizador evolutivo entre instancia personal y template público.

Permite mantener un único motor de producto (`templates/`, `tools/`, `frameworks/`,
`.claude/skills/`, `app/`, `auth.ts`, `proxy.ts`, `public/index.html`, `public/assets/`,
`SETUP.md`, `README.md`) y propagar todas las mejoras automáticamente al repositorio
template (`axellaban/meeting-prep-OS`) sin filtrar datos personales (`config.json`,
`public/meetings/`, `public/meetings.json`, `runs/`, `public/docs/`).

También permite el camino inverso (`--pull-upstream`): cualquier usuario que haya
clonado el template puede traer las últimas mejoras del motor sin perder su
`config.json` ni sus reuniones generadas.

Modos de uso:
  1. Exportar mejoras del repo personal -> repo template local:
     python3 tools/sync_template.py [--target ../meeting-prep-OS] [--dry-run]

  2. Exportar, commitear, pushear al template y opcionalmente publicar un GitHub Release:
     python3 tools/sync_template.py --push [--release v1.1.0] [--notes "Mejoras del motor"]

  3. Para usuarios que clonaron el template y quieren actualizar su motor desde upstream:
     python3 tools/sync_template.py --pull-upstream [--upstream https://github.com/axellaban/meeting-prep-OS.git]
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGET = ROOT.parent / "meeting-prep-OS"
DEFAULT_UPSTREAM_URL = "https://github.com/axellaban/meeting-prep-OS.git"

# Archivos y carpetas que componen el "motor" de Meeting Prep OS (se copian tal cual)
ENGINE_ITEMS = [
    ".claude/skills/meeting-prep-daily/SKILL.md",
    ".claude/skills/setup/SKILL.md",
    ".github/workflows/verify.yml",
    ".env.example",
    ".gitignore",
    "LICENSE",
    "SETUP.md",
    "VERSION",
    "auth.ts",
    "proxy.ts",
    "next.config.ts",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "vercel.json",
    "app/api/auth/[...nextauth]/route.ts",
    "app/config.json/route.ts",
    "app/globals.css",
    "app/layout.tsx",
    "app/login/page.tsx",
    "public/assets/marked.min.js",
    "frameworks/README.md",
    "frameworks/generic.md",
    "frameworks/kona-4w.md",
    "frameworks/meddic.md",
    "frameworks/spin.md",
    "templates/dashboard.html",
    "tools/generate_dashboard.py",
    "tools/sync_template.py",
    "tools/verify.py",
]

# Configuración limpia por defecto para el template público
TEMPLATE_CONFIG = {
    "$comment": "Configuración de Meeting Prep OS. Corré `/setup` en Claude Code para completarlo guiado, o editá los valores directamente.",
    "owner": {
        "name": "Tu Nombre Completo",
        "shortName": "Tu Nombre",
        "email": "vos@ejemplo.com",
        "calendarId": "vos@ejemplo.com",
        "timezone": "America/Argentina/Buenos_Aires",
        "utcOffset": "-03:00",
    },
    "branding": {
        "productName": "Meeting Prep OS",
        "navbarBrand": "Meeting Prep OS",
        "tagline": "Llegá preparado a cada reunión importante.",
        "footerNote": "Generado automáticamente con IA",
    },
    "pipeline": {
        "language": "es",
        "detection": {
            "mode": "tag",
            "tag": "#prep",
            "lookaheadDays": 1,
        },
        "research": {
            "minSources": 8,
            "maxSources": 15,
            "minContentChars": 15000,
        },
        "framework": "generic",
        "cronLocal": "06:03",
    },
    "publish": {
        "branch": "main",
        "siteUrl": "",
    },
}


def sanitize_portal_html(html: str) -> str:
    """Vacía el array INLINE_MEETINGS de public/index.html para el template limpio."""
    new_html, n = re.subn(
        r"const INLINE_MEETINGS = \[(?:\s*\];|.*?\n  \];)",
        "const INLINE_MEETINGS = [];",
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError("No se encontró el bloque INLINE_MEETINGS en public/index.html")
    return new_html


def sanitize_readme(readme: str) -> str:
    """Ajusta el árbol de directorios del README para el template limpio."""
    out = readme.replace(
        "│   ├── meetings/<id>/index.html        # Un dashboard por reunión\n"
        "│   ├── assets/marked.min.js            # Renderer de markdown (vendorizado)\n"
        "│   └── docs/arquitectura.html          # Cómo se conectan las piezas\n",
        "│   ├── meetings/<id>/index.html        # Un dashboard por reunión (vacío al empezar)\n"
        "│   └── assets/marked.min.js            # Renderer de markdown (vendorizado)\n",
    )
    return out


def export_to_template(target: Path, dry_run: bool = False) -> list[str]:
    """Sincroniza los archivos del motor hacia `target` con datos personales limpios."""
    if not target.exists():
        raise SystemExit(f"ERROR: el directorio destino '{target}' no existe.")

    changed: list[str] = []

    def write_if_changed(rel_path: str, content_bytes: bytes) -> None:
        dest = target / rel_path
        if dest.exists() and dest.read_bytes() == content_bytes:
            return
        changed.append(rel_path)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content_bytes)

    # 1. Copiar archivos del motor
    for rel in ENGINE_ITEMS:
        src = ROOT / rel
        if not src.exists():
            continue
        write_if_changed(rel, src.read_bytes())

    # 2. public/index.html con INLINE_MEETINGS vacío
    portal_html = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
    clean_portal = sanitize_portal_html(portal_html)
    write_if_changed("public/index.html", clean_portal.encode("utf-8"))

    # 3. README.md adaptado al template
    readme_txt = (ROOT / "README.md").read_text(encoding="utf-8")
    clean_readme = sanitize_readme(readme_txt)
    write_if_changed("README.md", clean_readme.encode("utf-8"))

    # 4. config.json y public/meetings.json limpios
    clean_cfg = (json.dumps(TEMPLATE_CONFIG, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_if_changed("config.json", clean_cfg)

    clean_meetings = (json.dumps({"meetings": []}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_if_changed("public/meetings.json", clean_meetings)

    # 5. Limpiar archivos del layout anterior (pre-Next.js) y directorios personales
    obsolete_paths = [
        "index.html",
        "meetings.json",
        "assets",
        "meetings",
        "runs",
        "docs",
        "public/meetings",
        "public/docs",
    ]
    for rel_obs in obsolete_paths:
        p = target / rel_obs
        if not p.exists():
            continue
        if p.is_file():
            changed.append(f"{rel_obs} (eliminado)")
            if not dry_run:
                p.unlink()
        elif p.is_dir() and any(p.iterdir()):
            changed.append(f"{rel_obs}/ (eliminado)")
            if not dry_run:
                shutil.rmtree(p)
        elif p.is_dir():
            if not dry_run:
                shutil.rmtree(p)

    # 6. Verificar que no hayan quedado datos del owner personal en el template
    personal_cfg_path = ROOT / "config.json"
    if personal_cfg_path.exists() and not dry_run:
        personal_cfg = json.loads(personal_cfg_path.read_text(encoding="utf-8"))
        owner = personal_cfg.get("owner") or {}
        marcas = {
            v.lower()
            for v in (owner.get("email"), owner.get("name"))
            if v and v.lower() not in {"tu nombre completo", "vos@ejemplo.com"}
        }
        for f in target.rglob("*"):
            if not f.is_file() or any(part in {".git", "node_modules", ".next"} for part in f.parts):
                continue
            if f.name == "LICENSE":
                continue
            txt = f.read_text(encoding="utf-8", errors="ignore").lower()
            for marca in marcas:
                if marca in txt:
                    raise SystemExit(
                        f"ERROR DE PRIVACIDAD: '{marca}' apareció en {f.relative_to(target)} del template"
                    )

    return changed


def run_verify(repo_dir: Path) -> None:
    res = subprocess.run(
        [sys.executable, str(repo_dir / "tools" / "verify.py")],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(f"ERROR: tools/verify.py falló en {repo_dir}")


def push_and_release(target: Path, release_tag: str | None, notes: str | None) -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "1.1.0"
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(target),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if status:
        subprocess.run(["git", "add", "-A"], cwd=str(target), check=True)
        msg = f"feat: sync Meeting Prep OS engine v{version}"
        if release_tag:
            msg = f"release: Meeting Prep OS {release_tag}"
        subprocess.run(["git", "commit", "-m", msg], cwd=str(target), check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=str(target), check=True)
        print(f"✅ Commit & push enviados a {target.name} (main)")
    else:
        print(f"ℹ️  {target.name} ya estaba al día en git.")

    if release_tag:
        tag = release_tag if release_tag.startswith("v") else f"v{release_tag}"
        release_notes = notes or (
            f"Release {tag} de Meeting Prep OS.\n\n"
            f"Para actualizar una instancia existente sin perder tus reuniones ni tu `config.json`:\n"
            f"```bash\npython3 tools/sync_template.py --pull-upstream\n```"
        )
        existing = subprocess.run(
            ["gh", "release", "view", tag],
            cwd=str(target),
            capture_output=True,
            text=True,
        )
        if existing.returncode == 0:
            print(f"ℹ️  El release {tag} ya existe en GitHub.")
        else:
            subprocess.run(
                ["gh", "release", "create", tag, "--title", f"Meeting Prep OS {tag}", "--notes", release_notes],
                cwd=str(target),
                check=True,
            )
            print(f"🚀 GitHub Release {tag} publicado en {target.name}")


def pull_upstream(upstream_url: str, dry_run: bool = False) -> list[str]:
    """Trae actualizaciones del motor desde el template público sin pisar config.json ni public/meetings/."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "upstream"
        subprocess.run(
            ["git", "clone", "--depth", "1", upstream_url, str(tmp_path)],
            check=True,
            capture_output=True,
            text=True,
        )

        changed: list[str] = []
        for rel in ENGINE_ITEMS:
            src = tmp_path / rel
            dest = ROOT / rel
            if not src.exists():
                continue
            data = src.read_bytes()
            if dest.exists() and dest.read_bytes() == data:
                continue
            changed.append(rel)
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)

        # Actualizar public/index.html preservando las reuniones locales en INLINE_MEETINGS
        upstream_portal = tmp_path / "public" / "index.html"
        local_portal = ROOT / "public" / "index.html"
        local_registry = ROOT / "public" / "meetings.json"
        if upstream_portal.exists() and local_portal.exists():
            meetings = []
            if local_registry.exists():
                meetings = json.loads(local_registry.read_text(encoding="utf-8")).get("meetings", [])
            new_portal = upstream_portal.read_text(encoding="utf-8")
            if meetings:
                block = json.dumps(meetings, ensure_ascii=False, indent=4)
                block = "\n".join(("  " + ln) if ln.strip() else ln for ln in block.splitlines())
                replacement = "const INLINE_MEETINGS = " + block.lstrip() + ";"
            else:
                replacement = "const INLINE_MEETINGS = [];"
            new_portal = re.sub(
                r"const INLINE_MEETINGS = \[(?:\s*\];|.*?\n  \];)",
                replacement,
                new_portal,
                count=1,
                flags=re.S,
            )
            if local_portal.read_text(encoding="utf-8") != new_portal:
                changed.append("public/index.html")
                if not dry_run:
                    local_portal.write_text(new_portal, encoding="utf-8")

        return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincronizador evolutivo de Meeting Prep OS")
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help="Ruta local al repo template meeting-prep-OS (default: ../meeting-prep-OS)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Muestra qué cambiaría sin tocar archivos")
    parser.add_argument("--push", action="store_true", help="Hace commit y push en el repo template")
    parser.add_argument("--release", type=str, default=None, help="Crea un GitHub Release con el tag indicado (ej. v1.1.0)")
    parser.add_argument("--notes", type=str, default=None, help="Notas para el GitHub Release")
    parser.add_argument(
        "--pull-upstream",
        action="store_true",
        help="Trae mejoras del motor desde meeting-prep-OS sin tocar tu config.json ni tus reuniones",
    )
    parser.add_argument(
        "--upstream",
        type=str,
        default=DEFAULT_UPSTREAM_URL,
        help=f"URL git del template upstream (default: {DEFAULT_UPSTREAM_URL})",
    )
    args = parser.parse_args()

    if args.pull_upstream:
        changed = pull_upstream(args.upstream, dry_run=args.dry_run)
        prefix = "🔍 [DRY-RUN]" if args.dry_run else "✅"
        if not changed:
            print(f"{prefix} El motor ya está actualizado con upstream.")
        else:
            print(f"{prefix} Archivos del motor actualizados desde upstream ({len(changed)}):")
            for c in changed:
                print(f"   • {c}")
        if not args.dry_run:
            run_verify(ROOT)
        return

    target = args.target.resolve()
    changed = export_to_template(target, dry_run=args.dry_run)
    prefix = "🔍 [DRY-RUN]" if args.dry_run else "✅"
    if not changed:
        print(f"{prefix} {target.name} ya está sincronizado con el motor actual.")
    else:
        print(f"{prefix} Sincronizados {len(changed)} archivo(s) hacia {target.name}:")
        for c in changed:
            print(f"   • {c}")

    if not args.dry_run:
        run_verify(target)
        print(f"✅ Verificación (tools/verify.py) superada en {target.name}")
        if args.push or args.release:
            push_and_release(target, args.release, args.notes)


if __name__ == "__main__":
    main()
