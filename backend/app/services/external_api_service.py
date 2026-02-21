import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ExternalApiService:
    @staticmethod
    async def search_web(query: str) -> Optional[str]:
        """Search the web using Tavily API."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Web search is disabled (missing API key)."
        
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 3
            }
            # Using requests for simplicity in this session
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results:
                    return "No results found."
                
                formatted = "I found some information on the web:\n"
                for r in results:
                    formatted += f"- {r.get('title')}: {r.get('url')}\n  {r.get('content')[:150]}...\n"
                return formatted
            else:
                logger.error(f"Tavily API error: {response.status_code}")
                return f"Sorry, I couldn't search the web right now (Error {response.status_code})."
        except Exception as e:
            logger.error(f"Failed to call Tavily: {e}")
            return "I encountered an error while searching the web."

    @staticmethod
    async def get_weather(city: str) -> Optional[str]:
        """Get weather info using OpenWeatherMap API."""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "Weather info is disabled (missing API key)."
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                return f"Currently in {city}, it's {temp}°C with {desc}. Humidity is {humidity}%."
            elif response.status_code == 401:
                return "The Weather API key is invalid or not yet active."
            else:
                logger.error(f"Weather API error: {response.status_code}")
                return "I couldn't fetch the weather for that location."
        except Exception as e:
            logger.error(f"Failed to call Weather API: {e}")
            return "I encountered an error while getting the weather."
