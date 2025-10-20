/**
 * WeatherForm Component - Weather Risk Assessment Form
 * NASA Weather Risk Navigator
 * Adapted from original HTML design
 */

import React, { useState } from 'react';
import { getCityCoordinates, getAutocompleteSuggestions } from '../utils/geocoding';

const WeatherForm = ({ onSubmit, loading, isNightMode, initialData }) => {
  const [formData, setFormData] = useState(initialData);
  const [cityInput, setCityInput] = useState('Montevideo');
  const [lat, setLat] = useState(-34.90);
  const [lon, setLon] = useState(-56.16);
  const [coordinateError, setCoordinateError] = useState('');
  const [searchingCity, setSearchingCity] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const weatherOptions = [
    { id: 'wet', emoji: '🌧️', label: 'Very Rainy' },
    { id: 'hot', emoji: '🔥', label: 'Very Hot' },
    { id: 'cold', emoji: '❄️', label: 'Very Cold' }
  ];

  const activityOptions = [
    { id: 'surf', emoji: '🏄', label: 'Surfing' },
    { id: 'beach', emoji: '🏖️', label: 'Beach Day' },
    { id: 'run', emoji: '🏃‍♂️', label: 'Running' },
    { id: 'hike', emoji: '⛰️', label: 'Hiking' },
    { id: 'sailing', emoji: '⛵', label: 'Sailing' },
    { id: 'picnic', emoji: '🧺', label: 'Picnic' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCityInputChange = (value) => {
    setCityInput(value);
    setCoordinateError('');
    
    // Show autocomplete suggestions
    if (value.length >= 2) {
      const filtered = getAutocompleteSuggestions(value, 5);
      setSuggestions(filtered);
    } else {
      setSuggestions([]);
    }
  };

  const handleCitySearch = async (cityName = cityInput) => {
    if (!cityName || cityName.trim().length === 0) {
      setCoordinateError('Please enter a city name');
      return;
    }

    setSearchingCity(true);
    setCoordinateError('');
    setSuggestions([]);

    try {
      const result = await getCityCoordinates(cityName);

      if (result) {
        setLat(result.lat);
        setLon(result.lon);
        setCityInput(result.city || cityName);
        
        // Update location in form data
        setFormData(prev => ({
          ...prev,
          location: result.displayName || cityName
        }));
        
        console.log(`✅ City found: ${result.displayName} (${result.lat}, ${result.lon})`);
      } else {
        setCoordinateError(`City "${cityName}" not found. Please try another name.`);
      }
    } catch (error) {
      console.error('City search error:', error);
      setCoordinateError('Error searching city. Please check your connection.');
    } finally {
      setSearchingCity(false);
    }
  };

  const handleSuggestionClick = (cityName) => {
    setCityInput(cityName);
    setSuggestions([]);
    handleCitySearch(cityName);
  };

  const validateCoordinates = () => {
    if (isNaN(lat) || lat < -90 || lat > 90) {
      setCoordinateError('Latitude must be a number between -90 and 90');
      return false;
    }
    if (isNaN(lon) || lon < -180 || lon > 180) {
      setCoordinateError('Longitude must be a number between -180 and 180');
      return false;
    }
    setCoordinateError('');
    return true;
  };

  const toggleWeatherCondition = (conditionId) => {
    setFormData(prev => ({
      ...prev,
      // Enforce single-select: select the clicked one or clear if clicked again
      weatherConditions: prev.weatherConditions.includes(conditionId)
        ? []
        : [conditionId]
    }));
  };

  const toggleActivity = (activityId) => {
    setFormData(prev => ({
      ...prev,
      activity: prev.activity === activityId ? null : activityId
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate coordinates before submitting
    if (!validateCoordinates()) {
      return; // Stop submission if validation fails
    }
    
    // Create payload with coordinates - ensure explicit float conversion
    const payload = {
      ...formData,
      latitude: parseFloat(lat), // Asegurar que es un número flotante
      longitude: parseFloat(lon), // Asegurar que es un número flotante
      event_date: formData.date,
      adverse_condition: formData.weatherConditions[0] || 'hot' // Send first selected condition
    };
    
    // Debugging: Log payload before sending
    console.log('WeatherForm Payload:', payload);
    console.log('Coordinates:', { lat: payload.latitude, lon: payload.longitude });
    
    onSubmit(payload);
  };

  return (
    <form id="weather-form" className="space-y-8" onSubmit={handleSubmit}>
      {/* Step 1 & 2: Location and Date - Side by side on desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Step 1: Location Search */}
        <div>
          <label className="block text-lg font-bold text-slate-300 mb-3">
            Step 1: Choose Location
          </label>
          <div className="space-y-4">
            {/* City Search Input */}
            <div className="relative">
              <label htmlFor="city-search" className="block text-sm font-medium text-slate-300 mb-2">
                City Name
              </label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                    <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                  </div>
                  <input
                    type="text"
                    id="city-search"
                    value={cityInput}
                    onChange={(e) => handleCityInputChange(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleCitySearch();
                      }
                    }}
                    className="bg-slate-800 border border-slate-700 text-white text-base rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-12 p-4"
                    placeholder="e.g., New York, Tokyo, Paris, London..."
                    disabled={searchingCity}
                  />
                  
                  {/* Autocomplete Suggestions */}
                  {suggestions.length > 0 && (
                    <div className="absolute z-50 w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                      {suggestions.map((city, index) => (
                        <div
                          key={index}
                          onClick={() => handleSuggestionClick(city)}
                          className="px-4 py-3 hover:bg-slate-700 cursor-pointer text-white border-b border-slate-700 last:border-b-0 transition-colors"
                        >
                          📍 {city}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                <button
                  type="button"
                  onClick={() => handleCitySearch()}
                  disabled={searchingCity}
                  className="px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-colors disabled:bg-slate-600 disabled:cursor-not-allowed"
                >
                  {searchingCity ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Searching...
                    </span>
                  ) : (
                    '🔍 Search'
                  )}
                </button>
              </div>
            </div>
            
            {/* Error Message */}
            {coordinateError && (
              <div className="text-red-400 text-sm bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                ⚠️ {coordinateError}
              </div>
            )}
            
            {/* Coordinates Display */}
            <div className="text-xs text-slate-400 bg-slate-800/50 border border-slate-700 rounded-lg p-3">
              <strong className="text-slate-300">📍 Coordinates:</strong> {lat.toFixed(4)}, {lon.toFixed(4)}<br/>
              <strong className="text-slate-300">🌍 Global Coverage:</strong> NASA POWER data available worldwide
            </div>
          </div>
        </div>

        {/* Step 2: Date */}
        <div>
          <label htmlFor="date" className="block text-lg font-bold text-slate-300 mb-3">
            Step 2: Select the date
          </label>
          <input
            type="date"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleInputChange}
            className="bg-slate-800 border border-slate-700 text-white text-base rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-4"
            required
          />
        </div>
      </div>

      {/* Step 3: Weather Conditions */}
      <div>
        <label className="block text-lg font-bold text-slate-300 mb-4">
          Step 3: What condition concerns you? (single choice)
        </label>
        <div id="weather-options" className="grid grid-cols-3 gap-4">
          {weatherOptions.map((option) => (
            <div
              key={option.id}
              className={`selectable-option weather-option flex flex-col items-center justify-center p-4 bg-slate-800 border-2 border-slate-700 rounded-xl cursor-pointer transition-all duration-200 aspect-square hover:scale-105 ${
                formData.weatherConditions.includes(option.id) ? 'selected' : ''
              }`}
              onClick={() => toggleWeatherCondition(option.id)}
            >
              <span className="text-4xl mb-2">{option.emoji}</span>
              <span className="font-bold text-sm text-center leading-tight">{option.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Step 4: Activity (Optional) */}
      <div>
        <label className="block text-lg font-bold text-slate-300 mb-4">
          Step 4 (Optional): Choose an activity
        </label>
        <div id="activity-options" className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {activityOptions.map((option) => (
            <div
              key={option.id}
              className={`selectable-option activity-option flex flex-col items-center justify-center p-4 bg-slate-800 border-2 border-slate-700 rounded-xl cursor-pointer transition-all duration-200 aspect-square hover:scale-105 ${
                formData.activity === option.id ? 'selected' : ''
              }`}
              onClick={() => toggleActivity(option.id)}
            >
              <span className="text-4xl mb-2">{option.emoji}</span>
              <span className="font-bold text-sm text-center leading-tight">{option.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <button
          type="submit"
          id="submit-button"
          className="w-full text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-800 text-lg"
          style={{ backgroundColor: 'var(--nasa-blue)' }}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="loading-ring"></span>
              Analyzing NASA data...
            </>
          ) : (
            '🔍 Analyze Historical Probability'
          )}
        </button>
      </div>
    </form>
  );
};

export default WeatherForm;
