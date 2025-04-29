# File: webhook_meta_server.py

import os
import json
import requests
import threading
from flask import Flask, request
from dropbox_oauth_handler import get_access_token

app = Flask(__name__)

# IG Webhook Tokens
VERIFY_TOKEN = os.environ.get("IG_VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")
GRAPH_API_URL = 'https://graph.facebook.com/v18.0/'

# Telegram Config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Dropbox Access Token
DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

# Dropbox Storage Threshold
THRESHOLD_MB = 500
TARGET_FREE_MB = 1000

# Webhook Routes
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token_sent = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token_sent == VERIFY_TOKEN:
            return challenge
        return 'Invalid verification token', 403
    elif request.method == 'POST':
        payload = request.get_json()
        try:
            entry = payload['entry'][0]
            changes = entry['changes'][0]
            if changes['field'] == 'comments':
                comment_id = changes['value']['id']
                sender_id = changes['value']['from']['id']
                text = changes['value']['message']
                # Handle IG Comment logic here
        except Exception as e:
            print(f"Error processing POST: {e}")
        return '200 OK', 200

# Telegram Notif
def send_telegram_message(message: str) -> bool:
    """
    Mengirim pesan ke Telegram Bot secara otomatis.

    Args:
        message (str): Pesan yang ingin dikirim.

    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"Gagal kirim pesan. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception saat kirim pesan Telegram: {e}")
        return False

# Example penggunaan manual (bisa dihapus kalau sudah diintegrasi ke server)
if __name__ == "__main__":
    test_message = "✅ Test pesan dari server webhook meta berhasil!"
    send_telegram_message(test_message)

# Dropbox Monitor & Cleanup

def get_dropbox_storage():
    url = 'https://api.dropboxapi.com/2/users/get_space_usage'
    headers = {
        'Authorization': f'Bearer {DROPBOX_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers)

if response.status_code != 200:
    print(f"[ERROR] Dropbox API failed! Status: {response.status_code}")
    print("Response text:", response.text)
    return 0  # atau raise Exception jika ingin stop

data = response.json()

    if 'allocation' not in data or 'used' not in data:
        send_telegram_message("❌ ERROR: Dropbox response missing 'allocation'.")
        print("[ERROR] Dropbox API response tidak valid:", data)
        return float('inf')  # Skip cleanup if unknown

    allocated = data['allocation'].get('allocated', 0)
    used = data.get('used', 0)
    free = allocated - used
    return free / (1024 * 1024)

def get_dropbox_files():
    url = 'https://api.dropboxapi.com/2/files/list_folder'
    headers = {'Authorization': f'Bearer {DROPBOX_TOKEN}', 'Content-Type': 'application/json'}
    data = {"path": "", "recursive": True}
    response = requests.post(url, headers=headers, json=data)
    return response.json().get('entries', [])

def delete_file(path_lower):
    url = 'https://api.dropboxapi.com/2/files/delete_v2'
    headers = {'Authorization': f'Bearer {DROPBOX_TOKEN}', 'Content-Type': 'application/json'}
    data = {"path": path_lower}
    requests.post(url, headers=headers, json=data)

def monitor_and_cleanup_dropbox():
    free_mb = get_dropbox_storage()
    if free_mb < THRESHOLD_MB:
        send_telegram_message(f"[WARNING] Free Dropbox space tinggal {free_mb:.2f}MB. Mulai cleanup!")
        files = get_dropbox_files()
        files = sorted((f for f in files if f['.tag'] == 'file'), key=lambda x: x['server_modified'])
        for file in files:
            delete_file(file['path_lower'])
            free_mb = get_dropbox_storage()
            if free_mb > TARGET_FREE_MB:
                send_telegram_message(f"[INFO] Cleanup selesai. Free space sekarang {free_mb:.2f}MB.")
                break

# Scheduler background

def schedule_cleanup():
    monitor_and_cleanup_dropbox()
    threading.Timer(3600, schedule_cleanup).start()

schedule_cleanup()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
