import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const LoadingScreen = () => {
  return (
    <LinearGradient
      colors={['#007bff', '#0056b3']}
      style={styles.container}
    >
      <View style={styles.content}>
        <Text style={styles.logo}>👗</Text>
        <Text style={styles.title}>Senera</Text>
        <ActivityIndicator size="large" color="white" style={styles.loader} />
        <Text style={styles.subtitle}>Loading your wardrobe...</Text>
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
  },
  logo: {
    fontSize: 80,
    marginBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 30,
  },
  loader: {
    marginBottom: 20,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
});

export default LoadingScreen;