import os
import base64
import requests
from flask import request, jsonify, Flask, send_from_directory
from PIL import Image
from dotenv import load_dotenv
import json  # Import json module

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

def resize_image(image_path, max_size=512):
    """Resize image to reduce token usage."""
    with Image.open(image_path) as img:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        output_path = image_path.replace('.jpg', '_resized.jpg')
        img.convert('RGB').save(output_path, 'JPEG', quality=85, optimize=True)
        return output_path

def tag_image(image_data, prompt):
    """Analyze a single clothing item image and assign tags."""
    api_key = os.getenv('OPENAI_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Construct the payload for GPT-4o
    analyze_payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"You are a fashion assistant. Analyze this image and assign the following tags: type, type_category, color, style, season, and occasion. Return the tags in JSON format. Prompt: '{prompt}'."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 250
    }

    # Send the request to GPT-4o
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=analyze_payload
    )

    if response.status_code == 200:
        # Parse the response to extract tags
        response_data = response.json()
        tags_content = response_data['choices'][0]['message']['content']
        return tags_content  # Return the tags as a JSON string
    else:
        raise Exception(f"GPT-4o error: {response.text}")


def parse_tags(response):
    """Parse the GPT-4o response to extract tags."""
    try:
        # If the response is already a dictionary, return it directly
        if isinstance(response, dict):
            return response
        
        # Handle markdown code block format
        if isinstance(response, str):
            # Remove markdown code block formatting
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]  # Remove ```json
            if response.startswith('```'):
                response = response[3:]   # Remove ```
            if response.endswith('```'):
                response = response[:-3]  # Remove closing ```
            response = response.strip()
        
        # Parse the cleaned JSON
        tags = json.loads(response)
        return tags
    except json.JSONDecodeError as e:
        # If the response is not JSON, return an error
        print(f"Error: GPT-4o response is not in JSON format. Error: {e}")
        print(f"Response content: {response}")
        return {
            'type': 'unknown',
            'type_category': 'unknown',
            'color': 'unknown',
            'style': [],
            'season': [],
            'occasion': []
        }