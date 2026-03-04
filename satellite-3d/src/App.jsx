import { useEffect, useState, useRef } from "react"
import { Canvas } from "@react-three/fiber"
import { OrbitControls, Stars } from "@react-three/drei"
import { fetchTLE, parseTLE } from "./api/tle"
import { fetchSpaceWeather } from "./api/spaceWeather"
import Earth from "./components/Earth"
import Satellite from "./components/Satellite"
import Magnetosphere from "./components/Magnetosphere"
import SpaceWeatherParticles from "./components/SpaceWeatherParticles"
import ImpactDashboard from "./components/ImpactDashboard"
import SpaceWeatherControls from "./components/SpaceWeatherControls"
import "./App.css"

function App() {
  const [satellites, setSatellites] = useState([])
  const [selectedSatellite, setSelectedSatellite] = useState(null)
  const [spaceWeather, setSpaceWeather] = useState({
    kpIndex: 3,
    f107: 120,
    solarWindSpeed: 400,
    protonFlux: 100
  })
  const [showMagnetosphere, setShowMagnetosphere] = useState(true)
  const [showParticles, setShowParticles] = useState(true)
  const kpRef = useRef(spaceWeather.kpIndex)

  // Load satellites
  useEffect(() => {
    async function loadTLE() {
      try {
        const text = await fetchTLE()
        const data = parseTLE(text)
        setSatellites(data.slice(0, 50)) // Load 0 satellites
        if (data.length > 0) {
          setSelectedSatellite(data[0])
        }
      } catch (error) {
        console.error("Failed to load satellites:", error)
      }
    }
    loadTLE()
  }, [])

  // Fetch real space weather data
  useEffect(() => {
    async function loadSpaceWeather() {
      try {
        const data = await fetchSpaceWeather()
        setSpaceWeather(prev => ({
          ...prev,
          kpIndex: data.kp || prev.kpIndex,
          f107: data.f107 || prev.f107,
          solarWindSpeed: data.solarWindSpeed || prev.solarWindSpeed
        }))
      } catch (error) {
        console.warn("Using default space weather values")
      }
    }
    loadSpaceWeather()
    
    // Update every 15 minutes
    const interval = setInterval(loadSpaceWeather, 15 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app-container">
      {/* 3D Visualization */}
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 0, 3], fov: 45 }}>
          <color attach="background" args={["#000000"]} />
          
          {/* Lighting */}
          <ambientLight intensity={0.3} />
          <directionalLight position={[5, 3, 5]} intensity={1} />
          <pointLight position={[-5, -3, -5]} intensity={0.5} />

          {/* Stars background */}
          <Stars radius={300} depth={60} count={5000} factor={7} />

          {/* Earth */}
          <Earth />

          {/* Magnetosphere */}
          {showMagnetosphere && <Magnetosphere kpRef={kpRef} />}

          {/* Space Weather Particles */}
          {showParticles && (
            <SpaceWeatherParticles
              kpRef={kpRef}
              solarWindSpeed={spaceWeather.solarWindSpeed}
            />
          )}


          {/* Satellites */}
          {satellites.map((sat, idx) => (
            <Satellite
              key={idx}
              tle1={sat.line1}
              tle2={sat.line2}
              name={sat.name}
              isSelected={selectedSatellite?.name === sat.name}
              onClick={() => setSelectedSatellite(sat)}
            />
          ))}

          <OrbitControls 
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={1.5}
            maxDistance={10}
          />
        </Canvas>

        {/* Overlay Info */}
        <div className="info-overlay">
          <h1>🛰️ Space Weather Impact Modeling System</h1>
          <div className="weather-status">
            <div className={`kp-badge kp-${Math.floor(spaceWeather.kpIndex / 3)}`}>
              Kp: {spaceWeather.kpIndex}
            </div>
            <div className="weather-stat">F10.7: {spaceWeather.f107}</div>
            <div className="weather-stat">Solar Wind: {spaceWeather.solarWindSpeed} km/s</div>
          </div>
        </div>
      </div>

      <SpaceWeatherControls
        spaceWeather={spaceWeather}
        setSpaceWeather={setSpaceWeather}
        kpRef={kpRef}   // 👈 ADD THIS
        showMagnetosphere={showMagnetosphere}
        setShowMagnetosphere={setShowMagnetosphere}
        showParticles={showParticles}
        setShowParticles={setShowParticles}
      />


      {/* Impact Dashboard */}
      <ImpactDashboard
        selectedSatellite={selectedSatellite}
        spaceWeather={spaceWeather}
        satellites={satellites}
        onSelectSatellite={setSelectedSatellite}
      />
    </div>
  )
}

export default App