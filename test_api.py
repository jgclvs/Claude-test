import requests

api_key = "AIzaSyAFSUjAJ3lSeuQeMt_YQt-wvIpFjDvN6sw"
print(f"API key: {api_key[:10]}...{api_key[-4:]}")

# Updated model name
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {
    "contents": [{
        "parts": [{
            "text": "Say hello and confirm you're working!"
        }]
    }]
}

response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")