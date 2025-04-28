# File: dropbox_oauth_handler.py

import requests
import json

# Isi dari Dropbox App kamu
APP_KEY = 'fdvhgveh2y6bp2z'
APP_SECRET = 'yfbfrtrolx5bo1w'
REDIRECT_URI = 'https://localhost'  # Untuk development, bisa localhost

# Simpan token disini
TOKEN_STORE_FILE = 'dropbox_tokens.json'

def generate_auth_url():
    return f"https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&redirect_uri={REDIRECT_URI}&response_type=code&token_access_type=offline"

def exchange_code_for_token(auth_code):
    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "code": auth_code,
        "grant_type": "authorization_code",
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(url, data=data)
    tokens = response.json()

    with open(TOKEN_STORE_FILE, 'w') as f:
        json.dump(tokens, f)

    print("Tokens saved successfully!")

def refresh_access_token():
    with open(TOKEN_STORE_FILE, 'r') as f:
        tokens = json.load(f)

    refresh_token = tokens.get('refresh_token')
    if not refresh_token:
        raise Exception("No refresh token found, need to authorize first.")

    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }

    response = requests.post(url, data=data)
    new_tokens = response.json()

    # Update access token
    tokens['access_token'] = new_tokens['access_token']

    with open(TOKEN_STORE_FILE, 'w') as f:
        json.dump(tokens, f)

    return tokens['access_token']

def get_access_token():
    try:
        with open(TOKEN_STORE_FILE, 'r') as f:
            tokens = json.load(f)
            return tokens['access_token']
    except FileNotFoundError:
        raise Exception("No tokens found. Please authorize first.")

if __name__ == "__main__":
    print("Go to the following URL and authorize the app:")
    print(generate_auth_url())

    auth_code = input("Paste the authorization code here: ").strip()
    exchange_code_for_token(auth_code)
