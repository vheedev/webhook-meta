from flask import Flask, request
import os

app = Flask(__name__)

VERIFY_TOKEN = 'mygentlevision2025'  # Token ini harus sama dengan yang di Meta Developer Settings

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token_sent = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token_sent == VERIFY_TOKEN:
            return challenge
        return 'Invalid verification token', 403
    elif request.method == 'POST':
        return '200 OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
