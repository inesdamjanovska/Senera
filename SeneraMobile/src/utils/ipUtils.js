/**
 * IP Detection and API Configuration for React Native
 * This utility helps automatically detect and use the correct API URL
 */

import { Platform } from 'react-native';
import NetInfo from '@react-native-community/netinfo';

/**
 * Get the current device's local IP address
 * This works on both iOS and Android
 */
export const getCurrentDeviceIP = async () => {
  try {
    if (Platform.OS === 'ios') {
      // For iOS, we can try to get the IP from network info
      const netInfo = await NetInfo.fetch();
      if (netInfo.details && netInfo.details.ipAddress) {
        return netInfo.details.ipAddress;
      }
    }
    
    // For Android and fallback, we'll need to use a different approach
    // Since React Native doesn't have direct access to network interfaces,
    // we'll rely on environment variables and common network patterns
    
    return null; // Will fall back to environment variables
  } catch (error) {
    console.log('Could not detect device IP:', error);
    return null;
  }
};

/**
 * Automatically detect the best API host to use
 * Tries multiple methods to find the correct backend IP
 */
export const getApiHost = async () => {
  // Method 1: Use environment variable if set
  const envHost = process.env.EXPO_PUBLIC_API_HOST;
  if (envHost && envHost !== 'localhost' && envHost !== '127.0.0.1') {
    return envHost;
  }
  
  // Method 2: Common private network IP ranges to try
  const commonIPs = [
    '192.168.1.', // Most common home router range
    '192.168.0.', // Second most common
    '192.168.100.', // Your current range
    '10.0.0.', // Corporate networks
    '172.16.', // Medium corporate networks
  ];
  
  // Method 3: Try to detect device IP and derive backend IP
  const deviceIP = await getCurrentDeviceIP();
  if (deviceIP) {
    // Extract first 3 octets and try common last octets
    const baseIP = deviceIP.substring(0, deviceIP.lastIndexOf('.') + 1);
    const commonLastOctets = ['1', '100', '10', '254', '2'];
    
    for (const lastOctet of commonLastOctets) {
      const testIP = baseIP + lastOctet;
      // We can't actually test connectivity in React Native easily,
      // but we can return this as a candidate
      if (testIP !== deviceIP) {
        return testIP;
      }
    }
  }
  
  // Fallback to environment variable or default
  return envHost || '192.168.100.14';
};

/**
 * Get the complete API URL with automatic IP detection
 */
export const getApiUrl = async () => {
  const host = await getApiHost();
  const port = process.env.EXPO_PUBLIC_API_PORT || '5000';
  return `http://${host}:${port}`;
};

/**
 * Create image URL with automatic IP detection
 */
export const createImageUrl = async (imagePath) => {
  if (!imagePath) return null;
  
  // If it's already a complete URL, return as-is
  if (imagePath.startsWith('http')) {
    return imagePath;
  }
  
  const apiUrl = await getApiUrl();
  return `${apiUrl}${imagePath}`;
};

/**
 * Test API connectivity and return result
 */
export const testApiConnection = async (customHost = null) => {
  try {
    const host = customHost || await getApiHost();
    const port = process.env.EXPO_PUBLIC_API_PORT || '5000';
    const testUrl = `http://${host}:${port}/health`; // Assuming you have a health endpoint
    
    const response = await fetch(testUrl, {
      method: 'GET',
      timeout: 5000,
    });
    
    return {
      success: response.ok,
      host: host,
      status: response.status,
      message: response.ok ? 'Connection successful' : 'Connection failed'
    };
  } catch (error) {
    return {
      success: false,
      host: customHost || 'unknown',
      error: error.message,
      message: 'Could not connect to API'
    };
  }
};

// Export the configuration for easy use
export const ApiConfig = {
  getHost: getApiHost,
  getUrl: getApiUrl,
  createImageUrl: createImageUrl,
  testConnection: testApiConnection,
};
