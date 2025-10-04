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
    weatherConditions: ['wet', 'hot'],
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

    // Simulate API call delay
    setTimeout(() => {
      setResults(data);
      setLoading(false);
    }, 2000);
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
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-md mx-auto p-4 md:p-6 app-content">
        {/* Header */}
        <header className="text-center my-8">
          <h1 className="text-4xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-blue-500">
            UcuWeather
          </h1>
          <p className="text-slate-400 mt-2 flex items-center justify-center space-x-2">
            <span>Planifica tu día perfecto con</span>
            <img
              src="https://placehold.co/80x20/0B3D91/FFFFFF?text=NASA"
              alt="Logo de la NASA"
              className="inline h-5 w-auto rounded-md"
            />
          </p>
        </header>

        {/* Main Form */}
        <main>
          <WeatherForm
            onSubmit={handleFormSubmit}
            loading={loading}
            isNightMode={isNightMode}
            initialData={formData}
          />

          {/* Temporary Message */}
          {tempMessage && (
            <div className={`mt-3 p-3 text-center rounded-lg font-bold transition-all duration-300 ${
              tempMessage.type === 'error' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
            }`}>
              {tempMessage.message}
            </div>
          )}
        </main>

        {/* Results Section */}
        {results && (
          <WeatherResults
            data={results}
            isNightMode={isNightMode}
          />
        )}
      </div>
    </div>
  );
}

export default App;
