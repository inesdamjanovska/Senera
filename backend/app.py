from flask import Flask
from flask_session import Session
from flask_cors import CORS
from config import Config
from db import db

app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS to allow your phone to connect
api_host = app.config['API_HOST']
CORS(app, origins=['http://localhost:3000', f'http://{api_host}:8081', f'exp://{api_host}:8081'], 
     supports_credentials=True)

# Initialize database with app
db.init_app(app)

# Configure session
Session(app)

# Import and setup your existing routes (don't change the route files!)
from routes.auth_routes import setup_auth_routes
from routes.routes import setup_routes

# Setup routes using your existing functions
setup_auth_routes(app)
setup_routes(app)

# Create tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    # Use configuration for host and port
    host = app.config['API_HOST']
    port = app.config['API_PORT']
    # Temporarily disable debug mode to avoid watchdog issue
    app.run(debug=False, host='0.0.0.0', port=port)
