/**
 * Fetch real-time space weather data from NOAA and NASA
 */

// NOAA Space Weather Prediction Center API
const NOAA_BASE_URL = "https://services.swpc.noaa.gov/json"

/**
 * Fetch current Kp index
 */
export async function fetchKpIndex() {
  try {
    const response = await fetch(`${NOAA_BASE_URL}/planetary_k_index_1m.json`)
    const data = await response.json()
    
    // Get most recent Kp value
    const latest = data[data.length - 1]
    return parseFloat(latest.kp_index)
  } catch (error) {
    console.error("Failed to fetch Kp index:", error)
    return 3 // Default quiet value
  }
}

/**
 * Fetch solar wind data
 */
export async function fetchSolarWind() {
  try {
    const response = await fetch(`${NOAA_BASE_URL}/plasma-7-day.json`)
    const data = await response.json()
    
    // Get most recent values
    const latest = data[data.length - 1]
    return {
      speed: parseFloat(latest.speed) || 400, // km/s
      density: parseFloat(latest.density) || 5, // particles/cm³
      temperature: parseFloat(latest.temperature) || 100000 // K
    }
  } catch (error) {
    console.error("Failed to fetch solar wind:", error)
    return { speed: 400, density: 5, temperature: 100000 }
  }
}

/**
 * Fetch F10.7 solar flux
 */
export async function fetchF107() {
  try {
    const response = await fetch(`${NOAA_BASE_URL}/f10_7_cm_flux.json`)
    const data = await response.json()
    
    const latest = data[data.length - 1]
    return parseFloat(latest.flux) || 120
  } catch (error) {
    console.error("Failed to fetch F10.7:", error)
    return 120 // Default value
  }
}

/**
 * Fetch proton flux (solar energetic particles)
 */
export async function fetchProtonFlux() {
  try {
    const response = await fetch(`${NOAA_BASE_URL}/goes/primary/integral-protons-plot-6-hour.json`)
    const data = await response.json()
    
    // Get latest >10 MeV proton flux
    const latest = data[data.length - 1]
    return parseFloat(latest.flux) || 1
  } catch (error) {
    console.error("Failed to fetch proton flux:", error)
    return 1 // Default quiet value
  }
}

/**
 * Fetch all space weather data
 */
export async function fetchSpaceWeather() {
  try {
    const [kp, solarWind, f107, protonFlux] = await Promise.all([
      fetchKpIndex(),
      fetchSolarWind(),
      fetchF107(),
      fetchProtonFlux()
    ])

    return {
      kpIndex: kp,
      f107: f107,
      solarWindSpeed: solarWind.speed,
      solarWindDensity: solarWind.density,
      solarWindTemp: solarWind.temperature,
      protonFlux: protonFlux,
      timestamp: new Date().toISOString()
    }
  } catch (error) {
    console.error("Failed to fetch space weather:", error)
    
    // Return default quiet conditions
    return {
      kpIndex: 3,
      f107: 120,
      solarWindSpeed: 400,
      solarWindDensity: 5,
      solarWindTemp: 100000,
      protonFlux: 1,
      timestamp: new Date().toISOString()
    }
  }
}

/**
 * Fetch geomagnetic storm warnings
 */
export async function fetchStormWarnings() {
  try {
    const response = await fetch(`${NOAA_BASE_URL}/alerts.json`)
    const alerts = await response.json()
    
    // Filter for geomagnetic storm warnings
    const stormAlerts = alerts.filter(alert => 
      alert.message_type === "Alert" && 
      alert.message.includes("Geomagnetic Storm")
    )
    
    return stormAlerts
  } catch (error) {
    console.error("Failed to fetch storm warnings:", error)
    return []
  }
}

/**
 * Fetch 3-day space weather forecast
 */
export async function fetchForecast() {
  try {
    const response = await fetch(`${NOAA_BASE_URL}/3-day-forecast.json`)
    const data = await response.json()
    
    return data
  } catch (error) {
    console.error("Failed to fetch forecast:", error)
    return null
  }
}

/**
 * NASA DONKI API - Coronal Mass Ejections
 * Note: Requires NASA API key (get free at https://api.nasa.gov)
 */
export async function fetchCMEData(apiKey = "DEMO_KEY") {
  try {
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    
    const response = await fetch(
      `https://api.nasa.gov/DONKI/CME?startDate=${startDate}&endDate=${endDate}&api_key=${apiKey}`
    )
    const data = await response.json()
    
    return data
  } catch (error) {
    console.error("Failed to fetch CME data:", error)
    return []
  }
}

/**
 * Check if conditions are stormy
 */
export function isStormConditions(spaceWeather) {
  return spaceWeather.kpIndex >= 5 || 
         spaceWeather.solarWindSpeed > 600 || 
         spaceWeather.protonFlux > 1000
}

/**
 * Get storm severity level
 */
export function getStormSeverity(kpIndex) {
  if (kpIndex >= 9) return "EXTREME (G5)"
  if (kpIndex >= 8) return "SEVERE (G4)"
  if (kpIndex >= 7) return "STRONG (G3)"
  if (kpIndex >= 6) return "MODERATE (G2)"
  if (kpIndex >= 5) return "MINOR (G1)"
  return "QUIET"
}