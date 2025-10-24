/**
 * Hook personalizado para gestión de temas (modo día/noche)
 * NASA Weather Risk Navigator
 */

import { useState, useEffect } from 'react';

const useTheme = () => {
  // Estado del tema visual - controla modo día/noche
  const [isNightMode, setIsNightMode] = useState(false);

  // Inicializa el modo visual basado en localStorage o hora del día
  useEffect(() => {
    const savedMode = localStorage.getItem('themeMode');
    let initialNightMode;
    
    if (savedMode) {
      // Usar preferencia guardada del usuario
      initialNightMode = savedMode === 'night';
      console.info('🎨 Theme loaded from localStorage:', savedMode);
    } else {
      // Determinar modo basado en hora actual (7 AM - 7 PM = día)
      const now = new Date();
      const hour = now.getHours();
      const sunriseHour = 7;
      const sunsetHour = 19;
      initialNightMode = !(hour >= sunriseHour && hour < sunsetHour);
      console.info('🎨 Theme determined by time:', { hour, mode: initialNightMode ? 'night' : 'day' });
    }
    
    setIsNightMode(initialNightMode);
  }, []); // ← SIN dependencias adicionales para evitar loops

  // Aplica clases CSS al body según el modo visual actual
  useEffect(() => {
    const body = document.body;
    if (isNightMode) {
      body.classList.remove('day-mode');
      body.classList.add('night-mode');
    } else {
      body.classList.remove('night-mode');
      body.classList.add('day-mode');
    }
  }, [isNightMode]);

  // Alterna entre modo día y noche, persistiendo la preferencia
  const toggleMode = () => {
    const newMode = !isNightMode;
    console.info('🎨 Theme toggled:', { 
      from: isNightMode ? 'night' : 'day', 
      to: newMode ? 'night' : 'day' 
    });
    setIsNightMode(newMode);
    localStorage.setItem('themeMode', newMode ? 'night' : 'day');
  };

  return {
    isNightMode,
    toggleMode
  };
};

export default useTheme;
