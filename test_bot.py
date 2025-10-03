import requests
import os

BOT_TOKEN = os.getenv("UPBIT_BOT_TOKEN")
CHAT_ID = os.getenv("UPBIT_CHAT_ID")

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram token or chat ID not set")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")

if __name__ == "__main__":
    send_telegram_message("✅ Test alert: Upbit scanner is live!")
