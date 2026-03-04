import "./SpaceWeatherControls.css"

export default function SpaceWeatherControls({
  spaceWeather,
  setSpaceWeather,
  kpRef,
  showMagnetosphere,
  setShowMagnetosphere,
  showParticles,
  setShowParticles
}) {
    // throttle timer (persists across calls)
  let kpTimeout = null

  function handleKpChange(value) {
    // update 3D instantly
    kpRef.current = value

    // throttle React state update (UI only)
    clearTimeout(kpTimeout)
    kpTimeout = setTimeout(() => {
      setSpaceWeather(prev => ({
        ...prev,
        kpIndex: value
      }))
    }, 100)
  }

  return (
    <div className="controls-panel">
      <h3>🌤️ Space Weather Parameters</h3>
      
      {/* Kp Index */}
      <div className="control-group">
        <label>
          <span>Kp Index</span>
          <span className={`kp-value kp-${Math.floor(spaceWeather.kpIndex / 3)}`}>
            {spaceWeather.kpIndex}
          </span>
        </label>
        <input
          type="range"
          min="0"
          max="9"
          step="1"
          value={spaceWeather.kpIndex}
          onChange={(e) => handleKpChange(parseFloat(e.target.value))}
        />
        <div className="range-labels">
          <span>Quiet</span>
          <span>Storm</span>
        </div>
      </div>

      {/* F10.7 Solar Flux */}
      <div className="control-group">
        <label>
          <span>F10.7 Solar Flux</span>
          <span className="value">{spaceWeather.f107}</span>
        </label>
        <input
          type="range"
          min="70"
          max="250"
          step="10"
          value={spaceWeather.f107}
          onChange={(e) => setSpaceWeather(prev => ({
            ...prev,
            f107: parseFloat(e.target.value)
          }))}
        />
        <div className="range-labels">
          <span>Low</span>
          <span>High</span>
        </div>
      </div>

      {/* Solar Wind Speed */}
      <div className="control-group">
        <label>
          <span>Solar Wind Speed</span>
          <span className="value">{spaceWeather.solarWindSpeed} km/s</span>
        </label>
        <input
          type="range"
          min="300"
          max="900"
          step="50"
          value={spaceWeather.solarWindSpeed}
          onChange={(e) => setSpaceWeather(prev => ({
            ...prev,
            solarWindSpeed: parseFloat(e.target.value)
          }))}
        />
        <div className="range-labels">
          <span>Slow</span>
          <span>Fast</span>
        </div>
      </div>

      {/* Proton Flux */}
      <div className="control-group">
        <label>
          <span>Proton Flux</span>
          <span className="value">{spaceWeather.protonFlux} pfu</span>
        </label>
        <input
          type="range"
          min="1"
          max="10000"
          step="100"
          value={spaceWeather.protonFlux}
          onChange={(e) => setSpaceWeather(prev => ({
            ...prev,
            protonFlux: parseFloat(e.target.value)
          }))}
        />
        <div className="range-labels">
          <span>Low</span>
          <span>Extreme</span>
        </div>
      </div>

      <hr />

      <h3>👁️ Visualization Options</h3>
      
      <div className="checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={showMagnetosphere}
            onChange={(e) => setShowMagnetosphere(e.target.checked)}
          />
          <span>Show Magnetosphere</span>
        </label>

        <label>
          <input
            type="checkbox"
            checked={showParticles}
            onChange={(e) => setShowParticles(e.target.checked)}
          />
          <span>Show Solar Wind Particles</span>
        </label>
      </div>

      {/* Quick Presets */}
      <div className="presets">
        <h4>Quick Scenarios</h4>
        <button onClick={() => setSpaceWeather({
          kpIndex: 2,
          f107: 90,
          solarWindSpeed: 350,
          protonFlux: 10
        })}>
          ☀️ Quiet Conditions
        </button>
        
        <button onClick={() => setSpaceWeather({
          kpIndex: 6,
          f107: 180,
          solarWindSpeed: 600,
          protonFlux: 1000
        })}>
          ⚡ Moderate Storm
        </button>
        
        <button onClick={() => setSpaceWeather({
          kpIndex: 9,
          f107: 250,
          solarWindSpeed: 850,
          protonFlux: 8000
        })}>
          🔥 Severe Storm
        </button>
      </div>
    </div>
  )
}