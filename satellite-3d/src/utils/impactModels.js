/**
 * Space Weather Impact Modeling Calculations
 * Based on NRLMSISE-00 (atmospheric model) and AP-8/AE-8 (radiation models)
 */

// 1. ATMOSPHERIC DRAG IMPACT
export function calculateDragImpact(altitude, kpIndex, f107Index) {
  // Baseline atmospheric density (kg/m³) - exponential decay with altitude
  const baselineDensity = 1.225 * Math.exp(-altitude / 8.5)
  
  // Kp effect on density (storms can increase density 2-10x)
  // Kp scale: 0 (quiet) to 9 (extreme storm)
  const kpMultiplier = 1 + (kpIndex - 3) * 0.4
  
  // F10.7 solar flux effect on thermosphere expansion
  // F10.7 typical range: 70 (solar minimum) to 250 (solar maximum)
  const solarMultiplier = 1 + (f107Index - 100) / 200
  
  // Current atmospheric density
  const atmosphericDensity = baselineDensity * kpMultiplier * solarMultiplier
  
  // Orbital velocity (simplified circular orbit) km/s
  const mu = 398600.4418 // Earth gravitational parameter
  const r = 6371 + altitude // km
  const velocity = Math.sqrt(mu / r) // km/s
  
  // Typical satellite parameters (can be customized per satellite)
  const dragCoeff = 2.2
  const area = altitude < 1000 ? 10 : altitude < 10000 ? 25 : 50 // m²
  const mass = altitude < 1000 ? 500 : altitude < 10000 ? 2000 : 5000 // kg
  
  // Drag force: F = 0.5 * ρ * v² * Cd * A
  const dragForce = 0.5 * atmosphericDensity * Math.pow(velocity * 1000, 2) * dragCoeff * area
  
  // Orbit decay rate (meters per day)
  const decayRate = (dragForce / mass) * 86400 * 0.5
  
  // Normal decay rate for comparison
  const normalDecay = altitude < 500 ? 100 : altitude < 1000 ? 20 : altitude < 10000 ? 2 : 0.1
  
  // Percentage increase
  const decayIncrease = ((decayRate / normalDecay) - 1) * 100
  
  // Days until reboost needed (assuming 1km safety threshold)
  const daysUntilReboost = decayRate > 10 ? Math.floor(1000 / decayRate) : 999
  
  return {
    decayRate: Math.max(0, decayRate),
    normalDecay,
    increase: Math.max(0, decayIncrease),
    daysUntilReboost,
    atmosphericDensity,
    dragForce
  }
}

// 2. RADIATION DOSE IMPACT
export function calculateRadiationImpact(altitude, kpIndex, protonFlux = 100) {
  // Van Allen radiation belts peak at 3,000 - 20,000 km
  // Inner belt (protons): ~3,000-10,000 km
  // Outer belt (electrons): ~15,000-25,000 km
  
  // Gaussian distribution for belt intensity
  const innerBeltPeak = 6000
  const outerBeltPeak = 20000
  const innerBeltFactor = Math.exp(-Math.pow((altitude - innerBeltPeak) / 4000, 2))
  const outerBeltFactor = Math.exp(-Math.pow((altitude - outerBeltPeak) / 8000, 2))
  const beltFactor = Math.max(innerBeltFactor, outerBeltFactor)
  
  // Outside belts
  const outsideBelts = altitude > 25000 || altitude < 1000 ? 0.1 : 1.0
  
  // Geomagnetic storm effect (pushes belts lower and intensifies)
  const stormMultiplier = 1 + (kpIndex - 3) * 0.3
  
  // Proton flux contribution (solar energetic particles)
  const protonDose = (protonFlux / 100) * (altitude < 2000 ? 0.5 : 1.0)
  
  // Baseline dose (mrad/day)
  const baselineDose = 10
  const currentDose = baselineDose * beltFactor * outsideBelts * stormMultiplier * (1 + protonDose)
  
  // Single Event Upset (SEU) probability
  // Simplified model: higher at higher altitudes and radiation zones
  const shielding = altitude < 1000 ? 0.6 : altitude < 10000 ? 0.8 : 1.0 // LEO has some shielding
  const seuProbability = Math.min(95, currentDose * shielding * 0.5)
  
  // Safe mode risk assessment
  const safeModeRisk = seuProbability > 50 ? 'HIGH' : 
                       seuProbability > 20 ? 'MEDIUM' : 'LOW'
  
  return {
    dose: currentDose,
    seuProbability,
    safeModeRisk,
    beltFactor
  }
}

// 3. SIGNAL/COMMUNICATION DEGRADATION
export function calculateSignalImpact(altitude, kpIndex, inclination = 45) {
  // Ionospheric scintillation effects (strongest at LEO and high latitudes)
  const ionosphericFactor = altitude < 2000 ? 1.0 : 0.1
  const polarFactor = Math.abs(inclination) > 60 ? 1.5 : 1.0
  
  // Scintillation index based on Kp
  const scintillationIndex = Math.max(0, (kpIndex - 2) * ionosphericFactor * polarFactor)
  
  // Signal loss in dB
  const signalLoss = Math.min(80, scintillationIndex * 12)
  
  // Signal degradation percentage
  const degradation = Math.min(100, (signalLoss / 0.8))
  
  // GPS position error (only for MEO satellites ~20,000 km)
  const isGPS = altitude > 19000 && altitude < 21000
  const normalError = 2 // meters
  const errorMultiplier = 1 + (kpIndex - 3) * 0.8
  const positionError = isGPS ? normalError * errorMultiplier : 0
  
  // Communication blackout duration (severe storms only)
  const blackoutDuration = kpIndex >= 7 ? 4 + (kpIndex - 7) * 2 : 0
  
  // Signal quality assessment
  const quality = signalLoss < 10 ? 'GOOD' : 
                 signalLoss < 30 ? 'DEGRADED' : 'SEVERE'
  
  return {
    signalLoss,
    degradation,
    positionError,
    blackoutDuration,
    quality,
    scintillationIndex
  }
}

// 4. OVERALL RISK ASSESSMENT
export function calculateOverallRisk(drag, radiation, signal) {
  let riskScore = 0
  
  // Drag risk contribution (0-30 points)
  if (drag.decayRate > 100) riskScore += 30
  else if (drag.decayRate > 50) riskScore += 20
  else if (drag.decayRate > 10) riskScore += 10
  else if (drag.decayRate > 5) riskScore += 5
  
  // Radiation risk contribution (0-40 points)
  if (radiation.seuProbability > 50) riskScore += 40
  else if (radiation.seuProbability > 30) riskScore += 30
  else if (radiation.seuProbability > 20) riskScore += 20
  else if (radiation.seuProbability > 5) riskScore += 10
  
  // Signal risk contribution (0-30 points)
  if (signal.signalLoss > 40) riskScore += 30
  else if (signal.signalLoss > 20) riskScore += 20
  else if (signal.signalLoss > 10) riskScore += 10
  
  // Risk level classification
  const riskLevel = riskScore >= 70 ? 'CRITICAL' : 
                   riskScore >= 50 ? 'HIGH' : 
                   riskScore >= 25 ? 'MEDIUM' : 'LOW'
  
  return {
    score: riskScore,
    level: riskLevel
  }
}

// 5. RECOMMENDATIONS GENERATOR
export function generateRecommendations(impacts) {
  const recommendations = []
  
  // Drag-related
  if (impacts.drag.daysUntilReboost < 30) {
    recommendations.push(`🚀 Schedule orbit reboost maneuver within ${impacts.drag.daysUntilReboost} days`)
  } else if (impacts.drag.decayRate > 50) {
    recommendations.push("📉 Monitor orbit decay closely - increased atmospheric drag detected")
  }
  
  // Radiation-related
  if (impacts.radiation.seuProbability > 40) {
    recommendations.push("⚡ Enable redundant systems - high SEU probability")
    recommendations.push("💾 Increase memory scrubbing frequency")
  } else if (impacts.radiation.seuProbability > 20) {
    recommendations.push("🛡️ Monitor telemetry for bit flips and anomalies")
  }
  
  // Signal-related
  if (impacts.signal.blackoutDuration > 0) {
    recommendations.push(`📡 Expect communication blackout: ${impacts.signal.blackoutDuration} hours`)
    recommendations.push("🔄 Switch to backup communication systems")
  } else if (impacts.signal.degradation > 40) {
    recommendations.push("📶 Signal degradation detected - use error correction")
  }
  
  // General recommendations
  if (impacts.overall.level === 'CRITICAL') {
    recommendations.push("🚨 CRITICAL: Activate emergency protocols")
    recommendations.push("👨‍💻 Increase ground station monitoring frequency")
  } else if (impacts.overall.level === 'HIGH') {
    recommendations.push("⚠️ Enhanced monitoring mode recommended")
  }
  
  if (recommendations.length === 0) {
    recommendations.push("✅ Continue normal operations")
    recommendations.push("📊 Standard telemetry monitoring sufficient")
  }
  
  return recommendations
}

// 6. MAIN IMPACT CALCULATION FUNCTION
export function calculateImpacts({ altitude, kpIndex, f107, solarWindSpeed, protonFlux, name }) {
  const drag = calculateDragImpact(altitude, kpIndex, f107)
  const radiation = calculateRadiationImpact(altitude, kpIndex, protonFlux)
  const signal = calculateSignalImpact(altitude, kpIndex)
  const overall = calculateOverallRisk(drag, radiation, signal)
  const recommendations = generateRecommendations({ drag, radiation, signal, overall })
  
  return {
    altitude,
    name,
    drag,
    radiation,
    signal,
    overall,
    recommendations
  }
}