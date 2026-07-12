import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BENGALURU_LAT = 12.9716
BENGALURU_LON = 77.5946

def get_current_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={BENGALURU_LAT}&lon={BENGALURU_LON}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        return {
            "city": "Bengaluru",
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "rainfall_1h": data.get("rain", {}).get("1h", 0),
            "flood_risk": calculate_flood_risk(data),
            "disaster_risk_level": calculate_disaster_risk(data)
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_flood_risk(data):
    rainfall = data.get("rain", {}).get("1h", 0)
    humidity = data["main"]["humidity"]
    
    if rainfall > 20 or humidity > 90:
        return "HIGH"
    elif rainfall > 10 or humidity > 75:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_disaster_risk(data):
    rainfall = data.get("rain", {}).get("1h", 0)
    wind = data["wind"]["speed"]
    
    if rainfall > 20 or wind > 15:
        return "HIGH"
    elif rainfall > 10 or wind > 10:
        return "MEDIUM"
    else:
        return "LOW"