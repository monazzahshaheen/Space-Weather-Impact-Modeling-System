import * as satellite from "satellite.js"

/**
 * Get satellite position from TLE
 * @param {string} tle1 - TLE line 1
 * @param {string} tle2 - TLE line 2
 * @returns {object} Position {x, y, z} in km
 */
export function getSatellitePosition(tle1, tle2) {
  try {
    const satrec = satellite.twoline2satrec(tle1, tle2)
    const now = new Date()
    const positionAndVelocity = satellite.propagate(satrec, now)
    
    if (positionAndVelocity.position && !positionAndVelocity.position.error) {
      return positionAndVelocity.position
    }
    return null
  } catch (error) {
    console.error("Error calculating satellite position:", error)
    return null
  }
}

/**
 * Scale position from km to Three.js units
 * Earth radius = 1 unit, so scale factor is 1/6371 km
 * @param {object} pos - Position {x, y, z} in km
 * @returns {array} [x, y, z] in Three.js units
 */
export function scalePosition(pos) {
  const scale = 1 / 6371 // Earth radius in Three.js = 1 unit
  return [
    pos.x * scale,
    pos.y * scale,
    pos.z * scale
  ]
}

/**
 * Extract altitude from TLE line 2
 * @param {string} tle2 - TLE line 2
 * @returns {number} Altitude in km
 */
export function getSatelliteAltitude(tle2) {
  try {
    // Parse mean motion (revolutions per day) from TLE
    const meanMotion = parseFloat(tle2.substring(52, 63))
    
    // Calculate semi-major axis using Kepler's third law
    const mu = 398600.4418 // Earth's gravitational parameter (km³/s²)
    const n = meanMotion * 2 * Math.PI / 86400 // Convert to rad/s
    const a = Math.pow(mu / (n * n), 1/3) // Semi-major axis in km
    
    // Altitude = semi-major axis - Earth radius
    const earthRadius = 6371 // km
    const altitude = a - earthRadius
    
    return altitude
  } catch (error) {
    console.error("Error calculating altitude:", error)
    return 400 // Default LEO altitude
  }
}

/**
 * Get orbital period in minutes
 * @param {string} tle2 - TLE line 2
 * @returns {number} Orbital period in minutes
 */
export function getOrbitalPeriod(tle2) {
  try {
    const meanMotion = parseFloat(tle2.substring(52, 63))
    const period = 1440 / meanMotion // minutes (1440 = 24 hours)
    return period
  } catch (error) {
    return 90 // Default ~90 minute period
  }
}

/**
 * Get satellite inclination from TLE
 * @param {string} tle2 - TLE line 2
 * @returns {number} Inclination in degrees
 */
export function getSatelliteInclination(tle2) {
  try {
    const inclination = parseFloat(tle2.substring(8, 16))
    return inclination
  } catch (error) {
    return 0
  }
}

/**
 * Get satellite eccentricity from TLE
 * @param {string} tle2 - TLE line 2
 * @returns {number} Eccentricity
 */
export function getSatelliteEccentricity(tle2) {
  try {
    const eccentricityStr = tle2.substring(26, 33)
    const eccentricity = parseFloat("0." + eccentricityStr)
    return eccentricity
  } catch (error) {
    return 0
  }
}

/**
 * Calculate distance from Earth center
 * @param {object} pos - Position {x, y, z} in km
 * @returns {number} Distance in km
 */
export function getDistanceFromEarth(pos) {
  return Math.sqrt(pos.x * pos.x + pos.y * pos.y + pos.z * pos.z)
}

/**
 * Determine orbital regime
 * @param {number} altitude - Altitude in km
 * @returns {string} Orbital regime (LEO, MEO, GEO)
 */
export function getOrbitalRegime(altitude) {
  if (altitude < 2000) return "LEO" // Low Earth Orbit
  if (altitude < 35786) return "MEO" // Medium Earth Orbit
  if (altitude < 36000) return "GEO" // Geosynchronous Orbit
  return "HEO" // Highly Elliptical Orbit
}

/**
 * Calculate orbital velocity
 * @param {number} altitude - Altitude in km
 * @returns {number} Velocity in km/s
 */
export function getOrbitalVelocity(altitude) {
  const mu = 398600.4418 // Earth's gravitational parameter
  const r = 6371 + altitude
  return Math.sqrt(mu / r)
}