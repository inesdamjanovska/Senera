#!/usr/bin/env python3
"""
Setup script for Senera Fashion AI project
Helps initialize the development environment
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_backend():
    """Setup backend environment"""
    print("\n🐍 Setting up Python backend...")
    
    # Change to backend directory
    os.chdir('backend')
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            return False
    
    # Activate virtual environment and install requirements
    if platform.system() == 'Windows':
        activate_cmd = 'venv\\Scripts\\activate && '
    else:
        activate_cmd = 'source venv/bin/activate && '
    
    # Install requirements
    install_cmd = f'{activate_cmd}pip install -r ../requirements.txt'
    if not run_command(install_cmd, 'Installing Python dependencies'):
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Network Configuration (auto-detected if not set)
API_HOST=192.168.100.14
API_PORT=5000

# Flask Security
SECRET_KEY=your_secure_random_secret_key_here

# Image Generation Service
# Options: dalle, pollinations, huggingface, replicate
IMAGE_GENERATION_SERVICE=pollinations
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created backend/.env file - please update with your API keys")
    
    # Initialize database
    init_cmd = f'{activate_cmd}python init_db.py'
    run_command(init_cmd, 'Initializing database')
    
    os.chdir('..')
    return True

def setup_frontend():
    """Setup React Native frontend"""
    print("\n📱 Setting up React Native frontend...")
    
    # Check if Node.js is installed
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        print("✅ Node.js and npm are installed")
    except subprocess.CalledProcessError:
        print("❌ Node.js and npm are required for React Native. Please install them first.")
        return False
    
    # Change to mobile directory
    os.chdir('SeneraMobile')
    
    # Install dependencies
    if not run_command('npm install', 'Installing React Native dependencies'):
        os.chdir('..')
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        env_content = """EXPO_PUBLIC_API_HOST=192.168.100.14
EXPO_PUBLIC_API_PORT=5000
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created frontend/.env file")
    
    os.chdir('..')
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        'backend/uploads',
        'backend/flask_session',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Senera Fashion AI - Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Run IP update script
    print("\n🌐 Updating IP configuration...")
    run_command('python update_ip.py', 'Updating IP addresses')
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update backend/.env with your OpenAI API key")
    print("2. Start the backend: cd backend && python app.py")
    print("3. Start the mobile app: cd SeneraMobile && npm start")
    print("4. Run update_ip.py if your IP address changes")
    print("\n💡 Helpful commands:")
    print("- Update IP addresses: python update_ip.py")
    print("- Install dev tools: pip install -r requirements-dev.txt")
    print("- Run tests: pytest (after installing dev requirements)")

if __name__ == "__main__":
    main()
