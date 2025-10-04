# 🏗️ NASA Weather Risk Navigator - Technical Architecture

## NASA Space Apps Challenge - Modern Web Application Architecture

## 📋 Overview

NASA Weather Risk Navigator is built with a modern, scalable architecture that separates concerns between frontend and backend, enabling easy maintenance, testing, and future enhancements.

## 🎯 Architecture Principles

- **Separation of Concerns**: Clear boundaries between UI, business logic, and data
- **API-First Design**: RESTful backend ready for multiple frontend implementations
- **Responsive Design**: Mobile-first approach with desktop enhancements
- **Modular Components**: Reusable React components and Python modules
- **Scalable Foundation**: Ready for Phase 2 enhancements and NASA API integration

## 🏛️ System Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐    File I/O    ┌─────────────────┐
│   React Frontend│ ←────────────→  │  FastAPI Backend│ ←────────────→ │   Mock Data     │
│   (Port 3000)   │                 │   (Port 8000)   │                │   (CSV Files)   │
└─────────────────┘                 └─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
    ┌─────────┐                         ┌─────────┐
    │ Browser │                         │  Logic  │
    │ Storage │                         │ Module  │
    │ (Theme) │                         │ (Python)│
    └─────────┘                         └─────────┘
```

## 🎨 Frontend Architecture (React)

### Component Hierarchy
```
App.js (Root Component)
├── WeatherForm.jsx (Form Management)
│   ├── Location Input
│   ├── Date Selector
│   ├── Weather Conditions Grid
│   └── Activity Selection Grid
└── WeatherResults.jsx (Results Display)
    ├── Activity Analysis Card
    ├── Weather Summary Card
    ├── Time Footprint Section
    └── Historical Distribution
```

### State Management
- **Local State**: React hooks for component-specific data
- **Global State**: App-level state for theme, form data, and results
- **Persistence**: localStorage for theme preference
- **API State**: Loading states and error handling

### Responsive Design Strategy
```css
/* Mobile First */
.base-styles { }

/* Tablet */
@media (min-width: 768px) { }

/* Desktop */
@media (min-width: 1024px) { }
```

### Key Features
- **Dark/Light Mode**: CSS variables and conditional classes
- **Animations**: CSS keyframes for clouds, stars, and transitions
- **Glassmorphism**: Backdrop blur effects with transparency
- **Touch Interactions**: Optimized for mobile and desktop

## ⚙️ Backend Architecture (FastAPI)

### API Structure
```
FastAPI Application
├── CORS Middleware (Frontend Communication)
├── Error Handling Middleware
├── Routes:
│   ├── GET / (Root endpoint)
│   ├── GET /health (Health check)
│   ├── POST /api/risk (Main risk assessment)
│   └── GET /docs (Auto-generated documentation)
└── Business Logic Integration
    └── logic.py (Core calculations)
```

### Data Flow
1. **Request Validation**: Pydantic models for input validation
2. **Data Processing**: CSV loading and filtering
3. **Risk Calculation**: 90th percentile methodology
4. **Response Formatting**: JSON response with risk metrics
5. **Error Handling**: Comprehensive error responses

### Key Features
- **Type Safety**: Pydantic models for request/response validation
- **Documentation**: Automatic OpenAPI/Swagger documentation
- **CORS Support**: Cross-origin requests from frontend
- **Error Handling**: Structured error responses
- **Caching**: In-memory data caching for performance

## 📊 Data Architecture

### Mock Data Structure
```csv
Year,Month,Max_Temperature_C,Precipitation_mm
2020,1,28.5,15.2
2020,2,30.1,25.8
...
```

### Data Processing Pipeline
1. **Data Loading**: CSV parsing with error handling
2. **Filtering**: Month-based data filtering
3. **Statistical Analysis**: Percentile calculations
4. **Risk Assessment**: Probability analysis
5. **Response Generation**: Formatted JSON output

## 🔧 Technology Stack

### Frontend Technologies
- **React 18**: Modern component-based UI library
- **Tailwind CSS**: Utility-first CSS framework
- **CSS3**: Custom animations and effects
- **JavaScript ES6+**: Modern JavaScript features
- **Axios**: HTTP client for API communication

### Backend Technologies
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Uvicorn**: ASGI server for FastAPI

### Development Tools
- **npm**: Frontend package management
- **pip**: Python package management
- **Git**: Version control
- **ESLint**: JavaScript linting (configurable)
- **Prettier**: Code formatting (configurable)

## 🌐 API Documentation

### Endpoints

#### POST /api/risk
**Purpose**: Calculate weather risk assessment

**Request Body**:
```json
{
  "lat": -34.90,
  "lon": -56.16,
  "month": 3
}
```

**Response**:
```json
{
  "temperature_risk": {
    "probability": 15.2,
    "risk_threshold": 29.8,
    "status_message": "⚠️ MODERATE RISK of warm weather...",
    "risk_level": "MODERATE"
  },
  "precipitation_risk": {
    "probability": 8.3,
    "risk_threshold": 45.1,
    "status_message": "☁️ LOW RISK of significant rain...",
    "risk_level": "LOW"
  }
}
```

#### GET /health
**Purpose**: Health check endpoint

**Response**:
```json
{
  "status": "ok",
  "message": "API is running smoothly."
}
```

## 🚀 Deployment Architecture

### Development Environment
```
Local Development
├── Frontend (React Dev Server)
│   └── http://localhost:3000
├── Backend (Uvicorn Dev Server)
│   └── http://localhost:8000
└── File System
    └── CSV data files
```

### Production Considerations
- **Frontend**: Build optimization and CDN deployment
- **Backend**: Production ASGI server (Gunicorn + Uvicorn)
- **Database**: Migration from CSV to PostgreSQL
- **Caching**: Redis for API response caching
- **Monitoring**: Application performance monitoring

## 🔄 Phase 2 Integration Points

### NASA API Integration
```python
# Future enhancement
async def fetch_nasa_data(lat: float, lon: float, month: int):
    # Real-time NASA MERRA-2 data
    pass
```

### Database Migration
```sql
-- Future schema
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    temperature_c DECIMAL,
    precipitation_mm DECIMAL,
    location_id INTEGER
);
```

### Machine Learning Integration
```python
# Future enhancement
class WeatherPredictor:
    def predict_risk(self, historical_data, current_conditions):
        # ML-based risk prediction
        pass
```

## 📈 Performance Considerations

### Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Webpack optimization
- **Image Optimization**: Compressed assets
- **Caching**: Browser caching strategies

### Backend Optimization
- **Data Caching**: In-memory data caching
- **Async Processing**: Non-blocking operations
- **Response Compression**: Gzip compression
- **Database Indexing**: Optimized queries (future)

## 🔒 Security Considerations

### Frontend Security
- **Input Validation**: Client-side validation
- **XSS Prevention**: React's built-in XSS protection
- **HTTPS**: Secure communication (production)

### Backend Security
- **Input Validation**: Pydantic model validation
- **CORS Configuration**: Restricted origins (production)
- **Rate Limiting**: API rate limiting (future)
- **Authentication**: JWT tokens (future)

## 🧪 Testing Strategy

### Frontend Testing
- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: API integration testing
- **E2E Tests**: End-to-end testing with Cypress

### Backend Testing
- **Unit Tests**: Function-level testing with pytest
- **API Tests**: Endpoint testing with FastAPI TestClient
- **Integration Tests**: Full workflow testing

## 📚 Documentation

### Code Documentation
- **Component Documentation**: JSDoc for React components
- **API Documentation**: OpenAPI/Swagger auto-generation
- **Inline Comments**: Comprehensive code comments

### User Documentation
- **README.md**: Project overview and setup
- **START_HERE.md**: Quick start guide
- **ARCHITECTURE.md**: Technical architecture (this file)

---

**Built with ❤️ for NASA Space Apps Challenge 2024**  
**Modern Web Architecture for Weather Risk Assessment**