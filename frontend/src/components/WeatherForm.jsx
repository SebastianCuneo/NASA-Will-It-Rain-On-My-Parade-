/**
 * WeatherForm Component - Weather Risk Assessment Form
 * NASA Weather Risk Navigator
 * Adapted from original HTML design
 */

import React, { useState } from 'react';
import MapSelector from './MapSelector.jsx';

const WeatherForm = ({ onSubmit, loading, isNightMode, initialData }) => {
  // Estado del formulario con datos iniciales proporcionados por el componente padre
  const [formData, setFormData] = useState(initialData);
  // Coordenadas por defecto para Montevideo, Uruguay (ubicación principal del proyecto)
  const [lat, setLat] = useState(-34.90);
  const [lon, setLon] = useState(-56.16);
  // Estado para manejar errores de validación en la interfaz
  const [validationErrors, setValidationErrors] = useState([]);

  // Configuración de opciones climáticas adversas - selección única
  const weatherOptions = [
    { id: 'wet', emoji: '🌧️', label: 'Very Rainy' },
    { id: 'hot', emoji: '🔥', label: 'Very Hot' },
    { id: 'cold', emoji: '❄️', label: 'Very Cold' }
  ];

  // Note: Activity selection removed - Plan B will suggest compatible activities based on weather

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Maneja la selección de ubicación desde el componente MapSelector
  const handleMapLocationSelect = (latitude, longitude) => {
    setLat(latitude);
    setLon(longitude);
    
    // Actualiza la ubicación en los datos del formulario con coordenadas formateadas
    setFormData(prev => ({
      ...prev,
      location: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
    }));
    
    // INFO: Registro de selección de ubicación exitosa
    console.info(`📍 Ubicación seleccionada: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
  };


  // Implementa selección única para condiciones climáticas adversas
  const toggleWeatherCondition = (conditionId) => {
    setFormData(prev => ({
      ...prev,
      // Lógica de selección única: selecciona el clickeado o limpia si se clickea nuevamente
      weatherConditions: prev.weatherConditions.includes(conditionId)
        ? []
        : [conditionId]
    }));
  };

  // Activity selection removed - generate Plan B activities compatible with weather

  // Valida los datos del formulario antes del envío
  const validateFormData = (data) => {
    const errors = [];
    
    // Validar coordenadas
    if (!data.latitude || !data.longitude) {
      errors.push('Location required');
    } else if (data.latitude < -90 || data.latitude > 90 || data.longitude < -180 || data.longitude > 180) {
      errors.push('Invalid coordinates range');
    }
    
    // Validar fecha
    if (!data.date) {
      errors.push('Date required');
    } else {
      const selectedDate = new Date(data.date);
      const today = new Date();
      const oneYearFromNow = new Date();
      oneYearFromNow.setFullYear(today.getFullYear() + 1);
      
      if (selectedDate < today) {
        errors.push('Date cannot be in the past');
      } else if (selectedDate > oneYearFromNow) {
        errors.push('Date cannot be more than one year in the future');
      }
    }
    
    // Validar condición climática
    if (!data.weatherConditions || data.weatherConditions.length === 0) {
      errors.push('Weather condition required');
    }
    
    return errors;
  };

  // Maneja el envío del formulario y transforma los datos para el backend
  const handleSubmit = (e) => {
    e.preventDefault();
    
    try {
      // Crea el payload con coordenadas - asegura conversión explícita a float
      // Map frontend weather options to backend expectations
      const weatherConditionMap = {
        'wet': 'Very Rainy',
        'hot': 'Very Hot',
        'cold': 'Very Cold'
      };
      
      const selectedCondition = formData.weatherConditions[0] || 'hot';
      const backendCondition = weatherConditionMap[selectedCondition] || 'Very Hot';
      
      const payload = {
        ...formData,
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        event_date: formData.date,
        adverse_condition: backendCondition  // "Very Rainy", "Very Hot", "Very Cold"
      };
      
      // Validar datos antes del envío
      const errors = validateFormData(payload);
      if (errors.length > 0) {
        console.error('❌ Errores de validación:', errors);
        setValidationErrors(errors);
        return;
      }
      
      // Limpiar errores si la validación es exitosa
      setValidationErrors([]);
      
      // INFO: Registro de envío de formulario con datos completos
      console.info('📤 Enviando formulario con datos:', {
        hasLocation: !!payload.latitude,
        hasDate: !!payload.event_date,
        hasCondition: !!payload.adverse_condition,
        hasActivity: !!payload.activity,
        coordinates: { lat: payload.latitude, lon: payload.longitude }
      });
      
      onSubmit(payload);
      
    } catch (error) {
      console.error('❌ Error en handleSubmit:', error);
      alert('Error al procesar el formulario. Por favor, inténtalo de nuevo.');
    }
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
          
          {/* Informative note about date range */}
          <div className="mt-2 text-xs text-slate-400 bg-slate-800/50 border border-slate-700 rounded-lg p-3">
            <div className="flex items-center">
              <span className="text-blue-400 mr-2">ℹ️</span>
              <span><strong>Note:</strong> Predictions are available for up to 1 year in the future</span>
            </div>
          </div>
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
        
        {/* Visualización de errores de validación */}
        {validationErrors.length > 0 && (
          <div className="mt-4 p-4 bg-red-900/20 border border-red-500 rounded-lg">
            <div className="flex items-center mb-2">
              <span className="text-red-400 text-lg mr-2">⚠️</span>
              <h3 className="text-red-400 font-bold text-sm">Validation errors:</h3>
            </div>
            <ul className="text-red-300 text-sm space-y-1">
              {validationErrors.map((error, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-red-400 mr-2">•</span>
                  <span>{error}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </form>
  );
};

export default WeatherForm;
