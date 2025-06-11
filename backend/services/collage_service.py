import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from db.models import WardrobeItem, Tag, db
from services.services import tag_image
from collections import defaultdict

def analyze_prompt_for_tags(user_prompt):
    """Send user prompt to GPT-4o to extract relevant tags for outfit selection"""
    api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    system_prompt = """You are a fashion stylist AI. Analyze the user's outfit request and return relevant clothing tags that would fit their needs. 

Return a JSON object with these categories:
- "type_categories": array of clothing types needed (e.g., ["top", "bottom", "footwear"])
- "styles": array of style preferences (e.g., ["casual", "streetwear"])
- "colors": array of preferred colors (e.g., ["blue", "black"])
- "occasions": array of occasions (e.g., ["casual", "outdoor"])
- "seasons": array of seasons (e.g., ["spring", "summer"])

Available values:
- type_categories: top, bottom, footwear, accessory, outerwear, headwear
- styles: casual, formal, sporty, business, streetwear, vintage, bohemian, chic, preppy, edgy, classic, minimalistic, elegant, punk, hip-hop, athleisure
- colors: red, blue, black, white, gray, green, yellow, orange, purple, pink, brown, beige, navy, teal, maroon, olive, gold, silver
- occasions: work, party, outdoor, travel, casual, formal, date, gym, beach, festival, wedding, holiday
- seasons: summer, winter, spring, fall, all-season

Example:
User: "casual coffee outfit"
Response: {"type_categories": ["top", "bottom", "footwear"], "styles": ["casual", "classic"], "colors": [], "occasions": ["casual"], "seasons": []}"""

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 200
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        response_data = response.json()
        tags_content = response_data['choices'][0]['message']['content']
        
        # Parse JSON response
        try:
            # Clean markdown formatting if present
            if tags_content.startswith('```json'):
                tags_content = tags_content[7:-3]
            elif tags_content.startswith('```'):
                tags_content = tags_content[3:-3]
            
            tags_data = json.loads(tags_content.strip())
            return tags_data
        except json.JSONDecodeError:
            print(f"Failed to parse GPT-4o response: {tags_content}")
            return {
                "type_categories": ["top", "bottom", "footwear"],
                "styles": ["casual"],
                "colors": [],
                "occasions": ["casual"],
                "seasons": []
            }
    else:
        raise Exception(f"GPT-4o error: {response.text}")

def score_item_relevance(item, target_tags):
    """Score how well an item matches the target tags"""
    score = 0
    item_tag_names = [tag.name for tag in item.tags]
    
    # Score based on matching tags
    for category, tag_list in target_tags.items():
        if category == 'type_categories':
            if item.type_category in tag_list:
                score += 10  # High priority for matching type category
        else:
            for tag in tag_list:
                if tag in item_tag_names:
                    score += 5  # Points for matching other tags
    
    return score

def select_items_for_collage(target_tags, max_per_category=3):
    """Select wardrobe items based on target tags"""
    # Get items by type category
    items_by_category = defaultdict(list)
    
    # Query all wardrobe items
    all_items = WardrobeItem.query.all()
    
    for item in all_items:
        items_by_category[item.type_category].append(item)
    
    selected_items = {}
    
    # For each requested type category, select best matching items
    for type_category in target_tags.get('type_categories', []):
        available_items = items_by_category.get(type_category, [])
        
        if available_items:
            # Score and sort items by relevance
            scored_items = []
            for item in available_items:
                score = score_item_relevance(item, target_tags)
                scored_items.append((score, item))
            
            # Sort by score (highest first) and take top items
            scored_items.sort(key=lambda x: x[0], reverse=True)
            selected_count = min(max_per_category, len(scored_items))
            selected_items[type_category] = [item for _, item in scored_items[:selected_count]]
    
    return selected_items

def create_collage(selected_items, collage_size=(1024, 768)):
    """Create an optimized collage image for GPT-4o analysis"""
    # Create blank canvas with white background
    collage = Image.new('RGB', collage_size, 'white')
    draw = ImageDraw.Draw(collage)
    
    # Load fonts - much smaller for minimal text
    try:
        # Very small fonts for minimal text interference
        category_font = ImageFont.truetype("arial.ttf", 14)  # Category labels
        tag_font = ImageFont.truetype("arial.ttf", 10)       # Item tags
    except:
        category_font = ImageFont.load_default()
        tag_font = ImageFont.load_default()
    
    # Calculate layout
    categories = list(selected_items.keys())
    if not categories:
        # No items selected, create empty collage with message
        draw.text((collage_size[0]//2 - 100, collage_size[1]//2), 
                 "No matching items found", fill='black', font=category_font)
        return collage
    
    # Optimized layout parameters for maximum image space
    margin = 15
    category_label_height = 20  # Reduced from 40
    tag_height = 12             # Minimal space for tags
    spacing = 8                 # Space between items
    
    # Calculate available space
    total_height = collage_size[1] - (margin * 2)
    category_height = total_height // len(categories)
    
    y_offset = margin
    
    for category in categories:
        items = selected_items[category]
        if not items:
            continue
        
        # Draw minimal category label
        draw.text((margin, y_offset), f"{category.upper()}:", 
                 fill='black', font=category_font)
        
        # Calculate dimensions - maximize image space
        available_width = collage_size[0] - (margin * 2)
        available_height = category_height - category_label_height - tag_height - spacing
        
        # Determine layout: prefer horizontal arrangement
        num_items = min(len(items), 3)
        if num_items == 1:
            item_width = available_width
            item_height = available_height
        elif num_items == 2:
            item_width = (available_width - spacing) // 2
            item_height = available_height
        else:  # 3 items
            item_width = (available_width - (spacing * 2)) // 3
            item_height = available_height
        
        x_offset = margin
        
        for i, item in enumerate(items[:3]):
            try:
                # Load and process item image
                item_path = os.path.join('uploads', os.path.basename(item.image_url))
                if os.path.exists(item_path):
                    item_img = Image.open(item_path)
                    
                    # Resize to fit space while maintaining aspect ratio
                    # Leave small margin for text
                    max_img_width = item_width - 4
                    max_img_height = item_height - 4
                    
                    # Calculate scaling
                    width_ratio = max_img_width / item_img.width
                    height_ratio = max_img_height / item_img.height
                    scale_ratio = min(width_ratio, height_ratio)
                    
                    # Resize image
                    new_width = int(item_img.width * scale_ratio)
                    new_height = int(item_img.height * scale_ratio)
                    item_img = item_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Center the image in its allocated space
                    img_x = x_offset + (item_width - new_width) // 2
                    img_y = y_offset + category_label_height + (item_height - new_height) // 2
                    
                    # Paste the image
                    if item_img.mode == 'RGBA':
                        collage.paste(item_img, (img_x, img_y), item_img)
                    else:
                        collage.paste(item_img, (img_x, img_y))
                    
                    # Add minimal tags at bottom (very small and unobtrusive)
                    tags_text = ','.join([tag.name for tag in item.tags[:2]])  # Max 2 tags
                    if len(tags_text) > 15:
                        tags_text = tags_text[:12] + "..."
                    
                    # Position tags at very bottom in small text
                    text_x = x_offset + 2
                    text_y = y_offset + category_height - tag_height - 2
                    draw.text((text_x, text_y), tags_text, fill='gray', font=tag_font)
                
                else:
                    # Draw placeholder if image not found
                    placeholder_color = '#f0f0f0'
                    draw.rectangle([x_offset + 2, y_offset + category_label_height + 2, 
                                  x_offset + item_width - 2, 
                                  y_offset + category_label_height + item_height - 2], 
                                  fill=placeholder_color, outline='#ddd')
                    
                    # Center "No Image" text
                    text_x = x_offset + item_width // 2 - 25
                    text_y = y_offset + category_label_height + item_height // 2
                    draw.text((text_x, text_y), "No Image", fill='gray', font=tag_font)
                
            except Exception as e:
                print(f"Error processing item {item.id}: {e}")
                # Draw error placeholder
                draw.rectangle([x_offset + 2, y_offset + category_label_height + 2, 
                              x_offset + item_width - 2, 
                              y_offset + category_label_height + item_height - 2], 
                              fill='#ffe0e0', outline='#ff9999')
                draw.text((x_offset + 5, y_offset + category_label_height + 5), 
                         "Error", fill='red', font=tag_font)
            
            x_offset += item_width + spacing
        
        y_offset += category_height
    
    return collage

def save_collage(collage_image, filename="collage.png"):
    """Save collage image to uploads folder with optimized settings"""
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, filename)
    
    # Save with optimal settings for GPT-4o
    collage_image.save(filepath, 'PNG', optimize=True, compress_level=6)
    return filepath