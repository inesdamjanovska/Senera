import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Dimensions,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');

const HomeScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const insets = useSafeAreaInsets();

  const handleLogout = async () => {
    await logout();
  };

  const fashionImages = [
    { id: 1, uri: 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400&h=300&fit=crop', title: 'Casual Chic' },
    { id: 2, uri: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=300&fit=crop', title: 'Street Style' },
    { id: 3, uri: 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400&h=300&fit=crop', title: 'Formal Wear' },
    { id: 4, uri: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=300&fit=crop', title: 'Summer Vibes' },
  ];

  return (
    <ScrollView 
      style={styles.container}
      contentContainerStyle={[
        styles.scrollContent,
        { paddingBottom: Platform.OS === 'ios' ? 100 : 85 } // Space for tab bar
      ]}
    >
      {/* Header */}
      <LinearGradient
        colors={['#007bff', '#0056b3']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.greeting}>Welcome back,</Text>
            <Text style={styles.userName}>{user?.display_name}! 👋</Text>
            <Text style={styles.tagline}>Create amazing outfits with AI</Text>
          </View>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Ionicons name="log-out-outline" size={24} color="white" />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionGrid}>
          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: '#e3f2fd' }]}
            onPress={() => navigation.navigate('Wardrobe')}
          >
            <Ionicons name="shirt-outline" size={32} color="#007bff" />
            <Text style={styles.actionTitle}>My Wardrobe</Text>
            <Text style={styles.actionSubtitle}>View & upload clothes</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: '#f3e5f5' }]}
            onPress={() => navigation.navigate('Closet')}
          >
            <Ionicons name="sparkles-outline" size={32} color="#9c27b0" />
            <Text style={styles.actionTitle}>Generate Outfit</Text>
            <Text style={styles.actionSubtitle}>AI-powered styling</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Fashion Inspiration */}
      <View style={styles.inspiration}>
        <Text style={styles.sectionTitle}>Fashion Inspiration</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {fashionImages.map((item) => (
            <View key={item.id} style={styles.inspirationCard}>
              <Image source={{ uri: item.uri }} style={styles.inspirationImage} />
              <View style={styles.inspirationOverlay}>
                <Text style={styles.inspirationTitle}>{item.title}</Text>
              </View>
            </View>
          ))}
        </ScrollView>
      </View>

      {/* Tips Section */}
      <View style={styles.tips}>
        <Text style={styles.sectionTitle}>Styling Tips</Text>
        <View style={styles.tipCard}>
          <Ionicons name="bulb-outline" size={24} color="#ff9800" />
          <View style={styles.tipContent}>
            <Text style={styles.tipTitle}>Upload Quality Photos</Text>
            <Text style={styles.tipText}>
              For best results, upload clear photos with good lighting. The AI works better with high-quality images!
            </Text>
          </View>
        </View>
        
        <View style={styles.tipCard}>
          <Ionicons name="color-palette-outline" size={24} color="#4caf50" />
          <View style={styles.tipContent}>
            <Text style={styles.tipTitle}>Mix & Match Colors</Text>
            <Text style={styles.tipText}>
              Try different color combinations! The AI can suggest unexpected pairings that look amazing together.
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    paddingTop: 50,
    paddingBottom: 30,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  greeting: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  tagline: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.7)',
  },
  logoutButton: {
    padding: 8,
  },
  quickActions: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  actionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionCard: {
    flex: 1,
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    marginHorizontal: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginTop: 10,
    textAlign: 'center',
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
    textAlign: 'center',
  },
  inspiration: {
    paddingLeft: 20,
    marginBottom: 20,
  },
  inspirationCard: {
    width: width * 0.6,
    height: 200,
    marginRight: 15,
    borderRadius: 15,
    overflow: 'hidden',
  },
  inspirationImage: {
    width: '100%',
    height: '100%',
  },
  inspirationOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    background: 'linear-gradient(transparent, rgba(0,0,0,0.6))',
    padding: 15,
  },
  inspirationTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  tips: {
    padding: 20,
  },
  tipCard: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 12,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  tipContent: {
    flex: 1,
    marginLeft: 15,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  tipText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});

export default HomeScreen;