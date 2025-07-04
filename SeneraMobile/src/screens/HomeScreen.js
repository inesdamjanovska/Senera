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
import { useTheme } from '../context/ThemeContext';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

const { width } = Dimensions.get('window');

const HomeScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();

  const handleLogout = async () => {
    await logout();
  };

  const handleSettings = () => {
    navigation.navigate('Settings');
  };

  const fashionImages = [
    { id: 1, uri: 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400&h=300&fit=crop', title: 'Casual Chic' },
    { id: 2, uri: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&h=300&fit=crop', title: 'Street Style' },
    { id: 3, uri: 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400&h=300&fit=crop', title: 'Formal Wear' },
    { id: 4, uri: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=300&fit=crop', title: 'Summer Vibes' },
  ];

  return (
    <ScrollView 
      style={[styles.container, { backgroundColor: theme.background }]}
      contentContainerStyle={[
        styles.scrollContent,
        { paddingBottom: Platform.OS === 'ios' ? 100 : 85 } // Space for tab bar
      ]}
    >
      <StatusBar style={theme.statusBarStyle} />
      
      {/* Header */}
      <LinearGradient
        colors={[theme.gradientStart, theme.gradientEnd]}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.greeting}>Welcome back,</Text>
            <Text style={styles.userName}>{user?.display_name}! 👋</Text>
            <Text style={styles.tagline}>Create amazing outfits with AI</Text>
          </View>
          <View style={styles.headerButtons}>
            <TouchableOpacity style={styles.headerButton} onPress={handleSettings}>
              <Ionicons name="settings-outline" size={24} color="white" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerButton} onPress={handleLogout}>
              <Ionicons name="log-out-outline" size={24} color="white" />
            </TouchableOpacity>
          </View>
        </View>
      </LinearGradient>

      {/* Quick Actions */}
      <View style={[styles.quickActions, { backgroundColor: theme.background }]}>
        <Text style={[styles.sectionTitle, { color: theme.text }]}>Quick Actions</Text>
        <View style={styles.actionGrid}>
          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: theme.card }]}
            onPress={() => navigation.navigate('Wardrobe')}
          >
            <Ionicons name="shirt-outline" size={32} color={theme.primary} />
            <Text style={[styles.actionTitle, { color: theme.text }]}>My Wardrobe</Text>
            <Text style={[styles.actionSubtitle, { color: theme.textSecondary }]}>View & upload clothes</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: theme.card }]}
            onPress={() => navigation.navigate('Closet')}
          >
            <Ionicons name="sparkles-outline" size={32} color={theme.primary} />
            <Text style={[styles.actionTitle, { color: theme.text }]}>Generate Outfit</Text>
            <Text style={[styles.actionSubtitle, { color: theme.textSecondary }]}>AI-powered styling</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Fashion Inspiration */}
      <View style={styles.inspiration}>
        <Text style={[styles.sectionTitle, { color: theme.text }]}>Fashion Inspiration</Text>
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
        <Text style={[styles.sectionTitle, { color: theme.text }]}>Styling Tips</Text>
        <View style={[styles.tipCard, { backgroundColor: theme.card }]}>
          <Ionicons name="bulb-outline" size={24} color={theme.warning} />
          <View style={styles.tipContent}>
            <Text style={[styles.tipTitle, { color: theme.text }]}>Upload Quality Photos</Text>
            <Text style={[styles.tipText, { color: theme.textSecondary }]}>
              For best results, upload clear photos with good lighting. The AI works better with high-quality images!
            </Text>
          </View>
        </View>
        
        <View style={[styles.tipCard, { backgroundColor: theme.card }]}>
          <Ionicons name="color-palette-outline" size={24} color={theme.success} />
          <View style={styles.tipContent}>
            <Text style={[styles.tipTitle, { color: theme.text }]}>Mix & Match Colors</Text>
            <Text style={[styles.tipText, { color: theme.textSecondary }]}>
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
  },
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    paddingTop: 15,
    paddingBottom: 15,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    padding: 8,
    marginLeft: 8,
  },
  greeting: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  userName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  tagline: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.7)',
  },
  quickActions: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
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
    marginTop: 10,
    textAlign: 'center',
  },
  actionSubtitle: {
    fontSize: 12,
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
    marginBottom: 5,
  },
  tipText: {
    fontSize: 14,
    lineHeight: 20,
  },
});

export default HomeScreen;