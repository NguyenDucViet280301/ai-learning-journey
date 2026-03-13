import requests
import json

url = "http://localhost:11434/api/generate"

def summarize_text(text):

    prompt = f"""
    Summarize the following text in concise bullets points:

    {text}
    """

    payload = {
        "model": "gpt-oss:20b",
        "prompt": prompt,
        "stream": True
    }

    response = requests.post(url, json=payload, stream=True)

    for line in response.iter_lines():
        
        if line:
            data = json.loads(line.decode("utf-8"))

            token = data.get("response", "")
            print(token, end="", flush=True)
    
