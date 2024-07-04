import requests
import json
import os

def send_slack_alert(message, is_block=False):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if is_block:
        payload = {
            "blocks": message
        }
    else:
        payload = {
            "text": message
        }
    
    print("Payload being sent to Slack:")
    print(json.dumps(payload, indent=4))  # Print the payload for debugging
    
    response = requests.post(
        webhook_url, data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"Slack API response status: {response.status_code}")
        print(f"Slack API response body: {response.text}")
        raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
