import subprocess
import os

from git import Repo

CK_OUTPUT_DIR = "./ck_output"
CK_JAR_PATH = "./app/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"


def clone_repo(repo_url, repo_name):
    clone_url = f"./repositories/{repo_name}"
    print(f"[+] Clonando repositório {repo_name} ...")

    if os.path.exists(clone_url):
        print(f"[!] O diretório {clone_url} já existe. Pulando clonagem.")
        return

    try:
        Repo.clone_from(repo_url, clone_url)
        print(f"Repositório clonado com sucesso: {clone_url}")
    except Exception as e:
        print(f"Erro ao clonar repositório: {e}")


def run_ck(repo_name):
    print(f"[+] Executando CK para o repositório {repo_name} ...")

    if not os.path.exists(CK_OUTPUT_DIR):
        os.makedirs(CK_OUTPUT_DIR)

    cmd = [
        "java",
        "-jar",
        CK_JAR_PATH,
        f"./repositories/{repo_name}",
        "false",
        "0",
        "false",
        f"{CK_OUTPUT_DIR}/{repo_name}-",
    ]

    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print("Erro ao executar o CK:", e)
