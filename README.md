# Senera Fashion AI

Senera is a full-stack fashion AI application that helps users generate stylish outfits using their own clothes. Users upload images of clothing items they own, and the system stores, tags, and organizes them using AI. Based on prompts like occasion, weather, or style, the app intelligently selects relevant clothing items and generates virtual outfit images using multiple AI models.

## ✨ Features

- 🏠 **Personal Wardrobe Management**: Upload and organize your clothing items
- 🤖 **AI-Powered Tagging**: Automatic categorization and tagging of clothing
- 🎨 **Multiple AI Models**: Choose from DALL-E 3, Pollinations.ai (free), Hugging Face, and more
- 📱 **Mobile App**: React Native mobile application
- 🔒 **User Authentication**: Secure user accounts and personal wardrobes
- 🎯 **Smart Outfit Generation**: AI selects best matching items for any occasion

## 🚀 Quick Start

### Automatic Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd Senera

# Run the automated setup
python setup.py
```

This will automatically:
- Create virtual environments
- Install all dependencies
- Set up configuration files
- Initialize the database
- Configure IP addresses

### Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your OpenAI API key
cp .env.example .env  # Edit with your API key

# Initialize database
python init_db.py

# Start the server
python app.py
```

#### Mobile App Setup
```bash
cd SeneraMobile

# Install dependencies
npm install

# Start the app
npm start
```

## 📁 Project Structure

```
Senera/
├── backend/                 # Flask API server
│   ├── app.py              # Main application
│   ├── config.py           # Configuration with auto IP detection
│   ├── ip_utils.py         # IP detection utilities
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── db/                 # Database models
│   └── uploads/            # User uploaded images
├── SeneraMobile/           # React Native mobile app
│   ├── src/
│   │   ├── screens/        # App screens
│   │   ├── components/     # Reusable components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
├── update_ip.py            # Automatic IP address updater
├── setup.py                # Automated environment setup
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
└── requirements-prod.txt   # Production dependencies
```

## 🔧 Configuration

### AI Model Selection

Choose from multiple AI image generation services:
- **DALL-E 3**: High quality, requires OpenAI API key (paid)
- **Pollinations.ai**: Free, no API key needed
- **Hugging Face**: Free tier available, requires setup
- **Replicate**: Various models available, requires API key

Set your preferred service in `backend/.env`:
```env
IMAGE_GENERATION_SERVICE=pollinations  # or dalle, huggingface, replicate
```

## 🌐 IP Address Management

The app includes automatic IP detection to eliminate manual configuration:

### Automatic Detection
The backend automatically detects your local IP address on startup.

### Manual Update
If your IP changes, run:
```bash
python update_ip.py
```

This updates all configuration files automatically.

## 📱 Mobile App Usage

1. **Register/Login**: Create an account or sign in
2. **Upload Clothes**: Take photos or upload images of your clothing
3. **AI Tagging**: Items are automatically tagged and categorized
4. **Generate Outfits**: Enter prompts like "casual date night" or "business meeting"
5. **Choose AI Model**: Select your preferred AI service for outfit generation
6. **View Results**: See AI-generated outfit photos using your actual clothes

## 🛠️ Development

### Install Development Tools
```bash
pip install -r requirements-dev.txt
```

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
flake8 .
```

### API Testing
The backend includes a health check endpoint at `/health` for connectivity testing.

## 🚢 Deployment

### Production Setup
```bash
pip install -r requirements-prod.txt
```

### Production Considerations
- Use a production WSGI server (Gunicorn included in prod requirements)
- Set up proper database (PostgreSQL recommended)
- Configure SSL/HTTPS
- Set up monitoring and logging
- Use environment variables for all secrets

## 🔍 Troubleshooting

### Common Issues

**Connection Problems:**
1. Run `python update_ip.py` to sync IP addresses
2. Ensure both devices are on the same network
3. Check firewall settings

**API Key Issues:**
1. Verify OpenAI API key in `backend/.env`
2. Check API key permissions and billing
3. Try free Pollinations.ai service as alternative

**Setup Problems:**
1. Ensure Python 3.8+ is installed
2. Check Node.js and npm installation for mobile app
3. Run `python setup.py` for automated setup

### Support
For additional help, check:
- `IP_MANAGEMENT.md` for network configuration
- `WARDROBE_FEATURES.md` for feature details
- Backend logs for error details

## 📋 Dependencies

### Backend (Python)
- Flask - Web framework
- OpenAI - AI image generation
- Pillow - Image processing
- rembg - Background removal
- SQLAlchemy - Database ORM
- Flask-Session - Session management

### Frontend (React Native)
- Expo - Mobile development platform
- React Navigation - Navigation
- Axios - HTTP client
- Various Expo modules for camera, image picker, etc.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request
