
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "virelle_webhook_token"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Error, invalid token", 403

    if request.method == 'POST':
        data = request.json
        print(f"Received webhook POST: {data}")
        return "Received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
