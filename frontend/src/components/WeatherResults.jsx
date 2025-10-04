/**
 * WeatherResults Component - Display Weather Risk Assessment Results
 * Adapted from original HTML design with mock data
 */

import React, { useState, useEffect } from 'react';

const WeatherResults = ({ data, isNightMode }) => {
  const [planBData, setPlanBData] = useState(null);
  const [planBLoading, setPlanBLoading] = useState(false);

  // Mock data for weather conditions
  const mockData = {
    wet: { text: 'lluvioso', percentage: 18.2, pastPercentage: 11.5, advice: "no olvides un paraguas." },
    hot: { text: 'caluroso', percentage: 25.7, pastPercentage: 19.1, advice: "mantente hidratado." },
    cold: { text: 'frío', percentage: 8.3, pastPercentage: 12.4, advice: "abrigate bien." },
    windy: { text: 'ventoso', percentage: 33.1, pastPercentage: 28.9, advice: "cuidado con objetos sueltos." },
    uncomfortable: { text: 'incómodo', percentage: 45.5, pastPercentage: 38.1, advice: "usa ropa ligera." },
    uv: { text: 'alta radiación UV', percentage: 60.1, pastPercentage: 52.3, advice: "usa protector solar." }
  };

  const activitiesDB = {
    surf: { name: "Surfear", icon: "🏄", dislikes: ['cold', 'wet'], likes: ['windy'] },
    beach: { name: "Día de Playa", icon: "🏖️", dislikes: ['wet', 'cold', 'windy'] },
    run: { name: "Correr", icon: "🏃‍♂️", dislikes: ['hot', 'wet', 'uncomfortable'] },
    hike: { name: "Senderismo", icon: "⛰️", dislikes: ['hot', 'wet', 'uncomfortable'] },
    sailing: { name: "Navegar", icon: "⛵", dislikes: ['wet'], likes: ['windy'] },
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
  
  // Determine risk level
  let riskLevel, riskColorClasses;
  if (avgPercentage < 20) { 
    riskLevel = 'Bajo'; 
    riskColorClasses = 'bg-green-500/20 text-green-300'; 
  } else if (avgPercentage < 40) { 
    riskLevel = 'Moderado'; 
    riskColorClasses = 'bg-yellow-500/20 text-yellow-300'; 
  } else { 
    riskLevel = 'Alto'; 
    riskColorClasses = 'bg-red-500/20 text-red-300'; 
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
        message: `No parece el mejor día. La alta probabilidad de clima ${mockData[badCondition].text} podría complicar la actividad.`, 
        reason: mockData[badCondition].text 
      };
    } else {
      return { 
        isGood: true, 
        name: currentActivity.name, 
        icon: '👍', 
        message: `¡Parece un día excelente para tu actividad! Las condiciones son favorables.` 
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
          { activityName: "Museo", recommendation: "Perfecto para días lluviosos, puedes disfrutar del arte sin preocuparte por el clima." },
          { activityName: "Café", recommendation: "Un lugar acogedor para pasar el tiempo mientras mejora el clima." }
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
            {activity ? `Análisis para: ${activityCompatibility.name}` : "Sugerencias de Actividades"}
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
                    <p className="text-sm font-bold text-red-400 mb-3">¡Plan B Activo! ✨</p>
                    {planBLoading ? (
                      <p className={isNightMode ? 'text-slate-400' : 'text-gray-500'}>Generando alternativas...</p>
                    ) : planBData ? (
                      <>
                        <p className={`text-sm font-bold mb-3 ${isNightMode ? 'text-slate-300' : 'text-gray-700'}`}>
                          Actividades Alternativas:
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
                  Basado en el clima, hoy podría ser un buen día para:
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
            Resumen del Clima
          </p>
          <div id="result-emojis" className="text-5xl mb-4 flex justify-center gap-x-3">{emojis}</div>
          <p className={`text-lg ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            Probabilidad combinada:
          </p>
          <p className={`text-6xl font-black my-3 ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
            {avgPercentage.toFixed(1)}%
          </p>
          <div className="flex justify-center mt-4">
            <span className={`text-sm font-bold px-6 py-2 rounded-full ${riskColorClasses}`}>
              Riesgo {riskLevel}
            </span>
          </div>
          
          {/* General Recommendation */}
          <div id="summary-message-container" className={`mt-6 text-left p-4 rounded-lg border ${
            isNightMode 
              ? 'bg-slate-900/50 border-slate-700' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <p className={`font-bold text-lg ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
              Recomendación General:
            </p>
            <p className={`${isNightMode ? 'text-slate-300' : 'text-gray-600'}`}>
              Por lo tanto, {adviceParts.join(" Además, ")}
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
            La Huella del Tiempo
          </h2>
          <p className={`text-center mb-6 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            Así ha cambiado el riesgo de estas condiciones con el tiempo.
          </p>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className={`border rounded-xl p-4 ${
              isNightMode 
                ? 'bg-slate-800/50 border-slate-700' 
                : 'bg-blue-50 border-blue-200'
            }`}>
              <p className="text-sm font-bold text-blue-400 mb-3">PASADO (1980-2000)</p>
              <svg viewBox="0 0 100 60" className="w-full h-auto my-3">
                <path d="M0,60 Q25,40 50,50 T100,45 L100,60 Z" fill="#22c55e"></path>
                <circle cx="20" cy="20" r="10" fill="#facc15"></circle>
                <rect x="65" y="35" width="5" height="15" fill="#8d5524"></rect>
                <circle cx="67.5" cy="30" r="8" fill="#16a34a"></circle>
              </svg>
              <p className={`text-3xl font-bold ${isNightMode ? 'text-white' : 'text-gray-800'}`}>
                {avgPastPercentage.toFixed(1)}%
              </p>
            </div>
            <div className="bg-red-900/20 border border-red-500 rounded-xl p-4">
              <p className="text-sm font-bold mb-3" style={{color: 'var(--nasa-red)'}}>
                PRESENTE (2001-2023)
              </p>
              <svg viewBox="0 0 100 60" className="w-full h-auto my-3">
                <path d="M0,60 Q25,50 50,52 T100,48 L100,60 Z" fill="#a16207"></path>
                <circle cx="20" cy="20" r="12" fill="#fb923c"></circle>
                <path d="M 65 50 L 63 35 L 70 35 Z" fill="#5c4033"></path>
              </svg>
              <p className="text-3xl font-bold text-white">{avgPercentage.toFixed(1)}%</p>
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
            Distribución Histórica
          </h3>
          <p className={`text-sm mb-4 ${isNightMode ? 'text-slate-400' : 'text-gray-600'}`}>
            Gráfico de frecuencia de las mediciones históricas. La línea roja marca el umbral del 10% más extremo.
          </p>
          <div className={`h-48 w-full rounded-lg flex items-center justify-center text-xs ${
            isNightMode ? 'bg-slate-700 text-slate-500' : 'bg-gray-100 text-gray-500'
          }`}>
            [ Aquí iría un gráfico de barras (histograma) ]
          </div>
          <button className={`mt-6 w-full font-bold py-3 px-4 rounded-lg transition-colors ${
            isNightMode 
              ? 'bg-slate-700 hover:bg-slate-600 text-white' 
              : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
          }`}>
            Descargar Datos (CSV)
          </button>
        </div>
      </div>
    </section>
  );
};

export default WeatherResults;
