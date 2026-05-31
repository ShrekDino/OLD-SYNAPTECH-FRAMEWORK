import { useRef, useEffect, useMemo } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'

interface Pulse {
  position: THREE.Vector3
  intensity: number
  decay: number
}

export function ActivationPulse({ position, intensity }: { position: THREE.Vector3; intensity: number }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const startTime = useRef(Date.now())
  const duration = 500

  useFrame(() => {
    if (!meshRef.current) return
    const elapsed = Date.now() - startTime.current
    const t = Math.max(0, 1 - elapsed / duration)

    const scale = 1 + (1 - t) * 3
    meshRef.current.scale.setScalar(scale)
    const mat = meshRef.current.material as THREE.MeshBasicMaterial
    mat.opacity = t * intensity * 0.8

    if (t <= 0) {
      mat.opacity = 0
    }
  })

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.8, 16, 16]} />
      <meshBasicMaterial
        color="#ffaa00"
        transparent
        opacity={0}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </mesh>
  )
}

interface PulseGroupProps {
  pulses: Map<number, { pos: THREE.Vector3; intensity: number }>
}

export function PulseGroup({ pulses }: PulseGroupProps) {
  const entries = useMemo(() => Array.from(pulses.entries()), [pulses])

  return (
    <group>
      {entries.map(([id, p]) => (
        <ActivationPulse key={id} position={p.pos} intensity={p.intensity} />
      ))}
    </group>
  )
}
