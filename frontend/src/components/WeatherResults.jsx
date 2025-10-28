/**
 * WeatherResults Component - Display Weather Risk Assessment Results
 * NASA Weather Risk Navigator
 * 
 * Shows:
 * 1. Weather risk analysis for selected condition
 * 2. Compatible activities from Plan B (AI-generated)
 * 3. Climate change analysis (long-term trends)
 */

import React from 'react';

const WeatherResults = ({ data, isNightMode }) => {
  // Extract real data from backend
  const { location, date, apiResults, selectedCondition } = data;
  
  // Check if using fallback data
  const isFallback = apiResults?.is_fallback || false;
  
  // Get risk analysis data
  const riskAnalysis = apiResults?.risk_analysis || null;
  const riskLevel = riskAnalysis?.risk_level || 'UNKNOWN';
  const riskProbability = riskAnalysis?.probability || 0;
  const riskMessage = riskAnalysis?.status_message || 'No data available';
  
  // Get Plan B alternatives
  const planBData = apiResults?.plan_b?.alternatives || [];
  const planBSuccess = apiResults?.plan_b?.success || false;
  const aiModel = apiResults?.plan_b?.ai_model || 'Backend System';
  
  // Get climate trend data
  const climateTrend = apiResults?.climate_trend || 'No trend data available';
  const climateTrendDetails = apiResults?.climate_trend_details || null;

  // Determine risk color based on level
  const getRiskColor = (level) => {
    if (level === 'HIGH') {
      return {
      backgroundColor: isNightMode ? 'rgba(252, 61, 33, 0.2)' : 'rgba(252, 61, 33, 0.1)', 
        color: isNightMode ? '#FC3D21' : '#2d3748',
        border: `1px solid ${isNightMode ? '#FC3D21' : '#e2e8f0'}`
      };
    } else if (level === 'MODERATE') {
        return { 
        backgroundColor: isNightMode ? 'rgba(11, 61, 145, 0.2)' : 'rgba(11, 61, 145, 0.1)',
        color: isNightMode ? '#0B3D91' : '#2d3748',
        border: `1px solid ${isNightMode ? '#0B3D91' : '#e2e8f0'}`
        };
    } else {
      return { 
        backgroundColor: isNightMode ? 'rgba(231, 244, 52, 0.2)' : 'rgba(231, 244, 52, 0.3)',
        color: isNightMode ? '#E7F434' : '#2d3748',
        border: `1px solid ${isNightMode ? '#E7F434' : '#e2e8f0'}`
      };
    }
  };

  const riskColorStyle = getRiskColor(riskLevel);

  return (
    <section className="fade-in space-y-6 mt-6">
      {/* FALLBACK WARNING */}
      {isFallback && (
        <div className={`border rounded-xl p-4 mb-4 ${
          isNightMode 
            ? 'bg-yellow-900/20 border-yellow-600' 
            : 'bg-yellow-50 border-yellow-300'
        }`}>
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <p className={`font-bold ${isNightMode ? 'text-yellow-300' : 'text-yellow-700'}`}>
                Using Fallback Data
              </p>
              <p className={`text-sm ${isNightMode ? 'text-yellow-400' : 'text-yellow-600'}`}>
                NASA API unavailable. Displaying data from Montevideo, Uruguay instead.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* 1. RISK ANALYSIS SECTION */}
      <div className={`border-2 rounded-xl p-6 ${
        isNightMode 
          ? 'bg-slate-800 border-slate-700' 
          : 'bg-white/90 border-gray-300'
      }`}>
        <h2 className={`text-2xl font-bold text-center mb-4 ${isNightMode ? 'text-slate-300' : 'text-gray-800'}`}>
          ⚠️ Weather Risk Analysis
        </h2>
        <p className={`text-center mb-6 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
          {location} on {date}
        </p>
        
        <div className="text-center">
          <div className={`inline-block px-6 py-3 rounded-full mb-4`} style={riskColorStyle}>
            <span className="text-4xl font-bold">{riskProbability.toFixed(1)}%</span>
            <span className="text-sm font-bold ml-2">Probability</span>
          </div>
          
          <div className="mt-4">
            <span className={`text-sm font-bold px-6 py-2 rounded-full`} style={riskColorStyle}>
              {riskLevel} RISK
            </span>
          </div>
          
          {/* Stats Grid */}
          <div className={`mt-6 grid grid-cols-2 gap-3`}>
            <div className={`p-4 rounded-lg border-2 ${
              isNightMode 
                ? 'bg-slate-800 border-slate-700' 
                : 'bg-gray-100 border-gray-300'
            }`}>
              <div className={`text-xs font-semibold mb-2 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                Risk Threshold
              </div>
              <div className={`text-2xl font-bold ${isNightMode ? 'text-slate-300' : 'text-gray-800'}`}>
                {riskAnalysis?.risk_threshold || 'N/A'}
              </div>
              <div className={`text-xs mt-1 ${isNightMode ? 'text-slate-500' : 'text-gray-500'}`}>
                Used for probability calculation
              </div>
            </div>
            
            <div className={`p-4 rounded-lg border-2 ${
              isNightMode 
                ? 'bg-purple-900/30 border-purple-600' 
                : 'bg-purple-50 border-purple-400'
            }`}>
              <div className={`text-xs font-semibold mb-2 ${isNightMode ? 'text-purple-300' : 'text-purple-700'}`}>
                Extreme Threshold
              </div>
              <div className={`text-2xl font-bold ${isNightMode ? 'text-purple-200' : 'text-purple-800'}`}>
                {(() => {
                  // Extract extreme threshold from message (e.g., "Extreme heat threshold: 33.7°C (P90)")
                  const match = riskMessage?.match(/Extreme.*?threshold:\s*([0-9.]+)/i);
                  return match ? match[1] : 'N/A';
                })()}
              </div>
              <div className={`text-xs mt-1 ${isNightMode ? 'text-purple-400' : 'text-purple-600'}`}>
                {selectedCondition === 'cold' ? 'P10 (extreme cold)' :
                 selectedCondition === 'wet' ? 'P90 (extreme rainfall)' :
                 'P90 (extreme heat)'}
              </div>
            </div>
            
            <div className={`p-3 rounded-lg border-2 ${
              isNightMode 
                ? 'bg-slate-800 border-slate-700' 
                : 'bg-gray-100 border-gray-300'
            }`}>
              <div className={`text-xs font-semibold mb-1 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                Adverse Days
              </div>
              <div className={`text-xl font-bold ${isNightMode ? 'text-slate-300' : 'text-gray-800'}`}>
                {riskAnalysis?.adverse_count || 0}
              </div>
            </div>
            
            <div className={`p-3 rounded-lg border-2 ${
              isNightMode 
                ? 'bg-slate-800 border-slate-700' 
                : 'bg-gray-100 border-gray-300'
            }`}>
              <div className={`text-xs font-semibold mb-1 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                Total Days
              </div>
              <div className={`text-xl font-bold ${isNightMode ? 'text-slate-300' : 'text-gray-800'}`}>
                {riskAnalysis?.total_observations || 0}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. PLAN B - COMPATIBLE ACTIVITIES */}
      {planBSuccess && planBData.length > 0 && (
        <div className={`border-2 rounded-xl p-6 ${
          isNightMode 
            ? 'bg-slate-800 border-slate-700' 
            : 'bg-white/90 border-gray-300'
        }`}>
          <h2 className={`text-2xl font-bold text-center mb-4 ${isNightMode ? 'text-slate-300' : 'text-gray-800'}`}>
            🌟 Compatible Activities
          </h2>
          <p className={`text-center mb-6 text-sm ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            Generated by {aiModel}
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {planBData.map((alt, index) => (
              <div key={index} className={`p-4 rounded-lg border-2 ${
                            isNightMode 
                  ? 'bg-slate-800 border-slate-700' 
                  : 'bg-gray-50 border-gray-300'
                          }`}>
                            <div className="flex items-start justify-between mb-2">
                  <h3 className={`font-bold text-lg ${isNightMode ? 'text-yellow-300' : 'text-blue-600'}`}>
                    {alt.title}
                  </h3>
                              {alt.type && (
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  alt.type === 'indoor' 
                                    ? (isNightMode ? 'bg-blue-900/30 text-blue-300' : 'bg-blue-100 text-blue-700')
                                    : alt.type === 'outdoor'
                                    ? (isNightMode ? 'bg-green-900/30 text-green-300' : 'bg-green-100 text-green-700')
                                    : (isNightMode ? 'bg-purple-900/30 text-purple-300' : 'bg-purple-100 text-purple-700')
                                }`}>
                                  {alt.type}
                                </span>
                              )}
                            </div>
                            
                            <p className={`text-sm mb-2 ${isNightMode ? 'text-slate-300' : 'text-gray-700'}`}>
                  {alt.description}
                            </p>
                            
                            {alt.reason && (
                  <div className={`mb-2 p-2 rounded ${isNightMode ? 'bg-slate-800' : 'bg-white'}`}>
                                <p className={`text-xs font-medium ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                      <strong>Why:</strong> {alt.reason}
                                </p>
                              </div>
                            )}
                            
                            {alt.tips && (
                  <p className={`text-xs ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                    💡 {alt.tips}
                                </p>
                            )}
                            
                            <div className="flex flex-wrap gap-2 mt-3">
                              {alt.location && (
                                <span className={`px-2 py-1 rounded text-xs ${isNightMode ? 'bg-slate-600 text-slate-300' : 'bg-gray-100 text-gray-600'}`}>
                                  📍 {alt.location}
                                </span>
                              )}
                              {alt.duration && (
                                <span className={`px-2 py-1 rounded text-xs ${isNightMode ? 'bg-slate-600 text-slate-300' : 'bg-gray-100 text-gray-600'}`}>
                                  ⏱️ {alt.duration}
                                </span>
                              )}
                              {alt.cost && (
                    <span className={`px-2 py-1 rounded text-xs ${isNightMode ? 'bg-slate-600 text-slate-300' : 'bg-gray-100 text-gray-600'}`}>
                                  💰 {alt.cost}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
          </div>
        </div>
      )}

      {/* 3. CLIMATE CHANGE ANALYSIS */}
      {climateTrendDetails && (
        <div className={`border-2 rounded-xl p-6 ${
          isNightMode 
            ? 'bg-slate-800 border-slate-700' 
            : 'bg-white/90 border-gray-300'
        }`}>
          <h2 className={`text-2xl font-bold text-center mb-4 ${isNightMode ? 'text-slate-300' : 'text-gray-800'}`}>
            🌍 Climate Change Impact
          </h2>
          <p className={`text-center mb-6 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            Long-term climate trends detected over the past 20 years
          </p>

          {/* Visual Risk Indicator */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className={`text-sm font-medium ${isNightMode ? 'text-slate-300' : 'text-gray-700'}`}>
                Climate Trend Level
              </span>
              <span className={`text-sm font-bold ${
                climateTrendDetails.trend_status === 'SIGNIFICANT_WARMING' ? 'text-red-500' :
                climateTrendDetails.trend_status === 'WARMING_TREND' ? 'text-orange-500' :
                climateTrendDetails.trend_status === 'COOLING_TREND' ? 'text-blue-500' :
                'text-green-500'
              }`}>
                {climateTrendDetails.trend_status?.replace(/_/g, ' ')}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  climateTrendDetails.trend_status === 'SIGNIFICANT_WARMING' ? 'bg-gradient-to-r from-red-600 to-red-500' :
                  climateTrendDetails.trend_status === 'WARMING_TREND' ? 'bg-gradient-to-r from-orange-500 to-orange-400' :
                  climateTrendDetails.trend_status === 'COOLING_TREND' ? 'bg-gradient-to-r from-blue-500 to-blue-400' :
                  'bg-gradient-to-r from-green-500 to-green-400'
                }`}
                style={{ 
                  width: `${Math.min(100, Math.abs(climateTrendDetails.difference || 0) * 50)}%` 
                }}
              />
            </div>
          </div>

          {/* Detailed Data Grid */}
          <div className={`grid grid-cols-2 gap-3 ${isNightMode ? 'text-slate-300' : 'text-gray-700'}`}>
            <div className={`p-3 rounded-lg border-2 ${isNightMode ? 'bg-slate-800 border-slate-700' : 'bg-gray-100 border-gray-300'}`}>
              <div className="text-xs font-semibold mb-1 opacity-70">Temperature Change</div>
              <div className="text-xl font-bold">
                {climateTrendDetails.difference >= 0 ? '+' : ''}{climateTrendDetails.difference?.toFixed(2)}°C
              </div>
              </div>
            
            <div className={`p-3 rounded-lg border-2 ${isNightMode ? 'bg-slate-800 border-slate-700' : 'bg-gray-100 border-gray-300'}`}>
              <div className="text-xs font-semibold mb-1 opacity-70">Analysis Period</div>
              <div className="text-xl font-bold">20 years</div>
          </div>
        </div>

          {/* Comparison Info */}
          <div className={`mt-4 p-3 rounded-lg border-2 ${isNightMode ? 'bg-slate-800 border-slate-700' : 'bg-blue-50 border-blue-300'}`}>
            <p className={`text-xs text-center ${isNightMode ? 'text-slate-400' : 'text-blue-600'}`}>
              📊 Comparing first 5 years ({climateTrendDetails.early_years?.[0]}–{climateTrendDetails.early_years?.[climateTrendDetails.early_years?.length - 1]}) 
              vs last 5 years ({climateTrendDetails.recent_years?.[0]}–{climateTrendDetails.recent_years?.[climateTrendDetails.recent_years?.length - 1]})
              </p>
            </div>
          </div>
        )}
    </section>
  );
};

export default WeatherResults;
