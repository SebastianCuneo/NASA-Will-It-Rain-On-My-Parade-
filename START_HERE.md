# 🚀 The Parade Planner - Quick Start Guide

## NASA Space Apps Challenge - Frontend/Backend Architecture

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

1. **Modern React Interface** with dark/light mode toggle
2. **Animated Background** with floating clouds
3. **Weather Risk Form** with location and month inputs
4. **Real-time Risk Assessment** from FastAPI backend
5. **Beautiful Results Display** with color-coded risk levels

### 📱 Features

- **Responsive Design**: Works on mobile, tablet, and desktop
- **Dark/Light Mode**: Toggle between themes
- **Real-time API**: Live weather risk calculation
- **Form Validation**: Input validation with error handling
- **Loading States**: User feedback during processing
- **Risk Visualization**: Temperature and precipitation risk assessment

### 🔧 Development URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 🏗️ Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ Data (CSV)
     ↓                    ↓
  User Interface    Risk Calculation
  Form Handling     API Endpoints
  Results Display   Data Processing
```

### 🎨 Design Features

- **NASA Color Scheme**: Blue, Red, Green
- **Smooth Animations**: Fade-in effects and floating clouds
- **Tailwind CSS**: Modern utility-first styling
- **Mobile-First**: Responsive design approach

### 📊 Data Flow

1. User enters location and month
2. Frontend sends POST request to `/api/risk`
3. Backend calculates temperature and precipitation risk
4. Results displayed with risk levels and recommendations

### 🚀 Ready for Phase 2!

This architecture is designed for easy extension:
- Modular React components
- RESTful API endpoints
- Scalable data processing
- Ready for real-time NASA data integration

---

**Built with ❤️ for NASA Space Apps Challenge 2024**
