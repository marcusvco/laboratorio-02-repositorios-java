from dotenv import load_dotenv

import os
import requests

load_dotenv()

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
          owner {
            login
          }
          stargazerCount
          forkCount
          url
          description
        }
      }
    }
  }
}
"""


def fetch_github_repos():
    query_string = "language:Java sort:stars"
    first = 100
    after_cursor = None
    all_repos = []

    while True:
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
            repo = edge["node"]
            all_repos.append(
                {
                    "name": repo["name"],
                    "owner": repo["owner"]["login"],
                    "stars": repo["stargazerCount"],
                    "forks": repo["forkCount"],
                    "url": repo["url"],
                    "description": repo["description"],
                }
            )

        page_info = result["data"]["search"]["pageInfo"]

        if page_info["hasNextPage"] and len(all_repos) < 1000:
            after_cursor = page_info["endCursor"]
        else:
            break

    return all_repos


if __name__ == "__main__":
    repos = fetch_github_repos()
    print(f"Fetched {len(repos)} repositories")
    for r in repos[:1000]:
        print(
            f"Stars: {r['stars']} Owner/Repo: {r['owner']}/{r['name']} - URL: {r['url']}"
        )
