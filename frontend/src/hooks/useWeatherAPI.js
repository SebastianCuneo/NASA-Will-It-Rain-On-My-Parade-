/**
 * Hook personalizado para comunicación con la API de clima
 * NASA Weather Risk Navigator
 */

import { useState } from 'react';

const useWeatherAPI = () => {
  // Estado de carga para mostrar indicadores durante llamadas API
  const [loading, setLoading] = useState(false);
  // Estado para almacenar resultados del análisis climático
  const [results, setResults] = useState(null);

  // Muestra mensajes temporales de error/éxito que se auto-ocultan después de 3 segundos
  const showTemporaryMessage = (message, type = 'error') => {
    // Esta función se puede mejorar para usar un estado de mensajes
    // Por ahora mantenemos la lógica simple
    console.log(`${type.toUpperCase()}: ${message}`);
  };

  // Maneja el envío del formulario y coordina la comunicación con el backend
  const handleFormSubmit = async (data) => {
    console.time('🌐 API Call Duration');
    
    // Validación básica antes de procesar
    if (data.weatherConditions.length === 0) {
      showTemporaryMessage('Please select at least one weather condition.', 'error');
      return;
    }
    
    console.info('🌐 Starting weather API call', { 
      hasLocation: !!data.latitude && !!data.longitude,
      hasDate: !!data.event_date,
      hasCondition: !!data.weatherConditions[0]
    });
    
    // Actualizar estado y preparar para llamada API
    setLoading(true);
    setResults(null);
    
    try {
      // Crear payload para la llamada API con datos del formulario
      const apiPayload = {
        latitude: data.latitude,  // Usar coordenadas del formulario
        longitude: data.longitude,
        event_date: data.event_date,  // Enviar fecha como string
        adverse_condition: data.weatherConditions[0] || 'Very Hot'  // Enviar primera condición seleccionada
      };
    
      // INFO: Log del payload antes del envío al backend
      console.info('🌐 API Payload:', apiPayload);
      console.debug('🌐 API URL: http://localhost:8000/api/visualizations-only');
      
      // Llamada al backend FastAPI usando endpoint de visualizaciones
      const response = await fetch('http://localhost:8000/api/visualizations-only', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiPayload)
      });
    
      // Verificación de respuesta HTTP exitosa
      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }

      // Parseo de respuesta JSON del backend
      const apiData = await response.json();
      
      // INFO: Log de la respuesta del backend
      console.info('🌐 API Response received:', { 
        success: apiData.success,
        hasVisualizations: !!apiData.visualizations,
        responseSize: JSON.stringify(apiData).length
      });
      
      // Extraer datos de visualizaciones de la respuesta API
      const visualizations = apiData.visualizations;
      
      // Crear datos mock para otros componentes ya que este endpoint solo proporciona visualizaciones
      const temperatureRisk = {
        probability: 25.0,
        risk_level: "MODERATE",
        status_message: "Moderate risk detected",
        risk_threshold: 28.0
      };
      const precipitationRisk = temperatureRisk;
      const coldRisk = temperatureRisk;
      const planB = {
        success: true,
        alternatives: [
         "Plan A: Main activity with precautions",
         "Plan B: Alternative indoor activity",
         "Plan C: Postpone for better weather"
        ],
        ai_model: "Simple",
        message: "Plans generated without AI"
      };
      const plotData = [];
      const climateTrend = visualizations?.climate_trend || "Climate trend analysis completed";
      
      // Combinar datos de API con datos del formulario para distribución a componentes
      const combinedData = {
        ...data,
        apiResults: apiData,
        temperature_risk: {
          probability: temperatureRisk.probability,
          risk_level: temperatureRisk.risk_level,
          status_message: temperatureRisk.status_message,
          risk_threshold: temperatureRisk.risk_threshold
        },
        precipitation_risk: {
          probability: precipitationRisk.probability,
          risk_level: precipitationRisk.risk_level,
          status_message: precipitationRisk.status_message,
          risk_threshold: precipitationRisk.risk_threshold
        },
        cold_risk: {
          probability: coldRisk.probability,
          risk_level: coldRisk.risk_level,
          status_message: coldRisk.status_message,
          risk_threshold: coldRisk.risk_threshold
        },
        plan_b: planB,
        
        // Datos de visualizaciones y análisis climático
        plot_data: plotData,
        climate_trend: climateTrend,
        visualizations: visualizations
      };

      setResults(combinedData);
      console.info('🌐 Weather analysis completed successfully');
      console.timeEnd('🌐 API Call Duration');
    
    } catch (error) {
      // ERROR: Manejo de errores de comunicación con el backend
      console.timeEnd('🌐 API Call Duration');
      console.error('🌐 API Error:', { 
        message: error.message, 
        status: error.status,
        endpoint: 'visualizations-only' 
      });
      showTemporaryMessage('Error connecting to weather service. Using offline data.', 'warning');
      // Fallback a datos mock en caso de error
      setResults(data);
    } finally {
      // Siempre desactivar estado de carga, independientemente del resultado
      setLoading(false);
    }
  };

  return {
    loading,
    results,
    handleFormSubmit,
    showTemporaryMessage
  };
};

export default useWeatherAPI;
