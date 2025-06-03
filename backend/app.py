from flask import Flask
from routes.routes import setup_routes  # Updated import
from config import Config
from db import db  # Updated import
from db.models import User, WardrobeItem, Tag, WardrobeItemTag

import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register routes
setup_routes(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
