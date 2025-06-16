from flask import request, jsonify, session, send_from_directory
from db.models import User, db
import re
from flask import send_from_directory, request, jsonify
from services.services import resize_image, tag_image, parse_tags
from db.models import WardrobeItem, Tag, WardrobeItemTag, db
import os
from rembg import remove
from PIL import Image
import base64
import io
from datetime import datetime
from services.collage_service import analyze_prompt_for_tags, select_items_for_collage, create_collage, save_collage, generate_outfit_from_collage
from .auth_routes import require_login, get_current_user_id

def setup_routes(app):
    @app.route('/')
    def serve_index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/index.html')
    def serve_index_html():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/wardrobe.html')
    def serve_wardrobe_html():
        return send_from_directory('../frontend', 'wardrobe.html')

    @app.route('/upload-clothing', methods=['POST'])
    def upload_clothing():
        # Check authentication
        auth_error = require_login()
        if auth_error:
            return auth_error
            
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image uploaded'}), 400

            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Save the uploaded image temporarily
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            print(f"Image saved temporarily at {temp_path}")

            # Remove background using rembg
            with open(temp_path, 'rb') as input_file:
                input_image = input_file.read()
            output_image = remove(input_image)
            print("Background removed successfully")

            # Save the cleaned-up image
            cleaned_path = os.path.join(app.config['UPLOAD_FOLDER'], f"cleaned_{filename}")
            with open(cleaned_path, 'wb') as output_file:
                output_file.write(output_image)
            print(f"Cleaned image saved at {cleaned_path}")

            # Resize and standardize the image
            resized_path = resize_image(cleaned_path)
            print(f"Image resized and saved at {resized_path}")

            # Send the image to GPT-4o for tagging
            with open(resized_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')

            # Predefined prompt for tagging
            prompt = """Tag the clothing item in this image using the following values and return them as
              JSON: one "type" and one "type_category", one "color", multiple "style", "season", and "occasion" 
              if relevant; allowed values are — type: shirt, jacket, pants, skirt, dress, shorts, blouse, coat,
                sweater, t-shirt, jeans, suit, blazer, scarf, hat, shoes, boots, sandals, sneakers, belt, gloves;
                  type_category: top, bottom, footwear, accessory, outerwear, headwear; color: red, blue, black,
                    white, gray, green, yellow, orange, purple, pink, brown, beige, navy, teal, maroon, olive,
                      gold, silver; style: casual, formal, sporty, business, streetwear, vintage, bohemian,
                        chic, preppy, edgy, classic, minimalistic, elegant, punk, hip-hop, athleisure; season: 
                        summer, winter, spring, fall, all-season; occasion: work, party, outdoor, travel,
                          casual, formal, date, gym, beach, festival, wedding, holiday; output JSON format:
                            {"type": "", "type_category": "", "color": "", "style": [], "season": [], "occasion":
                              []}."""

            tags_response = tag_image(img_data, prompt)
            print("Tags received from GPT-4o:", tags_response)

            # Parse the tags
            tags = parse_tags(tags_response)

            # Save the item and tags to the database with current user ID
            current_user_id = get_current_user_id()
            wardrobe_item = WardrobeItem(
                user_id=current_user_id,  # Use actual logged-in user ID
                image_url=f"/uploads/{os.path.basename(resized_path)}",
                type_category=tags.get('type_category', 'unknown'),
                timestamp=datetime.utcnow()
            )
            db.session.add(wardrobe_item)
            db.session.commit()

            # Add tags to the many-to-many relationship
            all_tags = []
            
            # Add type and color as single tags
            if tags.get('type'):
                all_tags.append(('type', tags['type']))
            if tags.get('color'):
                all_tags.append(('color', tags['color']))
            
            # Add style, season, and occasion as lists
            for style_tag in tags.get('style', []):
                all_tags.append(('style', style_tag))
            for season_tag in tags.get('season', []):
                all_tags.append(('season', season_tag))
            for occasion_tag in tags.get('occasion', []):
                all_tags.append(('occasion', occasion_tag))
            
            # Save all tags
            for category, tag_name in all_tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    # Create the tag if it doesn't exist
                    tag = Tag(name=tag_name, category=category)
                    db.session.add(tag)
                    db.session.commit()
                
                # Add to wardrobe item if not already added
                if tag not in wardrobe_item.tags:
                    wardrobe_item.tags.append(tag)
            
            db.session.commit()

            return jsonify({'message': 'Clothing item uploaded successfully!'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/wardrobe-items', methods=['GET'])
    def get_wardrobe_items():
        # Check authentication
        auth_error = require_login()
        if auth_error:
            return auth_error
            
        try:
            # Filter wardrobe items by current user only
            current_user_id = get_current_user_id()
            wardrobe_items = WardrobeItem.query.filter_by(user_id=current_user_id).all()
            
            items = []
            for item in wardrobe_items:
                items.append({
                    'id': item.id,
                    'image_url': item.image_url,
                    'type_category': item.type_category,
                    'tags': [tag.name for tag in item.tags]
                })
            return jsonify(items), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/uploads/<filename>')
    def serve_uploaded_file(filename):
        """Serve uploaded images"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/cleanup-unknown', methods=['DELETE'])
    def cleanup_unknown_items():
        """Remove wardrobe items that have unknown type_category or unknown tags for current user only"""
        # Check authentication
        auth_error = require_login()
        if auth_error:
            return auth_error
            
        try:
            current_user_id = get_current_user_id()
            
            # Find items with unknown type_category for current user
            unknown_items = WardrobeItem.query.filter_by(
                user_id=current_user_id, 
                type_category='unknown'
            ).all()
            
            # Also find items that only have 'unknown' tags for current user
            all_items = WardrobeItem.query.filter_by(user_id=current_user_id).all()
            items_to_delete = []
            
            for item in all_items:
                # Check if item has unknown type_category
                if item.type_category == 'unknown':
                    items_to_delete.append(item)
                    continue
                    
                # Check if item only has unknown tags
                if item.tags:
                    all_unknown = all(tag.name == 'unknown' for tag in item.tags)
                    if all_unknown:
                        items_to_delete.append(item)
                else:
                    # Item has no tags at all, consider it unknown
                    items_to_delete.append(item)
            
            # Remove duplicates
            items_to_delete = list(set(items_to_delete))
            
            deleted_count = len(items_to_delete)
            
            # Delete the items
            for item in items_to_delete:
                # Clear the many-to-many relationships first
                item.tags.clear()
                db.session.delete(item)
            
            db.session.commit()
            
            return jsonify({
                'message': f'Successfully removed {deleted_count} unknown items',
                'deleted_count': deleted_count
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/analyze-prompt', methods=['POST'])
    def analyze_outfit_prompt():
        """Analyze user prompt and return suggested tags"""
        # Check authentication
        auth_error = require_login()
        if auth_error:
            return auth_error
            
        try:
            data = request.get_json()
            user_prompt = data.get('prompt', '')
            
            if not user_prompt:
                return jsonify({'error': 'No prompt provided'}), 400
            
            # Get suggested tags from GPT-4o
            suggested_tags = analyze_prompt_for_tags(user_prompt)
            
            return jsonify({
                'suggested_tags': suggested_tags,
                'prompt': user_prompt
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/generate-complete-outfit', methods=['POST'])
    def generate_complete_outfit():
        """Generate both collage and final outfit in one step for current user only"""
        # Check authentication
        auth_error = require_login()
        if auth_error:
            return auth_error
            
        try:
            data = request.get_json()
            user_prompt = data.get('prompt', '')
            
            if not user_prompt:
                return jsonify({'error': 'No prompt provided'}), 400
            
            print(f"Generating complete outfit for prompt: {user_prompt}")
            
            # Step 1: Analyze prompt to get target tags
            target_tags = analyze_prompt_for_tags(user_prompt)
            print(f"Target tags: {target_tags}")
            
            # Step 2: Select items from current user's wardrobe only
            current_user_id = get_current_user_id()
            selected_items = select_items_for_collage(target_tags, current_user_id)
            print(f"Selected items: {[(k, len(v)) for k, v in selected_items.items()]}")
            
            if not selected_items or sum(len(items) for items in selected_items.values()) == 0:
                return jsonify({'error': 'No matching items found in your wardrobe for this prompt'}), 404
            
            # Step 3: Create collage image
            collage_image = create_collage(selected_items)
            
            # Step 4: Save collage
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            collage_filename = f"collage_{timestamp}.png"
            collage_path = save_collage(collage_image, collage_filename)
            print(f"Collage saved: {collage_path}")
            
            # Step 5: Generate outfit image from collage using DALL-E
            print("Generating outfit image with DALL-E...")
            outfit_image_url = generate_outfit_from_collage(collage_path, user_prompt)
            print(f"Outfit generated: {outfit_image_url}")
            
            # Step 6: Prepare response with selected items details
            items_details = {}
            for category, items in selected_items.items():
                items_details[category] = []
                for item in items:
                    items_details[category].append({
                        'id': item.id,
                        'image_url': item.image_url,
                        'type_category': item.type_category,
                        'tags': [tag.name for tag in item.tags]
                    })
            
            return jsonify({
                'collage_url': f"/uploads/{collage_filename}",
                'outfit_image_url': outfit_image_url,
                'target_tags': target_tags,
                'selected_items': items_details,
                'message': f'Complete outfit generated with {sum(len(items) for items in selected_items.values())} items'
            }), 200
            
        except Exception as e:
            print(f"Error generating complete outfit: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Keep the original generate-collage route for backward compatibility
    @app.route('/generate-collage', methods=['POST'])
    def generate_outfit_collage():
        """Generate collage only (legacy route) for current user only"""
        # Check authentication
        auth_error = require_login()
        if auth_error:
            return auth_error
            
        try:
            data = request.get_json()
            user_prompt = data.get('prompt', '')
            
            if not user_prompt:
                return jsonify({'error': 'No prompt provided'}), 400
            
            print(f"Generating collage for prompt: {user_prompt}")
            
            # Step 1: Analyze prompt to get target tags
            target_tags = analyze_prompt_for_tags(user_prompt)
            print(f"Target tags: {target_tags}")
            
            # Step 2: Select items from current user's wardrobe only
            current_user_id = get_current_user_id()
            selected_items = select_items_for_collage(target_tags, current_user_id)
            print(f"Selected items: {[(k, len(v)) for k, v in selected_items.items()]}")
            
            # Step 3: Create collage image
            collage_image = create_collage(selected_items)
            
            # Step 4: Save collage
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            collage_filename = f"collage_{timestamp}.png"
            collage_path = save_collage(collage_image, collage_filename)
            
            # Step 5: Return collage info and selected items details
            items_details = {}
            for category, items in selected_items.items():
                items_details[category] = []
                for item in items:
                    items_details[category].append({
                        'id': item.id,
                        'image_url': item.image_url,
                        'type_category': item.type_category,
                        'tags': [tag.name for tag in item.tags]
                    })
            
            return jsonify({
                'collage_url': f"/uploads/{collage_filename}",
                'target_tags': target_tags,
                'selected_items': items_details,
                'message': f'Collage generated with {sum(len(items) for items in selected_items.values())} items'
            }), 200
            
        except Exception as e:
            print(f"Error generating collage: {e}")
            return jsonify({'error': str(e)}), 500