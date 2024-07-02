# config.py
import os
from dotenv import load_dotenv

load_dotenv()

REPO_OWNER = 'jestjs'
REPO_NAME = 'jest'
ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')