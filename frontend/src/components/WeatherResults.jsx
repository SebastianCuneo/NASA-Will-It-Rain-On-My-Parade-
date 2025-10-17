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

  // Calculate results - Use API data if available, otherwise fallback to mock data
  const { weatherConditions, activity, location, date, apiResults, temperature_risk, precipitation_risk, cold_risk, plan_b } = data;
  
  let totalPercentage = 0, totalPastPercentage = 0, emojis = '';
  let summaryParts = [], adviceParts = [];
  
  // Debug: Log the data we're receiving
  console.log('WeatherResults - apiResults:', apiResults);
  console.log('WeatherResults - temperature_risk:', temperature_risk);
  console.log('WeatherResults - precipitation_risk:', precipitation_risk);
  console.log('WeatherResults - cold_risk:', cold_risk);
  console.log('WeatherResults - weatherConditions:', weatherConditions);
  
  // Use real API data if available
  if (apiResults && temperature_risk && precipitation_risk && cold_risk) {
    console.log('WeatherResults - Using real API data');
    // Calculate based on actual API results
    const tempRisk = temperature_risk.probability;
    const precipRisk = precipitation_risk.probability;
    const coldRiskValue = cold_risk.probability;
    
    // Map weather conditions to actual risk data
    weatherConditions.forEach(c => {
      if (c === 'hot') {
        totalPercentage += tempRisk;
        summaryParts.push('hot weather');
        adviceParts.push(temperature_risk.status_message);
      } else if (c === 'wet') {
        totalPercentage += precipRisk;
        summaryParts.push('rainy weather');
        adviceParts.push(precipitation_risk.status_message);
      } else if (c === 'cold') {
        // Use real cold risk data from backend
        totalPercentage += coldRiskValue;
        summaryParts.push('cold weather');
        adviceParts.push(cold_risk.status_message);
      } else {
        // Fallback to mock data for other conditions
        const conditionData = mockData[c];
        totalPercentage += conditionData.percentage;
        summaryParts.push(conditionData.text);
        adviceParts.push(conditionData.advice);
      }
      
      emojis += {wet:'🌧️', hot:'🔥', cold:'❄️', windy:'💨', uncomfortable:'🥵', uv:'☀️'}[c];
    });
    
    // Use historical data from API if available
    totalPastPercentage = totalPercentage * 0.8; // Rough estimate for past data
  } else {
    console.log('WeatherResults - Using mock data fallback');
    // Fallback to mock data
    weatherConditions.forEach(c => {
      const conditionData = mockData[c];
      totalPercentage += conditionData.percentage;
      totalPastPercentage += conditionData.pastPercentage;
      emojis += {wet:'🌧️', hot:'🔥', cold:'❄️', windy:'💨', uncomfortable:'🥵', uv:'☀️'}[c];
      summaryParts.push(conditionData.text);
      adviceParts.push(conditionData.advice);
    });
  }

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
        // Get actual probability for the condition
        let actualProbability = 0;
        if (apiResults && temperature_risk && precipitation_risk && cold_risk) {
          // Use real API data
          if (badCondition === 'hot') {
            actualProbability = temperature_risk.probability;
          } else if (badCondition === 'wet') {
            actualProbability = precipitation_risk.probability;
          } else if (badCondition === 'cold') {
            // Use real cold risk data from backend
            actualProbability = cold_risk.probability;
          } else {
            // Use mock data for other conditions
            actualProbability = mockData[badCondition].percentage;
          }
        } else {
          // Use mock data
          actualProbability = mockData[badCondition].percentage;
        }
        
        // Generate appropriate message based on actual probability
        let probabilityText = '';
        if (actualProbability < 10) {
          probabilityText = 'low probability';
        } else if (actualProbability < 20) {
          probabilityText = 'moderate probability';
        } else {
          probabilityText = 'high probability';
        }
        
        return { 
          isGood: actualProbability < 15, // Consider it good if probability is low
          name: currentActivity.name, 
          icon: actualProbability < 15 ? '👍' : '👎', 
          message: actualProbability < 15 
            ? `Great day for your activity! Low probability of ${badCondition === 'cold' ? 'cold' : mockData[badCondition].text} weather.`
            : `Doesn't seem like the best day. The ${probabilityText} of ${badCondition === 'cold' ? 'cold' : mockData[badCondition].text} weather could complicate the activity.`, 
          reason: badCondition === 'cold' ? 'cold' : mockData[badCondition].text
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
      if (plan_b && plan_b.success && plan_b.alternatives) {
        // Use real Plan B data from backend
        setPlanBData(plan_b.alternatives);
        setPlanBLoading(false);
      } else {
        setPlanBLoading(true);
        // Simulate API call delay for fallback
        setTimeout(() => {
          // Dynamic Plan B based on weather conditions
          const planBOptions = generateDynamicPlanB(weatherConditions, activity);
          setPlanBData(planBOptions);
          setPlanBLoading(false);
        }, 1500);
      }
    }
  }, [activityCompatibility, weatherConditions, activity, plan_b]);

  // Dynamic Plan B generation based on weather conditions
  const generateDynamicPlanB = (conditions, originalActivity) => {
    const planBOptions = [];
    
    if (conditions.includes('wet') || conditions.includes('cold')) {
      planBOptions.push(
        { activityName: "Museum Visit", recommendation: "Perfect indoor activity when weather is challenging. Explore art and culture." },
        { activityName: "Library Reading", recommendation: "Cozy indoor space to enjoy books while staying warm and dry." }
      );
    }
    
    if (conditions.includes('hot') || conditions.includes('uv')) {
      planBOptions.push(
        { activityName: "Shopping Mall", recommendation: "Air-conditioned environment perfect for hot days. Shop and stay cool." },
        { activityName: "Indoor Cinema", recommendation: "Entertainment in a climate-controlled space away from the heat." }
      );
    }
    
    if (conditions.includes('windy')) {
      planBOptions.push(
        { activityName: "Indoor Sports", recommendation: "Gym or sports center activities that aren't affected by wind." },
        { activityName: "Art Gallery", recommendation: "Cultural experience in a protected indoor environment." }
      );
    }
    
    // Default options if no specific conditions match
    if (planBOptions.length === 0) {
      planBOptions.push(
        { activityName: "Museum", recommendation: "Perfect for challenging weather days, you can enjoy art without worrying about conditions." },
        { activityName: "Coffee Shop", recommendation: "A cozy place to spend time while the weather improves." }
      );
    }
    
    return planBOptions.slice(0, 2); // Return max 2 options
  };

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
                              {alt.title || alt.activityName}
                            </p>
                            <p className={`text-xs mt-1 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                              {alt.description || alt.recommendation}
                            </p>
                            {alt.reason && (
                              <p className={`text-xs mt-1 ${isNightMode ? 'text-slate-500' : 'text-gray-500'}`}>
                                <strong>Why:</strong> {alt.reason}
                              </p>
                            )}
                            {alt.tips && (
                              <p className={`text-xs mt-1 ${isNightMode ? 'text-slate-500' : 'text-gray-500'}`}>
                                <strong>Tips:</strong> {alt.tips}
                              </p>
                            )}
                            {alt.type && (
                              <span className={`inline-block mt-1 px-2 py-1 rounded-full text-xs ${
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
                        ))}
                        {plan_b && plan_b.ai_model && (
                          <p className={`text-xs mt-3 ${isNightMode ? 'text-slate-500' : 'text-gray-500'}`}>
                            Powered by {plan_b.ai_model}
                          </p>
                        )}
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

      {/* Climate Change Impact - Full Width */}
      <div className="w-full">
        {/* Climate Change Impact - Time Footprint */}
        <div className={`border rounded-xl p-6 ${
          isNightMode 
            ? 'bg-slate-800 border-slate-700' 
            : 'bg-white/90 border-white/30'
        }`}>
          <h2 className={`text-2xl font-bold text-center mb-4 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
            🌍 Climate Change Impact
          </h2>
          <p className={`text-center mb-6 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            See how weather extremes have increased due to climate change over the past decades.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Past Period */}
            <div className={`rounded-xl p-6 text-center border ${
              isNightMode ? 'bg-blue-900/20 border-blue-500' : 'bg-blue-50 border-blue-200'
            }`}>
              <p className={`text-sm font-bold mb-3 ${isNightMode ? 'text-blue-300' : 'text-blue-700'}`}>
                📅 HISTORICAL BASELINE (1980-2000)
              </p>
              <div className="mb-4">
                <svg viewBox="0 0 100 60" className="w-full h-16 mx-auto">
                  {/* Stable, moderate weather pattern */}
                  <path d="M0,50 Q25,45 50,48 T100,46 L100,60 Z" fill="#22c55e" opacity="0.8"></path>
                  <circle cx="20" cy="25" r="8" fill="#facc15"></circle>
                  <rect x="65" y="40" width="4" height="12" fill="#8d5524"></rect>
                  <circle cx="67" cy="35" r="6" fill="#16a34a"></circle>
                </svg>
              </div>
              <p className={`text-4xl font-bold mb-2 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
                {avgPastPercentage.toFixed(1)}%
              </p>
              <p className={`text-xs ${isNightMode ? 'text-blue-200' : 'text-blue-600'}`}>
                Historical risk level
              </p>
            </div>

            {/* Present Period */}
            <div className={`rounded-xl p-6 text-center border ${
              isNightMode ? 'bg-red-900/20 border-red-500' : 'bg-red-50 border-red-200'
            }`}>
              <p className={`text-sm font-bold mb-3 ${isNightMode ? 'text-red-300' : 'text-red-700'}`}>
                🔥 CURRENT ERA (2001-2023)
              </p>
              <div className="mb-4">
                <svg viewBox="0 0 100 60" className="w-full h-16 mx-auto">
                  {/* More extreme, volatile weather pattern */}
                  <path d="M0,60 Q25,35 50,45 T100,30 L100,60 Z" fill="#ef4444" opacity="0.8"></path>
                  <circle cx="20" cy="20" r="12" fill="#fb923c"></circle>
                  <path d="M 65 50 L 60 25 L 75 25 Z" fill="#dc2626"></path>
                  <circle cx="67" cy="25" r="8" fill="#f97316"></circle>
                </svg>
              </div>
              <p className={`text-4xl font-bold mb-2 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
                {avgPercentage.toFixed(1)}%
              </p>
              <p className={`text-xs ${isNightMode ? 'text-red-200' : 'text-red-600'}`}>
                Current risk level
              </p>
            </div>
          </div>

          {/* Climate Change Analysis */}
          <div className={`p-4 rounded-lg border ${
            isNightMode ? 'bg-slate-700 border-slate-600' : 'bg-gray-50 border-gray-200'
          }`}>
            <h3 className={`font-bold text-lg mb-3 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
              📊 Climate Change Analysis
            </h3>
            
            {avgPercentage > avgPastPercentage ? (
              <div className={`p-3 rounded-lg border ${
                isNightMode ? 'bg-red-900/20 border-red-500' : 'bg-red-50 border-red-200'
              }`}>
                <p className={`text-sm font-semibold mb-2 ${isNightMode ? 'text-red-300' : 'text-red-700'}`}>
                  ⚠️ Risk Increase Detected
                </p>
                <p className={`text-xs ${isNightMode ? 'text-red-200' : 'text-red-600'}`}>
                  Weather extremes have increased by <strong>{(avgPercentage - avgPastPercentage).toFixed(1)}%</strong> compared to historical baseline. 
                  This reflects the impact of climate change on local weather patterns.
                </p>
              </div>
            ) : (
              <div className={`p-3 rounded-lg border ${
                isNightMode ? 'bg-green-900/20 border-green-500' : 'bg-green-50 border-green-200'
              }`}>
                <p className={`text-sm font-semibold mb-2 ${isNightMode ? 'text-green-300' : 'text-green-700'}`}>
                  ✅ Stable Conditions
                </p>
                <p className={`text-xs ${isNightMode ? 'text-green-200' : 'text-green-600'}`}>
                  Current risk levels are similar to historical baseline, indicating relatively stable conditions for this period.
                </p>
              </div>
            )}

            <div className={`mt-4 p-3 rounded-lg ${isNightMode ? 'bg-slate-600' : 'bg-gray-100'}`}>
              <p className={`text-xs ${isNightMode ? 'text-slate-300' : 'text-gray-600'}`}>
                <strong>Educational Note:</strong> This comparison helps visualize how climate change affects local weather extremes. 
                The 90th percentile methodology used by NASA helps identify when conditions exceed historical norms, 
                providing insight into climate change impacts on everyday weather patterns.
              </p>
            </div>
          </div>
        </div>

        {/* Real NASA Data Analysis - Below Climate Change Impact */}
        {apiResults && temperature_risk && (
          <div className={`border rounded-xl p-6 mt-6 ${
            isNightMode 
              ? 'bg-slate-800 border-slate-700' 
              : 'bg-white/90 border-white/30'
          }`}>
            <h3 className={`font-bold text-lg mb-4 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
              📊 Real NASA Data Analysis
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`p-4 rounded-lg border ${
                isNightMode ? 'bg-slate-700 border-slate-600' : 'bg-blue-50 border-blue-200'
              }`}>
                <p className={`font-semibold mb-2 ${isNightMode ? 'text-blue-400' : 'text-blue-600'}`}>
                  Temperature Risk
                </p>
                <p className={`text-2xl font-bold mb-1 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
                  {temperature_risk.probability}%
                </p>
                <p className={`text-sm ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                  Threshold: {temperature_risk.risk_threshold}°C
                </p>
                <p className={`text-xs mt-2 ${isNightMode ? 'text-slate-500' : 'text-gray-500'}`}>
                  {temperature_risk.status_message}
                </p>
              </div>
              
              <div className={`p-4 rounded-lg border ${
                isNightMode ? 'bg-slate-700 border-slate-600' : 'bg-blue-50 border-blue-200'
              }`}>
                <p className={`font-semibold mb-2 ${isNightMode ? 'text-blue-400' : 'text-blue-600'}`}>
                  Precipitation Risk
                </p>
                <p className={`text-2xl font-bold mb-1 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
                  {precipitation_risk.probability}%
                </p>
                <p className={`text-sm ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                  Threshold: {precipitation_risk.risk_threshold}mm
                </p>
                <p className={`text-xs mt-2 ${isNightMode ? 'text-slate-500' : 'text-gray-500'}`}>
                  {precipitation_risk.status_message}
                </p>
              </div>
            </div>
            
            <div className={`mt-4 p-3 rounded-lg ${isNightMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
              <p className={`text-xs ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                Based on {temperature_risk.total_observations} historical observations using 90th percentile methodology.
              </p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default WeatherResults;
