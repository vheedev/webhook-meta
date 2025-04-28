from flask import Flask, request
import os
import requests
import json
from dropbox_oauth_handler import get_access_token


app = Flask(__name__)

VERIFY_TOKEN = 'mygentlevision2025'
ACCESS_TOKEN = 'EAAk0jZA3kkOwBO7XtAY4XpUGdsZAVe2lzgjv6b0KLJZAMRV3qkIOnZCg7c3HjnEDGlzXDui8OxFVeCeHZBnQ5r6mTfjZC7cAOeZCUAHgsISlR84Ox1ZAffhW3WPbVCRNOA1ZBQmH2zgOZArzyak7Op7z9Pr2aOCwNCVwk0cms6bn7zIbYQhcRNJGyiNmHY5XrailV4h2LJOKbkTOUpGLKCLnK7eP0YFDlJ5mXO2ZBhoFvEZApT97TynTzm16KpBysf2cLVcfzAZDZD'
GRAPH_API_URL = 'https://graph.facebook.com/v18.0/'

DROPBOX_TOKEN = 'sl.u.AFvkQ-idv4o5pyc3s4-RXHugh4nWOviEKVZnSdnvt5RX62z0l4uNcMjRTTGz-sHKGMrIRz3DXMxWer5eNcbInq2rTfzJ0vgNj_0xv1wVOWNPefFo97p6Zm7JP6xCQfloLQPBATDX6MoqgPsg839JdJbTHHEzIZtBp2Kxp2rN9_lqbj5XXcseqV-5hSi5KSIqO8TN_bHXNr1lm3ogrllLqLqGg6QouFGe_1QWRCsVEZw8uNtHjd0vxD8TE8b_BlOHS5VBznvM4g8XK2pmSBxyDmTRieLU2T0mwPrr6il1IpD1AUJWmr0jEjkmQgtPDiOLXCY-XdTPJC8XdiHq7cUEaTxIN71bh_VcS2yaiP9BQ147Tr29owTYrS_VUZirVR0hSH_4FjyvpA46mARsCPkOJkaKAIV-6bXuhxDYX3r0HPHkA5aeCRePI45sg0Hp3_As4zeRH6pid-hw6S385Lw2cePKPmYTdfhc_f23waOyiOFLVPlO_81QYpmau7ve8F6GfkfYK-IgAOPiZ3gaIqp5VSr7t5ce20FB5WSWu6rcbfSjx2VpklJVvHnMbeg7G5nxVE6GIT6p1ToP6htTDDuBVQY_4uWGZHMJFmfqdzQd9k2F3RWM4mp-_lrnG8m3uTlStiSf5J-aznKZ2lWdBCh1Vq3fVxfjuxuf8v-DtlnHzVyDA9KTjDzEScbM5cIWXfdTS82_D-UEEfzpkDy4WBfF4PQ-36LiODA7o0_0T6NF22hq0towEzIakm-O63gtz6unZt7enVAmi-rpy3-s04eo9W5xJM8cHJYD3WcC67aSHQTXD5a9z2DgQ1X8YRlTRaOoZTnTEIj3H3rUbyyyivzqxtJH815tE3Cf9ri7cqOHZqqOm8UbDN9alZOjeXZIdgoGOMTKxThszEjVQPs2Vgaggq2D851wn2ef1UYPztRTYZUUBNsH8PzWhZXHzp7uyZHZZHxlWwq6isehxxeL4HtYkwQ_BA40INnKswIXG_hYP67NsCS8PF_jGu3M6rGGGZmEc4fMbmaYhWhcj6BLsKtTH-OWSPFakseCGKUtd7L5N7dDcqtgekm2WNMj_mJC9aBQPbhZn9KXSWLwVdv1xwplfor7hH-7eykD_MSWbQSV42J7cQjY7iHgmL2RzCRIhJs7N8foyHqqYeHHwyUpQLaJDgiV0tHxPzEfy-9vtCLXoeoDknGrSi8A3MB67WhsVeiS6-97qPhgzxZJstjkeux6aaUptzyleDGAkIMTRes8yM5E3UTNlmHEC6BEqAFZiG8tD73UG827vTlvnprsL0t7vgJJKtcAfZR2i-vVAcTJ0GGIvOwYGsK69QeqQ7RfwbzVO_8RKANAPqWUY1SBaU7KFZJ9QjMku7NS_nZEvN2DzswClYiUUd5TRSAzwaspJBmcAqYX2PX73HNK3ev6AJMNNeWl'

def list_dropbox_files():
    url = 'https://api.dropboxapi.com/2/files/list_folder'
    headers = {
        'Authorization': f'Bearer {DROPBOX_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'path': ''
    }
    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    
# Kemudian, sebelum kamu pakai Dropbox API, ambil token
DROPBOX_TOKEN = get_access_token()

# Gunakan DROPBOX_TOKEN untuk call Dropbox API
headers = {
    "Authorization": f"Bearer {DROPBOX_TOKEN}",
    "Content-Type": "application/json"
}

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
