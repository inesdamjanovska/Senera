import React, { createContext, useContext, useState, useEffect } from 'react';
import * as SecureStore from 'expo-secure-store';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Light Theme Colors
export const lightTheme = {
  // Primary colors
  primary: '#007bff', // Standard blue
  primaryDark: '#0056b3',
  primaryLight: '#66b3ff',
  
  // Background colors
  background: '#ffffff',
  surface: '#f8f9fa',
  card: '#ffffff',
  
  // Text colors
  text: '#333333',
  textSecondary: '#666666',
  textLight: '#999999',
  
  // UI Elements
  border: '#e9ecef',
  shadow: '#000000',
  success: '#28a745',
  error: '#dc3545',
  warning: '#ffc107',
  info: '#17a2b8',
  
  // Gradient colors (for headers)
  gradientStart: '#007bff',
  gradientEnd: '#0056b3',
  
  // Status bar
  statusBarStyle: 'dark-content',
  
  // Tab bar
  tabBarBackground: '#ffffff',
  tabBarActive: '#007bff',
  tabBarInactive: '#666666',
};

// Dark Theme Colors
export const darkTheme = {
  // Primary colors
  primary: '#66b3ff', // Lighter blue for dark mode
  primaryDark: '#0056b3',
  primaryLight: '#99ccff',
  
  // Background colors
  background: '#121212',
  surface: '#1e1e1e',
  card: '#2d2d2d',
  
  // Text colors
  text: '#ffffff',
  textSecondary: '#b3b3b3',
  textLight: '#808080',
  
  // UI Elements
  border: '#404040',
  shadow: '#000000',
  success: '#4caf50',
  error: '#f44336',
  warning: '#ff9800',
  info: '#2196f3',
  
  // Gradient colors (for headers)
  gradientStart: '#1e1e1e',
  gradientEnd: '#121212',
  
  // Status bar
  statusBarStyle: 'light-content',
  
  // Tab bar
  tabBarBackground: '#1e1e1e',
  tabBarActive: '#66b3ff',
  tabBarInactive: '#808080',
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(false);
  const [theme, setTheme] = useState(lightTheme);

  useEffect(() => {
    loadTheme();
  }, []);

  useEffect(() => {
    setTheme(isDark ? darkTheme : lightTheme);
  }, [isDark]);

  const loadTheme = async () => {
    try {
      const savedTheme = await SecureStore.getItemAsync('theme');
      if (savedTheme !== null) {
        const isDarkMode = savedTheme === 'dark';
        setIsDark(isDarkMode);
      }
    } catch (error) {
      console.error('Error loading theme:', error);
    }
  };

  const toggleTheme = async () => {
    try {
      const newTheme = !isDark;
      setIsDark(newTheme);
      await SecureStore.setItemAsync('theme', newTheme ? 'dark' : 'light');
    } catch (error) {
      console.error('Error saving theme:', error);
    }
  };

  const value = {
    isDark,
    theme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
