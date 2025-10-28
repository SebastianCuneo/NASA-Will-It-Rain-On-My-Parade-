
# 🚀 NASA Weather Risk Navigator - Quick Start Guide

## NASA Space Apps Challenge - Modern Web Application

### 📋 Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn
- (Optional) Gemini AI API key from https://makersuite.google.com/app/apikey

### ⚡ Quick Start (5 Steps)

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd NASA-Will-It-Rain-On-My-Parade-
```

#### 2. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### 3.5. Configure Gemini AI (Optional)
For AI-powered Plan B suggestions:

```bash
# Copy the template
cp config_example.env .env

# Edit .env and add your Gemini API key
# Get your API key from: https://makersuite.google.com/app/apikey
# GEMINI_API_KEY=your_api_key_here
```

**Note:** Without API key, the system uses fallback alternatives (predefined activities).

#### 4. Start Backend Server
```bash
cd backend
python -m uvicorn api:app --reload --port 8000
```
**Backend will be available at:** http://localhost:8000

#### 5. Start Frontend Application
```bash
cd frontend
npm start
```
**Frontend will be available at:** http://localhost:3000

### 🚀 Complete Command Sequence
Copy and paste this complete sequence:

```bash
# 1. Clone repository
git clone <repository-url>
cd NASA-Will-It-Rain-On-My-Parade-

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Node.js dependencies
cd frontend
npm install
cd ..

# 4. Start backend (Terminal 1)
cd backend
python -m uvicorn api:app --reload --port 8000

# 5. Start frontend (Terminal 2)
cd frontend
npm start
```

### 🎯 What You'll See

1. **Modern Web Interface** with responsive desktop/mobile design
2. **Dark/Light Mode Toggle** with smooth transitions
3. **Animated Backgrounds** - Floating clouds (day) / Starry sky (night)
4. **Multi-step Weather Form** with location, date, and condition selection
5. **Real-time Risk Assessment** with activity compatibility analysis
6. **Plan B Suggestions** for incompatible weather conditions

### 🖥️ Desktop Experience

- **2-Column Layout**: Form on left, results on right
- **Glassmorphism Effects**: Modern backdrop blur styling
- **Enhanced Hover Effects**: Smooth animations and interactions
- **Larger Touch Targets**: Optimized for desktop use
- **Better Typography**: Improved readability and spacing

### 📱 Mobile Experience

- **Single Column Layout**: Optimized for mobile screens
- **Touch-Friendly**: Large buttons and easy selection
- **Responsive Grid**: Adapts to different screen sizes
- **Smooth Scrolling**: Optimized performance on mobile devices

### 🔧 Development URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 🔑 Environment Variables

**Important Security Note:**
- The `.env` file contains your personal API keys
- It's already in `.gitignore` (not tracked by Git)
- **Never commit `.env` to GitHub**
- Each developer should create their own `.env` with their own API key

**For Your Team:**
1. Clone the repository
2. Copy `config_example.env` to `.env`
3. Add your own Gemini API key from https://makersuite.google.com/app/apikey
4. Start the backend

**What's Public on GitHub:**
- `config_example.env` (template without real API key)
- All code and documentation
- **NOT your personal API keys**


