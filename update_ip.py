#!/usr/bin/env python3
"""
Automatic IP Address Detection and Update Script
This script detects the local IP address and updates all configuration files
"""

import socket
import os
import re
import subprocess
import sys

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Method 1: Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to Google DNS (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception:
        pass
    
    try:
        # Method 2: Get hostname and resolve it
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip != "127.0.0.1":
            return local_ip
    except Exception:
        pass
    
    try:
        # Method 3: Windows-specific ipconfig parsing
        if os.name == 'nt':  # Windows
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            output = result.stdout
            
            # Look for IPv4 addresses that are not localhost
            ip_pattern = r'IPv4 Address[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)'
            matches = re.findall(ip_pattern, output)
            
            for ip in matches:
                if not ip.startswith('127.') and not ip.startswith('169.254'):
                    return ip
    except Exception:
        pass
    
    # Fallback to localhost
    return "127.0.0.1"

def update_env_file(file_path, new_ip):
    """Update environment file with new IP"""
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update API_HOST or EXPO_PUBLIC_API_HOST
        if 'API_HOST=' in content:
            content = re.sub(r'API_HOST=.*', f'API_HOST={new_ip}', content)
        if 'EXPO_PUBLIC_API_HOST=' in content:
            content = re.sub(r'EXPO_PUBLIC_API_HOST=.*', f'EXPO_PUBLIC_API_HOST={new_ip}', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def update_config_file(file_path, new_ip):
    """Update config.py file with new IP"""
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update the fallback IP in config.py
        content = re.sub(
            r"API_HOST = os\.getenv\('API_HOST', '[^']+'\)",
            f"API_HOST = os.getenv('API_HOST', '{new_ip}')",
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def update_frontend_files(new_ip):
    """Update frontend JavaScript files with new fallback IP"""
    files_to_update = [
        'SeneraMobile/src/services/api.js',
        'SeneraMobile/src/screens/WardrobeScreen.js',
        'SeneraMobile/src/screens/ClosetScreen.js'
    ]
    
    for relative_path in files_to_update:
        file_path = os.path.join(os.path.dirname(__file__), relative_path)
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Update fallback IP addresses in JavaScript files
            # Pattern matches: '192.168.x.x' (any IP address)
            old_pattern = r"'(\d+\.\d+\.\d+\.\d+)'"
            
            def replace_ip(match):
                old_ip = match.group(1)
                # Only replace if it's not localhost and looks like a private IP
                if (old_ip != '127.0.0.1' and 
                    (old_ip.startswith('192.168.') or 
                     old_ip.startswith('10.') or 
                     old_ip.startswith('172.'))):
                    return f"'{new_ip}'"
                return match.group(0)
            
            updated_content = re.sub(old_pattern, replace_ip, content)
            
            if updated_content != content:
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                print(f"✅ Updated {file_path}")
            else:
                print(f"ℹ️  No changes needed in {file_path}")
            
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")

def main():
    """Main function to detect IP and update all files"""
    print("🔍 Detecting local IP address...")
    
    # Get current IP
    current_ip = get_local_ip()
    print(f"📍 Detected IP address: {current_ip}")
    
    if current_ip == "127.0.0.1":
        print("⚠️  Could only detect localhost. You may need to manually set your network IP.")
        response = input("Do you want to continue with 127.0.0.1? (y/n): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled.")
            return
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\n🔄 Updating configuration files with IP: {current_ip}")
    print("=" * 50)
    
    # Update backend .env
    backend_env = os.path.join(script_dir, 'backend', '.env')
    update_env_file(backend_env, current_ip)
    
    # Update frontend .env
    frontend_env = os.path.join(script_dir, 'SeneraMobile', '.env')
    update_env_file(frontend_env, current_ip)
    
    # Update config.py
    config_file = os.path.join(script_dir, 'backend', 'config.py')
    update_config_file(config_file, current_ip)
    
    # Update frontend files
    print("\n📱 Updating frontend files...")
    update_frontend_files(current_ip)
    
    print("\n" + "=" * 50)
    print("🎉 IP address update complete!")
    print(f"📍 All files now use: {current_ip}")
    print("\n💡 Next steps:")
    print("1. Restart your Flask backend if it's running")
    print("2. Restart your React Native app if it's running")
    print("3. Test the connection between frontend and backend")

if __name__ == "__main__":
    main()
