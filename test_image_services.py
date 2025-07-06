#!/usr/bin/env python3
"""
Quick test script for different image generation services
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.collage_service import generate_outfit_with_pollinations

def test_pollinations():
    """Test Pollinations.ai service"""
    print("🎨 Testing Pollinations.ai...")
    
    clothing_description = """Navy blue crew neck cotton t-shirt, faded light blue high-waisted straight-leg jeans, white canvas sneakers with minimalist design. The fitted t-shirt pairs perfectly with relaxed jeans, creating a balanced casual look."""
    
    user_prompt = "casual coffee date outfit"
    
    try:
        image_url = generate_outfit_with_pollinations(clothing_description, user_prompt)
        print(f"✅ Generated image URL: {image_url}")
        print(f"🔗 Open this URL in your browser to see the result!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_different_descriptions():
    """Test with various outfit descriptions"""
    test_cases = [
        {
            "description": "Black leather jacket, white cotton t-shirt, dark blue skinny jeans, black ankle boots",
            "prompt": "edgy street style outfit"
        },
        {
            "description": "Light pink silk blouse, beige high-waisted trousers, nude pointed-toe heels, gold delicate jewelry",
            "prompt": "business casual professional look"
        },
        {
            "description": "Oversized gray hoodie, black athletic leggings, white running sneakers",
            "prompt": "comfortable gym workout outfit"
        }
    ]
    
    print("🧪 Testing multiple outfit combinations...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['prompt']} ---")
        try:
            image_url = generate_outfit_with_pollinations(
                test_case['description'], 
                test_case['prompt']
            )
            print(f"✅ Generated: {image_url}")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Free Image Generation Services")
    print("=" * 50)
    
    # Test Pollinations.ai (completely free)
    if test_pollinations():
        print("\n🎉 Pollinations.ai is working! This is completely free and requires no API key.")
        print("💡 You can change IMAGE_GENERATION_SERVICE=pollinations in your .env file to use this instead of DALL-E")
    
    print("\n" + "=" * 50)
    test_with_different_descriptions()
    
    print("\n📝 Notes:")
    print("• Pollinations.ai is completely free, no API key needed")
    print("• Results may vary - some might be better than DALL-E for fashion")
    print("• You can switch services by changing IMAGE_GENERATION_SERVICE in .env")
    print("• Available options: dalle, pollinations, huggingface, replicate")
