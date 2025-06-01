-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Type Categories table
CREATE TABLE type_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- e.g., "tops", "bottoms", "footwear", "jewelry", "accessories"
);

-- Tags table
CREATE TABLE tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- Tag name (e.g., "shirt", "blue", "summer")
    category ENUM('type', 'color', 'season', 'style', 'occasion') NOT NULL,
    type_category_id INT, -- Foreign key for type categories (only applicable for 'type' tags)
    FOREIGN KEY (type_category_id) REFERENCES type_categories(id) ON DELETE SET NULL
);

-- Wardrobe Items table
CREATE TABLE wardrobe_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL, -- Path or URL to the uploaded image
    type VARCHAR(50) NOT NULL, -- Broad category (e.g., "shirt", "pants")
    subtype VARCHAR(50), -- More specific category (e.g., "t-shirt", "jeans")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Join table for wardrobe items and tags
CREATE TABLE wardrobe_item_tags (
    wardrobe_item_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (wardrobe_item_id, tag_id),
    FOREIGN KEY (wardrobe_item_id) REFERENCES wardrobe_items(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);