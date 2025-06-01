import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()

# Populate type categories
type_categories = ['tops', 'bottoms', 'footwear', 'jewelry', 'accessories']
cursor.executemany("INSERT INTO type_categories (name) VALUES (%s)", [(tc,) for tc in type_categories])

# Populate tags
tags = [
    # Type tags
    ('shirt', 'type', 1), ('jacket', 'type', 1), ('pants', 'type', 2), ('skirt', 'type', 2),
    ('dress', 'type', 2), ('shorts', 'type', 2), ('blouse', 'type', 1), ('coat', 'type', 1),
    ('sweater', 'type', 1), ('t-shirt', 'type', 1), ('jeans', 'type', 2), ('suit', 'type', 2),
    ('blazer', 'type', 1), ('scarf', 'type', 5), ('hat', 'type', 5), ('shoes', 'type', 3),
    ('boots', 'type', 3), ('sandals', 'type', 3), ('sneakers', 'type', 3), ('belt', 'type', 5),
    ('gloves', 'type', 5), ('jewelry', 'type', 4), ('glasses', 'type', 4),

    # Color tags
    ('red', 'color', None), ('blue', 'color', None), ('black', 'color', None), ('white', 'color', None),
    ('gray', 'color', None), ('green', 'color', None), ('yellow', 'color', None), ('orange', 'color', None),
    ('purple', 'color', None), ('pink', 'color', None), ('brown', 'color', None), ('beige', 'color', None),
    ('navy', 'color', None), ('teal', 'color', None), ('maroon', 'color', None), ('olive', 'color', None),
    ('gold', 'color', None), ('silver', 'color', None),

    # Style tags
    ('casual', 'style', None), ('formal', 'style', None), ('sporty', 'style', None), ('business', 'style', None),
    ('streetwear', 'style', None), ('vintage', 'style', None), ('bohemian', 'style', None), ('chic', 'style', None),
    ('preppy', 'style', None), ('edgy', 'style', None), ('classic', 'style', None), ('minimalistic', 'style', None),
    ('elegant', 'style', None), ('punk', 'style', None), ('hip-hop', 'style', None), ('athleisure', 'style', None),

    # Season tags
    ('summer', 'season', None), ('winter', 'season', None), ('spring', 'season', None), ('fall', 'season', None),
    ('all-season', 'season', None),

    # Occasion tags
    ('work', 'occasion', None), ('party', 'occasion', None), ('outdoor', 'occasion', None), ('travel', 'occasion', None),
    ('casual', 'occasion', None), ('formal', 'occasion', None), ('date', 'occasion', None), ('gym', 'occasion', None),
    ('beach', 'occasion', None), ('festival', 'occasion', None), ('wedding', 'occasion', None), ('holiday', 'occasion', None)
]
cursor.executemany("INSERT INTO tags (name, category, type_category_id) VALUES (%s, %s, %s)", tags)

db.commit()
cursor.close()
db.close()