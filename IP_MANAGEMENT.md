# Automatic IP Address Management

This project now includes automatic IP address detection and management to eliminate the need for manual IP updates when your network configuration changes.

## 🚀 Quick Start

### Automatic Method (Recommended)

The backend now automatically detects your IP address on startup. Just run:

```bash
cd backend
python app.py
```

The system will automatically:
- Detect your current local IP address
- Use it for the API host configuration
- Display the detected IP in console

### Manual Update Method

If you need to update all configuration files manually:

**Windows:**
```bash
# Double-click the batch file or run:
update_ip.bat
```

**Command Line:**
```bash
python update_ip.py
```

## 📁 Files That Get Updated

The IP update system manages these files:

### Backend Files
- `backend/.env` - API_HOST setting
- `backend/config.py` - Automatic IP detection
- `backend/ip_utils.py` - IP detection utilities

### Frontend Files  
- `SeneraMobile/.env` - EXPO_PUBLIC_API_HOST setting
- `SeneraMobile/src/services/api.js` - Fallback IP addresses
- `SeneraMobile/src/screens/WardrobeScreen.js` - Image URL fallbacks
- `SeneraMobile/src/screens/ClosetScreen.js` - Image URL fallbacks

## 🔧 How It Works

### Backend Auto-Detection
The backend uses `ip_utils.py` to:
1. Connect to external servers to determine local IP
2. Parse `ipconfig` output on Windows
3. Fall back to hostname resolution
4. Use environment variables if available

### Frontend Utils
The frontend includes `ipUtils.js` to:
1. Detect device IP when possible
2. Try common private network ranges
3. Test API connectivity
4. Create proper image URLs

## 🎯 Usage Examples

### Backend Configuration
```python
# config.py automatically detects IP
from ip_utils import get_api_host

class Config:
    API_HOST = get_api_host()  # Auto-detects or uses env var
```

### Frontend Usage
```javascript
import { ApiConfig } from '../utils/ipUtils';

// Get current API URL
const apiUrl = await ApiConfig.getUrl();

// Test connectivity
const result = await ApiConfig.testConnection();

// Create image URL
const imageUrl = await ApiConfig.createImageUrl('/uploads/image.png');
```

## 🔍 Troubleshooting

### Backend Not Detecting Correct IP?
1. Set the IP manually in `backend/.env`:
   ```
   API_HOST=192.168.1.100
   ```

2. Run the update script:
   ```bash
   python update_ip.py
   ```

### Frontend Connection Issues?
1. Check the IP status component (if added to your screens)
2. Verify both devices are on the same network
3. Run the update script to sync all files

### Manual IP Override
You can always set IPs manually in the `.env` files:

**Backend (.env):**
```
API_HOST=192.168.1.100
API_PORT=5000
```

**Frontend (.env):**
```
EXPO_PUBLIC_API_HOST=192.168.1.100
EXPO_PUBLIC_API_PORT=5000
```

## 🧪 Testing IP Detection

Test the IP detection system:

```bash
# Test backend IP detection
cd backend
python ip_utils.py

# Test full update process
python update_ip.py
```

## 📱 Frontend IP Status (Optional)

Add the IP status component to your screens to monitor connection:

```javascript
import IPStatusComponent from '../components/IPStatusComponent';

// In your screen component:
<IPStatusComponent visible={true} />
```

This shows a small indicator with:
- 🟢 Green: Connected successfully
- 🔴 Red: Connection failed  
- 🟡 Orange: Testing connection

## 🔄 When to Update IPs

Run the update script when:
- Your router assigns a new IP to your computer
- You move to a different network
- The frontend can't connect to the backend
- You see connection errors in the app

## 📋 Command Reference

| Command | Purpose |
|---------|---------|
| `python update_ip.py` | Update all configuration files |
| `update_ip.bat` | Windows batch file for easy updating |
| `python backend/ip_utils.py` | Test IP detection only |
| `python backend/app.py` | Start backend with auto-detection |

The system prioritizes environment variables over auto-detection, so you can always override by setting values in `.env` files.
