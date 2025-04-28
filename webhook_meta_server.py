from flask import Flask, request
import os
import requests
import json

app = Flask(__name__)

VERIFY_TOKEN = 'mygentlevision2025'
ACCESS_TOKEN = 'EAAk0jZA3kkOwBO7XtAY4XpUGdsZAVe2lzgjv6b0KLJZAMRV3qkIOnZCg7c3HjnEDGlzXDui8OxFVeCeHZBnQ5r6mTfjZC7cAOeZCUAHgsISlR84Ox1ZAffhW3WPbVCRNOA1ZBQmH2zgOZArzyak7Op7z9Pr2aOCwNCVwk0cms6bn7zIbYQhcRNJGyiNmHY5XrailV4h2LJOKbkTOUpGLKCLnK7eP0YFDlJ5mXO2ZBhoFvEZApT97TynTzm16KpBysf2cLVcfzAZDZD'
GRAPH_API_URL = 'https://graph.facebook.com/v18.0/'

# Tambahan untuk tarik Notion
NOTION_TOKEN = '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'
DATABASE_ID = '1e23d146-b43a-80eb-abdd-d8edad000a4b'
NOTION_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_notion_triggers():
    response = requests.post(NOTION_URL, headers=headers)
    data = response.json()

    trigger_words = []
    pdf_mapping = {}

    for result in data['results']:
        properties = result['properties']

        if 'trigger key' in properties and properties['trigger key']['rich_text']:
            trigger = properties['trigger key']['rich_text'][0]['text']['content']
            trigger_words.append(trigger.lower())

            if 'PDF Idea' in properties and properties['PDF Idea']['rich_text']:
                pdf_title = properties['PDF Idea']['rich_text'][0]['text']['content']
                pdf_mapping[trigger.lower()] = f"https://www.dropbox.com/s/{pdf_title.replace(' ', '_')}.pdf?dl=1"

    return trigger_words, pdf_mapping

# Fetch dynamic triggers and PDF links dari Notion
TRIGGER_WORDS, PDF_LINKS = fetch_notion_triggers()

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

                # Check for trigger word
                for word in TRIGGER_WORDS:
                    if word.lower() in text.lower():
                        send_dm(sender_id, word)
                        break
        except Exception as e:
            print(f"Error processing POST: {e}")

        return '200 OK', 200

def send_dm(user_id, trigger_word):
    if trigger_word not in PDF_LINKS:
        print(f"No PDF link mapped for trigger {trigger_word}")
        return

    message_data = {
        "recipient": {"id": user_id},
        "message": {"text": f"Hi! Here's your download link: {PDF_LINKS[trigger_word]}"}
    }

    url = f"{GRAPH_API_URL}me/messages?access_token={ACCESS_TOKEN}"
    response = requests.post(url, json=message_data)
    print(f"Sent DM to {user_id}: {response.text}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
