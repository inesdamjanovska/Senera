from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os
import requests
import base64
from PIL import Image

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def resize_image(image_path, max_size=512):
    """Resize image to reduce token usage"""
    with Image.open(image_path) as img:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        output_path = image_path.replace('.jpg', '_resized.jpg')
        img.convert('RGB').save(output_path, 'JPEG', quality=85, optimize=True)
        return output_path

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/generate-outfit', methods=['POST'])
def generate_outfit():
    filepath = None
    resized_filepath = None

    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        file = request.files['image']
        prompt = request.form.get('prompt', 'Select an outfit for a stylish casual look.')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = 'temp_image.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        resized_filepath = resize_image(filepath)

        with open(resized_filepath, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')

        api_key = os.getenv('OPENAI_API_KEY')
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # GPT-4o: select the most suitable outfit
        analyze_payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You are a fashion assistant. From this image, choose 3–4 clothing items that best fit this style: '{prompt}'. Only pick items that are visible in the image and make sure they match in tone and form a cohesive outfit. Then briefly describe the selected items."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 250
        }

        analyze_response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=analyze_payload
        )

        if analyze_response.status_code != 200:
            return jsonify({'error': f'Analysis error: {analyze_response.text}'}), 500

        clothing_description = analyze_response.json()['choices'][0]['message']['content']

        # DALL·E 3: generate full-body image
        dalle_prompt = (
            f"Photo of a 1(one) fashion model standing full-body, head to toe, in a neutral pose. She only appears once in the image "
            f"The model is wearing: {clothing_description}. white background. "
            f"Styled for: {prompt}. High-quality studio lighting. No other people or props."
        )

        dalle_payload = {
            "model": "dall-e-3",
            "prompt": dalle_prompt,
            "size": "1024x1024",
            "quality": "standard",
            "n": 1
        }

        dalle_response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers=headers,
            json=dalle_payload
        )

        if dalle_response.status_code == 200:
            result = dalle_response.json()
            image_url = result['data'][0]['url']
            return jsonify({'outfit_image': image_url})
        else:
            return jsonify({'error': f'DALL·E error: {dalle_response.text}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        if resized_filepath and os.path.exists(resized_filepath):
            os.remove(resized_filepath)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
