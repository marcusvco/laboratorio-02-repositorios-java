from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("GITHUB_TOKEN")


if __name__ == "__main__":
    print("teste")
    print(token)
