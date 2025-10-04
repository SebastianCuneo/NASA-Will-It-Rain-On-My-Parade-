# 🚀 NASA Weather Risk Navigator - Quick Start Guide

## NASA Space Apps Challenge - Modern Web Application

### 📋 Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### ⚡ Quick Start (3 Steps)

#### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Start Backend Server
```bash
cd backend
python -m uvicorn api:app --reload
```
**Backend will be available at:** http://localhost:8000

#### 3. Start Frontend Application
```bash
cd frontend
npm install
npm start
```
**Frontend will be available at:** http://localhost:3000

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

### 🏗️ Modern Architecture

```
React Frontend (Port 3000) ←→ FastAPI Backend (Port 8000) ←→ Mock Data (CSV)
         ↓                           ↓
    User Interface              Risk Calculation
    Form Management             API Endpoints
    Results Display             Data Processing
    Responsive Design           Error Handling
```

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

- **Multi-step Form**: Intuitive 4-step process
- **Activity Compatibility**: Smart analysis with alternative suggestions
- **Historical Context**: Past vs. present risk comparison
- **Visual Risk Indicators**: Color-coded risk levels
- **Plan B Intelligence**: Automatic alternative activity suggestions
- **Responsive Design**: Perfect on all devices
- **Theme Persistence**: Remembers user's theme preference

### 🚀 Ready for Phase 2!

This modern architecture is designed for easy extension:
- **Modular React Components**: Reusable and maintainable
- **RESTful API Design**: Scalable backend architecture
- **Responsive UI Framework**: Ready for any screen size
- **Real-time Data Integration**: Prepared for NASA API connections
- **Advanced Analytics**: Foundation for ML and AI integration

---

**Built with ❤️ for NASA Space Apps Challenge 2024**
