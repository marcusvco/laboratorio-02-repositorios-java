from dotenv import load_dotenv
from datetime import datetime, timezone

import os
import requests
import csv
import subprocess 
import shutil     
import pandas as pd 
import stat

load_dotenv()

TOTAL_REPOSITORIOS = 100
CK_JAR_PATH = "./ck/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"
REPOS_DIR = "./repositorios_clonados"
OUTPUT_CSV_FILE = "analise_qualidade_repositorios.csv"

token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
query = """
query($queryString: String!, $first: Int!, $after: String) {
  search(query: $queryString, type: REPOSITORY, first: $first, after: $after) {
    repositoryCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        ... on Repository {
          name
          owner { login }
          stargazerCount
          createdAt
          releases { totalCount }
        }
      }
    }
  }
}
"""

def remove_readonly(func, path, excinfo):
    """
    Muda a permissão de arquivos somente leitura e tenta a operação novamente.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def fetch_github_repos():
    query_string = "language:Java sort:stars"
    first = 50
    after_cursor = None
    all_repos = []

    while len(all_repos) < TOTAL_REPOSITORIOS:
        variables = {"queryString": query_string, "first": first, "after": after_cursor}
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(f"Query failed: {response.status_code}, {response.text}")

        result = response.json()
        edges = result["data"]["search"]["edges"]

        for edge in edges:
            if len(all_repos) >= TOTAL_REPOSITORIOS:
                break
            
            repo = edge["node"]
            
            
            owner_login = repo["owner"]["login"]
            repo_name = repo["name"]
            full_repo_name = f"{owner_login}/{repo_name}"
            age_years = 0
            created_at_str = repo.get("createdAt")
            if created_at_str:
                created_at_date = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                age_delta = datetime.now(timezone.utc) - created_at_date
                age_years = age_delta.days / 365.25
            
            all_repos.append(
                {
                    "repositorio": full_repo_name,
                    "stars": repo["stargazerCount"],
                    "maturidade_anos": round(age_years, 2),
                    "atividade_releases": repo["releases"]["totalCount"],
                }
            )

        page_info = result["data"]["search"]["pageInfo"]

        if page_info["hasNextPage"] and len(all_repos) < TOTAL_REPOSITORIOS:
            after_cursor = page_info["endCursor"]
        else:
            break

    return all_repos[:TOTAL_REPOSITORIOS]

def text_to_csv(repositories, filename="output.csv"):
    if not repositories:
        print("Nenhum dado de repositório para salvar.")
        return
        
    headers = [
        'repositorio', 'estrelas', 'maturidade_anos', 'atividade_releases',
        'cbo_media', 'dit_media', 'lcom_media', 'tamanho_loc_total'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        for repo in repositories:
            writer.writerow(repo)



if __name__ == "__main__":
    os.makedirs(REPOS_DIR, exist_ok=True)
    
    repos_metadata = fetch_github_repos()
    
    for i, repo_data in enumerate(repos_metadata):
        repo_name = repo_data["repositorio"]
        repo_local_path = os.path.join(REPOS_DIR, repo_name.split('/')[1])
        
        print(f"\n--- Processando {i+1}/{len(repos_metadata)}: {repo_name} ---")

        default_ck_metrics = {
            'cbo_media': 'N/A', 'dit_media': 'N/A', 
            'lcom_media': 'N/A', 'tamanho_loc_total': 'N/A'
        }
        repo_data.update(default_ck_metrics)

        try:
            print(f"Clonando {repo_name}...")
            clone_url = f"https://github.com/{repo_name}.git"
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, repo_local_path],
                check=True, capture_output=True, text=True
            )

            print("Procurando por diretórios de código-fonte ('src/main/java')...")
            source_dirs = []
            for root, dirs, files in os.walk(repo_local_path):
                if '.git' in dirs:
                    dirs.remove('.git')
                if root.endswith(os.path.join('src', 'main', 'java')):
                    source_dirs.append(root)
            
            if not source_dirs:
                print(f"AVISO: Nenhum diretório 'src/main/java' encontrado. Repositório será salvo sem métricas CK.")
                continue 

            print(f"Diretórios de código encontrados: {len(source_dirs)}. Analisando cada um...")
            
            list_of_dfs = []
            ck_output_dir = os.path.join(repo_local_path, "ck_output")
            os.makedirs(ck_output_dir, exist_ok=True)

            for source_dir in source_dirs:
                ck_command = [
                    "java", "-jar", CK_JAR_PATH,
                    source_dir, "false", "0", "false", ck_output_dir
                ]
                subprocess.run(
                    ck_command, check=True, capture_output=True, text=True, encoding='utf-8'
                )
                
                class_csv_path = os.path.join(ck_output_dir, "class.csv")
                if os.path.exists(class_csv_path):
                    df_temp = pd.read_csv(class_csv_path)
                    list_of_dfs.append(df_temp)

            if list_of_dfs:
                df_ck = pd.concat(list_of_dfs, ignore_index=True)
                
                quality_metrics = {
                    'cbo_media': df_ck['cbo'].mean(),
                    'dit_media': df_ck['dit'].mean(),
                    'lcom_media': df_ck['lcom'].mean(),
                    'tamanho_loc_total': df_ck['loc'].sum()
                }
                
                repo_data.update(quality_metrics)
                print(f"Análise de {repo_name} concluída com sucesso.")
            else:
                print(f"AVISO: Análise CK não gerou dados para {repo_name}.")

        except subprocess.CalledProcessError as e:
            error_message = e.stderr.encode('utf-8', 'ignore').decode('utf-8')
            print(f"ERRO durante a análise CK de {repo_name}: {error_message}")
        
        finally:
            if os.path.exists(repo_local_path):
                print(f"Limpando pasta de {repo_name}...")
                shutil.rmtree(repo_local_path, onerror=remove_readonly)
    
    text_to_csv(repos_metadata, OUTPUT_CSV_FILE)
    print(f"\n✅ Processo finalizado! Resultados salvos em '{OUTPUT_CSV_FILE}'")