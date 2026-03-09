import os
import requests
from dotenv import load_dotenv

# 1. Load your .env file
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_token():
    # Use the token URL from your previous snippet
    url = "https://accounts.spotify.com/api/token"
    
    print(f"Attempting to connect with Client ID: {CLIENT_ID[:5]}...")
    
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print("\n✅ SUCCESS! Your token is:")
        print("-" * 20)
        print(token)
        print("-" * 20)
        print("\nThis token will expire in 1 hour.")
        return token
    else:
        print(f"\n❌ FAILED! Status Code: {response.status_code}")
        print(f"Error Message: {response.text}")
        return None

if __name__ == "__main__":
    get_token()