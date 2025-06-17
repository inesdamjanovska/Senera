import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Configure base URL for your backend
const BASE_URL = "USEYOURIPADDRESS"; // Update with your IP

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for session cookies
});

// API methods
export const authAPI = {
  register: (userData) => api.post('/register', userData),
  login: (credentials) => api.post('/login', credentials),
  logout: () => api.post('/logout'),
  getCurrentUser: () => api.get('/current-user'),
};

export const wardrobeAPI = {
  uploadClothing: (formData) => api.post('/upload-clothing', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getWardrobeItems: () => api.get('/wardrobe-items'),
  cleanupUnknown: () => api.delete('/cleanup-unknown'),
};

export const outfitAPI = {
  generateCompleteOutfit: (prompt) => api.post('/generate-complete-outfit', { prompt }),
  analyzePrompt: (prompt) => api.post('/analyze-prompt', { prompt }),
};

export default api;