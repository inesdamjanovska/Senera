import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Configure base URL for your backend using environment variables
const API_HOST = process.env.EXPO_PUBLIC_API_HOST || '192.168.100.253';
const API_PORT = process.env.EXPO_PUBLIC_API_PORT || '5000';
const BASE_URL = `http://${API_HOST}:${API_PORT}`;

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
  deleteItem: (itemId) => api.delete(`/wardrobe-items/${itemId}`),
  deleteItems: (itemIds) => api.delete('/wardrobe-items', { data: { item_ids: itemIds } }),
};

export const outfitAPI = {
  generateCompleteOutfit: (prompt) => api.post('/generate-complete-outfit', { prompt }),
  analyzePrompt: (prompt) => api.post('/analyze-prompt', { prompt }),
  saveOutfit: (outfitData) => api.post('/save-outfit', outfitData),
  getSavedOutfits: () => api.get('/saved-outfits'),
  deleteOutfit: (outfitId) => api.delete(`/saved-outfits/${outfitId}`),
  deleteOutfits: (outfitIds) => api.delete('/saved-outfits', { data: { outfit_ids: outfitIds } }),
  renameOutfit: (outfitId, newName) => api.put(`/saved-outfits/${outfitId}`, { name: newName }),
};

export default api;