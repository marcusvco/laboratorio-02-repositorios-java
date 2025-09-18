from dotenv import load_dotenv
from datetime import datetime, timezone

import os
import requests
import csv

from ck import clone_repo, run_ck

load_dotenv()

TOTAL_REPOSITORIOS = 1000

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
          stargazerCount
          createdAt
          url
          releases { totalCount }
        }
      }
    }
  }
}
"""


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

            age_years = 0
            created_at_str = repo.get("createdAt")
            if created_at_str:
                created_at_date = datetime.fromisoformat(
                    created_at_str.replace("Z", "+00:00")
                )
                age_delta = datetime.now(timezone.utc) - created_at_date
                age_years = age_delta.days / 365.25

            all_repos.append(
                {
                    "name": repo["name"],
                    "stars": repo["stargazerCount"],
                    "maturidade_anos": round(age_years, 2),
                    "atividade_releases": repo["releases"]["totalCount"],
                    "url": repo["url"],
                }
            )

        page_info = result["data"]["search"]["pageInfo"]

        if page_info["hasNextPage"] and len(all_repos) < TOTAL_REPOSITORIOS:
            after_cursor = page_info["endCursor"]
        else:
            break

    return all_repos[:TOTAL_REPOSITORIOS]


def text_to_csv(repositories, filename="output.csv"):
    headers = ["name", "releases", "stars", "idade"]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for repo in repositories:
            writer.writerow(
                {
                    "name": repo["name"],
                    "releases": repo["atividade_releases"],
                    "stars": repo["stars"],
                    "idade": repo["maturidade_anos"],
                }
            )


if __name__ == "__main__":
    repos = fetch_github_repos()

    text_to_csv(repos, "repositorios.csv")
    print("Arquivo repositorios.csv gerado com sucesso.\n")

    print(f"Fetched {len(repos)} repositories")
    for r in repos:
        clone_repo(r["url"], r["name"])
        run_ck(r["name"])
        print(
            f" Nome:{r['name']} | Atividade (Releases): {r['atividade_releases']} | Idade:{r['maturidade_anos']} \n"
            f" Stars: {r['stars']} \n"
            f" URL: {r['url']} \n"
            "--------------------------------------------------"
        )
