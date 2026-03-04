import { useRef, useState } from "react"
import { useFrame } from "@react-three/fiber"
import { Text } from "@react-three/drei"
import * as THREE from "three"
import satelliteIcon from "../assets/satellite.png"
import { getSatellitePosition, scalePosition } from "../utils/orbit"

export default function Satellite({ 
  tle1, 
  tle2, 
  name = "SAT",
  isSelected = false,
  onClick,
  riskLevel = "low" 
}) {
  const ref = useRef()
  const orbitRef = useRef()
  const glowRef = useRef()
  const [hovered, setHovered] = useState(false)
  
  const texture = new THREE.TextureLoader().load(satelliteIcon)
  
  // Risk color mapping
  const riskColors = {
    critical: "#ff0044",
    high: "#ff6600", 
    medium: "#ffaa00",
    low: "#00ff88"
  }

  useFrame((state) => {
    const pos = getSatellitePosition(tle1, tle2)
    if (pos && ref.current) {
      const scaled = scalePosition(pos)
      ref.current.position.set(...scaled)
      
      // Update orbit trail
      if (orbitRef.current && isSelected) {
        orbitRef.current.position.set(...scaled)
      }

      // Pulsing glow effect for selected satellite
      if (glowRef.current && isSelected) {
        const scale = 0.15 + Math.sin(state.clock.elapsedTime * 2) * 0.03
        glowRef.current.scale.set(scale, scale, scale)
      }
    }
  })

  return (
    <group>
      {/* Satellite sprite */}
      <sprite 
        ref={ref} 
        scale={isSelected ? [0.12, 0.12, 0.12] : [0.08, 0.08, 0.08]}
        onClick={onClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <spriteMaterial
          map={texture}
          transparent
          depthWrite={false}
          opacity={isSelected || hovered ? 1.0 : 0.8}
        />
      </sprite>

      {/* Risk indicator glow */}
      {(isSelected || hovered) && (
        <sprite ref={glowRef} scale={[0.15, 0.15, 0.15]}>
          <spriteMaterial
            color={riskColors[riskLevel]}
            transparent
            opacity={0.4}
            depthWrite={false}
            blending={THREE.AdditiveBlending}
          />
        </sprite>
      )}

      {/* Label */}
      {(isSelected || hovered) && (
        <Text
          position={[0, 0.15, 0]}
          fontSize={0.05}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {name.trim().substring(0, 20)}
        </Text>
      )}
    </group>
  )
}