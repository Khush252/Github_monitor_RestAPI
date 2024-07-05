# config.py
import os
from dotenv import load_dotenv

load_dotenv()

REPO_OWNER = 'Cpp-Club'
REPO_NAME = 'Cxx_HOPL4_zh'
ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')