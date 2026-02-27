import requests

url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3",
    "prompt": "Say hello like a powerful AI assistant",
    "stream": False
}

r = requests.post(url, json=data)

print(r.json()["response"])