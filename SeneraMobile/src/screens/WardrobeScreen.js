import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  RefreshControl,
  Dimensions,
  ActivityIndicator,
  Modal,
  TextInput,
  SafeAreaView,
  Pressable,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { wardrobeAPI, outfitAPI } from '../services/api';

const { width } = Dimensions.get('window');

const WardrobeScreen = () => {
  const [activeTab, setActiveTab] = useState('clothes'); // 'clothes' or 'outfits'
  const [wardrobeItems, setWardrobeItems] = useState([]);
  const [savedOutfits, setSavedOutfits] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Modal states
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedOutfit, setSelectedOutfit] = useState(null);
  const [itemModalVisible, setItemModalVisible] = useState(false);
  const [outfitModalVisible, setOutfitModalVisible] = useState(false);
  
  // Category filter states
  const [selectedCategory, setSelectedCategory] = useState('All');
  const categories = ['All', 'Tops', 'Bottoms', 'Shoes', 'Accessories', 'Outerwear'];
  
  // Map frontend categories to backend categories
  const categoryMap = {
    'All': null,
    'Tops': ['top'],
    'Bottoms': ['bottom'], 
    'Shoes': ['footwear'],
    'Accessories': ['accessory'],
    'Outerwear': ['outerwear']
  };
  
  // Multi-select states
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [selectedOutfits, setSelectedOutfits] = useState([]);
  
  // Outfit renaming state
  const [outfitNewName, setOutfitNewName] = useState('');
  const [isRenaming, setIsRenaming] = useState(false);

  useEffect(() => {
    if (activeTab === 'clothes') {
      loadWardrobeItems();
    } else {
      loadSavedOutfits();
    }
    // Reset selection mode when switching tabs
    setSelectionMode(false);
    setSelectedItems([]);
    setSelectedOutfits([]);
  }, [activeTab]);

  const loadWardrobeItems = async () => {
    try {
      setIsLoading(true);
      const response = await wardrobeAPI.getWardrobeItems();
      setWardrobeItems(response.data || []);
    } catch (error) {
      console.error('Error loading wardrobe:', error);
      Alert.alert('Error', 'Failed to load wardrobe items');
    } finally {
      setIsLoading(false);
    }
  };
  
  const loadSavedOutfits = async () => {
    try {
      setIsLoading(true);
      const response = await outfitAPI.getSavedOutfits();
      setSavedOutfits(response.data.outfits || []);
    } catch (error) {
      console.error('Error loading saved outfits:', error);
      Alert.alert('Error', 'Failed to load saved outfits');
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    if (activeTab === 'clothes') {
      await loadWardrobeItems();
    } else {
      await loadSavedOutfits();
    }
    setRefreshing(false);
  };

  // Filter items by category
  const getFilteredItems = () => {
    if (selectedCategory === 'All') {
      return wardrobeItems;
    }
    
    const allowedCategories = categoryMap[selectedCategory] || [];
    return wardrobeItems.filter(item => 
      allowedCategories.some(category => 
        item.type_category?.toLowerCase().includes(category.toLowerCase())
      )
    );
  };

  // Handle item selection (tap)
  const handleItemPress = (item) => {
    if (selectionMode) {
      toggleItemSelection(item.id);
    } else {
      setSelectedItem(item);
      setItemModalVisible(true);
    }
  };

  // Handle outfit selection (tap)
  const handleOutfitPress = (outfit) => {
    if (selectionMode) {
      toggleOutfitSelection(outfit.id);
    } else {
      setSelectedOutfit(outfit);
      setOutfitNewName(outfit.name);
      setOutfitModalVisible(true);
    }
  };

  // Handle long press for selection mode
  const handleItemLongPress = (itemId) => {
    if (!selectionMode) {
      setSelectionMode(true);
      setSelectedItems([itemId]);
    }
  };

  const handleOutfitLongPress = (outfitId) => {
    if (!selectionMode) {
      setSelectionMode(true);
      setSelectedOutfits([outfitId]);
    }
  };

  // Toggle item selection
  const toggleItemSelection = (itemId) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const toggleOutfitSelection = (outfitId) => {
    setSelectedOutfits(prev => 
      prev.includes(outfitId) 
        ? prev.filter(id => id !== outfitId)
        : [...prev, outfitId]
    );
  };

  // Exit selection mode
  const exitSelectionMode = () => {
    setSelectionMode(false);
    setSelectedItems([]);
    setSelectedOutfits([]);
  };

  // Delete selected items
  const deleteSelectedItems = () => {
    const count = activeTab === 'clothes' ? selectedItems.length : selectedOutfits.length;
    Alert.alert(
      'Delete Items',
      `Are you sure you want to delete ${count} ${activeTab === 'clothes' ? 'item(s)' : 'outfit(s)'}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              if (activeTab === 'clothes') {
                await wardrobeAPI.deleteItems(selectedItems);
                await loadWardrobeItems();
              } else {
                await outfitAPI.deleteOutfits(selectedOutfits);
                await loadSavedOutfits();
              }
              exitSelectionMode();
              Alert.alert('Success', `${count} ${activeTab === 'clothes' ? 'item(s)' : 'outfit(s)'} deleted`);
            } catch (error) {
              console.error('Delete error:', error);
              Alert.alert('Error', 'Failed to delete items');
            }
          },
        },
      ]
    );
  };

  // Delete single item from modal
  const deleteSingleItem = async (itemId) => {
    Alert.alert(
      'Delete Item',
      'Are you sure you want to delete this item?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await wardrobeAPI.deleteItem(itemId);
              setItemModalVisible(false);
              await loadWardrobeItems();
              Alert.alert('Success', 'Item deleted');
            } catch (error) {
              console.error('Delete error:', error);
              Alert.alert('Error', 'Failed to delete item');
            }
          },
        },
      ]
    );
  };

  // Delete single outfit from modal
  const deleteSingleOutfit = async (outfitId) => {
    Alert.alert(
      'Delete Outfit',
      'Are you sure you want to delete this outfit?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await outfitAPI.deleteOutfit(outfitId);
              setOutfitModalVisible(false);
              await loadSavedOutfits();
              Alert.alert('Success', 'Outfit deleted');
            } catch (error) {
              console.error('Delete error:', error);
              Alert.alert('Error', 'Failed to delete outfit');
            }
          },
        },
      ]
    );
  };

  // Rename outfit
  const renameOutfit = async () => {
    if (!outfitNewName.trim()) {
      Alert.alert('Error', 'Please enter a valid name');
      return;
    }
    
    try {
      setIsRenaming(true);
      await outfitAPI.renameOutfit(selectedOutfit.id, outfitNewName.trim());
      
      // Update local state
      setSavedOutfits(prev => 
        prev.map(outfit => 
          outfit.id === selectedOutfit.id 
            ? { ...outfit, name: outfitNewName.trim() }
            : outfit
        )
      );
      
      setSelectedOutfit(prev => ({ ...prev, name: outfitNewName.trim() }));
      Alert.alert('Success', 'Outfit renamed successfully');
    } catch (error) {
      console.error('Rename error:', error);
      Alert.alert('Error', 'Failed to rename outfit');
    } finally {
      setIsRenaming(false);
    }
  };

  const requestPermissions = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant permission to access your photos');
      return false;
    }
    return true;
  };

  const pickImage = async () => {
    const hasPermission = await requestPermissions();
    if (!hasPermission) return;

    Alert.alert(
      'Add Clothing Items',
      'Choose how you want to add clothing items',
      [
        { text: 'Take Photo', onPress: () => openCamera() },
        { text: 'Select One Photo', onPress: () => openImagePicker() },
        { text: 'Select Multiple Photos', onPress: () => openMultipleImagePicker() },
        { text: 'Cancel', style: 'cancel' },
      ]
    );
  };

  const openCamera = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Please grant camera permission');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      uploadImage(result.assets[0]);
    }
  };

  const openImagePicker = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      uploadImage(result.assets[0]);
    }
  };

  const openMultipleImagePicker = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultipleSelection: true,
      quality: 0.8,
      selectionLimit: 10, // Limit to 10 images at once
    });

    if (!result.canceled && result.assets) {
      uploadMultipleImages(result.assets);
    }
  };

  const uploadImage = async (imageAsset) => {
    try {
      setIsUploading(true);

      const formData = new FormData();
      formData.append('image', {
        uri: imageAsset.uri,
        type: 'image/jpeg',
        name: 'clothing.jpg',
      });

      const response = await wardrobeAPI.uploadClothing(formData);
      
      Alert.alert('Success!', response.data.message);
      await loadWardrobeItems(); // Refresh the wardrobe
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.error || 'Failed to upload image';
      Alert.alert('Upload Failed', errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const uploadMultipleImages = async (imageAssets) => {
    try {
      setIsUploading(true);
      const totalImages = imageAssets.length;
      let successCount = 0;
      let errorCount = 0;

      for (let i = 0; i < imageAssets.length; i++) {
        try {
          const formData = new FormData();
          formData.append('image', {
            uri: imageAssets[i].uri,
            type: 'image/jpeg',
            name: `clothing_${i + 1}.jpg`,
          });

          await wardrobeAPI.uploadClothing(formData);
          successCount++;
        } catch (error) {
          console.error(`Upload error for image ${i + 1}:`, error);
          errorCount++;
        }
      }

      const message = `Uploaded ${successCount} of ${totalImages} images successfully.`;
      if (errorCount > 0) {
        Alert.alert('Upload Complete', `${message}\n${errorCount} uploads failed.`);
      } else {
        Alert.alert('Success!', message);
      }
      
      await loadWardrobeItems(); // Refresh the wardrobe
    } catch (error) {
      console.error('Multiple upload error:', error);
      Alert.alert('Upload Failed', 'Failed to upload multiple images');
    } finally {
      setIsUploading(false);
    }
  };

  // Render category navbar
  const renderCategoryNavbar = () => (
    <ScrollView 
      horizontal 
      showsHorizontalScrollIndicator={false}
      style={styles.categoryNavbar}
      contentContainerStyle={styles.categoryNavbarContent}
    >
      {categories.map((category) => (
        <TouchableOpacity
          key={category}
          style={[
            styles.categoryButton,
            selectedCategory === category && styles.categoryButtonActive
          ]}
          onPress={() => setSelectedCategory(category)}
        >
          <Text style={[
            styles.categoryButtonText,
            selectedCategory === category && styles.categoryButtonTextActive
          ]}>
            {category}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  // Render wardrobe item (simplified - image only)
  const renderWardrobeItem = (item) => {
    const isSelected = selectedItems.includes(item.id);
    
    return (
      <TouchableOpacity
        key={item.id}
        style={[
          styles.wardrobeItemSimple,
          isSelected && styles.wardrobeItemSelected
        ]}
        onPress={() => handleItemPress(item)}
        onLongPress={() => handleItemLongPress(item.id)}
        activeOpacity={0.8}
      >
        <Image
          source={{ uri: `http://${process.env.EXPO_PUBLIC_API_HOST || '192.168.100.228'}:${process.env.EXPO_PUBLIC_API_PORT || '5000'}${item.image_url}` }}
          style={styles.itemImageSimple}
          defaultSource={require('../../assets/icon.png')}
        />
        {selectionMode && (
          <View style={styles.selectionOverlay}>
            <View style={[styles.selectionCircle, isSelected && styles.selectionCircleSelected]}>
              {isSelected && <Ionicons name="checkmark" size={16} color="white" />}
            </View>
          </View>
        )}
      </TouchableOpacity>
    );
  };
  
  // Render outfit item (simplified - image only)
  const renderOutfitItem = (outfit) => {
    const isSelected = selectedOutfits.includes(outfit.id);
    
    // Determine the correct image URI
    let imageUri;
    if (outfit.image_url.startsWith('http')) {
      imageUri = outfit.image_url;
    } else {
      imageUri = `http://${process.env.EXPO_PUBLIC_API_HOST || '192.168.100.228'}:${process.env.EXPO_PUBLIC_API_PORT || '5000'}${outfit.image_url}`;
    }
    
    return (
      <TouchableOpacity
        key={outfit.id}
        style={[
          styles.outfitItemSimple,
          isSelected && styles.outfitItemSelected
        ]}
        onPress={() => handleOutfitPress(outfit)}
        onLongPress={() => handleOutfitLongPress(outfit.id)}
        activeOpacity={0.8}
      >
        <Image
          source={{ uri: imageUri }}
          style={styles.outfitImageSimple}
          defaultSource={require('../../assets/icon.png')}
        />
        <View style={styles.outfitOverlay}>
          <Text style={styles.outfitNameOverlay} numberOfLines={1}>
            {outfit.name}
          </Text>
        </View>
        {selectionMode && (
          <View style={styles.selectionOverlay}>
            <View style={[styles.selectionCircle, isSelected && styles.selectionCircleSelected]}>
              {isSelected && <Ionicons name="checkmark" size={16} color="white" />}
            </View>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  // Item Detail Modal
  const renderItemModal = () => (
    <Modal
      visible={itemModalVisible}
      transparent={true}
      animationType="fade"
      onRequestClose={() => setItemModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalContent}>
            {/* Header */}
            <View style={styles.modalHeader}>
              <TouchableOpacity
                style={styles.modalCloseButton}
                onPress={() => setItemModalVisible(false)}
              >
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.modalDeleteButton}
                onPress={() => selectedItem && deleteSingleItem(selectedItem.id)}
              >
                <Ionicons name="trash-outline" size={20} color="#dc3545" />
              </TouchableOpacity>
            </View>

            {/* Image */}
            {selectedItem && (
              <View style={styles.modalImageContainer}>
                <Image
                  source={{ uri: `http://${process.env.EXPO_PUBLIC_API_HOST || '192.168.100.228'}:${process.env.EXPO_PUBLIC_API_PORT || '5000'}${selectedItem.image_url}` }}
                  style={styles.modalImage}
                  resizeMode="contain"
                />
              </View>
            )}

            {/* Details */}
            {selectedItem && (
              <View style={styles.modalDetails}>
                <Text style={styles.modalTitle}>{selectedItem.type_category}</Text>
                <Text style={styles.modalDate}>
                  Added on {new Date(selectedItem.timestamp).toLocaleDateString()}
                </Text>
                
                {/* Tags */}
                <View style={styles.modalTagsContainer}>
                  <Text style={styles.modalTagsTitle}>Tags:</Text>
                  <View style={styles.modalTagsWrapper}>
                    {selectedItem.tags?.map((tag, index) => (
                      <View key={index} style={styles.modalTag}>
                        <Text style={styles.modalTagText}>{tag}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              </View>
            )}
          </View>
        </SafeAreaView>
      </View>
    </Modal>
  );

  // Outfit Detail Modal
  const renderOutfitModal = () => (
    <Modal
      visible={outfitModalVisible}
      transparent={true}
      animationType="fade"
      onRequestClose={() => setOutfitModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalContent}>
            {/* Header */}
            <View style={styles.modalHeader}>
              <TouchableOpacity
                style={styles.modalCloseButton}
                onPress={() => setOutfitModalVisible(false)}
              >
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.modalDeleteButton}
                onPress={() => selectedOutfit && deleteSingleOutfit(selectedOutfit.id)}
              >
                <Ionicons name="trash-outline" size={20} color="#dc3545" />
              </TouchableOpacity>
            </View>

            {/* Image */}
            {selectedOutfit && (
              <View style={styles.modalImageContainer}>
                <Image
                  source={{ 
                    uri: selectedOutfit.image_url.startsWith('http') 
                      ? selectedOutfit.image_url 
                      : `http://${process.env.EXPO_PUBLIC_API_HOST || '192.168.100.228'}:${process.env.EXPO_PUBLIC_API_PORT || '5000'}${selectedOutfit.image_url}`
                  }}
                  style={styles.modalImage}
                  resizeMode="contain"
                />
              </View>
            )}

            {/* Details */}
            {selectedOutfit && (
              <View style={styles.modalDetails}>
                {/* Editable name */}
                <View style={styles.modalNameContainer}>
                  <TextInput
                    style={styles.modalNameInput}
                    value={outfitNewName}
                    onChangeText={setOutfitNewName}
                    placeholder="Outfit name"
                    onSubmitEditing={renameOutfit}
                  />
                  <TouchableOpacity
                    style={styles.modalRenameButton}
                    onPress={renameOutfit}
                    disabled={isRenaming}
                  >
                    <Ionicons 
                      name={isRenaming ? "hourglass-outline" : "checkmark"} 
                      size={20} 
                      color="#007bff" 
                    />
                  </TouchableOpacity>
                </View>
                
                <Text style={styles.modalDate}>
                  Created on {new Date(selectedOutfit.timestamp).toLocaleDateString()}
                </Text>
              </View>
            )}
          </View>
        </SafeAreaView>
      </View>
    </Modal>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>
          {activeTab === 'clothes' ? 'Loading your wardrobe...' : 'Loading your outfits...'}
        </Text>
      </View>
    );
  }

  const filteredItems = getFilteredItems();
  const hasSelectedItems = activeTab === 'clothes' ? selectedItems.length > 0 : selectedOutfits.length > 0;

  return (
    <View style={styles.container}>
      {/* Selection Mode Header */}
      {selectionMode && (
        <View style={styles.selectionHeader}>
          <TouchableOpacity onPress={exitSelectionMode}>
            <Ionicons name="close" size={24} color="#007bff" />
          </TouchableOpacity>
          <Text style={styles.selectionText}>
            {activeTab === 'clothes' ? selectedItems.length : selectedOutfits.length} selected
          </Text>
          <TouchableOpacity 
            onPress={deleteSelectedItems}
            disabled={!hasSelectedItems}
            style={[styles.deleteButton, !hasSelectedItems && styles.deleteButtonDisabled]}
          >
            <Ionicons name="trash-outline" size={24} color={hasSelectedItems ? "#dc3545" : "#ccc"} />
          </TouchableOpacity>
        </View>
      )}

      {/* Tabs */}
      {!selectionMode && (
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'clothes' && styles.activeTab]}
            onPress={() => setActiveTab('clothes')}
          >
            <Ionicons 
              name="shirt-outline" 
              size={20} 
              color={activeTab === 'clothes' ? '#007bff' : '#666'} 
            />
            <Text style={[styles.tabText, activeTab === 'clothes' && styles.activeTabText]}>
              Clothes
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'outfits' && styles.activeTab]}
            onPress={() => setActiveTab('outfits')}
          >
            <Ionicons 
              name="people-outline" 
              size={20} 
              color={activeTab === 'outfits' ? '#007bff' : '#666'} 
            />
            <Text style={[styles.tabText, activeTab === 'outfits' && styles.activeTabText]}>
              Outfits
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Content based on active tab */}
      {activeTab === 'clothes' ? (
        <View style={styles.contentContainer}>
          {/* Category Navigation */}
          {!selectionMode && renderCategoryNavbar()}

          {/* Wardrobe Items Grid */}
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContentContainer}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
            }
          >
            {filteredItems.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Ionicons name="shirt-outline" size={80} color="#ccc" />
                <Text style={styles.emptyTitle}>
                  {selectedCategory === 'All' ? 'Your wardrobe is empty' : `No ${selectedCategory.toLowerCase()} found`}
                </Text>
                <Text style={styles.emptySubtitle}>
                  {selectedCategory === 'All' 
                    ? 'Tap "Add New Items" to start building your digital wardrobe!' 
                    : `Try selecting a different category or add some ${selectedCategory.toLowerCase()}`
                  }
                </Text>
              </View>
            ) : (
              <View style={styles.itemsGridSimple}>
                {filteredItems.map(renderWardrobeItem)}
              </View>
            )}
          </ScrollView>

          {/* Upload Button - Moved to Bottom */}
          {!selectionMode && (
            <View style={styles.bottomButtonContainer}>
              <TouchableOpacity
                style={[styles.uploadButton, isUploading && styles.uploadButtonDisabled]}
                onPress={pickImage}
                disabled={isUploading}
              >
                <Ionicons 
                  name={isUploading ? "hourglass-outline" : "add-outline"} 
                  size={24} 
                  color="white" 
                />
                <Text style={styles.uploadButtonText}>
                  {isUploading ? 'Uploading...' : 'Add New Items'}
                </Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      ) : (
        /* Saved Outfits Tab */
        <ScrollView
          style={styles.scrollView}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {savedOutfits.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="people-outline" size={80} color="#ccc" />
              <Text style={styles.emptyTitle}>No saved outfits</Text>
              <Text style={styles.emptySubtitle}>
                Generate an outfit and save it to see it here!
              </Text>
            </View>
          ) : (
            <View style={styles.outfitsGridSimple}>
              {savedOutfits.map(renderOutfitItem)}
            </View>
          )}
        </ScrollView>
      )}

      {/* Modals */}
      {renderItemModal()}
      {renderOutfitModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  
  // Selection Mode
  selectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#f0f8ff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  selectionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007bff',
  },
  deleteButton: {
    padding: 5,
  },
  deleteButtonDisabled: {
    opacity: 0.3,
  },

  // Tabs
  tabContainer: {
    flexDirection: 'row',
    marginVertical: 10,
    marginHorizontal: 15,
    backgroundColor: '#e9ecef',
    borderRadius: 10,
    overflow: 'hidden',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
  },
  activeTab: {
    backgroundColor: '#fff',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  tabText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
    marginLeft: 5,
  },
  activeTabText: {
    color: '#007bff',
    fontWeight: '600',
  },

  // Category Navigation
  categoryNavbar: {
    maxHeight: 50,
    marginHorizontal: 15,
    marginBottom: 10,
  },
  categoryNavbarContent: {
    paddingHorizontal: 5,
    alignItems: 'center',
  },
  categoryButton: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    marginRight: 8,
    backgroundColor: '#e9ecef',
    borderRadius: 16,
    minHeight: 32,
    justifyContent: 'center',
  },
  categoryButtonActive: {
    backgroundColor: '#007bff',
  },
  categoryButtonText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#666',
  },
  categoryButtonTextActive: {
    color: 'white',
  },

  // Buttons
  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#007bff',
    padding: 18,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 6,
  },
  uploadButtonDisabled: {
    backgroundColor: '#ccc',
  },
  uploadButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },

  // Content
  contentContainer: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContentContainer: {
    paddingBottom: 100, // Add padding to prevent overlap with the button
  },
  bottomButtonContainer: {
    position: 'absolute',
    bottom: 65, // Moved down a few pixels to reduce gap with navbar
    left: 0,
    right: 0,
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    paddingHorizontal: 40,
  },
  contentContainer: {
    flex: 1,
    justifyContent: 'space-between',
  },
  scrollContentContainer: {
    paddingBottom: 80, // Add padding to prevent overlap with the button
  },

  // Simplified Item Grids
  itemsGridSimple: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    padding: 15,
  },
  wardrobeItemSimple: {
    width: (width - 45) / 2, // 2 columns with margins
    height: 150,
    marginBottom: 15,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  wardrobeItemSelected: {
    borderWidth: 3,
    borderColor: '#007bff',
  },
  itemImageSimple: {
    width: '100%',
    height: '100%',
    backgroundColor: '#f0f0f0',
  },

  outfitsGridSimple: {
    padding: 15,
  },
  outfitItemSimple: {
    height: 200,
    marginBottom: 15,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  outfitItemSelected: {
    borderWidth: 3,
    borderColor: '#007bff',
  },
  outfitImageSimple: {
    width: '100%',
    height: '100%',
    backgroundColor: '#f0f0f0',
  },
  outfitOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  outfitNameOverlay: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },

  // Selection overlay
  selectionOverlay: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  selectionCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'white',
    backgroundColor: 'rgba(255,255,255,0.3)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  selectionCircleSelected: {
    backgroundColor: '#007bff',
    borderColor: '#007bff',
  },

  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    flex: 1,
    width: '100%',
  },
  modalContent: {
    flex: 1,
    backgroundColor: 'white',
    marginTop: 50,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  modalCloseButton: {
    padding: 5,
  },
  modalDeleteButton: {
    padding: 5,
  },
  modalImageContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
  },
  modalImage: {
    width: '90%',
    height: '90%',
    maxHeight: 400,
  },
  modalDetails: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
    textTransform: 'capitalize',
  },
  modalDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  modalTagsContainer: {
    marginTop: 10,
  },
  modalTagsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  modalTagsWrapper: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  modalTag: {
    backgroundColor: '#e9ecef',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  modalTagText: {
    fontSize: 14,
    color: '#666',
  },

  // Outfit Modal Specific
  modalNameContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  modalNameInput: {
    flex: 1,
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
    paddingBottom: 5,
    marginRight: 10,
  },
  modalRenameButton: {
    padding: 5,
  },
});

export default WardrobeScreen;