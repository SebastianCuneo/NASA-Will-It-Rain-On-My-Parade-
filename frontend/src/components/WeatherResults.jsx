/**
 * WeatherResults Component - Display Weather Risk Assessment Results
 * Adapted from original HTML design
 */

import React from 'react';

const WeatherResults = ({ data, darkMode }) => {
  const { temperature_risk, precipitation_risk, location, month } = data;

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const getRiskBadgeClass = (riskLevel) => {
    switch (riskLevel.toLowerCase()) {
      case 'high':
        return 'risk-badge high';
      case 'moderate':
        return 'risk-badge moderate';
      case 'low':
        return 'risk-badge low';
      case 'minimal':
        return 'risk-badge minimal';
      default:
        return 'risk-badge';
    }
  };

  const getStatusMessageClass = (riskLevel) => {
    switch (riskLevel.toLowerCase()) {
      case 'high':
        return 'status-message high';
      case 'moderate':
        return 'status-message moderate';
      case 'low':
        return 'status-message low';
      case 'minimal':
        return 'status-message minimal';
      default:
        return 'status-message';
    }
  };

  return (
    <div className="fade-in space-y-6">
      {/* Location and Month Info */}
      <div className={`p-4 rounded-lg ${
        darkMode 
          ? 'bg-slate-700/50 border border-slate-600' 
          : 'bg-blue-50 border border-blue-200'
      }`}>
        <div className="flex items-center justify-between text-sm">
          <span className={`font-medium ${
            darkMode ? 'text-blue-200' : 'text-blue-700'
          }`}>
            📍 {location.lat}°N, {location.lon}°W
          </span>
          <span className={`font-medium ${
            darkMode ? 'text-blue-200' : 'text-blue-700'
          }`}>
            📅 {monthNames[month - 1]}
          </span>
        </div>
      </div>

      {/* Temperature Risk */}
      <div className="weather-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className={`text-lg font-semibold flex items-center ${
            darkMode ? 'text-white' : 'text-gray-800'
          }`}>
            🌡️ Temperature Risk
          </h3>
          <span className={getRiskBadgeClass(temperature_risk.risk_level)}>
            {temperature_risk.risk_level}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <span className={`text-sm ${
              darkMode ? 'text-slate-400' : 'text-gray-600'
            }`}>
              Probability:
            </span>
            <span className={`ml-2 font-semibold ${
              darkMode ? 'text-white' : 'text-gray-800'
            }`}>
              {temperature_risk.probability}%
            </span>
          </div>
          <div>
            <span className={`text-sm ${
              darkMode ? 'text-slate-400' : 'text-gray-600'
            }`}>
              Threshold:
            </span>
            <span className={`ml-2 font-semibold ${
              darkMode ? 'text-white' : 'text-gray-800'
            }`}>
              {temperature_risk.risk_threshold}°C
            </span>
          </div>
        </div>

        <div className={getStatusMessageClass(temperature_risk.risk_level)}>
          {temperature_risk.status_message}
        </div>

        <div className={`mt-2 text-xs ${
          darkMode ? 'text-slate-500' : 'text-gray-500'
        }`}>
          Based on {temperature_risk.total_observations} years of historical data
        </div>
      </div>

      {/* Precipitation Risk */}
      <div className="weather-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className={`text-lg font-semibold flex items-center ${
            darkMode ? 'text-white' : 'text-gray-800'
          }`}>
            🌧️ Precipitation Risk
          </h3>
          <span className={getRiskBadgeClass(precipitation_risk.risk_level)}>
            {precipitation_risk.risk_level}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <span className={`text-sm ${
              darkMode ? 'text-slate-400' : 'text-gray-600'
            }`}>
              Probability:
            </span>
            <span className={`ml-2 font-semibold ${
              darkMode ? 'text-white' : 'text-gray-800'
            }`}>
              {precipitation_risk.probability}%
            </span>
          </div>
          <div>
            <span className={`text-sm ${
              darkMode ? 'text-slate-400' : 'text-gray-600'
            }`}>
              Threshold:
            </span>
            <span className={`ml-2 font-semibold ${
              darkMode ? 'text-white' : 'text-gray-800'
            }`}>
              {precipitation_risk.risk_threshold}mm
            </span>
          </div>
        </div>

        <div className={getStatusMessageClass(precipitation_risk.risk_level)}>
          {precipitation_risk.status_message}
        </div>

        <div className={`mt-2 text-xs ${
          darkMode ? 'text-slate-500' : 'text-gray-500'
        }`}>
          Based on {precipitation_risk.total_observations} years of historical data
        </div>
      </div>

      {/* Recommendations */}
      <div className={`p-4 rounded-lg ${
        darkMode 
          ? 'bg-slate-700/50 border border-slate-600' 
          : 'bg-green-50 border border-green-200'
      }`}>
        <h4 className={`font-semibold mb-2 ${
          darkMode ? 'text-green-300' : 'text-green-700'
        }`}>
          💡 Recommendations
        </h4>
        <div className={`text-sm space-y-1 ${
          darkMode ? 'text-green-200' : 'text-green-600'
        }`}>
          {temperature_risk.risk_level === 'HIGH' || precipitation_risk.risk_level === 'HIGH' ? (
            <>
              <p>• Consider alternative dates with lower risk</p>
              <p>• Have indoor backup plans ready</p>
              <p>• Monitor weather forecasts closely</p>
            </>
          ) : temperature_risk.risk_level === 'MODERATE' || precipitation_risk.risk_level === 'MODERATE' ? (
            <>
              <p>• Monitor weather conditions</p>
              <p>• Have backup plans ready</p>
              <p>• Consider providing shelter/shade</p>
            </>
          ) : (
            <>
              <p>• Weather conditions are favorable</p>
              <p>• Standard outdoor planning sufficient</p>
              <p>• Enjoy your event!</p>
            </>
          )}
        </div>
      </div>

      {/* Technical Details */}
      <details className={`p-4 rounded-lg ${
        darkMode 
          ? 'bg-slate-700/30 border border-slate-600' 
          : 'bg-gray-50 border border-gray-200'
      }`}>
        <summary className={`cursor-pointer font-medium ${
          darkMode ? 'text-slate-300' : 'text-gray-700'
        }`}>
          🔬 Technical Details
        </summary>
        <div className={`mt-3 text-xs space-y-1 ${
          darkMode ? 'text-slate-400' : 'text-gray-600'
        }`}>
          <p><strong>Methodology:</strong> 90th percentile threshold analysis</p>
          <p><strong>Temperature Threshold:</strong> {temperature_risk.risk_threshold}°C</p>
          <p><strong>Precipitation Threshold:</strong> {precipitation_risk.risk_threshold}mm</p>
          <p><strong>Data Source:</strong> NASA MERRA-2 simulation (20 years)</p>
          <p><strong>Risk Levels:</strong> HIGH (≥20%), MODERATE (10-19%), LOW (5-9%), MINIMAL (&lt;5%)</p>
        </div>
      </details>
    </div>
  );
};

export default WeatherResults;
