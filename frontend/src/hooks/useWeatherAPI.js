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
      console.debug('🌐 API URL: http://localhost:8000/api/risk-working');
      
      // Llamada al backend FastAPI usando endpoint completo con datos de NASA
      const response = await fetch('http://localhost:8000/api/risk-working', {
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
        hasRiskAnalysis: !!apiData.risk_analysis,
        responseSize: JSON.stringify(apiData).length
      });
      
      // Extraer datos completos de la respuesta API del endpoint /api/risk-working
      const riskAnalysis = apiData.risk_analysis;
      const climateTrend = apiData.climate_trend;
      const plotData = apiData.plot_data || [];
      
      // Usar datos reales del backend en lugar de datos mock
      const temperatureRisk = {
        probability: riskAnalysis?.probability || 0,
        risk_level: riskAnalysis?.risk_level || "UNKNOWN",
        status_message: riskAnalysis?.status_message || "No data available",
        risk_threshold: riskAnalysis?.risk_threshold || 0,
        total_observations: riskAnalysis?.total_observations || 0
      };
      
      // Para precipitación y frío, usar los mismos datos por ahora (el backend actual solo calcula temperatura)
      const precipitationRisk = { ...temperatureRisk };
      const coldRisk = { ...temperatureRisk };
      
      // Combinar datos de API con datos del formulario para distribución a componentes
      const combinedData = {
        ...data,
        apiResults: apiData,
        temperature_risk: temperatureRisk,
        precipitation_risk: precipitationRisk,
        cold_risk: coldRisk,
        
        // Datos de análisis climático
        plot_data: plotData,
        climate_trend: climateTrend
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
        endpoint: 'risk-working' 
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
