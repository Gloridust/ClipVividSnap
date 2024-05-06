import requests
import api_config

url = api_config.chat_url

headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {api_config.APIKEY}'
}

data = {
  "model": "gpt-3.5-turbo",
  "messages": [{"role": "user", "content": "你好呀"}]
}

response = requests.post(url, headers=headers, json=data)
response_json=response.json()

for choice in response_json["choices"]:
    content = response_json["message"]["content"]
    print("Content:", content)