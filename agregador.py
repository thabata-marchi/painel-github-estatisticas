import requests
import json
import os
from datetime import datetime
import time

def get_all_repos(username, token=None):
    repos = []
    page = 1
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        
        try:
            response = requests.get(url, headers=headers)
            
            # Tratamento de rate limiting
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - int(time.time()), 60)
                print(f"Rate limit atingido. Aguardando {wait_time} segundos...")
                time.sleep(wait_time)
                response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Erro ao buscar repos de {username}: {response.status_code} - {response.text}")
            
            data = response.json()
            if not data:
                break
            repos.extend(data)
            page += 1
            
            # Pequena pausa para evitar rate limiting
            time.sleep(0.1)
            
        except requests.RequestException as e:
            print(f"Erro de conexão ao buscar repos de {username}: {e}")
            raise
    
    return repos

def get_detailed_stats(username, token=None):
    repos = get_all_repos(username, token)
    
    lang_count = {}
    total_repos = len(repos)
    total_stars = 0
    total_forks = 0
    public_repos = 0
    
    for repo in repos:
        # Contabilizar linguagens
        lang = repo.get('language')
        if lang:
            lang_count[lang] = lang_count.get(lang, 0) + 1
        
        # Outras estatísticas
        total_stars += repo.get('stargazers_count', 0)
        total_forks += repo.get('forks_count', 0)
        if not repo.get('private', True):
            public_repos += 1
    
    return {
        'username': username,
        'languages': lang_count,
        'total_repos': total_repos,
        'public_repos': public_repos,
        'total_stars': total_stars,
        'total_forks': total_forks,
        'top_language': max(lang_count.items(), key=lambda x: x[1])[0] if lang_count else None
    }

def save_statistics_to_json(stats, filename='estatisticas.json'):
    """Salva as estatísticas em um arquivo JSON"""
    timestamp = datetime.now().isoformat()
    
    # Estrutura dos dados
    data = {
        'last_updated': timestamp,
        'accounts': stats,
        'summary': {
            'total_accounts': len(stats),
            'combined_repos': sum(account['total_repos'] for account in stats.values()),
            'combined_stars': sum(account['total_stars'] for account in stats.values()),
            'combined_forks': sum(account['total_forks'] for account in stats.values()),
        }
    }
    
    # Combinar linguagens de todas as contas
    combined_languages = {}
    for account_stats in stats.values():
        for lang, count in account_stats['languages'].items():
            combined_languages[lang] = combined_languages.get(lang, 0) + count
    
    data['summary']['combined_languages'] = dict(sorted(combined_languages.items(), key=lambda x: x[1], reverse=True))
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Estatísticas salvas em {filename}")
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON: {e}")
        return False

if __name__ == "__main__":
    # Obter token do ambiente (se disponível)
    github_token = os.getenv('GITHUB_TOKEN')
    
    try:
        print("Coletando dados da conta empresa...")
        empresa_stats = get_detailed_stats('thabata1', github_token)
        
        print("Coletando dados da conta pessoal...")
        pessoal_stats = get_detailed_stats('thabata-marchi', github_token)
        
        # Organizar dados para salvar
        all_stats = {
            'empresa': empresa_stats,
            'pessoal': pessoal_stats
        }
        
        # Salvar em JSON
        if save_statistics_to_json(all_stats):
            print("\n✅ Dados coletados e salvos com sucesso!")
        
        # Exibir resumo
        print(f"\n📊 Resumo:")
        print(f"Conta empresa: {empresa_stats['total_repos']} repos, {empresa_stats['total_stars']} stars")
        print(f"Conta pessoal: {pessoal_stats['total_repos']} repos, {pessoal_stats['total_stars']} stars")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        exit(1)
