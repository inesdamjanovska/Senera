from db import db  # Updated import
from datetime import datetime

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=True)  # Optional for now
    wardrobe_items = db.relationship('WardrobeItem', backref='user', lazy=True)

# WardrobeItem model
class WardrobeItem(db.Model):
    __tablename__ = 'wardrobe_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    type_category = db.Column(db.String(50), nullable=False)  # e.g., tops, bottoms
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship('Tag', secondary='wardrobe_item_tags', backref='wardrobe_items')

# Tag model
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., color, style

# Many-to-Many relationship table
class WardrobeItemTag(db.Model):
    __tablename__ = 'wardrobe_item_tags'
    wardrobe_item_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)