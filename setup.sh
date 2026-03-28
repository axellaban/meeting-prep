#!/bin/bash
# ─────────────────────────────────────────────────────
# Meeting Prep OS — GitHub Setup Script
# Ejecutar UNA sola vez para inicializar el repo
# ─────────────────────────────────────────────────────

echo "⚡ Meeting Prep OS — Setup"
echo "──────────────────────────"

# 1. Init git
git init
git branch -M main

# 2. Add remote (reemplazá si el repo tiene otro nombre)
git remote add origin https://github.com/axellaban/meeting-prep.git

# 3. Commit inicial
git add .
git commit -m "feat: initial Meeting Prep OS setup

- Main portal with meeting registry
- First prep: Marcos Pueyrredon (VTEX)
- Vercel-ready static site structure"

# 4. Push
git push -u origin main

echo ""
echo "✅ Listo! Repo subido a GitHub."
echo ""
echo "📌 Próximos pasos:"
echo "   1. Andá a https://vercel.com/new"
echo "   2. Import → axellaban/meeting-prep"
echo "   3. Deploy (sin cambiar nada)"
echo "   4. Tu URL: https://meeting-prep-axellaban.vercel.app"
echo ""
echo "🔄 Para pushes futuros (automáticos desde Cowork):"
echo "   git add . && git commit -m 'feat: new meeting prep' && git push"
