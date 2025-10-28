# 🌍 NASA Weather Risk Navigator

**NASA Space Apps Challenge** - Will It Rain On My Parade?

An intelligent weather risk assessment platform that democratizes climate science through NASA-powered historical analysis and AI-driven alternatives.

## 🎯 Project Overview

NASA Weather Risk Navigator is a functional prototype developed for the NASA Space Apps Challenge Post-Hackathon. This solution addresses long-term event planning uncertainty by leveraging NASA POWER API's 20-year historical climate data to assess the probability of adverse conditions like extreme heat, heavy precipitation, or extreme cold.

### Key Features

- **🌡️ Unified Risk Methodology**: Fixed thresholds (30°C heat, 10°C cold, 5mm precipitation) with P90/P10 as scientific reference
- **📊 Climate Trend Analysis**: First 5 years vs. last 5 years comparison
- **🤖 AI-Powered Plan B**: Google Gemini generates contextual compatible activities based on weather and location
- **🌍 Global Coverage**: Uses NASA POWER API for any location worldwide
- **📱 Responsive Design**: Beautiful UI with day/night modes
- **🔬 Scientific Rigor**: Transparent methodology with detailed risk calculations

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- (Optional) Gemini API key for AI features

### Installation

```bash
# 1. Clone repository
git clone https://github.com/SebastianCuneo/NASA-Will-It-Rain-On-My-Parade-
cd NASA-Will-It-Rain-On-My-Parade-

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Configure Environment Variables (Optional)

For AI-powered Plan B suggestions:

```bash
# Create .env file from template
copy config_example.env .env

# Edit .env and add your Gemini API key
# Get your free key at: https://makersuite.google.com/app/apikey
```

### Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Access:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

## 📊 Scientific Methodology

### Risk Calculation

The prototype implements a **unified methodology** that separates probability calculation from extreme event reference:

#### Fixed Thresholds for Probability
- **Heat Risk**: >30°C (significant heat discomfort)
- **Cold Risk**: <10°C (significant cold discomfort)  
- **Precipitation Risk**: >5mm (significant rainfall)

These fixed thresholds ensure probabilities vary meaningfully across different climate zones.

#### P90/P10 as Scientific Reference
- **P90** defines what constitutes "extreme heat" or "extreme precipitation" for each specific location
- **P10** defines what constitutes "extreme cold" for each specific location

This approach avoids the mathematical pitfall where using percentiles directly for probability would always yield ~10%.

### Climate Change Trend Analysis

**Methodology:** 
- Compares average daily temperature (T2M) from **first 5 years** vs **last 5 years** of 20-year dataset
- Filters data by the target month for seasonal accuracy
- **Classification:**
  - **SIGNIFICANT_WARMING**: +1.0°C or more (IPCC threshold exceeded)
  - **WARMING_TREND**: +0.5°C to +1.0°C (statistically detectable)
  - **STABLE**: Less than +0.5°C (natural variability)
  - **COOLING_TREND**: -0.5°C or more (detectable cooling)

This analysis fulfills the educational objective of demonstrating climate change through local, tangible data.

## 🏗️ Architecture

```
### System Architecture Flow

```
User Input → Frontend (React) → API Request → FastAPI Backend → NASA POWER API
                                                              → Gemini AI
                                                              → Risk Analysis
                        ← JSON Response ←                      ← Scientific Calculations
```

### Project Structure

```
├── backend/                    # FastAPI backend
│   ├── api.py                  # Main API endpoint /api/risk
│   ├── logic.py                # Core scientific calculations
│   ├── inumet_montevideo_data.csv  # Fallback data
│   ├── tests/                  # Comprehensive test suite
│   └── requirements.txt
│
├── frontend/                   # React frontend  
│   ├── src/
│   │   ├── components/
│   │   │   ├── WeatherForm.jsx
│   │   │   ├── WeatherResults.jsx
│   │   │   └── MapSelector.jsx
│   │   ├── hooks/
│   │   │   ├── useWeatherAPI.js
│   │   │   └── useTheme.js
│   │   └── App.js
│   └── package.json
│
└── config_example.env          # Environment variables
```

### Technology Stack

**Backend Technologies:**
- **FastAPI** - Modern Python web framework with async support
- **Pandas & NumPy** - Scientific data processing and statistics
- **Google Gemini AI** - Intelligent Plan B generation
- **NASA POWER API** - Global historical climate data (20 years)
- **Python 3.10+** - Core programming language

**Frontend Technologies:**
- **React 18** - Component-based UI framework
- **Tailwind CSS** - Utility-first styling
- **Leaflet** - Interactive maps with React-Leaflet
- **React Hooks** - State and API management
- **CSS3** - Custom animations and theming

**Data Sources:**
- **NASA POWER API** - Primary global climate data source
- **Fallback CSV** - Montevideo historical data (when API unavailable)

**Development & Deployment:**
- **Git** - Version control
- **Uvicorn** - ASGI server for production
- **NPM** - Package management

## 📈 Prototype Scope & Justification

This prototype validates the **core scientific concept** and **technical architecture**. Key decisions:

| Feature | Implementation | Justification |
|---------|---------------|---------------|
| **Global Data Source** | NASA POWER API integration | Validates technical viability and global scalability |
| **Scientific Core** | P90/P10 methodology with fixed thresholds | Validates mathematical approach |
| **Climate Analysis** | First 5 vs last 5 years comparison | Fulfills educational objective |
| **AI Integration** | Google Gemini for Plan B | Adds innovation and practical value |
| **Architecture** | FastAPI + React | Modern, modular, scalable |
| **UI/UX** | Responsive design with maps, day/night modes | Makes climate data accessible to everyone |

## 🎯 How It Works

### User Flow

1. **Select Location**: Click on world map or use geolocation
2. **Choose Date**: Pick future date (up to 1 year ahead)
3. **Select Condition**: Heat, Cold, or Precipitation
4. **Get Analysis**: Receive probability, risk level, and climate trend
5. **Plan B Suggestions**: AI-generated compatible activities with alternatives

### API Endpoint

**POST /api/risk**

```json
{
  "latitude": -34.90,
  "longitude": -56.16,
  "event_date": "2026-12-15",
  "adverse_condition": "hot"
}
```

**Response:**
```json
{
  "risk_analysis": {
    "probability": 25.8,
    "risk_level": "MODERATE",
    "risk_threshold": 30.0,
    "adverse_count": 8,
    "total_observations": 31
  },
  "climate_trend": "WARMING TREND: +0.7°C over 20 years",
  "climate_trend_details": {
    "trend_status": "WARMING_TREND",
    "difference": 0.7,
    "early_years": [2005, 2006, 2007, 2008, 2009],
    "recent_years": [2020, 2021, 2022, 2023, 2024]
  },
  "plan_b": {
    "success": true,
    "alternatives": [
      {"title": "Indoor Museums", "type": "indoor", ...}
    ],
    "ai_model": "Gemini 2.0 Flash"
  }
}
```

## 🧪 Testing

```bash
# Run all backend tests
cd backend
python -m pytest tests/

# Test specific components
python tests/test_nasa_power_api.py
python tests/test_climate_trend.py
python tests/test_calculate_weather_risk.py
python tests/test_api_endpoint.py
```

## 🔧 Configuration

### Gemini AI Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Get your free API key
3. Create `.env` file in project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
4. The system gracefully falls back to generic suggestions if Gemini is unavailable

### NASA API Configuration

The system automatically uses NASA POWER API for global locations. Fallback data (Montevideo, Uruguay) is used if the API is unavailable.

## 📚 Next Steps & Future Enhancements

### Planned Features

- **Machine Learning Predictions**: Prophet model for 7 days to 1 year ahead
- **Enhanced Climate Analysis**: Comparison with pre-industrial baseline temperatures
- **Additional Variables**: Wind speed and UV radiation analysis
- **Accessibility**: Voice interface and high-contrast mode
- **Advanced NASA Datasets**: MERRA-2, GPM integration
- **Economic Extensions**: Tourism demand forecasting

## 🏆 Team & Credits
**Team ucuwaeather**
Developed for **NASA Space Apps Challenge Post-Hackathon** by:
- Sebastian Cuneo
- Candela Mangino
- Avril Viega

## 📄 License

Developed for NASA Space Apps Challenge 2024 - Educational and Research Purposes

---

**Built with ❤️ for Earth Science** | **NASA Space Apps Challenge 2025**

**Democratizing Climate Science Through Technology**
