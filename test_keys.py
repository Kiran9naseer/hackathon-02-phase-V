import requests
import json

def test_weather(key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Karachi&appid={key}"
    try:
        r = requests.get(url)
        print(f"Weather Status: {r.status_code}")
        print(f"Weather Body: {r.text}")
    except Exception as e:
        print(f"Weather Error: {e}")

def test_tavily(key):
    url = "https://api.tavily.com/search"
    payload = {"api_key": key, "query": "latest news"}
    try:
        r = requests.post(url, json=payload)
        print(f"Tavily Status: {r.status_code}")
        print(f"Tavily Body: {r.text}")
    except Exception as e:
        print(f"Tavily Error: {e}")

if __name__ == "__main__":
    weather_key = "87e3de8094173a10e4cf78f39b5f65b6"
    tavily_key = "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"
    
    print("Testing Keys...")
    test_weather(weather_key)
    test_tavily(tavily_key)
