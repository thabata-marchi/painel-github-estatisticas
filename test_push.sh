#!/bin/bash

set -e
trap 'echo "❌ Falha na linha $LINENO: $BASH_COMMAND"' ERR

echo "📥 Atualizando repositório local..."
git pull origin main

echo "⚙️ Executando scripts Python..."
source venv/bin/activate
python3 agregador.py
python3 generate_readme.py
deactivate

echo "🔍 Verificando alterações..."
if [ -n "$(git status --porcelain)" ]; then
  echo "📝 Mudanças detectadas. Preparando commit..."
  git config --local user.email "tatha.marchi@gmail.com"
  git config --local user.name "thabata-marchi"
  git add estatisticas.json
  git add index.html || true
  git add README.md || true
  git commit -m "🤖 Atualizar estatísticas - $(date -u +%Y-%m-%d)"
  
  echo "🔄 Rebase com o remoto..."
  git pull --rebase origin main

  echo "🚀 Enviando para o repositório remoto..."
  git push
else
  echo "✅ Nenhuma mudança detectada. Nada para fazer."
fi

echo "✅ Pronto!"