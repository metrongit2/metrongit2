import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    github_token: str = os.getenv("GITHUB_TOKEN")
    github_org: str = os.getenv("GITHUB_ORG")

settings = Settings()