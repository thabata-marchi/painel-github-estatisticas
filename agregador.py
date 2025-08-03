import requests

def get_all_repos(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Erro ao buscar repos: {response.status_code} - {response.text}")
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_top_languages(username):
    repos = get_all_repos(username)
    lang_count = {}
    for repo in repos:
        lang = repo.get('language')
        if lang:
            lang_count[lang] = lang_count.get(lang, 0) + 1
    return lang_count

if __name__ == "__main__":
    empresa = get_top_languages('thabata1')
    pessoal = get_top_languages('thabata-marchi')

    print("Conta empresa:", empresa)
    print("Conta pessoal:", pessoal)
