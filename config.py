import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'arborai.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Azure OpenAI settings
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-02-01')
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.environ.get('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME', 'gpt-4o-kenya-hack')
    
    # # Weather API settings
    # WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    # WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
    
    # Marketplace settings
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    @staticmethod
    def init_app(app):
        pass