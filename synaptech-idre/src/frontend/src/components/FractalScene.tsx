import { useRef } from 'react'
import { OrbitControls } from '@react-three/drei'
import { MorphingNeurons } from './MorphingNeurons'
import { CircuitTraces } from './CircuitTraces'

interface Props {
  morphRef: { current: { morph: number } }
}

export default function FractalScene({ morphRef }: Props) {
  const controlsRef = useRef<any>(null)

  return (
    <>
      <ambientLight intensity={0.5} />

      <MorphingNeurons morphRef={morphRef} />
      <CircuitTraces morphRef={morphRef} />

      <OrbitControls
        ref={controlsRef}
        autoRotate
        autoRotateSpeed={0.15}
        enableDamping={false}
        enableZoom={false}
        enablePan={false}
      />
    </>
  )
}
