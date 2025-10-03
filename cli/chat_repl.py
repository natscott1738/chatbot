import os
import requests

API_KEY = os.getenv("API_KEY", "")
BASE = "http://localhost:8000/v1"

def repl():
    if not API_KEY:
        print("Set API_KEY env var or add to .env and export before running.")
        return
    print("CBK Chatbot (type 'exit' to quit)")
    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        r = requests.post(
            f"{BASE}/chat",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json={"text": q, "use_rag": True},
            timeout=20,
        )
        if r.ok:
            print("Bot:", r.json().get("reply"))
        else:
            print("Error:", r.status_code, r.text)

if __name__ == "__main__":
    repl()
