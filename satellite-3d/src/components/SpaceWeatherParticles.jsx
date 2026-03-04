import { useRef, useEffect } from "react"
import { useFrame } from "@react-three/fiber"
import * as THREE from "three"

export default function SpaceWeatherParticles({ kpRef, solarWindSpeed = 400 }) {
  const particlesRef = useRef()
  const velocitiesRef = useRef()

  const PARTICLE_COUNT = 2000

  useEffect(() => {
    const positions = new Float32Array(PARTICLE_COUNT * 3)
    const velocities = new Float32Array(PARTICLE_COUNT * 3)
    const colors = new Float32Array(PARTICLE_COUNT * 3)

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3
      const angle = Math.random() * Math.PI * 2
      const radius = 15 + Math.random() * 5

      positions[i3] = radius * Math.cos(angle)
      positions[i3 + 1] = (Math.random() - 0.5) * 10
      positions[i3 + 2] = radius * Math.sin(angle)

      velocities[i3] = 0
      velocities[i3 + 1] = 0
      velocities[i3 + 2] = 0

      colors[i3] = 1.0
      colors[i3 + 1] = 0.6
      colors[i3 + 2] = 0.2
    }

    velocitiesRef.current = velocities

    particlesRef.current.geometry.setAttribute(
      "position",
      new THREE.BufferAttribute(positions, 3)
    )

    particlesRef.current.geometry.setAttribute(
      "color",
      new THREE.BufferAttribute(colors, 3)
    )
  }, [])

  useFrame(() => {
    if (!particlesRef.current) return

    const kp = kpRef.current
    const speedFactor = (solarWindSpeed / 400) * (0.02 + kp * 0.01)

    const positions = particlesRef.current.geometry.attributes.position.array
    const velocities = velocitiesRef.current

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3

      velocities[i3] = -speedFactor
      velocities[i3 + 1] *= 0.98
      velocities[i3 + 2] *= 0.98

      positions[i3] += velocities[i3]
      positions[i3 + 1] += velocities[i3 + 1]
      positions[i3 + 2] += velocities[i3 + 2]

      const dist = Math.sqrt(
        positions[i3] ** 2 +
        positions[i3 + 1] ** 2 +
        positions[i3 + 2] ** 2
      )

      if (dist < 2 || dist > 30) {
        const angle = Math.random() * Math.PI * 2
        const radius = 15 + Math.random() * 5

        positions[i3] = radius * Math.cos(angle)
        positions[i3 + 1] = (Math.random() - 0.5) * 10
        positions[i3 + 2] = radius * Math.sin(angle)
      }
    }

    particlesRef.current.geometry.attributes.position.needsUpdate = true
    particlesRef.current.material.opacity = Math.min(0.9, kp / 9)
  })

  return (
    <points ref={particlesRef}>
      <bufferGeometry />
      <pointsMaterial
        size={0.12}
        vertexColors
        transparent
        opacity={0.6}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}
