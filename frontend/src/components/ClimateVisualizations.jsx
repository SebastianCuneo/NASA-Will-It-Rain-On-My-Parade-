/**
 * ClimateVisualizations Component - Display the 3 Plotly charts
 * NASA Weather Risk Navigator
 * Shows P90 trend, climate comparison, and heat risk analysis
 */

import React from 'react';
import PlotlyChart from './PlotlyChart';

const ClimateVisualizations = ({ visualizations, isNightMode }) => {
  console.log('ClimateVisualizations received:', visualizations);
  
  if (!visualizations || !visualizations.success || !visualizations.charts) {
    return (
      <div className={`p-4 rounded-2xl shadow-xl mb-6 ${
        isNightMode 
          ? 'bg-slate-700/70 border border-slate-600 text-white' 
          : 'bg-gray-100/90 border border-gray-200 text-gray-800'
      }`}>
        <h3 className="text-xl font-bold mb-3">
          📊 Análisis de Visualizaciones Climáticas
        </h3>
        <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 text-center p-4">
          <p className="text-gray-500">
            No hay datos de visualización disponibles
          </p>
        </div>
      </div>
    );
  }

  const charts = visualizations.charts;
  
  // Chart titles and descriptions
  const chartConfigs = [
    {
      title: "📈 Evolución del Percentil 90 (P90) de Temperatura",
      description: "Muestra la tendencia del P90 de temperatura máxima a lo largo de los años, incluyendo la línea de tendencia y comparación con la temperatura media.",
      type: "p90_trend"
    },
    {
      title: "📊 Comparación Climática: P90 vs Histórico",
      description: "Análisis comparativo que muestra P90 vs temperaturas históricas y rangos de temperatura (mínima, media, máxima).",
      type: "climate_comparison"
    },
    {
      title: "🔥 Análisis de Riesgo de Calor",
      description: "Visualización de riesgo de calor con áreas coloreadas según umbrales de riesgo y comparación P90 vs temperatura máxima.",
      type: "heat_risk_analysis"
    }
  ];

  return (
    <div className={`p-4 rounded-2xl shadow-xl mb-6 ${
      isNightMode 
        ? 'bg-slate-700/70 border border-slate-600 text-white' 
        : 'bg-gray-100/90 border border-gray-200 text-gray-800'
    }`}>
      <h3 className="text-xl font-bold mb-4">
        📊 Visualizaciones Climáticas Interactivas
      </h3>
      
      <div className="space-y-8 max-w-full overflow-hidden">
        {chartConfigs.map((config, index) => {
          const chart = charts.find(c => c.chart_type === config.type);
          
          if (!chart) {
            return (
              <div key={index} className="border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 p-6">
                <h4 className="font-semibold mb-2">{config.title}</h4>
                <p className="text-sm text-gray-500">Gráfico no disponible</p>
              </div>
            );
          }

          return (
            <div key={index} className="border border-gray-200 rounded-lg p-4 bg-white/50 shadow-lg max-w-full overflow-hidden">
              <div className="mb-4">
                <h4 className="font-semibold mb-2 text-lg text-center">
                  {config.title}
                </h4>
                <p className="text-sm text-gray-600 text-center">
                  {config.description}
                </p>
              </div>
              <div className={`h-[${chart.chart_type === 'climate_comparison' ? '280px' : '320px'}] w-full max-w-full overflow-hidden flex justify-center`}>
                <div className="w-full max-w-[400px]">
                  <PlotlyChart 
                    chartData={chart} 
                    isNightMode={isNightMode}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Climate trend summary */}
      {visualizations.climate_trend && (
        <div className={`mt-6 p-4 rounded-lg ${
          isNightMode 
            ? 'bg-slate-600/50 border border-slate-500' 
            : 'bg-blue-50 border border-blue-200'
        }`}>
          <h4 className="font-semibold mb-2">📋 Resumen de Tendencia Climática</h4>
          <p className="text-sm">{visualizations.climate_trend}</p>
        </div>
      )}
    </div>
  );
};

export default ClimateVisualizations;
