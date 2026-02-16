import requests
import os
from flask import Flask
import threading

# ===== CONFIG =====
UPBIT_BOT_TOKEN = os.getenv("UPBIT_BOT_TOKEN")
UPBIT_CHAT_ID = os.getenv("UPBIT_CHAT_ID")

# ===== DEBUG PRINT (without leaking secrets) =====
print("🔹 Debug: Checking environment variables")
print("UPBIT_BOT_TOKEN set ✅" if UPBIT_BOT_TOKEN else "UPBIT_BOT_TOKEN is NOT set ❌")
print("UPBIT_CHAT_ID set ✅" if UPBIT_CHAT_ID else "UPBIT_CHAT_ID is NOT set ❌")

# ===== TELEGRAM TEST FUNCTION =====
def send_telegram_message(message):
    if not UPBIT_BOT_TOKEN or not UPBIT_CHAT_ID:
        print("⚠️ Telegram token or chat ID not set")
        return
    url = f"https://api.telegram.org/bot{UPBIT_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": UPBIT_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        print(f"Telegram response: {resp.text}")
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")

# ===== FLASK KEEP-ALIVE =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Debug bot running!"

@app.route('/test-alert')
def test_alert():
    send_telegram_message("🚀 Test alert from debug bot!")
    return "Test message sent!", 200

def run_web():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Start Flask in a background daemon thread to avoid blocking and prevent
    # unintended server startup on import.
    threading.Thread(target=run_web, daemon=True).start()

    # ===== Send one test message on startup =====
    send_telegram_message("🚀 Debug: Test message on startup!")
