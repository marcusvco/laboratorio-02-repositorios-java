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

TOTAL_REPOSITORIOS = 5
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
    
    final_results = []
    
    for i, repo_data in enumerate(repos_metadata):
        repo_name = repo_data["repositorio"]
        repo_local_path = os.path.join(REPOS_DIR, repo_name.split('/')[1])
        
        print(f"\n--- Processando {i+1}/{len(repos_metadata)}: {repo_name} ---")

        try:
            print(f"Clonando {repo_name}...")
            clone_url = f"https://github.com/{repo_name}.git"
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, repo_local_path],
                check=True, capture_output=True, text=True
            )

            print(f"Executando CK para {repo_name}...")
            ck_output_dir = os.path.join(repo_local_path, "ck_output")
            os.makedirs(ck_output_dir, exist_ok=True)
            
            ck_command = [
                "java", "-jar", CK_JAR_PATH,
                repo_local_path, "false", "0", "false", ck_output_dir
            ]
            result = subprocess.run(
                ck_command, 
                check=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8' # Adicionado para melhor compatibilidade
            )
            
            # IMPRIMIMOS O QUE O CK DISSE (SAÍDA PADRÃO E ERRO PADRÃO)
            print(f"--- Saída do CK para {repo_name} ---")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            print("------------------------------------")

            class_csv_path = os.path.join(ck_output_dir, "class.csv")
            if os.path.exists(class_csv_path):
                df_ck = pd.read_csv(class_csv_path)
                
                quality_metrics = {
                        'cbo_media': df_ck['cbo'].mean(),
                        'dit_media': df_ck['dit'].mean(),
                        'lcom_media': df_ck['lcom'].mean(),
                        'tamanho_loc_total': df_ck['loc'].sum() # LOC para a métrica de Tamanho
                    }
                
                # Juntamos os metadados do GitHub com as métricas de qualidade
                repo_data.update(quality_metrics)
                final_results.append(repo_data)
                print(f"Análise de {repo_name} concluída com sucesso.")
            else:
                print(f"AVISO: Arquivo class.csv não foi gerado para {repo_name}. Pulando.")

        except subprocess.CalledProcessError as e:
            print(f"ERRO ao processar {repo_name}: {e.stderr}")
        
        finally:
            # ETAPA DE AUTOMAÇÃO 4: LIMPAR (REMOVER A PASTA DO REPOSITÓRIO)
            if os.path.exists(repo_local_path):
                print(f"Limpando pasta de {repo_name}...")
                shutil.rmtree(repo_local_path, onerror=remove_readonly)
    
    text_to_csv(final_results, OUTPUT_CSV_FILE)
    print(f"\n✅ Processo finalizado! Resultados salvos em '{OUTPUT_CSV_FILE}'")