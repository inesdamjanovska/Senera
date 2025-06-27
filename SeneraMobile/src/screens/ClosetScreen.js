import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Image,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { outfitAPI } from '../services/api';

const { width } = Dimensions.get('window');

const ClosetScreen = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState(null);
  const [selectedItems, setSelectedItems] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [outfitName, setOutfitName] = useState('');

  const generateOutfit = async () => {
    if (!prompt.trim()) {
      Alert.alert('Error', 'Please enter an outfit description');
      return;
    }

    try {
      setIsGenerating(true);
      setGeneratedOutfit(null);
      setSelectedItems(null);

      const response = await outfitAPI.generateCompleteOutfit(prompt.trim());
      
      if (response.data.outfit_image_url) {
        setGeneratedOutfit(response.data.outfit_image_url);
      }
      
      if (response.data.selected_items) {
        setSelectedItems(response.data.selected_items);
      }

      Alert.alert('Success!', response.data.message);
    } catch (error) {
      console.error('Generation error:', error);
      const errorMessage = error.response?.data?.error || 'Failed to generate outfit';
      Alert.alert('Generation Failed', errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const clearResults = () => {
    setGeneratedOutfit(null);
    setSelectedItems(null);
    setPrompt('');
    setOutfitName('');
  };
  
  const saveOutfit = async () => {
    if (!generatedOutfit) {
      Alert.alert('Error', 'No outfit to save');
      return;
    }
    
    if (!outfitName.trim()) {
      Alert.alert('Name Required', 'Please give your outfit a name to save it');
      return;
    }
    
    try {
      setIsSaving(true);
      
      const outfitData = {
        name: outfitName.trim(),
        image_url: generatedOutfit,
        prompt: prompt
      };
      
      const response = await outfitAPI.saveOutfit(outfitData);
      Alert.alert('Success', 'Outfit saved successfully!');
      setOutfitName('');
    } catch (error) {
      console.error('Save error:', error);
      const errorMessage = error.response?.data?.error || 'Failed to save outfit';
      Alert.alert('Save Failed', errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  const promptSuggestions = [
    'Casual coffee date outfit',
    'Business meeting attire',
    'Weekend casual look',
    'Summer beach outfit',
    'Formal dinner ensemble',
    'Gym workout clothes',
    'Travel comfortable outfit',
    'Party night look',
  ];

  const selectSuggestion = (suggestion) => {
    setPrompt(suggestion);
  };

  const renderSelectedItems = () => {
    if (!selectedItems) return null;

    return (
      <View style={styles.selectedItemsContainer}>
        <Text style={styles.sectionTitle}>Selected Items:</Text>
        {Object.entries(selectedItems).map(([category, items]) => (
          <View key={category} style={styles.categoryContainer}>
            <Text style={styles.categoryTitle}>{category.toUpperCase()}</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {items.map((item, index) => (
                <View key={index} style={styles.selectedItem}>
                  <Image
                    source={{ uri: `http://${process.env.EXPO_PUBLIC_API_HOST || '192.168.100.228'}:${process.env.EXPO_PUBLIC_API_PORT || '5000'}${item.image_url}` }}
                    style={styles.selectedItemImage}
                    defaultSource={require('../../assets/icon.png')}
                  />
                  <View style={styles.selectedItemTags}>
                    {item.tags.slice(0, 2).map((tag, tagIndex) => (
                      <Text key={tagIndex} style={styles.selectedItemTag}>
                        {tag}
                      </Text>
                    ))}
                  </View>
                </View>
              ))}
            </ScrollView>
          </View>
        ))}
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <LinearGradient
        colors={['#9c27b0', '#7b1fa2']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <Ionicons name="sparkles" size={40} color="white" />
          <Text style={styles.headerTitle}>AI Outfit Generator</Text>
          <Text style={styles.headerSubtitle}>
            Describe your perfect outfit and let AI create it!
          </Text>
        </View>
      </LinearGradient>

      {/* Prompt Input */}
      <View style={styles.inputContainer}>
        <Text style={styles.inputLabel}>Describe your outfit:</Text>
        <TextInput
          style={styles.textInput}
          placeholder="e.g., Casual outfit for warm weather"
          placeholderTextColor="#999"
          value={prompt}
          onChangeText={setPrompt}
          multiline
          numberOfLines={3}
        />
        
        <TouchableOpacity
          style={[styles.generateButton, isGenerating && styles.generateButtonDisabled]}
          onPress={generateOutfit}
          disabled={isGenerating}
        >
          <Ionicons 
            name={isGenerating ? "hourglass-outline" : "sparkles-outline"} 
            size={24} 
            color="white" 
          />
          <Text style={styles.generateButtonText}>
            {isGenerating ? 'Generating...' : 'Generate Outfit'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Prompt Suggestions */}
      <View style={styles.suggestionsContainer}>
        <Text style={styles.suggestionsTitle}>Quick Ideas:</Text>
        <View style={styles.suggestionsGrid}>
          {promptSuggestions.map((suggestion, index) => (
            <TouchableOpacity
              key={index}
              style={styles.suggestionChip}
              onPress={() => selectSuggestion(suggestion)}
            >
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Loading State */}
      {isGenerating && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#9c27b0" />
          <Text style={styles.loadingText}>
            Analyzing your wardrobe and generating outfit...
          </Text>
        </View>
      )}

      {/* Selected Items */}
      {renderSelectedItems()}

      {/* Generated Outfit */}
      {generatedOutfit && (
        <View style={styles.resultContainer}>
          <View style={styles.resultHeader}>
            <Text style={styles.sectionTitle}>Your AI-Generated Outfit:</Text>
            <TouchableOpacity style={styles.clearButton} onPress={clearResults}>
              <Ionicons name="close" size={20} color="#666" />
            </TouchableOpacity>
          </View>
          
          <View style={styles.outfitImageContainer}>
            <Image
              source={{ uri: generatedOutfit }}
              style={styles.outfitImage}
              resizeMode="contain"
            />
          </View>
          
          <View style={styles.promptDisplay}>
            <Text style={styles.promptLabel}>Your Request:</Text>
            <Text style={styles.promptText}>"{prompt}"</Text>
          </View>
          
          {/* Subtle Save Button */}
          <View style={styles.saveContainer}>
            <TextInput
              style={styles.saveNameInput}
              placeholder="Name this outfit to save it"
              value={outfitName}
              onChangeText={setOutfitName}
            />
            <TouchableOpacity 
              style={[styles.saveButton, isSaving && styles.saveButtonDisabled]} 
              onPress={saveOutfit}
              disabled={isSaving || !outfitName.trim()}
            >
              <Ionicons 
                name={isSaving ? "hourglass-outline" : "bookmark-outline"} 
                size={20} 
                color="white" 
              />
              <Text style={styles.saveButtonText}>
                {isSaving ? 'Saving...' : 'Save Outfit'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Tips */}
      <View style={styles.tipsContainer}>
        <Text style={styles.sectionTitle}>Tips for Better Results:</Text>
        
        <View style={styles.tipItem}>
          <Ionicons name="bulb-outline" size={20} color="#ff9800" />
          <Text style={styles.tipText}>
            Be specific about the occasion (e.g., "work meeting", "date night")
          </Text>
        </View>
        
        <View style={styles.tipItem}>
          <Ionicons name="sunny-outline" size={20} color="#ffc107" />
          <Text style={styles.tipText}>
            Mention weather or season for better recommendations
          </Text>
        </View>
        
        <View style={styles.tipItem}>
          <Ionicons name="color-palette-outline" size={20} color="#4caf50" />
          <Text style={styles.tipText}>
            Include preferred colors or styles you want to incorporate
          </Text>
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
  header: {
    padding: 20,
    paddingTop: 50,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 10,
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.9)',
    textAlign: 'center',
  },
  inputContainer: {
    padding: 20,
  },
  inputLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  textInput: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    fontSize: 16,
    borderWidth: 2,
    borderColor: '#e0e0e0',
    textAlignVertical: 'top',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  generateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#9c27b0',
    padding: 15,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3.84,
    elevation: 5,
  },
  generateButtonDisabled: {
    backgroundColor: '#ccc',
  },
  generateButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  suggestionsContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  suggestionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  suggestionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  suggestionChip: {
    backgroundColor: 'white',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  suggestionText: {
    fontSize: 14,
    color: '#666',
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 15,
    textAlign: 'center',
  },
  selectedItemsContainer: {
    padding: 20,
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  categoryContainer: {
    marginBottom: 15,
  },
  categoryTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  selectedItem: {
    marginRight: 10,
    alignItems: 'center',
  },
  selectedItemImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  selectedItemTags: {
    marginTop: 5,
  },
  selectedItemTag: {
    fontSize: 10,
    color: '#666',
    textAlign: 'center',
  },
  resultContainer: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingBottom: 10,
  },
  clearButton: {
    padding: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  outfitImageContainer: {
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  outfitImage: {
    width: width - 80,
    height: width - 80,
    borderRadius: 12,
  },
  promptDisplay: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  promptLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 5,
  },
  promptText: {
    fontSize: 16,
    color: '#333',
    fontStyle: 'italic',
  },
  tipsContainer: {
    padding: 20,
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    marginLeft: 10,
  },
  saveContainer: {
    padding: 15,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    marginTop: 10,
  },
  saveNameInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 10,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#28a745',
    padding: 12,
    borderRadius: 8,
    opacity: 0.9,
  },
  saveButtonDisabled: {
    backgroundColor: '#cccccc',
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: 'white',
    marginLeft: 8,
  },
});

export default ClosetScreen;