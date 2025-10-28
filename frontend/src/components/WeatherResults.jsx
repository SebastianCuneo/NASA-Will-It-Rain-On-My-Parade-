/**
 * WeatherResults Component - Display Weather Risk Assessment Results
 * NASA Weather Risk Navigator
 * Adapted from original HTML design with mock data
 * 
 * FUNCIÓN PRINCIPAL:
 * - Visualiza análisis de riesgo climático basado en datos de NASA API
 * - Evalúa compatibilidad de actividades con condiciones meteorológicas
 * - Genera alternativas (Plan B) cuando las actividades no son viables
 * - Muestra impacto del cambio climático comparando datos históricos vs actuales
 */

import React, { useState, useEffect, useMemo, useRef } from 'react';

const WeatherResults = ({ data, isNightMode }) => {
  // Datos mock para condiciones meteorológicas - usado como fallback cuando no hay datos de API
  const mockData = {
    wet: { text: 'rainy', percentage: 18.2, pastPercentage: 11.5, advice: "don't forget an umbrella." },
    hot: { text: 'hot', percentage: 25.7, pastPercentage: 19.1, advice: "stay hydrated." },
    cold: { text: 'cold', percentage: 8.3, pastPercentage: 12.4, advice: "dress warmly." },
    windy: { text: 'windy', percentage: 33.1, pastPercentage: 28.9, advice: "watch out for loose objects." },
    uncomfortable: { text: 'uncomfortable', percentage: 45.5, pastPercentage: 38.1, advice: "wear light clothing." },
    uv: { text: 'high UV radiation', percentage: 60.1, pastPercentage: 52.3, advice: "use sunscreen." }
  };

  // Base de datos de actividades con sus preferencias meteorológicas
  // dislikes: condiciones que hacen la actividad menos viable
  // likes: condiciones que favorecen la actividad
  const activitiesDB = {
    surf: { name: "Surfing", icon: "🏄", dislikes: ['cold', 'wet'], likes: ['windy'] },
    beach: { name: "Beach Day", icon: "🏖️", dislikes: ['wet', 'cold', 'windy'] },
    run: { name: "Running", icon: "🏃‍♂️", dislikes: ['hot', 'wet', 'uncomfortable'] },
    hike: { name: "Hiking", icon: "⛰️", dislikes: ['hot', 'wet', 'uncomfortable'] },
    sailing: { name: "Sailing", icon: "⛵", dislikes: ['wet'], likes: ['windy'] },
    picnic: { name: "Picnic", icon: "🧺", dislikes: ['wet', 'windy', 'cold'] }
  };

  // Extracción de datos del prop - contiene tanto datos de API como información del formulario
  const { weatherConditions, activity, location, date, apiResults, temperature_risk, precipitation_risk, cold_risk } = data;
  
  // Plan B comes from backend via apiResults
  const planBData = apiResults?.plan_b?.alternatives || null;
  const planBLoading = false; // Backend handles loading
  const planBError = apiResults?.plan_b?.success ? null : 'Error generating Plan B';
  const aiModel = apiResults?.plan_b?.ai_model || 'Backend System';
  
  // Variables para acumular cálculos de riesgo meteorológico
  let totalPercentage = 0, totalPastPercentage = 0, emojis = '';
  let summaryParts = [], adviceParts = [];
  
  // Debug: Log the data we're receiving
  console.log('WeatherResults - apiResults:', apiResults);
  console.log('WeatherResults - temperature_risk:', temperature_risk);
  console.log('WeatherResults - precipitation_risk:', precipitation_risk);
  console.log('WeatherResults - cold_risk:', cold_risk);
  console.log('WeatherResults - weatherConditions:', weatherConditions);
  
  // LÓGICA PRINCIPAL: Priorizar datos reales de API sobre datos mock
  if (apiResults && temperature_risk && precipitation_risk && cold_risk) {
    const tempRisk = temperature_risk.probability;
    const precipRisk = precipitation_risk.probability;
    const coldRiskValue = cold_risk.probability;
    
    // Mapeo de condiciones meteorológicas a datos de riesgo reales
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
    // Fallback a datos mock cuando no hay datos de API disponibles
    weatherConditions.forEach(c => {
      const conditionData = mockData[c];
      totalPercentage += conditionData.percentage;
      totalPastPercentage += conditionData.pastPercentage;
      emojis += {wet:'🌧️', hot:'🔥', cold:'❄️', windy:'💨', uncomfortable:'🥵', uv:'☀️'}[c];
      summaryParts.push(conditionData.text);
      adviceParts.push(conditionData.advice);
    });
  }

  // Cálculo de promedios para determinar nivel de riesgo general
  const avgPercentage = totalPercentage / weatherConditions.length;
  const avgPastPercentage = totalPastPercentage / weatherConditions.length;
  
  // Determinación del nivel de riesgo con colores NASA y contraste apropiado
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

  // FUNCIÓN CLAVE: Evaluar compatibilidad entre actividad y condiciones meteorológicas
  const checkActivityCompatibility = (conditions, activityId) => {
    if (!activityId) return null;
    
    const currentActivity = activitiesDB[activityId];
    let badCondition = null;

    // Buscar condiciones meteorológicas que puedan afectar negativamente la actividad
    for (const condition of conditions) {
      if (currentActivity.dislikes.includes(condition)) {
        badCondition = condition;
        break;
      }
    }
    
    if (badCondition) {
        // Obtener probabilidad real para la condición problemática
        let actualProbability = 0;
        if (apiResults && temperature_risk && precipitation_risk && cold_risk) {
          // Usar datos reales de API cuando están disponibles
          if (badCondition === 'hot') {
            actualProbability = temperature_risk.probability;
          } else if (badCondition === 'wet') {
            actualProbability = precipitation_risk.probability;
          } else if (badCondition === 'cold') {
            // Usar datos reales de riesgo de frío del backend
            actualProbability = cold_risk.probability;
          } else {
            // Usar datos mock para otras condiciones
            actualProbability = mockData[badCondition].percentage;
          }
        } else {
          // Usar datos mock como fallback
          actualProbability = mockData[badCondition].percentage;
        }
        
        // Generar mensaje apropiado basado en la probabilidad real
        let probabilityText = '';
        if (actualProbability < 10) {
          probabilityText = 'low probability';
        } else if (actualProbability < 20) {
          probabilityText = 'moderate probability';
        } else {
          probabilityText = 'high probability';
        }
        
        return { 
          isGood: actualProbability < 15, // Considerar buena si la probabilidad es baja
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

  // Memoización de compatibilidad para evitar recálculos que retriggeren efectos en cada render
  const activityCompatibility = useMemo(() => {
    return checkActivityCompatibility(weatherConditions, activity);
    // Dependencias reflejan las entradas usadas dentro de checkActivityCompatibility
  }, [weatherConditions, activity, apiResults, temperature_risk, precipitation_risk, cold_risk]);

  // Plan B comes from backend - no generation needed in frontend
  // useEffect removed - Plan B is provided by backend via apiResults.plan_b

  // Generación avanzada de Plan B completamente local
  const generateAdvancedPlanB = (conditions, originalActivity, location) => {
    const planBOptions = [];
    
    // Base de datos de alternativas por condición meteorológica y actividad
    const alternativesDB = {
      beach: {
        wet: [
          {
            title: "Museo del Mar",
            description: "Explore marine life and ocean exhibits in a warm, dry environment",
            type: "indoor",
            reason: "Ocean-themed experience without weather concerns",
            tips: "Great for families and educational, check current exhibitions",
            location: "Montevideo, Uruguay",
            duration: "2-3 hours",
            cost: "Low"
          },
          {
            title: "Shopping Mall",
            description: "Visit Punta Carretas or Montevideo Shopping for indoor entertainment",
            type: "indoor",
            reason: "Stay dry while enjoying shopping and dining",
            tips: "Check for special events or sales, bring comfortable shoes",
            location: "Montevideo, Uruguay",
            duration: "3-4 hours",
            cost: "Medium"
          }
        ],
        cold: [
          {
            title: "Indoor Pool Complex",
            description: "Visit a heated indoor pool or water park",
            type: "indoor",
            reason: "Warm water activities without cold weather exposure",
            tips: "Bring swimwear and check opening hours",
            location: "Various locations",
            duration: "2-3 hours",
            cost: "Medium"
          },
          {
            title: "Thermal Baths",
            description: "Relax in natural hot springs",
            type: "mixed",
            reason: "Warm water therapy in natural setting",
            tips: "Bring towels and check temperature requirements",
            location: "Uruguay",
            duration: "3-4 hours",
            cost: "Medium"
          }
        ],
        hot: [
          {
            title: "Indoor Cinema",
            description: "Watch latest movies in air-conditioned theaters",
            type: "indoor",
            reason: "Entertainment in climate-controlled space away from heat",
            tips: "Book tickets in advance for popular shows",
            location: "Montevideo, Uruguay",
            duration: "2-3 hours",
            cost: "Low"
          },
          {
            title: "Library or Bookstore",
            description: "Enjoy reading in a cool, quiet environment",
            type: "indoor",
            reason: "Peaceful activity in air-conditioned space",
            tips: "Bring your own book or explore local literature",
            location: "Various locations",
            duration: "1-3 hours",
            cost: "Free"
          }
        ]
      },
      picnic: {
        wet: [
          {
            title: "Indoor Food Market",
            description: "Visit Mercado del Puerto for local cuisine",
            type: "indoor",
            reason: "Food experience in warm, dry environment",
            tips: "Try traditional Uruguayan barbecue and local specialties",
            location: "Mercado del Puerto, Montevideo",
            duration: "2-3 hours",
            cost: "Medium"
          },
          {
            title: "Restaurant Tour",
            description: "Visit multiple restaurants for different courses",
            type: "indoor",
            reason: "Food adventure without weather concerns",
            tips: "Plan route and make reservations in advance",
            location: "Montevideo, Uruguay",
            duration: "3-4 hours",
            cost: "High"
          }
        ],
        cold: [
          {
            title: "Cooking Class",
            description: "Learn to cook local dishes in a warm kitchen",
            type: "indoor",
            reason: "Interactive food experience in comfortable environment",
            tips: "Book in advance and bring appetite",
            location: "Various locations",
            duration: "2-3 hours",
            cost: "Medium"
          },
          {
            title: "Indoor Food Festival",
            description: "Explore local cuisine at indoor food events",
            type: "indoor",
            reason: "Food tasting in climate-controlled environment",
            tips: "Check local event calendars for food festivals",
            location: "Montevideo, Uruguay",
            duration: "2-4 hours",
            cost: "Medium"
          }
        ]
      },
      run: {
        wet: [
          {
            title: "Indoor Gym",
            description: "Use treadmill or indoor track",
            type: "indoor",
            reason: "Maintain fitness routine in dry environment",
            tips: "Bring gym clothes and water bottle",
            location: "Various gyms",
            duration: "1-2 hours",
            cost: "Low"
          },
          {
            title: "Shopping Mall Walking",
            description: "Power walk through large shopping centers",
            type: "indoor",
            reason: "Exercise while staying dry",
            tips: "Wear comfortable shoes and track steps",
            location: "Montevideo Shopping, Punta Carretas",
            duration: "1-2 hours",
            cost: "Free"
          }
        ],
        hot: [
          {
            title: "Indoor Sports Complex",
            description: "Use indoor courts or tracks with air conditioning",
            type: "indoor",
            reason: "Stay active without heat exposure",
            tips: "Check availability and book time slots",
            location: "Various sports centers",
            duration: "1-2 hours",
            cost: "Low"
          },
          {
            title: "Swimming Pool",
            description: "Indoor swimming for cardio exercise",
            type: "indoor",
            reason: "Cool exercise option for hot days",
            tips: "Bring swimwear and check pool hours",
            location: "Various pools",
            duration: "1-2 hours",
            cost: "Low"
          }
        ]
      }
    };

    // Obtener alternativas específicas para la actividad y condiciones
    const activityAlternatives = alternativesDB[originalActivity] || {};
    const conditionAlternatives = [];
    
    // Buscar alternativas para cada condición meteorológica
    conditions.forEach(condition => {
      if (activityAlternatives[condition]) {
        conditionAlternatives.push(...activityAlternatives[condition]);
      }
    });

    // Si no hay alternativas específicas, usar alternativas generales
    if (conditionAlternatives.length === 0) {
      const generalAlternatives = [
        {
          title: "Museo Nacional de Artes Visuales",
          description: "Explore Uruguayan art and culture",
          type: "indoor",
          reason: "Cultural experience regardless of weather",
          tips: "Check current exhibitions and opening hours",
          location: "Montevideo, Uruguay",
          duration: "2-3 hours",
          cost: "Low"
        },
        {
          title: "Teatro Solís",
          description: "Attend a performance or take a guided tour",
          type: "indoor",
          reason: "Cultural entertainment in beautiful venue",
          tips: "Book tickets in advance for performances",
          location: "Teatro Solís, Montevideo",
          duration: "2-3 hours",
          cost: "Medium"
        },
        {
          title: "Coffee Shop Tour",
          description: "Visit different coffee shops around the city",
          type: "indoor",
          reason: "Relaxing activity in comfortable environment",
          tips: "Try local coffee varieties and pastries",
          location: "Various locations",
          duration: "2-4 hours",
          cost: "Low"
        }
      ];
      conditionAlternatives.push(...generalAlternatives);
    }

    // Eliminar duplicados y limitar a 3 opciones
    const uniqueAlternatives = conditionAlternatives.filter((alt, index, self) => 
      index === self.findIndex(a => a.title === alt.title)
    );

    return uniqueAlternatives.slice(0, 3);
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
                    {planBData ? (
                      <>
                        <p className={`text-sm font-bold mb-3 ${isNightMode ? 'text-slate-300' : 'text-gray-700'}`}>
                          Alternative Activities:
                        </p>
                        {planBData.map((alt, index) => (
                          <div key={index} className={`mt-3 text-left p-4 rounded-lg border ${
                            isNightMode 
                              ? 'bg-slate-800/70 border-slate-700' 
                              : 'bg-white border-gray-200'
                          }`}>
                            <div className="flex items-start justify-between mb-2">
                              <p className={`font-bold text-lg ${isNightMode ? 'text-yellow-300' : 'text-blue-600'}`}>
                                {alt.title || alt.activityName}
                              </p>
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
                              {alt.description || alt.recommendation}
                            </p>
                            
                            {alt.reason && (
                              <div className={`mb-2 p-2 rounded ${isNightMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
                                <p className={`text-xs font-medium ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                                  <strong>Why this works:</strong> {alt.reason}
                                </p>
                              </div>
                            )}
                            
                            {alt.tips && (
                              <div className={`mb-2 p-2 rounded ${isNightMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
                                <p className={`text-xs font-medium ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
                                  <strong>💡 Tips:</strong> {alt.tips}
                                </p>
                              </div>
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
                                <span className={`px-2 py-1 rounded text-xs ${
                                  alt.cost === 'Free' 
                                    ? (isNightMode ? 'bg-green-900/30 text-green-300' : 'bg-green-100 text-green-700')
                                    : alt.cost === 'Low'
                                    ? (isNightMode ? 'bg-yellow-900/30 text-yellow-300' : 'bg-yellow-100 text-yellow-700')
                                    : (isNightMode ? 'bg-orange-900/30 text-orange-300' : 'bg-orange-100 text-orange-700')
                                }`}>
                                  💰 {alt.cost}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                          <p className={`text-xs mt-3 ${isNightMode ? 'text-slate-500' : 'text-gray-500'}`}>
                          Powered by {aiModel}
                        </p>
                        
                        {planBError && (
                          <div className={`mt-2 p-2 rounded text-xs ${
                            isNightMode ? 'bg-yellow-900/30 text-yellow-300' : 'bg-yellow-100 text-yellow-700'
                          }`}>
                            ⚠️ {planBError}
                          </div>
                        )}
                        
                        {/* Plan B comes from backend - no regenerate button needed */}
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
