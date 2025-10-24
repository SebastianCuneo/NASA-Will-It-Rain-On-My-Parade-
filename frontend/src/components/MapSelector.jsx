/**
 * MapSelector Component - Interactive Map for Location Selection
 * NASA Weather Risk Navigator
 * 
 * FUNCIÓN PRINCIPAL:
 * - Proporciona mapa interactivo para selección de ubicación
 * - Permite hacer clic en el mapa para obtener coordenadas
 * - Incluye geolocalización automática del usuario
 * - Reemplaza búsqueda de ciudades con selección visual
 * 
 * CONEXIONES:
 * - ❌ NO se conecta al backend
 * - ✅ Usa OpenStreetMap (servicio externo gratuito)
 * - ✅ Usa API de geolocalización del navegador
 * - ✅ Comunica coordenadas al componente padre via callback
 * 
 * SERVICIOS EXTERNOS:
 * - OpenStreetMap tiles: https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
 * - Geolocation API del navegador (navigator.geolocation)
 */

import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// CONFIGURACIÓN: Arreglar iconos por defecto de react-leaflet
// Esto es necesario porque react-leaflet tiene problemas con los iconos por defecto
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// ICONO PERSONALIZADO: Configurar marcador visual para el mapa
const customIcon = new L.Icon({
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// COMPONENTE: Manejador de eventos de clic en el mapa
// Este componente usa el hook useMapEvents para capturar clics del usuario
function MapClickHandler({ onLocationSelect }) {
  useMapEvents({
    click: (e) => {
      // Extraer coordenadas del evento de clic
      const { lat, lng } = e.latlng;
      // Comunicar coordenadas al componente padre
      onLocationSelect(lat, lng);
    },
  });
  return null; // Este componente no renderiza nada visual
}

const MapSelector = ({ onLocationSelect, isNightMode, initialLat = -34.90, initialLon = -56.16 }) => {
  // ESTADO: Ubicación seleccionada (por defecto Montevideo, Uruguay)
  const [selectedLocation, setSelectedLocation] = useState({
    lat: initialLat,
    lng: initialLon
  });
  // ESTADO: Control de carga del mapa
  const [isMapReady, setIsMapReady] = useState(false);

  // INICIALIZACIÓN: Marcar mapa como listo después del mount
  useEffect(() => {
    setIsMapReady(true);
  }, []);

  // FUNCIÓN: Manejar selección de ubicación desde clic en mapa
  const handleLocationSelect = (lat, lng) => {
    const newLocation = { lat, lng };
    setSelectedLocation(newLocation);
    // Comunicar nueva ubicación al componente padre
    onLocationSelect(lat, lng);
  };

  // FUNCIÓN: Obtener ubicación actual del usuario usando geolocalización
  const handleCurrentLocation = () => {
    if (navigator.geolocation) {
      // Usar API de geolocalización del navegador
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          handleLocationSelect(latitude, longitude);
        },
        (error) => {
          console.error('Error getting current location:', error);
          alert('Unable to get your current location. Please click on the map to select a location.');
        }
      );
    } else {
      alert('Geolocation is not supported by this browser. Please click on the map to select a location.');
    }
  };

  // LOADING: Mostrar spinner mientras el mapa se carga
  if (!isMapReady) {
    return (
      <div className="w-full h-96 bg-slate-800 rounded-lg flex items-center justify-center">
        <div className="text-slate-300 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
          Loading map...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* CONTROLES: Botones y display de ubicación seleccionada */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* BOTÓN: Geolocalización automática */}
        <button
          type="button"
          onClick={handleCurrentLocation}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
          Use My Location
        </button>
        
        {/* DISPLAY: Mostrar coordenadas seleccionadas */}
        <div className="flex-1 text-sm text-slate-400 bg-slate-800/50 border border-slate-700 rounded-lg p-3">
          <strong className="text-slate-300">📍 Selected:</strong> {selectedLocation.lat.toFixed(4)}, {selectedLocation.lng.toFixed(4)}
        </div>
      </div>

      {/* MAPA INTERACTIVO: Contenedor principal del mapa */}
      <div className="w-full h-96 rounded-lg overflow-hidden border border-slate-700">
        <MapContainer
          center={[selectedLocation.lat, selectedLocation.lng]}
          zoom={10}
          style={{ height: '100%', width: '100%' }}
          className="z-0"
        >
          {/* TILES: Usar OpenStreetMap como fuente de datos del mapa */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* MARCADOR: Mostrar ubicación seleccionada */}
          <Marker 
            position={[selectedLocation.lat, selectedLocation.lng]} 
            icon={customIcon}
          >
            <Popup>
              <div className="text-center">
                <strong>Selected Location</strong><br/>
                Lat: {selectedLocation.lat.toFixed(4)}<br/>
                Lng: {selectedLocation.lng.toFixed(4)}
              </div>
            </Popup>
          </Marker>
          
          {/* MANEJADOR: Capturar clics del usuario en el mapa */}
          <MapClickHandler onLocationSelect={handleLocationSelect} />
        </MapContainer>
      </div>

      {/* INSTRUCCIONES: Guía de uso para el usuario */}
      <div className="text-xs text-slate-400 bg-slate-800/50 border border-slate-700 rounded-lg p-3">
        <strong className="text-slate-300">🗺️ Instructions:</strong> Click anywhere on the map to select your location, or use "Use My Location" to automatically detect your current position.
      </div>
    </div>
  );
};

export default MapSelector;
