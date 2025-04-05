import requests
from flask import current_app
from datetime import datetime

class WeatherService:
    @staticmethod
    def get_current_weather(location):
        try:
            response = requests.get(
                current_app.config['WEATHER_API_URL'],
                params={
                    'key': current_app.config['WEATHER_API_KEY'],
                    'q': location,
                    'aqi': 'no'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'location': f"{data['location']['name']}, {data['location']['country']}",
                'temp_c': data['current']['temp_c'],
                'temp_f': data['current']['temp_f'],
                'condition': data['current']['condition']['text'],
                'humidity': data['current']['humidity'],
                'wind_kph': data['current']['wind_kph'],
                'last_updated': data['current']['last_updated'],
                'is_day': data['current']['is_day']
            }, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_season(location):
        # This is a simplified version - you might want to use a more accurate method
        # based on hemisphere and location
        now = datetime.now()
        month = now.month
        
        if 3 <= month <= 5:
            return "Spring"
        elif 6 <= month <= 8:
            return "Summer"
        elif 9 <= month <= 11:
            return "Fall"
        else:
            return "Winter"
    
    @staticmethod
    def get_gardening_tips(weather_data):
        temp = weather_data['temp_c']
        condition = weather_data['condition'].lower()
        humidity = weather_data['humidity']
        
        tips = []
        
        # Temperature-based tips
        if temp < 5:
            tips.append("It's very cold - protect sensitive plants from frost.")
        elif 5 <= temp < 15:
            tips.append("Cool weather - good for planting cool-season crops.")
        elif 15 <= temp < 25:
            tips.append("Mild temperatures - ideal for most gardening activities.")
        else:
            tips.append("Hot weather - water plants early in the morning or late in the evening.")
        
        # Condition-based tips
        if 'rain' in condition:
            tips.append("Rainy conditions - reduce watering and check for proper drainage.")
        if 'sun' in condition or 'clear' in condition:
            tips.append("Sunny weather - ensure plants have adequate water and shade if needed.")
        if 'wind' in condition:
            tips.append("Windy conditions - protect young plants and stake tall plants.")
        
        # Humidity-based tips
        if humidity > 70:
            tips.append("High humidity - watch for fungal diseases and ensure good air circulation.")
        elif humidity < 30:
            tips.append("Low humidity - plants may need more frequent watering.")
        
        return tips