from flask import Flask
from flask_session import Session
from routes.routes import setup_routes
from routes.auth_routes import setup_auth_routes
from config import Config
from db import db
from db.models import User, WardrobeItem, Tag, WardrobeItemTag

import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize session management
Session(app)

# Initialize the database
db.init_app(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register routes
setup_routes(app)
setup_auth_routes(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Run without reloader to avoid watchdog issues
    app.run(debug=True, port=5000, use_reloader=False)
