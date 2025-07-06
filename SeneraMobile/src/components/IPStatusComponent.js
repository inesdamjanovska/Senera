import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { ApiConfig } from '../utils/ipUtils';

const IPStatusComponent = ({ visible = true }) => {
  const [currentIP, setCurrentIP] = useState('Loading...');
  const [connectionStatus, setConnectionStatus] = useState('Testing...');
  const [isConnected, setIsConnected] = useState(null);

  useEffect(() => {
    if (visible) {
      checkConnectionStatus();
    }
  }, [visible]);

  const checkConnectionStatus = async () => {
    try {
      // Get current API host
      const host = await ApiConfig.getHost();
      setCurrentIP(host);

      // Test connection
      const result = await ApiConfig.testConnection();
      setIsConnected(result.success);
      setConnectionStatus(result.message);

      if (!result.success) {
        console.log('Connection test failed:', result);
      }
    } catch (error) {
      setConnectionStatus('Connection test failed');
      setIsConnected(false);
      console.error('IP status check error:', error);
    }
  };

  const showIPDetails = () => {
    Alert.alert(
      'API Configuration',
      `Current IP: ${currentIP}\nStatus: ${connectionStatus}\n\nIf you're having connection issues, try:\n1. Run update_ip.py script\n2. Restart the backend server\n3. Check if both devices are on the same network`,
      [
        { text: 'Retry', onPress: checkConnectionStatus },
        { text: 'OK' }
      ]
    );
  };

  if (!visible) return null;

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.statusContainer} onPress={showIPDetails}>
        <View style={[styles.indicator, { backgroundColor: isConnected ? '#4CAF50' : isConnected === false ? '#F44336' : '#FF9800' }]} />
        <Text style={styles.statusText}>
          {currentIP} {isConnected ? '✓' : isConnected === false ? '✗' : '⏳'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 50,
    right: 10,
    zIndex: 1000,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  indicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontFamily: 'monospace',
  },
});

export default IPStatusComponent;
