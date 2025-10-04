/**
 * The Parade Planner - Main App Component
 * NASA Space Apps Challenge - React Application
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import RiskForm from './components/RiskForm';
import WeatherResults from './components/WeatherResults';

function App() {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
      document.body.classList.remove('day-mode');
    } else {
      document.body.classList.add('day-mode');
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  // Handle weather risk calculation
  const handleWeatherAnalysis = async (formData) => {
    setLoading(true);
    setError(null);
    setWeatherData(null);

    try {
      const response = await fetch('http://localhost:8000/api/risk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch weather risk assessment');
      }

      const data = await response.json();
      setWeatherData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen transition-all duration-1000 ${
      darkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-100 via-blue-200 to-indigo-200'
    }`}>
      
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Clouds Animation */}
        <div className="absolute top-10 left-10 w-20 h-12 bg-white/20 rounded-full animate-float opacity-60"></div>
        <div className="absolute top-32 right-20 w-16 h-10 bg-white/15 rounded-full animate-float-delayed opacity-50"></div>
        <div className="absolute bottom-40 left-1/4 w-24 h-14 bg-white/10 rounded-full animate-float-slow opacity-40"></div>
        <div className="absolute top-1/2 right-1/3 w-18 h-11 bg-white/25 rounded-full animate-float opacity-70"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 p-4">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div className="text-center">
            <h1 className={`text-3xl font-bold ${
              darkMode ? 'text-white' : 'text-gray-800'
            }`}>
              🌤️ The Parade Planner
            </h1>
            <p className={`text-sm ${
              darkMode ? 'text-blue-200' : 'text-blue-600'
            }`}>
              Will It Rain On My Parade? - NASA Space Apps Challenge
            </p>
          </div>
          
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleDarkMode}
            className={`p-2 rounded-full transition-all duration-300 ${
              darkMode 
                ? 'bg-yellow-400 text-gray-800 hover:bg-yellow-300' 
                : 'bg-gray-800 text-white hover:bg-gray-700'
            }`}
            title={darkMode ? 'Switch to Day Mode' : 'Switch to Night Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Left Column - Form */}
            <div className="space-y-6">
              <div className={`p-6 rounded-2xl shadow-xl backdrop-blur-sm ${
                darkMode 
                  ? 'bg-slate-800/70 border border-slate-700' 
                  : 'bg-white/80 border border-white/20'
              }`}>
                <h2 className={`text-xl font-semibold mb-4 ${
                  darkMode ? 'text-white' : 'text-gray-800'
                }`}>
                  📍 Event Planning
                </h2>
                <RiskForm 
                  onAnalyze={handleWeatherAnalysis}
                  loading={loading}
                  darkMode={darkMode}
                />
              </div>
            </div>

            {/* Right Column - Results */}
            <div className="space-y-6">
              <div className={`p-6 rounded-2xl shadow-xl backdrop-blur-sm ${
                darkMode 
                  ? 'bg-slate-800/70 border border-slate-700' 
                  : 'bg-white/80 border border-white/20'
              }`}>
                <h2 className={`text-xl font-semibold mb-4 ${
                  darkMode ? 'text-white' : 'text-gray-800'
                }`}>
                  📊 Risk Assessment
                </h2>
                
                {loading && (
                  <div className="flex items-center justify-center py-8">
                    <div className="loading-ring"></div>
                    <span className={`ml-2 ${
                      darkMode ? 'text-white' : 'text-gray-600'
                    }`}>
                      Analyzing weather data...
                    </span>
                  </div>
                )}

                {error && (
                  <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                    <p className="text-sm">❌ {error}</p>
                  </div>
                )}

                {weatherData && (
                  <WeatherResults 
                    data={weatherData} 
                    darkMode={darkMode}
                  />
                )}

                {!loading && !error && !weatherData && (
                  <div className={`text-center py-8 ${
                    darkMode ? 'text-slate-400' : 'text-gray-500'
                  }`}>
                    <p className="text-sm">
                      Enter your event details to get weather risk assessment
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 p-4 mt-8">
        <div className="max-w-4xl mx-auto text-center">
          <p className={`text-xs ${
            darkMode ? 'text-blue-200' : 'text-blue-600'
          }`}>
            NASA Space Apps Challenge 2024 | Built with ❤️ for Earth Science
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
