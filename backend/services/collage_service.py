import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from db.models import WardrobeItem, Tag, db
from services.services import tag_image
from collections import defaultdict
import base64

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

def select_items_for_collage(target_tags, user_id, max_per_category=5):
    """Select wardrobe items based on target tags for specific user only"""
    # Get items by type category for the specific user
    items_by_category = defaultdict(list)
    
    # Query wardrobe items for the specific user only
    all_items = WardrobeItem.query.filter_by(user_id=user_id).all()
    
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
        
        # Determine layout: arrange items in rows if needed
        num_items = min(len(items), 5)
        if num_items <= 3:
            # Single row layout for 1-3 items
            if num_items == 1:
                item_width = available_width
                item_height = available_height
                items_per_row = 1
            elif num_items == 2:
                item_width = (available_width - spacing) // 2
                item_height = available_height
                items_per_row = 2
            else:  # 3 items
                item_width = (available_width - (spacing * 2)) // 3
                item_height = available_height
                items_per_row = 3
        else:
            # Two row layout for 4-5 items
            items_per_row = 3 if num_items == 4 else 3  # First row: 3 items, second row: 1-2 items
            item_width = (available_width - (spacing * 2)) // 3
            item_height = (available_height - spacing) // 2
        
        x_offset = margin
        
        for i, item in enumerate(items[:5]):
            try:
                # Calculate position for multi-row layout
                col_offset = 0
                if num_items <= 3:
                    # Single row
                    row = 0
                    col = i
                    current_x = margin + col * (item_width + spacing)
                    current_y = y_offset + category_label_height + row * (item_height + spacing)
                else:
                    # Two rows: first 3 items in first row, remaining in second row
                    if i < 3:
                        row = 0
                        col = i
                        current_x = margin + col * (item_width + spacing)
                    else:
                        row = 1
                        col = i - 3
                        # Center items in second row if less than 3
                        if num_items == 4:  # Only 1 item in second row
                            col_offset = item_width + spacing  # Center it
                        elif num_items == 5 and col < 2:  # 2 items in second row
                            col_offset = (item_width + spacing) // 2  # Slight offset
                        
                        current_x = margin + col * (item_width + spacing) + col_offset
                    
                    current_y = y_offset + category_label_height + row * (item_height + spacing)
                
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
                    img_x = current_x + (item_width - new_width) // 2
                    img_y = current_y + (item_height - new_height) // 2
                    
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
                    text_x = current_x + 2
                    text_y = current_y + item_height - 12
                    draw.text((text_x, text_y), tags_text, fill='gray', font=tag_font)
                
                else:
                    # Draw placeholder if image not found
                    placeholder_color = '#f0f0f0'
                    draw.rectangle([current_x + 2, current_y + 2, 
                                  current_x + item_width - 2, 
                                  current_y + item_height - 2], 
                                  fill=placeholder_color, outline='#ddd')
                    
                    # Center "No Image" text
                    text_x = current_x + item_width // 2 - 25
                    text_y = current_y + item_height // 2
                    draw.text((text_x, text_y), "No Image", fill='gray', font=tag_font)
                
            except Exception as e:
                print(f"Error processing item {item.id}: {e}")
                # Calculate position for error placeholder (simplified)
                if num_items <= 3:
                    current_x = margin + i * (item_width + spacing)
                    current_y = y_offset + category_label_height
                else:
                    if i < 3:
                        current_x = margin + i * (item_width + spacing)
                        current_y = y_offset + category_label_height
                    else:
                        col = i - 3
                        col_offset = (item_width + spacing) // 2 if num_items == 4 else 0
                        current_x = margin + col * (item_width + spacing) + col_offset
                        current_y = y_offset + category_label_height + item_height + spacing
                
                # Draw error placeholder
                draw.rectangle([current_x + 2, current_y + 2, 
                              current_x + item_width - 2, 
                              current_y + item_height - 2], 
                              fill='#ffe0e0', outline='#ff9999')
                draw.text((current_x + 5, current_y + 5), 
                         "Error", fill='red', font=tag_font)
        
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

def generate_outfit_from_collage(collage_path, user_prompt, image_service="dalle"):
    """Send collage image to AI service to generate outfit photo
    
    Args:
        collage_path: Path to the collage image
        user_prompt: User's outfit request
        image_service: Which service to use ("dalle", "pollinations", "huggingface", "replicate")
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Encode image to base64
    with open(collage_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Enhanced GPT-4o analysis to SELECT the best matching items
    analyze_payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are a professional fashion stylist. Analyze this clothing collage and SELECT the best combination of items that would create a stylish, cohesive outfit for: "{user_prompt}"

FROM ALL THE ITEMS SHOWN (up to 5 items per category), choose only 3-6 pieces that work best together and would create the most fashionable outfit. You now have more variety to choose from in each category.

For your SELECTED items only, provide extremely detailed descriptions:

1. EXACT CLOTHING TYPES: Identify each selected piece precisely (e.g., "crew neck cotton t-shirt", "high-waisted straight-leg jeans", "white canvas sneakers")

2. COLORS & PATTERNS: Describe exact colors, patterns (even the amount of stripes for example), textures (e.g., "navy blue", "faded light blue denim", "solid white")

3. STYLE DETAILS: Note specific design elements (e.g., "button-front", "rolled cuffs", "minimalist design")

4. FIT & SILHOUETTE: How items should fit together (e.g., "fitted top with relaxed jeans", "oversized sweater tucked into high-waisted pants")

5. WHY THESE WORK TOGETHER: Briefly explain why this combination creates a cohesive look and how they will be styled together.

Focus on creating ONE perfect outfit that matches the "{user_prompt}" style. With more options available, select the best matching items and ignore those that don't fit well with your selection."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 450
    }
    
    # Get detailed clothing description from GPT-4o
    analyze_response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=analyze_payload
    )
    
    if analyze_response.status_code != 200:
        raise Exception(f"GPT-4o analysis error: {analyze_response.text}")
    
    clothing_description = analyze_response.json()['choices'][0]['message']['content']
    print(f"Selected outfit description: {clothing_description}")
    
    # Choose image generation service
    if image_service.lower() == "pollinations":
        print("Using Pollinations.ai for image generation...")
        return generate_outfit_with_pollinations(clothing_description, user_prompt)
    
    elif image_service.lower() == "huggingface":
        print("Using Hugging Face for image generation...")
        result = generate_outfit_with_huggingface(clothing_description, user_prompt)
        if result:
            return result
        else:
            print("Hugging Face failed, falling back to DALL-E...")
    
    elif image_service.lower() == "replicate":
        print("Using Replicate for image generation...")
        result = generate_outfit_with_replicate(clothing_description, user_prompt)
        if result:
            return result
        else:
            print("Replicate failed, falling back to DALL-E...")
    
    # Default to DALL-E or fallback
    print("Using DALL-E 3 for image generation...")
    
    # Updated DALL-E prompt with enhanced styling instructions
    dalle_prompt = f"""Full-body photo of a single female fashion model **wearing the following outfit**: {clothing_description}

Instructions:
- The model must be **wearing all the described clothing and accessories**
- Model is standing in a neutral pose, front-facing
- Pure white studio background, catalog photography style
- No collage layout, no flat-lay images, no side-by-side items
- No multiple angles, no floating clothes, no split panels
- Focus on realism and professional fashion photography
- Emphasize styling with jewelry and formal elegance for a high-end restaurant setting

Style theme: {user_prompt}
"""
    
    print(f"DALL-E prompt: {dalle_prompt}")
    
    # Generate outfit image with DALL-E 3
    dalle_payload = {
        "model": "dall-e-3",
        "prompt": dalle_prompt,
        "size": "1024x1024",
        "quality": "hd",
        "style": "natural",
        "n": 1
    }
    
    dalle_response = requests.post(
        'https://api.openai.com/v1/images/generations',
        headers=headers,
        json=dalle_payload
    )
    
    if dalle_response.status_code == 200:
        result = dalle_response.json()
        outfit_image_url = result['data'][0]['url']
        return outfit_image_url
    else:
        raise Exception(f"DALL-E error: {dalle_response.text}")

def generate_outfit_with_pollinations(clothing_description, user_prompt):
    """Generate outfit using Pollinations.ai (free, no API key needed)"""
    # Enhanced prompt for Pollinations with dress handling
    prompt = f"""Fashion catalog photo: single female model wearing {clothing_description}, {user_prompt} style.

Instructions:
- Head-to-toe full body view, standing pose
- White background, professional e-commerce photography
- If outfit includes a full-length dress or maxi dress, do NOT add separate bottoms (pants/skirts)
- Dresses are complete garments worn alone, not with additional bottoms
- Show complete outfit from head to feet including footwear
- One person only, no duplicates, no collages
- Realistic fashion photography style"""
    
    # URL encode the prompt
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Pollinations.ai API endpoint
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&enhance=true"
    
    return pollinations_url

def generate_outfit_with_huggingface(clothing_description, user_prompt):
    """Generate outfit using Hugging Face Stable Diffusion (free tier)"""
    try:
        import requests
        import io
        from datetime import datetime
        
        # Get Hugging Face API key from environment
        hf_token = os.getenv('HUGGINGFACE_API_KEY')
        if not hf_token:
            print("Hugging Face API key not found in environment variables")
            return None
        
        # Hugging Face API endpoint for Stable Diffusion
        HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        
        # Enhanced prompt for Hugging Face with dress handling
        prompt = f"""Fashion catalog photo: single female model wearing {clothing_description}, {user_prompt} style.

Instructions:
- Head-to-toe full body view, standing pose
- White background, professional e-commerce photography
- If outfit includes a full-length dress or maxi dress, do NOT add separate bottoms
- Show complete outfit from head to feet including footwear
- One person only, no duplicates, realistic fashion photography"""
        
        negative_prompt = "multiple people, busy background, shadows, blurry, low quality, cropped, duplicates, side-by-side, collage, floating clothes"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 8.0,
                "width": 1024,
                "height": 1024
            }
        }
        
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        print(f"Hugging Face prompt: {prompt}")
        
        # Make API request
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            # Save the generated image
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"hf_outfit_{timestamp}.png"
            filepath = os.path.join('uploads', filename)
            
            # Ensure uploads directory exists
            os.makedirs('uploads', exist_ok=True)
            
            # Save the image data
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Return the full URL that the frontend can access
            from config import Config
            base_url = f"http://{os.getenv('API_HOST', '192.168.100.14')}:{os.getenv('API_PORT', '5000')}"
            return f"{base_url}/uploads/{filename}"
            
        elif response.status_code == 503:
            print("Hugging Face model is loading, please try again in a few moments")
            return None
        else:
            print(f"Hugging Face API error {response.status_code}: {response.text}")
            return None
        
    except Exception as e:
        print(f"Hugging Face generation error: {e}")
        return None

def generate_outfit_with_replicate(clothing_description, user_prompt):
    """Generate outfit using Replicate (free tier available)"""
    try:
        # This would require the replicate Python package and API key
        # pip install replicate
        # import replicate
        
        prompt = f"Fashion catalog: single model wearing {clothing_description}, {user_prompt} style, white background, professional photo"
        
        # Example Replicate API call (commented out as it requires setup)
        # output = replicate.run(
        #     "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
        #     input={
        #         "prompt": prompt,
        #         "negative_prompt": "multiple people, busy background, blurry",
        #         "width": 1024,
        #         "height": 1024,
        #         "num_inference_steps": 25,
        #         "guidance_scale": 7.5
        #     }
        # )
        # return output[0] if output else None
        
        return None
        
    except Exception as e:
        print(f"Replicate generation error: {e}")
        return None