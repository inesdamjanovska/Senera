# Senera


Senera is a web-based app that helps users generate stylish outfits using their own clothes. Users upload images of clothing items they own (or want to buy), and the system stores, tags, and organizes them. Later, based on prompts like occasion, weather, or style, the app intelligently selects relevant clothing items and generates a virtual outfit image using OpenAI's image API.

🧰 Tech Stack
🐍 Backend: Python + Flask

📦 Database: MySQL with SQLAlchemy ORM

🧠 AI: OpenAI API (image generation & text prompting)

🧼 Image Processing: rembg for background removal, Pillow for image manipulation

🌐 Frontend: React with Tailwind CSS

📡 API Calls: Axios

🔐 Auth: Basic login (optional Google OAuth for future)

🖼️ Deployment (optional): Cloudinary or local static folder for image storage

🧱 How It Works
Users upload images of their clothing. The app removes the background (PNG) and tags them (category, color, season, etc.).

The images are stored in the backend with metadata in a MySQL database.

When the user requests an outfit (e.g., “Casual outfit for warm weather”), the backend:

Filters the wardrobe based on tags and prompt context

Generates a collage image from selected clothing

Sends this image + prompt to OpenAI’s image generation API

The resulting outfit image is returned and displayed in the frontend. Development Flow (Inside-Out Approach)
✅ Set up and test OpenAI API call using a premade collage image and a prompt

🔧 Backend:

Setup Flask entry point and test route

Add clothing upload + tag routes

Implement metadata search logic

Build outfit generation pipeline

🧪 Frontend:

Build upload + gallery UI

Create form to select occasion, weather, etc.

Show loading + AI outfit result image

🌐 Connect frontend to backend via Axios API

🔐 Add basic auth (optional: Google OAuth later)

📦 Store image uploads (local or Cloudinary)

📱 Ensure mobile-friendly design (no native app needed)

🧪 Testing
Test OpenAI API calls in isolation first (pass prompt + collage manually)

Unit test image-processing functions

Ensure backend filters clothing correctly

Simulate a full outfit flow using dummy data

📝 Example Prompts
“Cute spring outfit for a sunny picnic”

“Minimalist winter work outfit with black pants”

“Edgy streetwear with white sneakers”
