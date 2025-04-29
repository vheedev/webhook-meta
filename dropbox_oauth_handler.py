import os
import requests

def get_access_token():
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if token:
        return token
    else:
        raise Exception("Dropbox access token not found in environment variables.")
