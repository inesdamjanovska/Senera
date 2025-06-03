import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from db import db
from db.models import Tag

def populate_tags():
    tags = [
        # Type
        ('shirt', 'type'), ('jacket', 'type'), ('pants', 'type'), ('skirt', 'type'),
        ('dress', 'type'), ('shorts', 'type'), ('blouse', 'type'), ('coat', 'type'),
        ('sweater', 'type'), ('t-shirt', 'type'), ('jeans', 'type'), ('suit', 'type'),
        ('blazer', 'type'), ('scarf', 'type'), ('hat', 'type'), ('shoes', 'type'),
        ('boots', 'type'), ('sandals', 'type'), ('sneakers', 'type'), ('belt', 'type'),
        ('gloves', 'type'), ('jewelry', 'type'), ('glasses', 'type'),

        # Color
        ('red', 'color'), ('blue', 'color'), ('black', 'color'), ('white', 'color'),
        ('gray', 'color'), ('green', 'color'), ('yellow', 'color'), ('orange', 'color'),
        ('purple', 'color'), ('pink', 'color'), ('brown', 'color'), ('beige', 'color'),
        ('navy', 'color'), ('teal', 'color'), ('maroon', 'color'), ('olive', 'color'),
        ('gold', 'color'), ('silver', 'color'),

        # Style
        ('casual', 'style'), ('formal', 'style'), ('sporty', 'style'), ('business', 'style'),
        ('streetwear', 'style'), ('vintage', 'style'), ('bohemian', 'style'), ('chic', 'style'),
        ('preppy', 'style'), ('edgy', 'style'), ('classic', 'style'), ('minimalistic', 'style'),
        ('elegant', 'style'), ('punk', 'style'), ('hip-hop', 'style'), ('athleisure', 'style'),

        # Season
        ('summer', 'season'), ('winter', 'season'), ('spring', 'season'), ('fall', 'season'),
        ('all-season', 'season'),

        # Occasion
        ('work', 'occasion'), ('party', 'occasion'), ('outdoor', 'occasion'), ('travel', 'occasion'),
        ('casual', 'occasion'), ('formal', 'occasion'), ('date', 'occasion'), ('gym', 'occasion'),
        ('beach', 'occasion'), ('festival', 'occasion'), ('wedding', 'occasion'), ('holiday', 'occasion'),
    ]

    with app.app_context():
        for name, category in tags:
            # Check if the tag already exists
            existing_tag = Tag.query.filter_by(name=name).first()
            if not existing_tag:
                tag = Tag(name=name, category=category)
                db.session.add(tag)
        db.session.commit()
        print("Tags populated successfully!")

if __name__ == '__main__':
    populate_tags()