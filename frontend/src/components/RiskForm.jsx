/**
 * RiskForm Component - Weather Risk Assessment Form
 * Adapted from original HTML design
 */

import React, { useState } from 'react';

const RiskForm = ({ onAnalyze, loading, darkMode }) => {
  const [formData, setFormData] = useState({
    lat: -34.90,  // Montevideo, Uruguay
    lon: -56.16,
    month: 3  // March
  });

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }));
  };

  const handleMonthChange = (e) => {
    setFormData(prev => ({
      ...prev,
      month: parseInt(e.target.value)
    }));
  };

  const validateForm = () => {
    if (!formData.lat || formData.lat < -90 || formData.lat > 90) {
      alert('Latitude must be between -90 and 90');
      return false;
    }
    if (!formData.lon || formData.lon < -180 || formData.lon > 180) {
      alert('Longitude must be between -180 and 180');
      return false;
    }
    if (!formData.month || formData.month < 1 || formData.month > 12) {
      alert('Month must be between 1 and 12');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    onAnalyze(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Location Inputs */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className={`block text-sm font-medium mb-2 ${
            darkMode ? 'text-blue-200' : 'text-gray-700'
          }`}>
            Latitude
          </label>
          <input
            type="number"
            name="lat"
            value={formData.lat}
            onChange={handleInputChange}
            step="0.0001"
            min="-90"
            max="90"
            className="form-input"
            placeholder="Enter latitude"
            disabled={loading}
          />
        </div>

        <div>
          <label className={`block text-sm font-medium mb-2 ${
            darkMode ? 'text-blue-200' : 'text-gray-700'
          }`}>
            Longitude
          </label>
          <input
            type="number"
            name="lon"
            value={formData.lon}
            onChange={handleInputChange}
            step="0.0001"
            min="-180"
            max="180"
            className="form-input"
            placeholder="Enter longitude"
            disabled={loading}
          />
        </div>
      </div>

      {/* Month Selection */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${
          darkMode ? 'text-blue-200' : 'text-gray-700'
        }`}>
          Event Month
        </label>
        <select
          name="month"
          value={formData.month}
          onChange={handleMonthChange}
          className="form-input"
          disabled={loading}
        >
          {monthNames.map((month, index) => (
            <option key={index + 1} value={index + 1}>
              {month}
            </option>
          ))}
        </select>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center"
      >
        {loading ? (
          <>
            <div className="loading-ring mr-2"></div>
            Analyzing Weather Risk...
          </>
        ) : (
          '🔍 Analyze Weather Risk'
        )}
      </button>

      {/* Location Info */}
      <div className={`text-xs text-center ${
        darkMode ? 'text-slate-400' : 'text-gray-500'
      }`}>
        <p>📍 Default location: Montevideo, Uruguay</p>
        <p>📅 Default month: March</p>
      </div>
    </form>
  );
};

export default RiskForm;
