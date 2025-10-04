# 🌤️ The Parade Planner - NASA Space Apps Challenge

**Will It Rain On My Parade?** - Advanced weather risk assessment tool for outdoor event planning.

## 🚀 Project Overview

This project provides a comprehensive risk assessment platform for outdoor events based on historical weather patterns. Built with modular architecture for Phase 2 reusability and integration with real-time NASA data sources.

### 🎯 Key Features

- **Historical Risk Analysis**: 90th percentile threshold methodology
- **Interactive Visualizations**: Altair-powered temperature distribution charts
- **Educational Interface**: User-friendly Streamlit dashboard
- **Modular Architecture**: Reusable components for Phase 2 integration
- **NASA MERRA-2 Simulation**: Realistic atmospheric reanalysis data

## 📁 Project Structure

```
NASA-Will-It-Rain-On-My-Parade-/
├── app.py              # Streamlit user interface
├── logic.py            # Core business logic (REUSABLE MODULE)
├── mock_data.csv       # 20 years of simulated temperature data
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- pip package manager

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NASA-Will-It-Rain-On-My-Parade-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the dashboard**
   - Open your browser to `http://localhost:8501`
   - Enter event location coordinates
   - Select target month
   - Click "Analyze Weather Risk"

## 📊 Technical Architecture

### Core Components

#### `logic.py` - REUSABLE MODULE
- `load_historical_data(month_filter)`: Data loading with error handling
- `calculate_adverse_probability(monthly_data)`: Risk calculation engine
- `get_month_name(month_number)`: Utility functions
- `validate_coordinates(lat, lon)`: Input validation

#### `app.py` - Streamlit Interface
- **Sidebar Controls**: Location inputs, month selection
- **Educational Visualization**: Altair histogram with risk threshold overlay
- **Risk Assessment Display**: Probability metrics and recommendations
- **Methodology Explanation**: NASA MERRA-2 simulation details

#### `mock_data.csv` - Historical Data
- **20 years** of simulated temperature data (2004-2023)
- **4 months** coverage (January-April)
- **Realistic ranges**: 20-35°C maximum temperatures
- **NASA MERRA-2 format**: Compatible with real data sources

## 🔬 Methodology

### Risk Assessment Algorithm
1. **Data Loading**: Filter historical data by target month
2. **Threshold Calculation**: Compute 90th percentile of maximum temperatures
3. **Probability Analysis**: Calculate percentage of years exceeding threshold
4. **Risk Classification**: 
   - HIGH (≥20%): 🚨 Extreme heat risk
   - MODERATE (10-19%): ⚠️ Monitor conditions
   - LOW (5-9%): 🌤️ Generally favorable
   - MINIMAL (<5%): ☀️ Excellent conditions

### Educational Visualization
- **Histogram**: Temperature distribution over historical period
- **Red Threshold Line**: 90th percentile risk boundary
- **Interactive Elements**: Hover tooltips and zoom capabilities
- **Statistical Context**: Clear interpretation guidelines

## 🎓 Educational Value

### NASA Data Simulation
- **MERRA-2 Methodology**: Atmospheric reanalysis techniques
- **Climate Science**: Understanding temperature extremes
- **Risk Communication**: Translating data into actionable insights

### Learning Outcomes
- Statistical analysis of climate data
- Risk assessment methodologies
- Data visualization best practices
- Event planning with scientific rigor

## 🔄 Phase 2 Integration Ready

### Modular Design Benefits
- **Separated Concerns**: UI logic vs. business logic
- **API-Ready**: Functions can be easily wrapped as web services
- **Data Source Flexibility**: Easy to swap mock data for real NASA APIs
- **Extensibility**: Simple to add new risk variables and methodologies

### Extension Points
- Real-time NASA data integration
- Additional weather variables (precipitation, wind, humidity)
- Machine learning risk prediction models
- Geographic expansion beyond current dataset

## 🌍 NASA Space Apps Context

This project addresses the **"Will It Rain On My Parade?"** challenge by:
- Providing scientific basis for outdoor event planning
- Demonstrating practical applications of NASA climate data
- Creating educational tools for climate awareness
- Building foundation for larger-scale weather risk platforms

## 📈 Future Enhancements

### Phase 2 Roadmap
- [ ] Real-time NASA API integration
- [ ] Multi-variable risk assessment (precipitation, wind)
- [ ] Machine learning prediction models
- [ ] Geographic coverage expansion
- [ ] Mobile-responsive interface
- [ ] Historical trend analysis

### Technical Improvements
- [ ] Database integration for larger datasets
- [ ] Caching mechanisms for performance
- [ ] Unit test coverage
- [ ] API documentation
- [ ] Docker containerization

## 🤝 Contributing

This project was developed for the NASA Space Apps Challenge with focus on:
- **Educational Impact**: Making climate science accessible
- **Practical Application**: Real-world event planning utility
- **Scientific Rigor**: NASA-grade data analysis methodology
- **Modular Architecture**: Foundation for future development

## 📄 License

Developed for NASA Space Apps Challenge 2024 - Educational and Research Purposes

---

**Built with ❤️ for Earth Science** | **NASA Space Apps Challenge 2024**
Nasa proyect about weather
