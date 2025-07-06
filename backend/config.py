import os
from dotenv import load_dotenv
from ip_utils import get_api_host

load_dotenv()

class Config:
    UPLOAD_FOLDER = 'uploads'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'senera.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Network Configuration - Auto-detect IP if not set in environment
    API_HOST = get_api_host()  # This will auto-detect if API_HOST env var is not set
    API_PORT = int(os.getenv('API_PORT', '5000'))
    
    # Image Generation Service Configuration
    # Options: "dalle", "pollinations", "huggingface", "replicate"
    IMAGE_GENERATION_SERVICE = os.getenv('IMAGE_GENERATION_SERVICE', 'pollinations')