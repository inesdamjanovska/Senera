#!/usr/bin/env python3
"""
Test script to verify API endpoints work correctly
"""
import requests
import json

BASE_URL = "http://192.168.100.228:5000"

def test_login():
    """Test login to get a session"""
    login_data = {
        "email": "test@test.com",
        "password": "test123"
    }
    
    session = requests.Session()
    
    # Login
    login_response = session.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login status: {login_response.status_code}")
    print(f"Login response: {login_response.text}")
    
    if login_response.status_code == 200:
        return session
    else:
        print("Login failed")
        return None

def test_wardrobe_items(session):
    """Test getting wardrobe items"""
    response = session.get(f"{BASE_URL}/wardrobe-items")
    print(f"Wardrobe items status: {response.status_code}")
    print(f"Wardrobe items: {response.text}")
    
    if response.status_code == 200:
        items = response.json()
        if items:
            # Try to delete the first item
            item_id = items[0]['id']
            print(f"Trying to delete item {item_id}")
            delete_response = session.delete(f"{BASE_URL}/wardrobe-items/{item_id}")
            print(f"Delete item status: {delete_response.status_code}")
            print(f"Delete item response: {delete_response.text}")

def test_saved_outfits(session):
    """Test getting saved outfits"""
    response = session.get(f"{BASE_URL}/saved-outfits")
    print(f"Saved outfits status: {response.status_code}")
    print(f"Saved outfits: {response.text}")
    
    if response.status_code == 200:
        outfits = response.json()
        if outfits.get('outfits'):
            # Try to delete the first outfit
            outfit_id = outfits['outfits'][0]['id']
            print(f"Trying to delete outfit {outfit_id}")
            delete_response = session.delete(f"{BASE_URL}/saved-outfits/{outfit_id}")
            print(f"Delete outfit status: {delete_response.status_code}")
            print(f"Delete outfit response: {delete_response.text}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    session = test_login()
    if session:
        print("\n--- Testing Wardrobe Items ---")
        test_wardrobe_items(session)
        
        print("\n--- Testing Saved Outfits ---")
        test_saved_outfits(session)
    else:
        print("Could not login, stopping tests")
