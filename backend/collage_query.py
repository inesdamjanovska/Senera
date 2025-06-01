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

cursor = db.cursor(dictionary=True)

# Query for collage generation
def get_collage_items(tags, limit_per_type=3):
    query = """
    SELECT wi.id, wi.image_url, t.name AS tag_name, tc.name AS type_category
    FROM wardrobe_items wi
    JOIN wardrobe_item_tags wit ON wi.id = wit.wardrobe_item_id
    JOIN tags t ON wit.tag_id = t.id
    LEFT JOIN type_categories tc ON t.type_category_id = tc.id
    WHERE t.name IN (%s)
    GROUP BY tc.name, wi.id
    LIMIT %s;
    """
    cursor.execute(query, (", ".join(tags), limit_per_type))
    return cursor.fetchall()

# Example usage
tags = ['casual', 'summer', 'party']
items = get_collage_items(tags)
for item in items:
    print(item)

cursor.close()
db.close()