import { useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stats } from '@react-three/drei'

import { NeuronInstances } from './NeuronInstances'
import { useGraphLayout } from '../hooks/useGraphLayout'
import { useSSEStore } from '../hooks/useSSE'

const N_NEURONS = 130_000

interface Props {
  selectedNeuron: number | null
  onSelect: (id: number | null) => void
}

function SceneContent({ selectedNeuron, onSelect }: Props) {
  const { layout, loading } = useGraphLayout()
  const neuronStates = useSSEStore((s) => s.neuronStates)
  const controlsRef = useRef<any>(null)

  if (loading) {
    return (
      <mesh>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color="#4488ff" wireframe />
      </mesh>
    )
  }

  if (!layout) {
    return null
  }

  return (
    <>
      <ambientLight intensity={0.15} />
      <directionalLight position={[10, 10, 10]} intensity={0.6} />
      <directionalLight position={[-10, -5, -10]} intensity={0.3} />

      <NeuronInstances
        layout={layout}
        neuronStates={neuronStates}
        neuronCount={N_NEURONS}
        selectedNeuron={selectedNeuron}
        onSelect={onSelect}
      />

      <OrbitControls
        ref={controlsRef}
        autoRotate
        autoRotateSpeed={0.2}
        enableDamping
        dampingFactor={0.05}
        minDistance={5}
        maxDistance={200}
      />
    </>
  )
}

export default function BrainViewer({ selectedNeuron, onSelect }: Props) {
  return (
    <Canvas
      camera={{ position: [0, 0, 60], fov: 50, near: 0.1, far: 500 }}
      gl={{
        antialias: true,
        alpha: false,
        powerPreference: 'high-performance',
      }}
      style={{ width: '100%', height: '100%' }}
    >
      <color attach="background" args={['#08080f']} />
      <SceneContent selectedNeuron={selectedNeuron} onSelect={onSelect} />
      <Stats />
    </Canvas>
  )
}
