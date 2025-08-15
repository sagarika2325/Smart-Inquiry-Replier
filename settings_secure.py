# Add this at the top of settings.py after the imports
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Google Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
