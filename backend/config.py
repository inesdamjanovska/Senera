import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPLOAD_FOLDER = 'uploads'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'senera.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources