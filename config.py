# config.py
import os
from dotenv import load_dotenv

load_dotenv()

REPO_OWNER = 'Khush252'
REPO_NAME = 'Github_monitor_testing'
ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')