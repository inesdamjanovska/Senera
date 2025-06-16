from app import app
from db import db
from db.models import User, WardrobeItem, Tag, WardrobeItemTag

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        # Drop all tables and recreate (for development)
        db.drop_all()
        db.create_all()
        
        print("Database initialized successfully!")
        print("Tables created:")
        print("- users")
        print("- wardrobe_items") 
        print("- tags")
        print("- wardrobe_item_tags")

if __name__ == '__main__':
    init_database()