import { useRef } from "react"
import { useFrame } from "@react-three/fiber"
import * as THREE from "three"

export default function Magnetosphere({ kpRef }) {
  const innerBeltRef = useRef(null)
  const outerBeltRef = useRef(null)
  const magnetopauseRef = useRef(null)

  // ✅ Create geometries ONCE (no kp dependency)
  const innerBeltGeometry = new THREE.TorusGeometry(1.8, 0.3, 16, 100)
  const outerBeltGeometry = new THREE.TorusGeometry(4.5, 1.5, 16, 100)

  const magnetopauseGeometry = (() => {
    const curve = new THREE.EllipseCurve(
      0, 0,
      10, 8,
      0, Math.PI * 2
    )
    const points = curve.getPoints(100)
    return new THREE.BufferGeometry().setFromPoints(points)
  })()

  // ✅ Animate transforms only (NO geometry rebuild)
  useFrame(() => {
    const kp = kpRef.current

    // Storms compress magnetosphere
    const compression = 1 - (kp - 3) * 0.05
    const safeCompression = Math.max(0.6, compression)

    if (innerBeltRef.current) {
      innerBeltRef.current.rotation.x = Math.PI / 2
      innerBeltRef.current.rotation.z += 0.001
      innerBeltRef.current.scale.setScalar(safeCompression)
    }

    if (outerBeltRef.current) {
      outerBeltRef.current.rotation.x = Math.PI / 2
      outerBeltRef.current.rotation.z -= 0.0005
      outerBeltRef.current.scale.setScalar(safeCompression)
    }

    if (magnetopauseRef.current) {
      magnetopauseRef.current.scale.setScalar(safeCompression)
    }
  })

  return (
    <group>
      {/* Inner Van Allen Belt */}
      <mesh ref={innerBeltRef} geometry={innerBeltGeometry}>
        <meshBasicMaterial
          color="#ff6666"
          transparent
          opacity={0.15}
          side={THREE.DoubleSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Outer Van Allen Belt */}
      <mesh ref={outerBeltRef} geometry={outerBeltGeometry}>
        <meshBasicMaterial
          color="#ff9944"
          transparent
          opacity={0.12}
          side={THREE.DoubleSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Magnetopause Boundary */}
      <line ref={magnetopauseRef} geometry={magnetopauseGeometry}>
        <lineBasicMaterial
          color="#8866ff"
          transparent
          opacity={0.3}
        />
      </line>
    </group>
  )
}
