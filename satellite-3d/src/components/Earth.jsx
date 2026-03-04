import { useLoader } from "@react-three/fiber"
import { TextureLoader } from "three"

export default function Earth() {
  const texture = useLoader(
    TextureLoader,
    "https://threejs.org/examples/textures/land_ocean_ice_cloud_2048.jpg"
  )

  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}
