# 🌤️ NASA Weather Risk Navigator - NASA Space Apps Challenge

**Will It Rain On My Parade?** - Democratizing climate science through intelligent weather risk assessment.

## 🚀 Project Overview

The NASA Weather Risk Navigator is a cutting-edge web application built on a FastAPI (Backend) and React (Frontend) architecture to democratize climate science. It moves beyond standard weather forecasting to assess the historical likelihood of adverse conditions such as extreme heat, heavy precipitation, or strong winds by applying the 90th percentile methodology. For the Hackathon MVP, this methodology is validated using mock climate data to ensure operational stability, with the immediate goal of integrating full NASA MERRA-2 and GPM datasets.

The application provides historical weather risk analysis using a 90th percentile methodology to assess the likelihood of adverse conditions such as extreme heat and heavy precipitation. It offers a probability-based risk assessment system (0-100%) with four risk levels (MINIMAL, LOW, MODERATE, HIGH). Users specify location coordinates and dates to receive activity-specific compatibility analysis with automatic Plan B suggestions. The platform includes educational visualizations showing historical trends and promotes climate literacy through accessible weather science.

### 🎯 Key Features

- **90th Percentile Methodology**: NASA-grade statistical analysis for extreme weather risk assessment
- **Probability-Based Risk System**: 0-100% risk assessment with four levels (MINIMAL, LOW, MODERATE, HIGH)
- **Activity Compatibility Analysis**: Smart weather-activity matching with automatic Plan B suggestions
- **AI-Powered Plan B Generation**: Intelligent alternatives using Google Gemini AI for contextual suggestions
- **Seasonal & Activity-Aware Logic**: Contextual risk assessment based on season and activity type
- **Educational Visualizations**: Climate change impact demonstrations with historical trends
- **Mobile-Responsive Design**: Dynamic day/night theming with smooth animations
- **Real-time API Integration**: FastAPI backend with comprehensive weather calculations
- **Climate Literacy Focus**: Making complex meteorological data accessible to everyone

## 📁 Project Structure

```
NASA-Will-It-Rain-On-My-Parade-/
│
├── backend/                           # Backend Python (FastAPI)
│   ├── api.py                         # API REST con endpoints
│   ├── logic.py                       # Lógica de negocio y cálculos
│   ├── mock_data.csv                  # Datos de fallback
│   ├── requirements.txt               # Dependencias Python
│   └── tests/                         # Tests del backend
│       ├── test_gemini_plan_b.py      # Tests de Gemini AI
│       └── test_verification.py       # Tests de NASA API
│
├── frontend/                          # Frontend React
│   ├── src/
│   │   ├── App.js                     # Componente principal
│   │   ├── App.css                    # Estilos globales
│   │   ├── index.js                   # Entry point React
│   │   ├── components/
│   │   │   ├── WeatherForm.jsx        # Formulario multi-paso
│   │   │   └── WeatherResults.jsx     # Visualización resultados
│   │   ├── context/
│   │   │   └── ThemeContext.jsx       # Sistema de temas
│   │   └── utils/
│   │       └── geocoding.js           # Utilidades
│   ├── public/
│   │   └── index.html                 # HTML base
│   └── package.json                   # Dependencias npm
│
├── scripts/                           # Scripts de desarrollo
│   ├── demo_gemini_plan_b.py          # Demo de IA
│   └── setup_gemini.py                # Setup Gemini API
│
├── config_example.env                 # Ejemplo de configuración
├── requirements.txt                   # Instrucciones instalación
├── README.md                          # Documentación principal
├── ARCHITECTURE.md                    # Arquitectura técnica
└── START_HERE.md                      # Guía de inicio rápido
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Quick Start

#### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd NASA-Will-It-Rain-On-My-Parade-
```

#### Step 2: Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

#### Step 2.5: Configure Gemini AI (Optional)
For AI-powered Plan B generation, you can optionally configure Gemini AI:

**Option A: Automated Setup (Recommended)**
```bash
python scripts/setup_gemini.py
```

**Option B: Manual Setup**
1. **Get a Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your free API key
2. **Set Environment Variable**: 
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   
   # Linux/Mac
   export GEMINI_API_KEY=your_api_key_here
   ```
3. **Copy Configuration Template**:
   ```bash
   copy config_example.env .env
   # Edit .env and add your API key
   ```

**Test Gemini AI Integration:**
```bash
python backend/tests/test_gemini_plan_b.py
```

**Note**: The system works perfectly without Gemini AI using intelligent fallback alternatives.

#### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### Step 4: Start the Application

**Option A: Modern React + FastAPI (Recommended)**

Open **2 terminals** and run:

**Terminal 1 - Backend Server:**
```bash
# Desde el directorio raíz del proyecto:
python -m uvicorn backend.api:app --reload --port 8000

# O desde el directorio backend:
cd backend
python -m uvicorn api:app --reload --port 8000
```

**Terminal 2 - Frontend Server:**
```bash
cd frontend
npm start
```


#### Step 5: Access the Application

**Modern Version (React + FastAPI):**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/health


### 🚀 Complete Command Sequence

Copy and paste this complete sequence to get everything running:

```bash
# 1. Clone repository
git clone <repository-url>
cd NASA-Will-It-Rain-On-My-Parade-

# 2. Install Python dependencies
pip install -r backend/requirements.txt

# 3. Install Node.js dependencies
cd frontend
npm install
cd ..

# 4. Start backend (Terminal 1)
python -m uvicorn backend.api:app --reload --port 8000

# 5. Start frontend (Terminal 2)
cd frontend
npm start
```

### 🔧 Development Commands

**Backend Commands:**
```bash
# Start backend server (desde directorio raíz)
python -m uvicorn backend.api:app --reload --port 8000

# O desde directorio backend
cd backend
python -m uvicorn api:app --reload --port 8000

# Test API endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/risk \
  -H "Content-Type: application/json" \
  -d '{"lat": -34.90, "lon": -56.16, "month": 3}'
```

**Frontend Commands:**
```bash
# Start development server
cd frontend
npm start

# Build for production
npm run build

# Run tests
npm test

# Install new dependencies
npm install <package-name>
```


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
   pip install -r backend/requirements.txt --force-reinstall
   ```

3. **Node modules issues:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **API connection issues:**
   - Ensure backend is running on port 8000
   - Check CORS settings in `backend/api.py`
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

**Test Integration:**
- Frontend should successfully call backend API
- Results should display weather risk analysis
- Plan B suggestions should appear for incompatible activities

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

#### `backend/logic.py` - Core Logic Module
- `load_historical_data()`: NASA POWER API integration
- `calculate_adverse_probability()`: Temperature risk calculation
- `calculate_precipitation_risk()`: Precipitation risk calculation
- `calculate_cold_risk()`: Cold weather risk calculation
- `generate_plan_b_with_gemini()`: AI-powered Plan B generation
- **Multi-variable Support**: Temperature and precipitation analysis

#### `backend/mock_data.csv` - Fallback Data
- **Fallback data** when NASA POWER API is unavailable
- **5 years** of simulated data (2020-2024)
- **4 months** coverage (January-April)
- **Dual Variables**: Temperature and precipitation data
- **Purpose**: Ensure system reliability

## 🔬 Scientific Methodology

### How It Works
The project functions via a modular FastAPI backend handling all scientific processing, including the calculation of the 90th Percentile for adverse conditions and probability-based risk assessment. The backend processes mock historical data to validate the methodology and ensure rapid, stable demo responses. The mobile-responsive React frontend consumes real-time data from the API and presents comprehensive weather risk analysis including temperature and precipitation probabilities, automatic Plan B suggestions, and educational climate change visualizations that demonstrate historical vs. present risk trends.

### Risk Assessment Algorithm
1. **Data Loading**: Filter mock historical data by target month (Montevideo region)
2. **Threshold Calculation**: Compute 90th percentile for temperature and precipitation
3. **Probability Analysis**: Calculate percentage of years exceeding threshold
4. **Risk Classification System**: 
   - **HIGH (≥20%)**: 🚨 Extreme risk - Consider alternative dates
   - **MODERATE (10-19%)**: ⚠️ Monitor conditions closely
   - **LOW (5-9%)**: 🌤️ Generally favorable conditions
   - **MINIMAL (<5%)**: ☀️ Excellent weather expected

### Activity Intelligence System
- **Weather-Activity Matching**: Smart analysis of weather conditions vs. planned activities
- **Plan B Generation**: Automatic alternative suggestions for incompatible conditions
- **Risk Mitigation**: Proactive recommendations for weather challenges
- **Educational Context**: Learning about weather impacts on outdoor activities

## 💡 Benefits & Impact

### What Benefits Does It Have?

- **Risk Reduction**: Enables informed outdoor planning decisions by analyzing historical weather patterns instead of basic forecasts
- **Data Transparency**: Provides complete scientific methodology, including 90th percentile thresholds and calculation details for full auditability
- **Climate Literacy**: Builds environmental awareness through visual demonstrations of how weather risks have evolved over decades
- **Activity Intelligence**: Offers tailored risk assessments for specific outdoor activities with automatic Plan B suggestions
- **AI-Powered Alternatives**: Intelligent Plan B generation using Google Gemini AI for contextual, location-aware suggestions
- **Seasonal Awareness**: Contextual risk assessment that considers Southern Hemisphere seasons and activity-specific thresholds
- **Scientific Accuracy**: Uses percentile-based statistical analysis with real historical data processing for research-quality insights
- **User Experience**: Features responsive design with dynamic day/night theming and smooth animations
- **Educational Value**: Makes complex meteorological data accessible through intuitive visualizations and clear explanations
- **Reliability**: Robust system with graceful fallbacks ensuring continuous functionality even during API issues

### Intended Impact
The broader impact is to democratize climate science and inspire data-driven decision-making. We transform reactive forecasting into proactive planning by applying NASA's scientific methodology (90th Percentile) to historical risk assessment. Our mobile-first design and educational visualizations make complex meteorological analysis available globally, fostering climate literacy and resilience planning in every community.

## 🛠️ Technology Stack

### What Tools, Coding Languages, Hardware, or Software Did You Use?

The project utilizes a modern Frontend/Backend architecture:

**Backend:**
- **Python**: Core programming language
- **FastAPI**: For API robustness and speed
- **Pandas & NumPy**: For statistical analysis and data processing

**Frontend:**
- **JavaScript**: Modern ES6+ features
- **React**: Component-based UI framework
- **HTML/CSS**: Semantic markup and styling
- **Tailwind CSS**: For professional, responsive design

**Data Processing:**
- **Mock Historical Climate Data**: Simulating NASA MERRA-2 datasets with 90th percentile statistical analysis

**Infrastructure:**
- **RESTful API Design**: With CORS support
- **Responsive Web Architecture**: Mobile-first approach
- **Development**: Git version control, modular component design, error handling and graceful fallbacks

## 🎨 Creativity & Innovation

### How Is Your Project Creative?

Creativity lies in transforming weather reporting into proactive risk intelligence through our innovative Historical Risk Assessment methodology. We created a dynamic activity compatibility system that turns weather data into actionable planning by generating "Plan B" suggestions.

Our project shows creativity in communication by integrating educational climate visualizations with real-time risk calculations, making complex meteorological concepts accessible through interactive analysis.

### Key Design Factors Considered

We approached the design and development with three core factors in mind:

1. **Technical Scalability**: We chose a FastAPI (Backend) and React (Frontend) microservices architecture to ensure the product is production-ready, easily handles future feature integration (e.g., Wind Risk), and can efficiently manage high user traffic.

2. **Compliance and Communication**: We maintained strict adherence to the English-only requirement for global eligibility and ensured that our Historical Risk Methodology is communicated through clear, auditable visualizations.

3. **Accessibility and Inclusion (Future-Proofing)**: We designed the UI to support future implementations such as a Voice Interface for users with motor or visual disabilities and a Simplified Mode (high contrast, large fonts) for elderly users, guaranteeing that NASA science remains accessible to all communities.

## 🤖 Use of Artificial Intelligence (AI)

Artificial intelligence was central to establishing our architecture and accelerating development, directly driving the migration from design to a production-ready application:

### Strategic Design & Initial Prototyping (Gemini Canvas)
We used Gemini's Canvas feature to rapidly sketch our mobile-first design and generate the initial HTML/CSS/JavaScript document. This process quickly validated the user experience and provided the necessary blueprint for the frontend.

### Architecture Migration (Cursor)
We utilized Cursor to execute the critical technical leap: turning the Gemini-generated static HTML blueprint into functional, modular React components and developing the required FastAPI endpoints. This ensured we established a scalable, production-ready architecture and successfully met the aggressive delivery timeline of the Hackathon.

### Compliance Note
Gemini was also used for strategic planning, documentation, and ensuring compliance with the official challenge requirements.

## 🌍 NASA Data Integration

### Target NASA Datasets
- **NASA MERRA-2 Reanalysis Data**: Atmospheric reanalysis for historical weather patterns
- **NASA GPM Precipitation Data**: Global precipitation measurements
- **NASA Earthdata Search API**: Comprehensive Earth observation data access
- **NASA POWER**: https://power.larc.nasa.gov/data-access-viewer/

### Additional Data Sources
- **INUMET Uruguay**: https://catalogodatos.gub.uy/dataset/inumet-observaciones-meteorologicas-temperatura-del-aire-en-el-uruguay
- **Precipitation Data**: https://catalogodatos.gub.uy/dataset/inumet-observaciones-meteorologicas-precipitacion-puntual-en-el-uruguay
- **AGESIC Observations**: https://catalogodatos.gub.uy/dataset/agesic-observaciones-meteorologicas

## 🎯 NASA Space Apps Challenge Alignment

NASA Weather Risk Navigator addresses the **"Will It Rain On My Parade?"** challenge by:

### Core Value Proposition
- **Democratizing Climate Science**: Making NASA-grade weather analysis accessible to everyone
- **Scientific Rigor**: 90th percentile methodology based on atmospheric reanalysis principles
- **Practical Application**: Real-world event planning with intelligent recommendations
- **Educational Impact**: Climate change awareness through interactive visualizations

### Technical Innovation
- **Modular Architecture**: Frontend/Backend separation for scalability
- **Mock Data Validation**: Proven methodology ready for real NASA datasets
- **Responsive Design**: Mobile-first with desktop enhancements
- **Theme System**: Dark/Light mode with animated backgrounds
- **API-First Design**: Ready for Phase 2 NASA API integration

## 📈 Future Enhancements

### Phase 2 Roadmap
- [x] **Modern Web Interface**: React frontend with responsive design
- [x] **API Architecture**: FastAPI backend with RESTful endpoints
- [x] **Activity Analysis**: Smart compatibility checking with Plan B
- [x] **Multi-device Support**: Desktop and mobile optimization
- [ ] **Real-time NASA APIs**: Live MERRA-2 and GPM data integration
- [ ] **Machine Learning**: AI-powered risk prediction models
- [ ] **Geographic Expansion**: Multi-location support beyond Uruguay
- [ ] **Advanced Analytics**: Enhanced data visualization with NASA datasets

### Technical Improvements
- [ ] **Database Integration**: PostgreSQL for larger NASA datasets
- [ ] **Caching Layer**: Redis for performance optimization
- [ ] **Testing Suite**: Comprehensive unit and integration tests
- [ ] **CI/CD Pipeline**: Automated deployment and testing
- [ ] **Docker Containerization**: Easy deployment and scaling
- [ ] **Performance Monitoring**: Application metrics and logging
- [ ] **Accessibility Features**: Voice interface and simplified mode

## 🚀 Getting Started

For detailed setup instructions, see [START_HERE.md](START_HERE.md)

### Quick Commands
```bash
# Backend (desde directorio raíz)
python -m uvicorn backend.api:app --reload --port 8000

# Frontend  
cd frontend && npm start
```

## 🤝 Contributing

This project was developed for the NASA Space Apps Challenge with focus on:
- **Educational Impact**: Making climate science accessible through modern web technologies
- **Practical Application**: Real-world event planning utility with intelligent recommendations
- **Scientific Rigor**: NASA-grade data analysis methodology with user-friendly presentation
- **Modern Architecture**: Scalable foundation for future development and integration
- **Democratizing Science**: Bringing NASA's Earth observation capabilities to everyone

## 📄 License

Developed for NASA Space Apps Challenge 2024 - Educational and Research Purposes

---

**Built with ❤️ for Earth Science** | **NASA Space Apps Challenge 2024**  
**Democratizing Climate Science Through Technology**
