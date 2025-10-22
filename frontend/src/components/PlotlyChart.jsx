/**
 * PlotlyChart Component - Display Plotly visualizations
 * NASA Weather Risk Navigator
 * Handles the 3 interactive Plotly charts for climate analysis
 */

import React from 'react';
import Plot from 'react-plotly.js';

const PlotlyChart = ({ chartData, isNightMode, title }) => {
  console.log('PlotlyChart received chartData:', chartData);
  
  if (!chartData || !chartData.figure) {
    return (
      <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 text-center p-4">
        <p className="text-gray-500">No chart data available</p>
      </div>
    );
  }

  // Theme configuration based on mode
  const theme = isNightMode ? 'plotly_dark' : 'plotly_white';
  
  // Update layout for dark mode
  const layout = {
    ...chartData.figure.layout,
    template: theme,
    paper_bgcolor: isNightMode ? '#1e293b' : '#ffffff',
    plot_bgcolor: isNightMode ? '#334155' : '#ffffff',
    font: {
      color: isNightMode ? '#e2e8f0' : '#1f2937'
    }
  };

  return (
    <div className="w-full">
      <div className="w-full h-full min-h-[280px] max-w-full overflow-hidden">
        <Plot
          data={chartData.figure.data}
          layout={layout}
          config={{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            responsive: true,
            toImageButtonOptions: {
              format: 'png',
              filename: 'climate_analysis',
              height: 500,
              width: 800,
              scale: 2
            }
          }}
          style={{ 
            width: '100%', 
            height: '100%',
            maxWidth: '100%',
            overflow: 'hidden'
          }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
};

export default PlotlyChart;
