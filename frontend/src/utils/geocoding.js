/**
 * Geocoding utility using OpenStreetMap Nominatim API (Free, no API key needed)
 * NASA Weather Risk Navigator - Global City Search
 */

/**
 * Search for a city and get its coordinates
 * @param {string} cityName - City name (e.g., "New York", "Tokyo", "Montevideo")
 * @returns {Promise<Object|null>} - { lat, lon, displayName } or null if not found
 */
export async function getCityCoordinates(cityName) {
  if (!cityName || cityName.trim().length === 0) {
    return null;
  }

  try {
    // OpenStreetMap Nominatim API (Free, no API key required)
    const url = `https://nominatim.openstreetmap.org/search?` +
      `q=${encodeURIComponent(cityName)}&` +
      `format=json&` +
      `limit=1&` +
      `addressdetails=1`;

    const response = await fetch(url, {
      headers: {
        'User-Agent': 'NASA-Weather-Risk-Navigator/1.0' // Required by Nominatim
      }
    });

    if (!response.ok) {
      throw new Error(`Geocoding API error: ${response.status}`);
    }

    const data = await response.json();

    if (data.length > 0) {
      const result = data[0];
      return {
        lat: parseFloat(result.lat),
        lon: parseFloat(result.lon),
        displayName: result.display_name,
        country: result.address?.country || 'Unknown',
        city: result.address?.city || result.address?.town || cityName
      };
    }

    return null; // City not found
  } catch (error) {
    console.error('Geocoding error:', error);
    return null;
  }
}

/**
 * Popular cities for autocomplete suggestions
 */
export const POPULAR_CITIES = [
  // Latin America
  'Montevideo',
  'Buenos Aires',
  'São Paulo',
  'Rio de Janeiro',
  'Santiago',
  'Lima',
  'Bogotá',
  'Mexico City',
  
  // North America
  'New York',
  'Los Angeles',
  'Chicago',
  'Miami',
  'Toronto',
  'Vancouver',
  
  // Europe
  'London',
  'Paris',
  'Madrid',
  'Barcelona',
  'Rome',
  'Berlin',
  'Amsterdam',
  'Vienna',
  
  // Asia
  'Tokyo',
  'Seoul',
  'Beijing',
  'Shanghai',
  'Mumbai',
  'Bangkok',
  'Singapore',
  'Dubai',
  
  // Oceania
  'Sydney',
  'Melbourne',
  'Auckland',
  
  // Africa
  'Cairo',
  'Cape Town',
  'Johannesburg'
];

/**
 * Filter popular cities based on user input
 * @param {string} input - User input
 * @param {number} limit - Maximum number of suggestions
 * @returns {Array<string>} - Filtered city names
 */
export function getAutocompleteSuggestions(input, limit = 5) {
  if (!input || input.length < 2) {
    return [];
  }

  const lowerInput = input.toLowerCase();
  
  return POPULAR_CITIES
    .filter(city => city.toLowerCase().includes(lowerInput))
    .slice(0, limit);
}

