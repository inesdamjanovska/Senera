#!/usr/bin/env python3
"""
Test script to verify the new image processing changes:
1. Light grey background instead of transparent
2. Borders instead of cropping to make images square
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
import io
from services.services import resize_image
from rembg import remove

def create_test_image():
    """Create a test image with a simple shape to test processing"""
    # Create a test image with transparency
    img = Image.new('RGBA', (300, 200), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    
    # Draw a simple red rectangle
    draw.rectangle([50, 50, 250, 150], fill=(255, 0, 0, 255))  # Red rectangle
    
    # Save as test image
    test_path = os.path.join('uploads', 'test_image.png')
    os.makedirs('uploads', exist_ok=True)
    img.save(test_path, 'PNG')
    print(f"Test image created at: {test_path}")
    return test_path

def test_background_processing():
    """Test the new background processing"""
    print("Testing new image processing...")
    
    # Create test image
    test_path = create_test_image()
    
    try:
        # Test the resize_image function with borders and light background
        processed_path = resize_image(test_path)
        print(f"Processed image saved at: {processed_path}")
        
        # Verify the processed image
        with Image.open(processed_path) as processed_img:
            print(f"Original size: {Image.open(test_path).size}")
            print(f"Processed size: {processed_img.size}")
            print(f"Processed mode: {processed_img.mode}")
            
            # Check if the image is square
            width, height = processed_img.size
            if width == height:
                print("✓ Image is square (borders added correctly)")
            else:
                print("✗ Image is not square")
                
            # Check corners for light grey background
            corner_pixel = processed_img.getpixel((0, 0))
            print(f"Corner pixel color: {corner_pixel}")
            
            # Light grey should be around (248, 248, 248)
            if corner_pixel == (248, 248, 248):
                print("✓ Light grey background applied correctly")
            else:
                print(f"✗ Background color is {corner_pixel}, expected (248, 248, 248)")
                
    except Exception as e:
        print(f"Error during processing: {e}")
    
    print("Test completed!")

if __name__ == "__main__":
    test_background_processing()
