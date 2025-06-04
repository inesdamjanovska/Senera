from flask import send_from_directory, request, jsonify
from services.services import generate_outfit, resize_image, tag_image, parse_tags
from db.models import WardrobeItem, Tag, WardrobeItemTag, db
import os
from rembg import remove
from PIL import Image
import base64
import io
from datetime import datetime

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

    @app.route('/generate-outfit', methods=['POST'])
    def generate_outfit_route():
        return generate_outfit()

    @app.route('/upload-clothing', methods=['POST'])
    def upload_clothing():
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

            # Save the item and tags to the database
            wardrobe_item = WardrobeItem(
                user_id=1,  # Default user ID for now
                image_url=f"/uploads/{os.path.basename(resized_path)}",
                type_category=tags.get('type', 'unknown'),
                timestamp=datetime.utcnow()
            )
            db.session.add(wardrobe_item)
            db.session.commit()

            # Add tags to the many-to-many relationship
            for tag_name in tags.get('tags', []):
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    wardrobe_item.tags.append(tag)
            db.session.commit()

            return jsonify({'message': 'Clothing item uploaded successfully!'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/wardrobe-items', methods=['GET'])
    def get_wardrobe_items():
        try:
            wardrobe_items = WardrobeItem.query.all()
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