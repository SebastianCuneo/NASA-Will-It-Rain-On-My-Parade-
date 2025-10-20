/**
 * UcuWeather - Main App Component
 * NASA Space Apps Challenge - React Application
 * Adapted from original HTML design
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import WeatherForm from './components/WeatherForm';
import WeatherResults from './components/WeatherResults';

function App() {
  const [isNightMode, setIsNightMode] = useState(false);
  const [formData, setFormData] = useState({
    location: 'Montevideo',
    date: new Date().toISOString().split('T')[0],
    weatherConditions: ['wet'],
    activity: null
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tempMessage, setTempMessage] = useState(null);

  // Initialize mode based on localStorage or time
  useEffect(() => {
    const savedMode = localStorage.getItem('themeMode');
    let initialNightMode;
    
    if (savedMode) {
      initialNightMode = savedMode === 'night';
    } else {
      const now = new Date();
      const hour = now.getHours();
      const sunriseHour = 7;
      const sunsetHour = 19;
      initialNightMode = !(hour >= sunriseHour && hour < sunsetHour);
    }
    
    setIsNightMode(initialNightMode);
  }, []);

  // Apply mode classes to body
  useEffect(() => {
    const body = document.body;
    if (isNightMode) {
      body.classList.remove('day-mode');
      body.classList.add('night-mode');
    } else {
      body.classList.remove('night-mode');
      body.classList.add('day-mode');
    }
  }, [isNightMode]);

  const toggleMode = () => {
    const newMode = !isNightMode;
    setIsNightMode(newMode);
    localStorage.setItem('themeMode', newMode ? 'night' : 'day');
  };

  const showTemporaryMessage = (message, type = 'error') => {
    setTempMessage({ message, type });
    setTimeout(() => setTempMessage(null), 3000);
  };

  const handleFormSubmit = async (data) => {
    if (data.weatherConditions.length === 0) {
    showTemporaryMessage('Por favor, selecciona al menos una condición climática.', 'error');
     return;
     }
    
     setFormData(data);
     setLoading(true);
     setResults(null);
    
     try {
     // Create payload for API call
     const apiPayload = {
     latitude: data.latitude,  // Use coordinates from form
     longitude: data.longitude,
     event_date: data.event_date,  // Send date as string
     adverse_condition: data.weatherConditions[0] || 'Very Hot'  // Send first selected condition
       };
    
    // Debugging: Log API payload
     console.log('App.js API Payload:', apiPayload);
     console.log('API URL: http://localhost:8000/api/risk');
    
     // Call the FastAPI backend
     const response = await fetch('http://localhost:8000/api/risk', {
     method: 'POST',
     headers: {
     'Content-Type': 'application/json',
     },
     body: JSON.stringify(apiPayload)
     });
    
          // === 1. ÚNICA VERIFICACIÓN DE RESPUESTA ===
          if (!response.ok) {
            throw new Error(`API call failed: ${response.status}`);
          }
    
          // === 2. PARSEO DE JSON ===
          const apiData = await response.json();
          
          // Debugging: Log API response
          console.log('App.js API Response:', apiData);
          
          // Extract data from the new API response structure
          const temperatureRisk = apiData.data.temperature_risk;
          const precipitationRisk = apiData.data.precipitation_risk;
          const coldRisk = apiData.data.cold_risk;
          const planB = apiData.data.plan_b;
          
          // === NUEVAS CLAVES DE logic.py ===
          const plotData = apiData.data.plot_data; 
          const climateTrend = apiData.data.climate_trend;
          // ==================================
          
          // Combine API data with form data
          const combinedData = {
            ...data,
            apiResults: apiData,
            temperature_risk: {
              probability: temperatureRisk.probability,
              risk_level: temperatureRisk.risk_level,
              status_message: temperatureRisk.status_message,
              risk_threshold: temperatureRisk.risk_threshold
            },
            precipitation_risk: {
              probability: precipitationRisk.probability,
              risk_level: precipitationRisk.risk_level,
              status_message: precipitationRisk.status_message,
              risk_threshold: precipitationRisk.risk_threshold
            },
            cold_risk: {
              probability: coldRisk.probability,
              risk_level: coldRisk.risk_level,
              status_message: coldRisk.status_message,
              risk_threshold: coldRisk.risk_threshold
            },
            plan_b: planB,
            
            // === AÑADIR DATOS DE PLOTLY Y CLIMA AL OBJETO RESULTS ===
            plot_data: plotData,
            climate_trend: climateTrend
            // ========================================================
          };
    
          setResults(combinedData);
    
        } catch (error) {
          console.error('API Error:', error);
          showTemporaryMessage('Error connecting to weather service. Using offline data.', 'warning');
          // Fallback to mock data
          setResults(data);
        } finally {
          setLoading(false);
        }
      };

  return (
    <div className="min-h-screen relative">
      {/* Mode Toggle Button */}
      <button
        id="mode-toggle-button"
        onClick={toggleMode}
        className="absolute top-4 right-4 p-2 rounded-full shadow-lg transition-colors duration-300 z-20"
        title={isNightMode ? 'Switch to Day Mode' : 'Switch to Night Mode'}
      >
        {/* Sun Icon */}
        <svg
          id="mode-icon-sun"
          className={`w-6 h-6 ${isNightMode ? 'hidden' : 'block'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
        {/* Moon Icon */}
        <svg
          id="mode-icon-moon"
          className={`w-6 h-6 ${isNightMode ? 'block' : 'hidden'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      </button>

      {/* Cloud Animation Layer (only visible in day mode) */}
      {!isNightMode && (
        <div id="cloud-layer" className="cloud-animation-layer">
          <div id="cloud-1" className="cloud"></div>
          <div id="cloud-2" className="cloud"></div>
          <div id="cloud-3" className="cloud"></div>
          <div id="cloud-4" className="cloud"></div>
          <div id="cloud-5" className="cloud"></div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-4 md:p-6 lg:p-8 app-content">
        {/* Header */}
        <header className="text-center my-8 lg:my-12">
                      <h1 className="text-5xl lg:text-6xl font-black tracking-tight" style={{
                        color: isNightMode ? 'var(--nasa-white)' : '#1a365d',
                        textShadow: isNightMode 
                          ? '2px 2px 4px rgba(0,0,0,0.8)' 
                          : '2px 2px 4px rgba(255,255,255,0.8)'
                      }}>
                        NASA Weather Risk Navigator
                      </h1>
          <p className={`mt-4 flex items-center justify-center space-x-2 text-lg ${isNightMode ? 'text-slate-300' : 'text-gray-700'}`}>
            <span>Plan your perfect day with</span>
            <img
              src="https://placehold.co/100x25/0B3D91/FFFFFF?text=NASA"
              alt="NASA Logo"
              className="inline h-6 w-auto rounded-md"
            />
          </p>
        </header>

        {/* Main Layout - Desktop: Side by side, Mobile: Stacked */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
          
          {/* Left Column - Form */}
          <div className="space-y-6">
            <div className={`p-6 lg:p-8 rounded-2xl shadow-2xl backdrop-blur-sm ${
              isNightMode 
                ? 'bg-slate-800/70 border border-slate-700' 
                : 'bg-white/90 border border-white/30'
            }`}>
              <h2 className={`text-2xl font-bold mb-6 ${
                isNightMode ? 'text-white' : 'text-gray-800'
              }`}>
                📍 Event Configuration
              </h2>
              
              <WeatherForm
                onSubmit={handleFormSubmit}
                loading={loading}
                isNightMode={isNightMode}
                initialData={formData}
              />

              {/* Temporary Message */}
              {tempMessage && (
                <div className={`mt-4 p-4 text-center rounded-lg font-bold transition-all duration-300 ${
                  tempMessage.type === 'error' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
                }`}>
                  {tempMessage.message}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            <div className={`p-6 lg:p-8 rounded-2xl shadow-2xl backdrop-blur-sm ${
              isNightMode 
                ? 'bg-slate-800/70 border border-slate-700' 
                : 'bg-white/90 border border-white/30'
            }`}>
              <h2 className={`text-2xl font-bold mb-6 ${
                isNightMode ? 'text-white' : 'text-gray-800'
              }`}>
                📊 Risk Analysis
              </h2>
              
              {loading && (
                <div className="flex items-center justify-center py-12">
                  <div className="loading-ring"></div>
                  <span className={`ml-3 text-lg ${
                    isNightMode ? 'text-white' : 'text-gray-600'
                  }`}>
                    Analyzing NASA data...
                  </span>
                </div>
              )}

              {results && (
                <>
                  {/* ========================================================= */}
                  {/* 1. BANNER DE CAMBIO CLIMÁTICO */}
                  {results.climate_trend && (
                    <div className={`p-4 rounded-xl shadow-md mb-6 transition-all ${
                        results.climate_trend.trend_status === 'SIGNIFICANT_WARMING' 
                          ? 'bg-red-600/30 text-red-100 border-l-4 border-red-500' 
                          : 'bg-green-600/30 text-green-100 border-l-4 border-green-500'
                        }`}>
                      <p className="font-bold">Análisis de Tendencia Climática:</p>
                      <p>{results.climate_trend.message}</p>
                    </div>
                  )}
                  
                  {/* ========================================================= */}
                  {/* 2. GRÁFICO P90 (Placeholder de Plotly) */}
                  {results.plot_data && (
                    <div className={`p-4 rounded-2xl shadow-xl mb-6 ${
                      isNightMode 
                        ? 'bg-slate-700/70 border border-slate-600 text-white' 
                        : 'bg-gray-100/90 border border-gray-200 text-gray-800'
                      }`}>
                        <h3 className="text-xl font-bold mb-3">
                          📈 Gráfico: Umbral P90 vs. Tendencia
                        </h3>
                        {/* 🛑 ESTE ES EL LUGAR DONDE VA EL COMPONENTE REAL DE PLOTLY */}
                        <div className="h-64 flex items-center justify-center border-2 border-dashed border-sky-500/50 rounded-lg bg-sky-500/10 text-center p-4">
                          <p className='text-sm font-semibold'>
                            Placeholder: Para ver el gráfico, debes instalar **react-plotly.js** y crear el componente `<PlotlyChart />` aquí. 
                          </p>
                        </div>
                    </div>
                  )}
                  
                  {/* 3. RIESGOS Y PLAN B (Componente Existente) */}
                  <WeatherResults
                    data={results}
                    isNightMode={isNightMode}
                  />
                </>
              )}


              {!loading && !results && (
                <div className={`text-center py-12 ${
                  isNightMode ? 'text-slate-300' : 'text-gray-600'
                }`}>
                  <div className="text-6xl mb-4">🌤️</div>
                  <p className="text-lg">
                    Complete the form to get the climate risk analysis
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
