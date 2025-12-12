# uv add python-dotenv requests

import os

import dotenv
import requests

dotenv.load_dotenv()


def send_slack_notification(message, is_error=True):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if is_error:
        # ペイロードを定義
        payload = {"text": message}
    else:
        payload = {"text": message, "icon_emoji": ":white_check_mark:"}
    # POSTリクエストを送信
    response = requests.post(webhook_url, json=payload)
    return response
