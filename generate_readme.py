#!/usr/bin/env python3
"""
Gerador automático de README.md com estatísticas do GitHub
"""

import json
import os
from datetime import datetime

def generate_language_bar(language, count, max_count, width=20):
    """Gera uma barra de progresso ASCII para linguagens"""
    filled = int((count / max_count) * width)
    bar = '█' * filled + '░' * (width - filled)
    percentage = (count / max_count) * 100
    return f"{language:<15} {bar} {count:>3} ({percentage:>5.1f}%)"

def load_statistics():
    """Carrega estatísticas do arquivo JSON"""
    try:
        with open('estatisticas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo estatisticas.json não encontrado!")
        return None
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON!")
        return None

def generate_readme(data):
    """Gera o conteúdo do README.md"""
    
    last_updated = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
    formatted_date = last_updated.strftime('%d/%m/%Y às %H:%M UTC')
    
    summary = data['summary']
    accounts = data['accounts']
    
    # Linguagens combinadas (top 10)
    top_languages = list(summary['combined_languages'].items())[:10]
    max_lang_count = max([count for _, count in top_languages]) if top_languages else 1
    
    readme_content = f"""# 📊 Painel de Estatísticas GitHub

> Estatísticas agregadas e atualizadas automaticamente das minhas contas do GitHub

[![Atualização Automática](https://github.com/{os.getenv('GITHUB_REPOSITORY', 'usuario/repo')}/actions/workflows/update-statistics.yml/badge.svg)](https://github.com/{os.getenv('GITHUB_REPOSITORY', 'usuario/repo')}/actions/workflows/update-statistics.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://{os.getenv('GITHUB_REPOSITORY_OWNER', 'usuario')}.github.io/{os.getenv('GITHUB_REPOSITORY', 'repo').split('/')[-1]})

## 🚀 Resumo Geral

| Métrica | Valor |
|---------|--------|
| 🏢 **Contas Monitoradas** | {summary['total_accounts']} |
| 📁 **Total de Repositórios** | {summary['combined_repos']:,} |
| ⭐ **Total de Stars** | {summary['combined_stars']:,} |
| 🍴 **Total de Forks** | {summary['combined_forks']:,} |

## 🌍 Linguagens Mais Utilizadas

```
"""

    # Adicionar barras de linguagens
    for language, count in top_languages:
        readme_content += generate_language_bar(language, count, max_lang_count) + "\n"
    
    readme_content += "```\n\n"
    
    # Seção de detalhes por conta
    readme_content += "## 👥 Detalhes por Conta\n\n"
    
    for account_name, stats in accounts.items():
        icon = "🏢" if account_name == "empresa" else "👨‍💻"
        title = "Empresa" if account_name == "empresa" else "Pessoal"
        
        readme_content += f"""### {icon} {title} (`{stats['username']}`)

| Métrica | Valor |
|---------|--------|
| 📁 Repositórios Totais | {stats['total_repos']:,} |
| 🌐 Repositórios Públicos | {stats['public_repos']:,} |
| ⭐ Stars Recebidas | {stats['total_stars']:,} |
| 🍴 Forks Recebidos | {stats['total_forks']:,} |
| 🔥 Linguagem Principal | {stats['top_language'] or 'N/A'} |

#### Top 5 Linguagens:
"""
        
        # Top 5 linguagens da conta
        account_languages = sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True)[:5]
        if account_languages:
            max_account_count = max([count for _, count in account_languages])
            for lang, count in account_languages:
                readme_content += f"- **{lang}**: {count} repositórios\n"
        else:
            readme_content += "- Nenhuma linguagem identificada\n"
        
        readme_content += "\n"
    
    # Rodapé
    readme_content += f"""## 📈 Visualização Interativa

🎯 **[Acesse o painel interativo aqui!](https://{os.getenv('GITHUB_REPOSITORY_OWNER', 'usuario')}.github.io/{os.getenv('GITHUB_REPOSITORY', 'repo').split('/')[-1]})**

O painel contém:
- 📊 Gráficos interativos de linguagens
- 📋 Estatísticas detalhadas por conta  
- 🎨 Interface responsiva e moderna
- 🔄 Atualização automática dos dados

## 🤖 Automação

Este repositório utiliza **GitHub Actions** para:
- 🕐 Coletar dados automaticamente (diariamente)
- 💾 Salvar estatísticas em JSON
- 📝 Atualizar este README
- 🚀 Publicar painel no GitHub Pages

## 📅 Última Atualização

**{formatted_date}**

---

<div align="center">
  <sub>🤖 Gerado automaticamente com GitHub Actions</sub>
</div>
"""

    return readme_content

def main():
    """Função principal"""
    print("📝 Gerando README.md...")
    
    # Carregar dados
    data = load_statistics()
    if not data:
        return False
    
    # Gerar README
    readme_content = generate_readme(data)
    
    # Salvar arquivo
    try:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ README.md gerado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar README.md: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)