from db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)  # Used as username
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    wardrobe_items = db.relationship('WardrobeItem', backref='user', lazy=True, cascade='all, delete-orphan')
    saved_outfits = db.relationship('SavedOutfit', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (exclude password)"""
        return {
            'id': self.id,
            'display_name': self.display_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

# WardrobeItem model (no changes needed - relationship already exists)
class WardrobeItem(db.Model):
    __tablename__ = 'wardrobe_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    type_category = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship('Tag', secondary='wardrobe_item_tags', backref='wardrobe_items')
    
    def to_dict(self):
        """Convert wardrobe item to dictionary"""
        return {
            'id': self.id,
            'image_url': self.image_url,
            'type_category': self.type_category,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'tags': [tag.name for tag in self.tags]
        }

# Tag model (no changes needed)
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)

# Many-to-Many relationship table (no changes needed)
class WardrobeItemTag(db.Model):
    __tablename__ = 'wardrobe_item_tags'
    wardrobe_item_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

# SavedOutfit model for storing user's saved outfits
class SavedOutfit(db.Model):
    __tablename__ = 'saved_outfits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)  # Path to the saved collage image
    prompt = db.Column(db.Text, nullable=True)  # Store the original prompt used to generate the outfit
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert saved outfit to dictionary"""
        # Format image_url correctly depending on whether it's an external URL or local file
        image_url = self.image_url
        if not image_url.startswith('http'):
            # It's a local file, prepend /uploads/ path
            image_url = f"/uploads/{image_url}"
            
        return {
            'id': self.id,
            'name': self.name,
            'image_url': image_url,
            'prompt': self.prompt,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }