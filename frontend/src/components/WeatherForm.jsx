/**
 * WeatherForm Component - Weather Risk Assessment Form
 * NASA Weather Risk Navigator
 * Adapted from original HTML design
 */

import React, { useState } from 'react';

const WeatherForm = ({ onSubmit, loading, isNightMode, initialData }) => {
  const [formData, setFormData] = useState(initialData);
  const [lat, setLat] = useState(-34.90);
  const [lon, setLon] = useState(-56.16);
  const [coordinateError, setCoordinateError] = useState('');

  const weatherOptions = [
    { id: 'wet', emoji: '🌧️', label: 'Very Rainy' },
    { id: 'hot', emoji: '🔥', label: 'Very Hot' },
    { id: 'cold', emoji: '❄️', label: 'Very Cold' },
    { id: 'windy', emoji: '💨', label: 'Very Windy' },
    { id: 'uncomfortable', emoji: '🥵', label: 'Uncomfortable' },
    { id: 'uv', emoji: '☀️', label: 'UV Radiation' }
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

  const handleLatitudeChange = (e) => {
    const value = parseFloat(e.target.value);
    setLat(value);
    setCoordinateError('');
  };

  const handleLongitudeChange = (e) => {
    const value = parseFloat(e.target.value);
    setLon(value);
    setCoordinateError('');
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
      weatherConditions: prev.weatherConditions.includes(conditionId)
        ? prev.weatherConditions.filter(id => id !== conditionId)
        : [...prev.weatherConditions, conditionId]
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
    
    // Create payload with coordinates
    const payload = {
      ...formData,
      latitude: lat,
      longitude: lon,
      event_date: formData.date
    };
    
    onSubmit(payload);
  };

  return (
    <form id="weather-form" className="space-y-8" onSubmit={handleSubmit}>
      {/* Step 1 & 2: Location and Date - Side by side on desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Step 1: Location Coordinates */}
        <div>
          <label className="block text-lg font-bold text-slate-300 mb-3">
            Step 1: Choose the location coordinates
          </label>
          <div className="space-y-3">
            {/* Latitude Input */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </div>
              <input
                type="number"
                id="latitude"
                name="latitude"
                value={lat}
                onChange={handleLatitudeChange}
                className="bg-slate-800 border border-slate-700 text-white text-base rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-12 p-3"
                placeholder="Latitude (-90 to 90)"
                step="0.000001"
                min="-90"
                max="90"
                required
              />
              <label htmlFor="latitude" className="absolute -top-2 left-3 bg-slate-800 px-2 text-xs text-slate-400">
                Latitude
              </label>
            </div>
            
            {/* Longitude Input */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
                <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </div>
              <input
                type="number"
                id="longitude"
                name="longitude"
                value={lon}
                onChange={handleLongitudeChange}
                className="bg-slate-800 border border-slate-700 text-white text-base rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-12 p-3"
                placeholder="Longitude (-180 to 180)"
                step="0.000001"
                min="-180"
                max="180"
                required
              />
              <label htmlFor="longitude" className="absolute -top-2 left-3 bg-slate-800 px-2 text-xs text-slate-400">
                Longitude
              </label>
            </div>
            
            {/* Error Message */}
            {coordinateError && (
              <div className="text-red-400 text-sm bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                {coordinateError}
              </div>
            )}
            
            {/* Location Info */}
            <div className="text-xs text-slate-400 bg-slate-800/50 border border-slate-700 rounded-lg p-3">
              <strong>Default:</strong> Montevideo, Uruguay (-34.90, -56.16)<br/>
              <strong>Tip:</strong> You can find coordinates using Google Maps or other mapping services.
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
          Step 3: What conditions concern you?
        </label>
        <div id="weather-options" className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-4">
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
        <div id="activity-options" className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-4">
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
