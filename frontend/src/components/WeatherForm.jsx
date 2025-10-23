/**
 * WeatherForm Component - Weather Risk Assessment Form
 * NASA Weather Risk Navigator
 * Adapted from original HTML design
 */

import React, { useState } from 'react';
import MapSelector from './MapSelector.jsx';

const WeatherForm = ({ onSubmit, loading, isNightMode, initialData }) => {
  const [formData, setFormData] = useState(initialData);
  const [lat, setLat] = useState(-34.90);
  const [lon, setLon] = useState(-56.16);

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

  const handleMapLocationSelect = (latitude, longitude) => {
    setLat(latitude);
    setLon(longitude);
    
    // Update location in form data with coordinates
    setFormData(prev => ({
      ...prev,
      location: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
    }));
    
    console.log(`✅ Location selected: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
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
        {/* Step 1: Interactive Map */}
        <div>
          <label className="block text-lg font-bold text-slate-300 mb-3">
            Step 1: Choose Location
          </label>
          <MapSelector
            onLocationSelect={handleMapLocationSelect}
            isNightMode={isNightMode}
            initialLat={lat}
            initialLon={lon}
          />
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
