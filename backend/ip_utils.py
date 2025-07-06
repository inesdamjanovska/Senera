"""
IP Detection Utility Module
Can be imported and used to automatically detect and use the current IP
"""

import socket
import os
import subprocess
import re

def get_current_ip():
    """
    Automatically detect the current local IP address
    Returns the best available IP address for the current network
    """
    try:
        # Method 1: Connect to external server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            # Validate it's a proper private network IP
            if (local_ip.startswith('192.168.') or 
                local_ip.startswith('10.') or 
                (local_ip.startswith('172.') and 16 <= int(local_ip.split('.')[1]) <= 31)):
                return local_ip
    except Exception:
        pass
    
    try:
        # Method 2: Windows ipconfig parsing for more reliable detection
        if os.name == 'nt':  # Windows
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
            output = result.stdout
            
            # Look for active network adapters (not virtual ones)
            lines = output.split('\n')
            current_adapter = ""
            
            for line in lines:
                line = line.strip()
                
                # Track current adapter
                if "adapter" in line.lower() and ":" in line:
                    current_adapter = line.lower()
                
                # Look for IPv4 addresses in physical adapters
                if "ipv4 address" in line.lower() and ":" in line:
                    # Skip virtual adapters
                    if any(virtual in current_adapter for virtual in 
                          ['virtual', 'vmware', 'virtualbox', 'hyper-v', 'loopback']):
                        continue
                    
                    # Extract IP
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        # Prefer private network IPs
                        if (ip.startswith('192.168.') or 
                            ip.startswith('10.') or 
                            (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31)):
                            return ip
    except Exception:
        pass
    
    try:
        # Method 3: Hostname resolution fallback
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip != "127.0.0.1":
            return local_ip
    except Exception:
        pass
    
    # Default fallback
    return "127.0.0.1"

def get_api_host():
    """
    Get the API host, using environment variable or auto-detected IP
    This function can be used in config.py to automatically use current IP
    """
    # First check environment variable
    env_host = os.getenv('API_HOST')
    if env_host:
        return env_host
    
    # If no environment variable, auto-detect
    detected_ip = get_current_ip()
    print(f"🔍 Auto-detected IP: {detected_ip}")
    return detected_ip

def get_frontend_api_url():
    """
    Get the complete API URL for frontend use
    """
    host = get_api_host()
    port = os.getenv('API_PORT', '5000')
    return f"http://{host}:{port}"

# Test function to verify IP detection
def test_ip_detection():
    """Test and display current IP detection results"""
    print("🔍 IP Detection Test Results:")
    print("=" * 40)
    
    current_ip = get_current_ip()
    print(f"Detected IP: {current_ip}")
    
    api_host = get_api_host()
    print(f"API Host: {api_host}")
    
    frontend_url = get_frontend_api_url()
    print(f"Frontend API URL: {frontend_url}")
    
    # Test connectivity
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex((current_ip, 5000))
            if result == 0:
                print("✅ Port 5000 is reachable")
            else:
                print("⚠️  Port 5000 is not currently open")
    except Exception as e:
        print(f"⚠️  Connection test failed: {e}")

if __name__ == "__main__":
    test_ip_detection()
