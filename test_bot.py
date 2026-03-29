import requests
import os

BOT_TOKEN = os.getenv("   ")
CHAT_ID = os.getenv("    ")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)

send_telegram_message("✅ Test alert: Upbit scanner is live!")
