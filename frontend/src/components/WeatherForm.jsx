/**
 * WeatherForm Component - Weather Risk Assessment Form
 * NASA Weather Risk Navigator
 * Adapted from original HTML design
 */

import React, { useState } from 'react';

const WeatherForm = ({ onSubmit, loading, isNightMode, initialData }) => {
  const [formData, setFormData] = useState(initialData);

  const weatherOptions = [
    { id: 'wet', emoji: '🌧️', label: 'Muy Lluvioso' },
    { id: 'hot', emoji: '🔥', label: 'Muy Caluroso' },
    { id: 'cold', emoji: '❄️', label: 'Muy Frío' },
    { id: 'windy', emoji: '💨', label: 'Muy Ventoso' },
    { id: 'uncomfortable', emoji: '🥵', label: 'Incómodo' },
    { id: 'uv', emoji: '☀️', label: 'Radiación UV' }
  ];

  const activityOptions = [
    { id: 'surf', emoji: '🏄', label: 'Surfear' },
    { id: 'beach', emoji: '🏖️', label: 'Día de Playa' },
    { id: 'run', emoji: '🏃‍♂️', label: 'Correr' },
    { id: 'hike', emoji: '⛰️', label: 'Senderismo' },
    { id: 'sailing', emoji: '⛵', label: 'Navegar' },
    { id: 'picnic', emoji: '🧺', label: 'Picnic' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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
    onSubmit(formData);
  };

  return (
    <form id="weather-form" className="space-y-8" onSubmit={handleSubmit}>
      {/* Step 1 & 2: Location and Date - Side by side on desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Step 1: Location */}
        <div>
          <label htmlFor="location" className="block text-lg font-bold text-slate-300 mb-3">
            Paso 1: Elige la ubicación
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
              <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </div>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              className="bg-slate-800 border border-slate-700 text-white text-base rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-12 p-4"
              placeholder="Ej: Montevideo, Uruguay"
              required
            />
          </div>
        </div>

        {/* Step 2: Date */}
        <div>
          <label htmlFor="date" className="block text-lg font-bold text-slate-300 mb-3">
            Paso 2: Selecciona la fecha
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
          Paso 3: ¿Qué condiciones te preocupan?
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
          Paso 4 (Opcional): Elige una actividad
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
              Analizando datos de la NASA...
            </>
          ) : (
            '🔍 Analizar Probabilidad Histórica'
          )}
        </button>
      </div>
    </form>
  );
};

export default WeatherForm;
