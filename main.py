import os
import sys
import requests
import json

def get_api_key():
    api_key = os.environ.get("NVIDIA_API_KEY")
    
    if not api_key:
        print("NVIDIA_API_KEY belum diset di terminal")
        print("""Silahkan set dengan cara jalankan: \n
              export NVIDIA_API_KEY=\"nvapi-***\"""")
    return api_key

def ask_ai(prompt_text):
    api_key = get_api_key()

    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
            }
    payload = {
            "model": "nvidia/nemotron-3.5-bolt-e4b",
            "messages": [
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ],
            "temperature": 0.6,
            "max_tokens": 512
            }
    print("Mengirim pesan...")

    try:
        response = requests.post(invoke_url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print("\n AI: ")
            print(answer)
        else:
            print(f"\n[Error Server {response.status_code}]: {response.text}")
    except Exception as e:
        print(f"\n[Error Koneksi]: {e}")

if __name__ == "__main__":
    ask_ai("Halo, sapa singkat di terminal saya.")


