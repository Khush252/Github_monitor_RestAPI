# config.py
import os
from dotenv import load_dotenv

load_dotenv()

REPO_OWNER = 'i5ting'
REPO_NAME = 'asynchronous-flow-control'
ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')