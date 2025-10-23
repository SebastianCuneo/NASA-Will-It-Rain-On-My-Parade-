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
          📊 Climate Visualization Analysis
        </h3>
        <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 text-center p-4">
          <p className="text-gray-500">
            No visualization data available
          </p>
        </div>
      </div>
    );
  }

  const charts = visualizations.charts;
  
  // Chart titles and descriptions
  const chartConfigs = [
    {
      title: "📈 Evolution of 90th Percentile (P90) Temperature",
      description: "Shows the trend of P90 maximum temperature over the years, including the trend line and comparison with mean temperature.",
      type: "p90_trend"
    },
    {
      title: "📊 Climate Comparison: P90 vs Historical",
      description: "Comparative analysis showing P90 vs historical temperatures and temperature ranges (min, mean, max).",
      type: "climate_comparison"
    },
    {
      title: "🔥 Heat Risk Analysis",
      description: "Heat risk visualization with colored areas according to risk thresholds and P90 vs maximum temperature comparison.",
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
        📊 Interactive Climate Visualizations
      </h3>
      
      <div className="space-y-8 max-w-full overflow-hidden">
        {chartConfigs.map((config, index) => {
          const chart = charts.find(c => c.chart_type === config.type);
          
          if (!chart) {
            return (
              <div key={index} className="border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 p-6">
                <h4 className="font-semibold mb-2">{config.title}</h4>
                <p className="text-sm text-gray-500">Chart not available</p>
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
          <h4 className="font-semibold mb-2">📋 Climate Trend Summary</h4>
          <p className="text-sm">{visualizations.climate_trend}</p>
        </div>
      )}
    </div>
  );
};

export default ClimateVisualizations;
