# 🌤️ NASA Weather Risk Navigator - NASA Space Apps Challenge

**Will It Rain On My Parade?** - Modern weather risk assessment platform for outdoor event planning.

## 🚀 Project Overview

NASA Weather Risk Navigator is a comprehensive weather risk assessment platform that combines historical data analysis with modern web technologies. Built with a responsive React frontend and FastAPI backend, it provides intelligent weather risk assessment with activity compatibility analysis and Plan B suggestions.

### 🎯 Key Features

- **Modern Web Interface**: Responsive React application with desktop/mobile optimization
- **Intelligent Risk Analysis**: Multi-variable weather risk assessment
- **Activity Compatibility**: Smart analysis with automatic Plan B suggestions
- **Dark/Light Mode**: Beautiful theme switching with animated backgrounds
- **Real-time API**: FastAPI backend with comprehensive weather calculations
- **Historical Context**: Past vs. present risk comparison with visualizations

## 📁 Project Structure

```
NASA-Will-It-Rain-On-My-Parade-/
├── frontend/                    # React Application
│   ├── src/
│   │   ├── components/          # React Components
│   │   │   ├── WeatherForm.jsx  # Multi-step form component
│   │   │   └── WeatherResults.jsx # Results display component
│   │   ├── App.js              # Main application component
│   │   ├── App.css             # Styles and animations
│   │   └── index.js            # React entry point
│   ├── public/
│   │   └── index.html          # HTML template
│   ├── backup/
│   │   └── index-original.html # Original HTML design
│   └── package.json            # Frontend dependencies
├── backend/
│   └── api.py                  # FastAPI backend server
├── app.py                      # Original Streamlit MVP (legacy)
├── logic.py                    # Core business logic (REUSABLE MODULE)
├── mock_data.csv              # Historical weather data
├── requirements.txt           # Backend dependencies
├── START_HERE.md             # Quick start guide
└── README.md                 # Project documentation
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NASA-Will-It-Rain-On-My-Parade-
   ```

2. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Start the application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python -m uvicorn api:app --reload
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

5. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

### Alternative: Legacy Streamlit Version
```bash
streamlit run app.py
# Access at: http://localhost:8501
```

## 📊 Technical Architecture

### Frontend (React)
- **Modern UI Components**: Modular, reusable React components
- **Responsive Design**: Mobile-first with desktop enhancements
- **State Management**: React hooks for form and theme management
- **API Integration**: Axios for backend communication
- **Animations**: CSS animations for clouds, stars, and transitions

### Backend (FastAPI)
- **RESTful API**: Clean, documented endpoints
- **Risk Calculation Engine**: Core business logic from `logic.py`
- **Data Processing**: CSV data handling and analysis
- **CORS Support**: Frontend-backend communication
- **Error Handling**: Comprehensive error responses

### Core Components

#### `frontend/src/components/WeatherForm.jsx`
- **Multi-step Form**: Location, date, conditions, activities
- **Interactive Selection**: Visual condition and activity pickers
- **Form Validation**: Real-time input validation
- **Responsive Layout**: Adapts to screen size

#### `frontend/src/components/WeatherResults.jsx`
- **Risk Display**: Temperature and precipitation analysis
- **Activity Analysis**: Compatibility checking with Plan B
- **Historical Visualization**: Past vs. present comparison
- **Interactive Elements**: Expandable sections and charts

#### `backend/api.py` - FastAPI Server
- **POST /api/risk**: Main risk assessment endpoint
- **GET /health**: Health check endpoint
- **GET /docs**: Automatic API documentation
- **Error Handling**: Comprehensive error responses

#### `logic.py` - REUSABLE MODULE
- `load_historical_data()`: Data loading with error handling
- `calculate_adverse_probability()`: Risk calculation engine
- **Multi-variable Support**: Temperature and precipitation analysis

#### `mock_data.csv` - Historical Data
- **5 years** of simulated data (2020-2024)
- **4 months** coverage (January-April)
- **Dual Variables**: Temperature and precipitation data
- **Montevideo Focus**: Realistic data for Uruguay region

## 🔬 Methodology

### Risk Assessment Algorithm
1. **Data Loading**: Filter historical data by target month
2. **Threshold Calculation**: Compute 90th percentile for temperature and precipitation
3. **Probability Analysis**: Calculate percentage of years exceeding threshold
4. **Risk Classification**: 
   - HIGH (≥20%): 🚨 Extreme risk - Consider alternative dates
   - MODERATE (10-19%): ⚠️ Monitor conditions closely
   - LOW (5-9%): 🌤️ Generally favorable conditions
   - MINIMAL (<5%): ☀️ Excellent weather expected

### Activity Compatibility Analysis
- **Weather-Activity Matching**: Smart analysis of weather conditions vs. planned activities
- **Plan B Generation**: Automatic alternative suggestions for incompatible conditions
- **Risk Mitigation**: Proactive recommendations for weather challenges

### Enhanced Visualizations
- **Responsive Charts**: Temperature and precipitation distributions
- **Historical Comparison**: Past vs. present risk trends
- **Interactive Elements**: Hover effects and expandable sections
- **Risk Indicators**: Color-coded visual risk assessment

## 🎓 Educational Value

### Modern Web Development
- **React Architecture**: Component-based UI development
- **API Design**: RESTful backend development with FastAPI
- **Responsive Design**: Mobile-first development principles
- **User Experience**: Intuitive interface design

### Climate Science Education
- **MERRA-2 Methodology**: Atmospheric reanalysis techniques
- **Risk Communication**: Translating data into actionable insights
- **Statistical Analysis**: Understanding climate data patterns
- **Event Planning**: Scientific approach to weather risk

### Learning Outcomes
- Modern web application development
- API integration and data flow
- Responsive design implementation
- Climate data analysis and visualization
- User interface design principles

## 🔄 Phase 2 Integration Ready

### Modern Architecture Benefits
- **Scalable Frontend**: React components ready for expansion
- **API-First Backend**: RESTful design for easy integration
- **Responsive Framework**: Works on any device or screen size
- **Real-time Ready**: Prepared for live NASA data feeds

### Extension Points
- **Real-time NASA APIs**: Live weather data integration
- **Machine Learning**: AI-powered risk prediction models
- **Geographic Expansion**: Multi-location support
- **Advanced Analytics**: Enhanced data visualization
- **Mobile App**: React Native implementation
- **Social Features**: User accounts and event sharing

## 🌍 NASA Space Apps Context

NASA Weather Risk Navigator addresses the **"Will It Rain On My Parade?"** challenge by:
- **Modern Web Platform**: Professional-grade weather risk assessment
- **Scientific Rigor**: NASA-grade data analysis methodology
- **User-Centric Design**: Intuitive interface for all skill levels
- **Educational Impact**: Making climate science accessible and engaging
- **Real-world Application**: Practical tool for event planning decisions

## 📈 Future Enhancements

### Phase 2 Roadmap
- [x] **Modern Web Interface**: React frontend with responsive design
- [x] **API Architecture**: FastAPI backend with RESTful endpoints
- [x] **Activity Analysis**: Smart compatibility checking with Plan B
- [x] **Multi-device Support**: Desktop and mobile optimization
- [ ] **Real-time NASA APIs**: Live weather data integration
- [ ] **Machine Learning**: AI-powered risk prediction models
- [ ] **Geographic Expansion**: Multi-location support
- [ ] **Advanced Analytics**: Enhanced data visualization

### Technical Improvements
- [ ] **Database Integration**: PostgreSQL for larger datasets
- [ ] **Caching Layer**: Redis for performance optimization
- [ ] **Testing Suite**: Comprehensive unit and integration tests
- [ ] **CI/CD Pipeline**: Automated deployment and testing
- [ ] **Docker Containerization**: Easy deployment and scaling
- [ ] **Performance Monitoring**: Application metrics and logging

## 🚀 Getting Started

For detailed setup instructions, see [START_HERE.md](START_HERE.md)

### Quick Commands
```bash
# Backend
cd backend && python -m uvicorn api:app --reload

# Frontend  
cd frontend && npm start
```

## 🤝 Contributing

This project was developed for the NASA Space Apps Challenge with focus on:
- **Educational Impact**: Making climate science accessible through modern web technologies
- **Practical Application**: Real-world event planning utility with intelligent recommendations
- **Scientific Rigor**: NASA-grade data analysis methodology with user-friendly presentation
- **Modern Architecture**: Scalable foundation for future development and integration

## 📄 License

Developed for NASA Space Apps Challenge 2024 - Educational and Research Purposes

---

**Built with ❤️ for Earth Science** | **NASA Space Apps Challenge 2024**  
**Modern Weather Risk Assessment Platform**
