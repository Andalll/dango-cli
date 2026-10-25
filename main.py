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
            "Accept": "text/event-stream",
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
            "max_tokens": 512,
            "stream": True
            }
    print("\nAI ❯", end="", flush=True)

    try:
        response = requests.post(invoke_url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"\n[Error Server {response.status_code}]: {response.text}")
            return
        for line in response.iter_lines():
            if line:
              line_str = line.decode("utf-8")
              if line_str.startswith("data: "): 
                data_content = line_str[6:]
                if data_content.strip() == "[DONE]":
                  break 
                try :
                  json_data = json.loads(data_content)
                  choices = json_data.get("choices", [])
                  if choices and len(choices) > 0:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                      print(content, end="", flush=True)
                except json.JSONDecodeError:
                  pass
        print()
    except Exception as e:
      print(f"\n[Error Koneksi]: {e}")

if __name__ == "__main__":
  ask_ai("Jelaskan apa itu streaming data dalam 2 kalimat saja.")