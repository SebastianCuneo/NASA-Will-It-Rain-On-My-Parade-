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
      // Use condition ID directly (cold, hot, wet)
      const selectedCondition = data.weatherConditions[0] || 'hot';
      
      // Crear payload para la llamada API con datos del formulario
      const apiPayload = {
        latitude: data.latitude,
        longitude: data.longitude,
        event_date: data.event_date,
        adverse_condition: selectedCondition  // "cold", "hot", "wet"
      };
    
      // INFO: Log del payload antes del envío al backend
      console.info('🌐 API Payload:', apiPayload);
      console.debug('🌐 API URL: https://nasa-will-it-rain-on-my-parade.onrender.com/risk');
      
      // Llamada al backend FastAPI usando endpoint único consolidado
      const response = await fetch('https://nasa-will-it-rain-on-my-parade.onrender.com/api/risk', {
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
      
      // Extraer datos completos de la respuesta API del endpoint /api/risk
      const riskAnalysis = apiData.risk_analysis;
      const climateTrend = apiData.climate_trend;
      const planB = apiData.plan_b;
      
      // Usar datos reales del backend (risk_analysis ya incluye toda la información necesaria)
      const riskData = {
        probability: riskAnalysis?.probability || 0,
        risk_level: riskAnalysis?.risk_level || "UNKNOWN",
        status_message: riskAnalysis?.status_message || "No data available",
        risk_threshold: riskAnalysis?.risk_threshold || 0,
        total_observations: riskAnalysis?.total_observations || 0
      };
      
      // Create individual risk objects for compatibility with WeatherResults
      // Backend only returns risk for the selected condition, so we map it to the appropriate risk type
      const tempRisk = selectedCondition === 'hot' ? riskData : null;
      const precipRisk = selectedCondition === 'wet' ? riskData : null;
      const coldRisk = selectedCondition === 'cold' ? riskData : null;
      
      // Combinar datos de API con datos del formulario para distribución a componentes
      const combinedData = {
        ...data,
        apiResults: apiData,
        risk_data: riskData,
        temperature_risk: tempRisk,
        precipitation_risk: precipRisk,
        cold_risk: coldRisk,
        climate_trend: climateTrend,
        plan_b: planB,
        selectedCondition: selectedCondition  // "cold", "hot", "wet" - para mostrar threshold correcto
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
        endpoint: 'risk' 
      });
      showTemporaryMessage('Error connecting to weather service. Please try again.', 'warning');
      // No establecer resultados en caso de error para mostrar mensaje de error
      setResults(null);
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
