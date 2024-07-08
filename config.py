# config.py
import os
from dotenv import load_dotenv

load_dotenv()

REPO_OWNER = 'wizardforcel'
REPO_NAME = 'eloquent-js-3e-zh'
ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')