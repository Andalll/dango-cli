import os
import sys
import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

console = Console()
MODEL = "nvidia/nemotron-3.5-bolt-e4b" 
MAX_TOKEN = 1024
TEMPERATURE = 0.6
TIMEOUT = (10, 120)

def get_api_key():
    api_key = os.environ.get("NVIDIA_API_KEY")
    
    if not api_key:
        console.print("[bold red][ERROR][/bold red] NVIDIA_API_KEY belum diset di terminal")
        console.print('Silakan set dengan cara jalankan: \n[green]export NVIDIA_API_KEY=\"nvapi-***\"[green]')
        sys.exit(1)
    return api_key

def ask_ai(messages):
    api_key = get_api_key()
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
            }
    payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKEN,
            "stream": True
            }
  
    console.print("[bold cyan]AI❯ [/bold cyan]")
  
    try:
      with requests.post(invoke_url, headers=headers, json=payload, stream=True, timeout=TIMEOUT) as response:
        if response.status_code != 200:
              console.print(f"[bold red][Error Server {response.status_code}][/bold red]: {response.text}")
              return None
        full_text = ""
        with console.status("[cyan]Menunggu response...", spinner="dots"): 
          for line in response.iter_lines():
              if not line:
                continue
              line_str = line.decode("utf-8")
              if not line_str.startswith("data: "):
                continue
              data_content = line_str[6:]
              if data_content.strip() == "[DONE]":
                break 
              try:
                json_data = json.loads(data_content)
              except json.JSONDecodeError:
                continue
              choices = json_data.get("choices", [])
              if choices and len(choices) > 0:
                content = choices[0].get("delta", {}).get("content")
                if content:
                  full_text += content
        if full_text:
          console.print(Markdown(full_text))
                  
    except KeyboardInterrupt:
      console.print("[dim]Respon dibatalkan![/dim]")
      return None
      
    except request.RequestException as e:
      console.print(f"\n[bold red][Error Koneksi][/bold red]: {e}")
      return None
      
    return full_text

def chat_loop():
  console.print(
    Panel.fit(
      "[bold cyan]Dango: AI CLI Assistant[/bold cyan] \n"
      "[dim]Supported by NVIDIA NIM[/dim]\n"
      "Ketik [yellow]exit[/yellow] atau tekan [yellow]ctrl+c[/yellow] untuk keluar.",
      border_style="cyan"
    )
  )
  history = []
  

  while True:
    try:
      user_input = console.input("\n[bold green]Anda❯ [/bold green]")

      if user_input.strip().lower() in ["exit", "quit", "/exit"]:
        console.print("[dim]Sampai jumpa![/dim]")
        break 

      if not user_input.strip(): 
        continue 

      history.append({"role": "user", "content": user_input})
      reply = ask_ai(history)

      if reply:
        history.append({"role": "assistant", "content": reply})
      else:
        history.pop()
        
    except KeyboardInterrupt:
      console.print("\n[dim]Program dihentikan.[/dim]")
      break
      
  

if __name__ == "__main__":
  chat_loop()