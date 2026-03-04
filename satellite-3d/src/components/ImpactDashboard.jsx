import { useMemo } from "react"
import { calculateImpacts } from "../utils/impactModels"
import { getSatelliteAltitude } from "../utils/orbit"
import "./ImpactDashboard.css"

export default function ImpactDashboard({ 
  selectedSatellite, 
  spaceWeather,
  satellites,
  onSelectSatellite 
}) {
  // Calculate impacts for selected satellite
  const impacts = useMemo(() => {
    if (!selectedSatellite) return null
    
    const altitude = getSatelliteAltitude(selectedSatellite.line2)
    
    return calculateImpacts({
      altitude,
      name: selectedSatellite.name,
      ...spaceWeather
    })
  }, [selectedSatellite, spaceWeather])

  if (!selectedSatellite || !impacts) {
    return (
      <div className="impact-dashboard">
        <h2>📊 Impact Analysis</h2>
        <p className="no-selection">Select a satellite to view impact analysis</p>
      </div>
    )
  }

  const getRiskColorClass = (level) => {
    const colors = {
      CRITICAL: 'risk-critical',
      HIGH: 'risk-high',
      MEDIUM: 'risk-medium',
      LOW: 'risk-low'
    }
    return colors[level] || 'risk-low'
  }

  return (
    <div className="impact-dashboard">
      <h2>📊 Impact Analysis</h2>
      
      {/* Satellite Info */}
      <div className="satellite-info">
        <h3>{selectedSatellite.name.trim()}</h3>
        <p>Altitude: {impacts.altitude.toFixed(0)} km</p>
      </div>

      {/* Overall Risk */}
      <div className={`risk-card ${getRiskColorClass(impacts.overall.level)}`}>
        <div className="risk-header">
          <h3>OVERALL RISK</h3>
          <div className="risk-score">{impacts.overall.score}/100</div>
        </div>
        <div className="risk-level">{impacts.overall.level}</div>
      </div>

      {/* Atmospheric Drag Impact */}
      <div className="impact-card">
        <h4>🌀 Atmospheric Drag</h4>
        <div className="impact-metrics">
          <div className="metric">
            <span className="label">Orbit Decay Rate:</span>
            <span className="value">{impacts.drag.decayRate.toFixed(2)} m/day</span>
          </div>
          <div className="metric">
            <span className="label">Normal Decay:</span>
            <span className="value sub">{impacts.drag.normalDecay.toFixed(2)} m/day</span>
          </div>
          <div className="metric">
            <span className="label">Increase:</span>
            <span className={`value ${impacts.drag.increase > 100 ? 'warning' : ''}`}>
              +{impacts.drag.increase.toFixed(0)}%
            </span>
          </div>
          {impacts.drag.daysUntilReboost < 100 && (
            <div className="alert alert-warning">
              ⚠️ Reboost required within {impacts.drag.daysUntilReboost} days
            </div>
          )}
        </div>
      </div>

      {/* Radiation Impact */}
      <div className="impact-card">
        <h4>☢️ Radiation Effects</h4>
        <div className="impact-metrics">
          <div className="metric">
            <span className="label">Radiation Dose:</span>
            <span className="value">{impacts.radiation.dose.toFixed(1)} mrad/day</span>
          </div>
          <div className="metric">
            <span className="label">SEU Probability:</span>
            <span className={`value ${impacts.radiation.seuProbability > 30 ? 'warning' : ''}`}>
              {impacts.radiation.seuProbability.toFixed(1)}%
            </span>
          </div>
          <div className="metric">
            <span className="label">Safe Mode Risk:</span>
            <span className={`value ${impacts.radiation.safeModeRisk === 'HIGH' ? 'warning' : ''}`}>
              {impacts.radiation.safeModeRisk}
            </span>
          </div>
          {impacts.radiation.seuProbability > 30 && (
            <div className="alert alert-caution">
              ⚡ Elevated SEU risk - Monitor telemetry
            </div>
          )}
        </div>
      </div>

      {/* Communication Impact */}
      <div className="impact-card">
        <h4>📡 Communication/Signal</h4>
        <div className="impact-metrics">
          <div className="metric">
            <span className="label">Signal Quality:</span>
            <span className={`value ${impacts.signal.quality === 'SEVERE' ? 'warning' : ''}`}>
              {impacts.signal.quality}
            </span>
          </div>
          <div className="metric">
            <span className="label">Signal Loss:</span>
            <span className="value">{impacts.signal.signalLoss.toFixed(1)} dB</span>
          </div>
          <div className="metric">
            <span className="label">Degradation:</span>
            <span className="value">{impacts.signal.degradation.toFixed(0)}%</span>
          </div>
          {impacts.signal.blackoutDuration > 0 && (
            <div className="alert alert-warning">
              📡 Comm blackout expected: {impacts.signal.blackoutDuration}h
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      <div className="recommendations">
        <h4>💡 Recommended Actions</h4>
        <ul>
          {impacts.recommendations.map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ul>
      </div>

      {/* Satellite List */}
      <div className="satellite-list">
        <h4>All Satellites</h4>
        {satellites.slice(0, 10).map((sat, idx) => {
          const alt = getSatelliteAltitude(sat.line2)
          const satImpacts = calculateImpacts({ altitude: alt, ...spaceWeather })
          
          return (
            <button
              key={idx}
              className={`sat-item ${selectedSatellite.name === sat.name ? 'active' : ''}`}
              onClick={() => onSelectSatellite(sat)}
            >
              <span className="sat-name">{sat.name.trim().substring(0, 25)}</span>
              <span className={`sat-risk ${getRiskColorClass(satImpacts.overall.level)}`}>
                {satImpacts.overall.level}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}