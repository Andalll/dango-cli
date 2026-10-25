import os
import sys
import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

console = Console()

def get_api_key():
    api_key = os.environ.get("NVIDIA_API_KEY")
    
    if not api_key:
        console.print("[bold red][ERROR][/bold red] NVIDIA_API_KEY belum diset di terminal")
        console.print("""Silahkan set dengan cara jalankan: \n
              [green]export NVIDIA_API_KEY=\"nvapi-***\"[green]""")
        sys.exit(1)
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
    console.print("[bold cyan]AI❯ [/bold cyan]")

    try:
        response = requests.post(invoke_url, headers=headers, json=payload)

        if response.status_code != 200:
            console.print(f"[bold red][Error Server {response.status_code}][/bold red]: {response.text}")
            return

        full_text = ""
        with Live(Markdown(""), console=console, refresh_per_second=10) as live: 
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
                        full_text += content
                        live.update(Markdown(full_text))
                  except json.JSONDecodeError:
                    pass
    except Exception as e:
      console.print(f"\n[bold red][Error Koneksi][/bold red]: {e}")

def chat_loop():
  console.print(
    Panel.fit(
      "[bold cyan]Dango: AI CLI Assistant[/bold cyan] \n"
      "[dim]Supported by NVIDIA NIM[/dim]\n"
      "Ketik [yellow]exit[/yellow] atau tekan [yellow]ctrl+c[/yellow] untuk keluar.",
      border_style="cyan"
    )
  )
  

  while True:
    try:
      user_input = console.input("\n[bold green]Anda❯ [/bold green]")

      if user_input.strip().lower() in ["exit", "quit", "/exit"]:
        console.print("[dim]Sampai jumpa![/dim]")
        break 

      if not user_input.strip(): 
        continue 

      ask_ai(user_input)

    except KeyboardInterrupt:
      console.print("\n[dim]Program dihentikan.[/dim]")
      break
      
  

if __name__ == "__main__":
  chat_loop()