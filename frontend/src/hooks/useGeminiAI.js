import { useState } from 'react';
import { GoogleGenerativeAI } from '@google/generative-ai';

const useGeminiAI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const generatePlanB = async (conditions, activity, location = 'Montevideo, Uruguay') => {
    setIsLoading(true);
    setError(null);

    try {
      // Verificar si hay API key
      const apiKey = process.env.REACT_APP_GEMINI_API_KEY || 'AIzaSyCp0Jvb1FVFIUOo1NHRCyFFf_G09lzU5G0';
      console.log('🔑 All environment variables:', process.env);
      console.log('🔑 Gemini API Key check:', apiKey ? 'Found' : 'Not found');
      console.log('🔑 API Key value:', apiKey ? `${apiKey.substring(0, 10)}...` : 'undefined');
      
      if (!apiKey || apiKey === 'your_gemini_api_key_here') {
        throw new Error('GEMINI_API_KEY not found or not configured properly');
      }

      // Inicializar Gemini
      const genAI = new GoogleGenerativeAI(apiKey);
      const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

      // Crear prompt contextual
      const prompt = createPrompt(conditions, activity, location);

      // Generar respuesta
      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      // Parsear respuesta JSON
      const alternatives = parseGeminiResponse(text);

      return {
        success: true,
        alternatives,
        ai_model: 'Gemini 2.0 Flash (Frontend)',
        generated_at: new Date().toISOString()
      };

    } catch (err) {
      console.error('Gemini AI Error:', err);
      setError(err.message);
      return {
        success: false,
        alternatives: [],
        error: err.message,
        ai_model: 'Error'
      };
    } finally {
      setIsLoading(false);
    }
  };

  return {
    generatePlanB,
    isLoading,
    error
  };
};

const createPrompt = (conditions, activity, location) => {
  const conditionText = conditions.join(', ');
  const currentDate = new Date().toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  return `You are an expert weather planning assistant for ${location}. Generate intelligent Plan B alternatives for outdoor activities when weather conditions are unfavorable.

CONTEXT:
- Original Activity: ${activity}
- Weather Conditions: ${conditionText}
- Location: ${location}
- Current Date: ${currentDate}

REQUIREMENTS:
1. Provide exactly 3 specific, actionable alternatives
2. Consider the location, weather conditions, and activity context
3. Make suggestions practical, enjoyable, and realistic
4. Include both indoor and outdoor options when weather permits
5. Be creative but maintain feasibility
6. Consider local attractions and activities specific to Uruguay
7. Provide specific locations or venues when possible
8. Consider cost, accessibility, and time requirements

RESPONSE FORMAT: Return ONLY a valid JSON response with this exact structure:
{ 
  "alternatives": [
    {
      "title": "Specific activity name",
      "description": "Brief but detailed description of the activity",
      "type": "indoor/outdoor/mixed",
      "reason": "Why this is a good alternative for the weather conditions",
      "tips": "Practical tips for this activity",
      "location": "Specific location or venue (if applicable)",
      "duration": "Estimated time needed",
      "cost": "Free/Low/Medium/High"
    }
  ]
}

Focus on making the day enjoyable despite the weather conditions. Be specific, helpful, and consider the local context of Uruguay.`;
};

const parseGeminiResponse = (text) => {
  try {
    // Limpiar la respuesta
    let cleanText = text.trim();
    
    // Remover markdown si existe
    cleanText = cleanText.replace(/```json/g, '').replace(/```/g, '').trim();
    
    // Buscar JSON en la respuesta
    const jsonStart = cleanText.indexOf('{');
    const jsonEnd = cleanText.lastIndexOf('}') + 1;
    
    if (jsonStart === -1 || jsonEnd === 0) {
      throw new Error('No JSON found in response');
    }
    
    const jsonText = cleanText.substring(jsonStart, jsonEnd);
    const data = JSON.parse(jsonText);
    
    // Validar estructura
    if (!data.alternatives || !Array.isArray(data.alternatives)) {
      throw new Error('Invalid response structure');
    }
    
    // Validar cada alternativa
    return data.alternatives.map(alt => ({
      title: alt.title || 'Activity',
      description: alt.description || 'No description available',
      type: alt.type || 'mixed',
      reason: alt.reason || 'Good alternative for current conditions',
      tips: alt.tips || 'Enjoy your activity!',
      location: alt.location || 'Various locations',
      duration: alt.duration || '1-3 hours',
      cost: alt.cost || 'Varies'
    }));
    
  } catch (err) {
    console.error('Error parsing Gemini response:', err);
    // Fallback: intentar extraer información básica
    return extractBasicAlternatives(text);
  }
};

const extractBasicAlternatives = (text) => {
  const alternatives = [];
  const lines = text.split('\n').filter(line => line.trim());
  
  let currentAlt = null;
  
  for (const line of lines) {
    const trimmedLine = line.trim();
    
    // Buscar títulos de actividades
    if (trimmedLine.match(/^\d+\.|^[-*]|^[A-Z][^.!?]*[.!?]$/)) {
      if (currentAlt) {
        alternatives.push(currentAlt);
      }
      currentAlt = {
        title: trimmedLine.replace(/^\d+\.|^[-*]\s*/, ''),
        description: '',
        type: 'mixed',
        reason: 'Good alternative for current conditions',
        tips: 'Enjoy your activity!',
        location: 'Various locations',
        duration: '1-3 hours',
        cost: 'Varies'
      };
    } else if (currentAlt && trimmedLine) {
      if (!currentAlt.description) {
        currentAlt.description = trimmedLine;
      }
    }
  }
  
  if (currentAlt) {
    alternatives.push(currentAlt);
  }
  
  return alternatives.slice(0, 3); // Limitar a 3 alternativas
};

export default useGeminiAI;
