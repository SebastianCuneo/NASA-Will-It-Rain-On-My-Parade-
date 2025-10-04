# The Parade Planner - Architecture Documentation

## NASA Space Apps Challenge - Frontend/Backend Architecture

### Project Structure

```
NASA-Will-It-Rain-On-My-Parade-/
├── backend/
│   ├── api.py              # FastAPI backend server
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
├── frontend/
│   ├── RiskForm.jsx       # React component
│   ├── package.json       # Node.js dependencies
│   └── README.md         # Frontend documentation
├── app.py                 # Original Streamlit app (MVP)
├── logic.py              # Core business logic
├── mock_data.csv         # Historical weather data
├── requirements.txt      # Main Python dependencies
└── ARCHITECTURE.md      # This file
```

### Architecture Overview

#### Backend (FastAPI)
- **API Server**: `backend/api.py`
- **Port**: 8000
- **Endpoints**:
  - `POST /api/risk` - Main risk assessment endpoint
  - `GET /health` - Health check
  - `GET /api/test` - Test endpoint
- **CORS**: Enabled for frontend communication
- **Data Processing**: Temperature and precipitation risk calculation

#### Frontend (React)
- **Component**: `frontend/RiskForm.jsx`
- **Port**: 3000 (development)
- **Features**:
  - Form inputs for location and month
  - API integration with backend
  - Risk visualization
  - Error handling and loading states

### API Integration Flow

1. **User Input**: Frontend form collects lat, lon, month
2. **API Request**: POST to `/api/risk` with JSON payload
3. **Data Processing**: Backend loads historical data and calculates risks
4. **Response**: JSON with temperature and precipitation risk assessments
5. **UI Update**: Frontend displays results with risk levels and messages

### Development Workflow

#### Starting Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --reload
```

#### Starting Frontend
```bash
cd frontend
npm install
npm start
```

### Data Flow

1. **Historical Data**: `mock_data.csv` contains 20 years of simulated weather data
2. **Risk Calculation**: 90th percentile methodology for both temperature and precipitation
3. **Response Format**: Structured JSON with risk levels, probabilities, and status messages
4. **UI Display**: Color-coded risk badges and detailed assessment information

### Phase 2 Readiness

This architecture is designed for easy extension in Phase 2:
- Modular backend with clear API endpoints
- Reusable React components
- Separation of concerns between UI and business logic
- Ready for real-time NASA data integration
- Scalable for additional weather variables

### Technology Stack

- **Backend**: FastAPI, Pandas, NumPy
- **Frontend**: React, JavaScript (ES6+)
- **Data**: CSV-based historical weather simulation
- **Communication**: RESTful API with JSON
- **Deployment**: Local development setup
