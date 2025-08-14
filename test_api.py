import os
import sys
import requests

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
    print("Please set the environment variable to run this test.", file=sys.stderr)
    sys.exit(1)

print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")

# Updated model name
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {
    "contents": [{
        "parts": [{
            "text": "Say hello and confirm you're working!"
        }]
    }]
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}", file=sys.stderr)
    sys.exit(1)