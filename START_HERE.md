# 🚀 NASA Weather Risk Navigator - Quick Start Guide

## NASA Space Apps Challenge - Modern Web Application

### 📋 Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

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

### 🐛 Troubleshooting

**Common Issues:**

1. **Port already in use:**
   ```bash
   # Kill process on port 3000
   npx kill-port 3000
   
   # Kill process on port 8000
   npx kill-port 8000
   ```

2. **Python dependencies not found:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **Node modules issues:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **API connection issues:**
   - Ensure backend is running on port 8000
   - Check that both terminals are running
   - Verify proxy settings in `frontend/package.json`

### 📊 Testing the Setup

**Test Backend API:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "NASA Weather Risk Navigator API"}
```

**Test Frontend:**
- Open http://localhost:3000
- Fill out the form
- Submit and verify results appear

### 🏗️ Modern Architecture

```
React Frontend (Port 3000) ←→ FastAPI Backend (Port 8000) ←→ Mock Data (CSV)
         ↓                           ↓
    User Interface              Risk Calculation
    Form Management             API Endpoints
    Results Display             Data Processing
    Responsive Design           Error Handling
    Dark/Light Mode            Mock Data Validation
    Plan B Suggestions         Scientific Methodology
```

### 📊 Data Architecture
- **Mock Data**: 5 years of simulated weather data (2020-2024)
- **Variables**: Temperature and precipitation for Montevideo region
- **Methodology**: 90th percentile risk assessment
- **Purpose**: MVP demonstration with scientifically valid approach

### 🎨 Advanced Design Features

- **NASA Color Scheme**: Blue (#0B3D91), Red (#FC3D21), Green (#34D399)
- **Smooth Animations**: Fade-in effects, cloud drift, star movement
- **Glassmorphism**: Modern backdrop blur with transparency
- **Responsive Breakpoints**: Mobile-first with desktop enhancements
- **Dark/Light Theme**: Automatic switching based on time of day

### 📊 Enhanced Data Flow

1. **User Input**: Location, date, weather conditions, activity selection
2. **Form Validation**: Real-time validation with error messages
3. **API Request**: POST to `/api/risk` with user data
4. **Risk Calculation**: Temperature and precipitation analysis
5. **Activity Analysis**: Compatibility checking with Plan B suggestions
6. **Results Display**: Comprehensive risk assessment with visualizations

### 🌟 Key Features

- **Multi-step Form**: Intuitive 4-step process (Location → Date → Conditions → Activity)
- **Activity Compatibility**: Smart analysis with automatic Plan B suggestions
- **Historical Context**: Past vs. present risk comparison showing climate change
- **Visual Risk Indicators**: Color-coded risk levels (HIGH/MODERATE/LOW/MINIMAL)
- **Plan B Intelligence**: AI-powered alternative activity suggestions
- **Responsive Design**: Perfect on all devices with desktop enhancements
- **Theme Persistence**: Remembers user's theme preference
- **Mock Data Validation**: Proven methodology ready for real NASA datasets
- **Educational Impact**: Climate science made accessible and engaging

### 🚀 Ready for Phase 2!

This modern architecture is designed for easy extension:
- **Modular React Components**: Reusable and maintainable
- **RESTful API Design**: Scalable backend architecture
- **Responsive UI Framework**: Ready for any screen size
- **Real-time Data Integration**: Prepared for NASA API connections
- **Advanced Analytics**: Foundation for ML and AI integration

---

**Built with ❤️ for NASA Space Apps Challenge 2024**
