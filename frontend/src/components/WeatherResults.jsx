/**
 * WeatherResults Component - Display Weather Risk Assessment Results
 * NASA Weather Risk Navigator
 * Adapted from original HTML design with mock data
 */

import React, { useState, useEffect } from 'react';

const WeatherResults = ({ data, isNightMode }) => {
  const [planBData, setPlanBData] = useState(null);
  const [planBLoading, setPlanBLoading] = useState(false);

  // Mock data for weather conditions
  const mockData = {
    wet: { text: 'rainy', percentage: 18.2, pastPercentage: 11.5, advice: "don't forget an umbrella." },
    hot: { text: 'hot', percentage: 25.7, pastPercentage: 19.1, advice: "stay hydrated." },
    cold: { text: 'cold', percentage: 8.3, pastPercentage: 12.4, advice: "dress warmly." },
    windy: { text: 'windy', percentage: 33.1, pastPercentage: 28.9, advice: "watch out for loose objects." },
    uncomfortable: { text: 'uncomfortable', percentage: 45.5, pastPercentage: 38.1, advice: "wear light clothing." },
    uv: { text: 'high UV radiation', percentage: 60.1, pastPercentage: 52.3, advice: "use sunscreen." }
  };

  const activitiesDB = {
    surf: { name: "Surfing", icon: "🏄", dislikes: ['cold', 'wet'], likes: ['windy'] },
    beach: { name: "Beach Day", icon: "🏖️", dislikes: ['wet', 'cold', 'windy'] },
    run: { name: "Running", icon: "🏃‍♂️", dislikes: ['hot', 'wet', 'uncomfortable'] },
    hike: { name: "Hiking", icon: "⛰️", dislikes: ['hot', 'wet', 'uncomfortable'] },
    sailing: { name: "Sailing", icon: "⛵", dislikes: ['wet'], likes: ['windy'] },
    picnic: { name: "Picnic", icon: "🧺", dislikes: ['wet', 'windy', 'cold'] }
  };

  // Calculate results
  const { weatherConditions, activity, location, date } = data;
  
  let totalPercentage = 0, totalPastPercentage = 0, emojis = '';
  let summaryParts = [], adviceParts = [];
  
  weatherConditions.forEach(c => {
    const conditionData = mockData[c];
    totalPercentage += conditionData.percentage;
    totalPastPercentage += conditionData.pastPercentage;
    emojis += {wet:'🌧️', hot:'🔥', cold:'❄️', windy:'💨', uncomfortable:'🥵', uv:'☀️'}[c];
    summaryParts.push(conditionData.text);
    adviceParts.push(conditionData.advice);
  });

  const avgPercentage = totalPercentage / weatherConditions.length;
  const avgPastPercentage = totalPastPercentage / weatherConditions.length;
  
  // Determine risk level with NASA colors and proper contrast
  let riskLevel, riskColorStyle;
  if (avgPercentage < 20) { 
    riskLevel = 'Low'; 
    riskColorStyle = {
      backgroundColor: isNightMode ? 'rgba(231, 244, 52, 0.2)' : 'rgba(231, 244, 52, 0.3)', 
      color: isNightMode ? 'var(--nasa-yellow)' : '#2d3748',
      border: `1px solid ${isNightMode ? 'var(--nasa-yellow)' : '#e2e8f0'}`
    }; 
  } else if (avgPercentage < 40) { 
    riskLevel = 'Moderate'; 
    riskColorStyle = {
      backgroundColor: isNightMode ? 'rgba(11, 61, 145, 0.2)' : 'rgba(11, 61, 145, 0.1)', 
      color: isNightMode ? 'var(--nasa-blue)' : '#2d3748',
      border: `1px solid ${isNightMode ? 'var(--nasa-blue)' : '#e2e8f0'}`
    }; 
  } else { 
    riskLevel = 'High'; 
    riskColorStyle = {
      backgroundColor: isNightMode ? 'rgba(252, 61, 33, 0.2)' : 'rgba(252, 61, 33, 0.1)', 
      color: isNightMode ? 'var(--nasa-red)' : '#2d3748',
      border: `1px solid ${isNightMode ? 'var(--nasa-red)' : '#e2e8f0'}`
    }; 
  }

  // Check activity compatibility
  const checkActivityCompatibility = (conditions, activityId) => {
    if (!activityId) return null;
    
    const currentActivity = activitiesDB[activityId];
    let badCondition = null;

    for (const condition of conditions) {
      if (currentActivity.dislikes.includes(condition)) {
        badCondition = condition;
        break;
      }
    }
    
    if (badCondition) {
        return { 
          isGood: false, 
          name: currentActivity.name, 
          icon: '👎', 
          message: `Doesn't seem like the best day. The high probability of ${mockData[badCondition].text} weather could complicate the activity.`, 
          reason: mockData[badCondition].text 
        };
    } else {
      return { 
        isGood: true, 
        name: currentActivity.name, 
        icon: '👍', 
        message: `Looks like an excellent day for your activity! The conditions are favorable.` 
      };
    }
  };

  const suggestActivities = (conditions) => {
    let suggestions = [];
    if (!conditions.includes('wet') && !conditions.includes('cold') && !conditions.includes('windy')) suggestions.push('🧺');
    if (!conditions.includes('wet') && !conditions.includes('cold')) suggestions.push('🏖️');
    if (!conditions.includes('hot') && !conditions.includes('wet')) suggestions.push('🏃‍♂️', '⛰️');
    if (conditions.includes('windy') && !conditions.includes('wet')) suggestions.push('⛵');
    if(suggestions.length === 0) return ['🏠'];
    return suggestions;
  };

  const activityCompatibility = checkActivityCompatibility(weatherConditions, activity);

  // Generate Plan B if activity is not compatible
  useEffect(() => {
    if (activityCompatibility && !activityCompatibility.isGood) {
      setPlanBLoading(true);
      // Simulate API call delay
      setTimeout(() => {
                    setPlanBData([
                      { activityName: "Museum", recommendation: "Perfect for rainy days, you can enjoy art without worrying about the weather." },
                      { activityName: "Coffee Shop", recommendation: "A cozy place to spend time while the weather improves." }
                    ]);
        setPlanBLoading(false);
      }, 1500);
    }
  }, [activityCompatibility]);

  return (
    <section className="fade-in space-y-6">
      {/* Top Row: Activity Analysis and Weather Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Result Card */}
        <div id="activity-result-card" className={`border rounded-xl p-6 shadow-2xl ${
          isNightMode 
            ? 'bg-slate-800 border-slate-700 shadow-blue-500/10' 
            : 'bg-white/90 border-white/30 shadow-blue-500/5'
        }`}>
          <p id="activity-title" className={`text-center font-bold text-xl mb-4 ${
            isNightMode ? 'text-white' : 'text-gray-800'
          }`}>
            {activity ? `Analysis for: ${activityCompatibility.name}` : "Activity Suggestions"}
          </p>
          <div id="activity-recommendation" className="text-center">
            {activity ? (
              <>
                <p className="text-4xl mb-3">{activityCompatibility.icon}</p>
                <p className={`text-lg ${isNightMode ? 'text-slate-300' : 'text-gray-600'}`}>
                  {activityCompatibility.message}
                </p>
                
                {!activityCompatibility.isGood && (
                  <div className={`mt-4 p-4 rounded-lg ${
                    isNightMode ? 'bg-slate-900' : 'bg-gray-100'
                  }`}>
                    <p className="text-sm font-bold text-red-400 mb-3">Plan B Active! ✨</p>
                    {planBLoading ? (
                      <p className={isNightMode ? 'text-slate-400' : 'text-gray-500'}>Generating alternatives...</p>
                    ) : planBData ? (
                      <>
                        <p className={`text-sm font-bold mb-3 ${isNightMode ? 'text-slate-300' : 'text-gray-700'}`}>
                          Alternative Activities:
                        </p>
                        {planBData.map((alt, index) => (
                          <div key={index} className={`mt-3 text-left p-3 rounded-md ${
                            isNightMode 
                              ? 'bg-slate-800/70 border border-slate-700' 
                              : 'bg-white border border-gray-200'
                          }`}>
                            <p className={`font-bold ${isNightMode ? 'text-yellow-300' : 'text-blue-600'}`}>
                              {alt.activityName}
                            </p>
                            <p className={`text-xs mt-1 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                              {alt.recommendation}
                            </p>
                          </div>
                        ))}
                      </>
                    ) : null}
                  </div>
                )}
              </>
            ) : (
              <>
                <p className={isNightMode ? 'text-slate-300' : 'text-gray-600'}>
                  Based on the weather, today could be a good day for:
                </p>
                <p className="text-4xl mt-4">{suggestActivities(weatherConditions).join(' ')}</p>
              </>
            )}
          </div>
        </div>

        {/* Weather Summary Card */}
        <div id="result-card" className={`border rounded-xl p-6 text-center ${
          isNightMode 
            ? 'bg-slate-800 border-slate-700' 
            : 'bg-white/90 border-white/30'
        }`}>
          <p className={`font-bold mb-4 text-xl ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
            Weather Summary
          </p>
          <div id="result-emojis" className="text-5xl mb-4 flex justify-center gap-x-3">{emojis}</div>
          <p className={`text-lg ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            Combined probability:
          </p>
          <p className={`text-6xl font-black my-3 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
            {avgPercentage.toFixed(1)}%
          </p>
          <div className="flex justify-center mt-4">
            <span className="text-sm font-bold px-6 py-2 rounded-full" style={riskColorStyle}>
              {riskLevel} Risk
            </span>
          </div>
          
          {/* General Recommendation */}
          <div id="summary-message-container" className={`mt-6 text-left p-4 rounded-lg border ${
            isNightMode 
              ? 'bg-slate-900/50 border-slate-700' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <p className={`font-bold text-lg ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
              General Recommendation:
            </p>
            <p className={`${isNightMode ? 'text-slate-300' : 'text-gray-600'}`}>
              Therefore, {adviceParts.join(" Also, ")}
            </p>
          </div>
        </div>
      </div>

      {/* Bottom Row: Time Footprint and Historical Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time Footprint */}
        <div className={`border rounded-xl p-6 ${
          isNightMode 
            ? 'bg-slate-800 border-slate-700' 
            : 'bg-white/90 border-white/30'
        }`}>
          <h2 className={`text-2xl font-bold text-center mb-4 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
            Time Footprint
          </h2>
          <p className={`text-center mb-6 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            How the risk of these conditions has changed over time.
          </p>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="border rounded-xl p-4" style={{
              backgroundColor: isNightMode ? 'rgba(11, 61, 145, 0.3)' : 'rgba(11, 61, 145, 0.1)',
              borderColor: 'var(--nasa-blue)',
              color: isNightMode ? 'var(--nasa-white)' : '#2d3748'
            }}>
              <p className="text-sm font-bold mb-3" style={{color: isNightMode ? 'var(--nasa-blue)' : '#1a365d'}}>PAST (1980-2000)</p>
              <svg viewBox="0 0 100 60" className="w-full h-auto my-3">
                <path d="M0,60 Q25,40 50,50 T100,45 L100,60 Z" fill="#22c55e"></path>
                <circle cx="20" cy="20" r="10" fill="#facc15"></circle>
                <rect x="65" y="35" width="5" height="15" fill="#8d5524"></rect>
                <circle cx="67.5" cy="30" r="8" fill="#16a34a"></circle>
              </svg>
              <p className="text-3xl font-bold" style={{color: isNightMode ? 'var(--nasa-white)' : '#2d3748'}}>
                {avgPastPercentage.toFixed(1)}%
              </p>
            </div>
                      <div className="rounded-xl p-4" style={{
                        backgroundColor: isNightMode ? 'rgba(252, 61, 33, 0.2)' : 'rgba(252, 61, 33, 0.1)', 
                        border: '1px solid var(--nasa-red)',
                        color: isNightMode ? 'var(--nasa-white)' : '#2d3748'
                      }}>
                        <p className="text-sm font-bold mb-3" style={{color: isNightMode ? 'var(--nasa-red)' : '#c53030'}}>
                          PRESENT (2001-2023)
                        </p>
              <svg viewBox="0 0 100 60" className="w-full h-auto my-3">
                <path d="M0,60 Q25,50 50,52 T100,48 L100,60 Z" fill="#a16207"></path>
                <circle cx="20" cy="20" r="12" fill="#fb923c"></circle>
                <path d="M 65 50 L 63 35 L 70 35 Z" fill="#5c4033"></path>
              </svg>
              <p className="text-3xl font-bold" style={{color: isNightMode ? 'var(--nasa-white)' : '#2d3748'}}>{avgPercentage.toFixed(1)}%</p>
            </div>
          </div>
        </div>

        {/* Historical Distribution */}
        <div className={`border rounded-xl p-6 ${
          isNightMode 
            ? 'bg-slate-800 border-slate-700' 
            : 'bg-white/90 border-white/30'
        }`}>
          <h3 className={`font-bold text-lg mb-2 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
            Historical Distribution
          </h3>
          <p className={`text-sm mb-4 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            Frequency chart of historical measurements. The red line marks the 10% most extreme threshold.
          </p>
          <div className={`h-48 w-full rounded-lg flex items-center justify-center text-xs ${
            isNightMode ? 'bg-slate-700 text-slate-500' : 'bg-gray-100 text-gray-500'
          }`}>
            [ Bar chart (histogram) would go here ]
          </div>
          <button className={`mt-6 w-full font-bold py-3 px-4 rounded-lg transition-colors ${
            isNightMode 
              ? 'bg-slate-700 hover:bg-slate-600 text-white' 
              : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
          }`}>
            Download Data (CSV)
          </button>
        </div>
      </div>
    </section>
  );
};

export default WeatherResults;
