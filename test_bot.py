import requests
import os

BOT_TOKEN = os.getenv("8205514298:AAEaL4Btdl0oT5Ohu3RZj7moY3DU3HuPS6w")
CHAT_ID = os.getenv("7523660884")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

send_telegram_message("✅ Test alert: Upbit scanner is live!")
