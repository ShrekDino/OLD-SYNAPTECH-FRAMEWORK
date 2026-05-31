import { useRef, useCallback } from 'react'
import { Canvas } from '@react-three/fiber'
import * as THREE from 'three'
import gsap from 'gsap'

import FractalScene from '../components/FractalScene'
import SignInCard from '../components/SignInCard'

interface Props {
  onEnter: () => void
}

export default function SignInScreen({ onEnter }: Props) {
  const cameraRef = useRef<THREE.PerspectiveCamera>(null)
  const morphRef = useRef<{ morph: number }>({ morph: 0 })
  const cardRef = useRef<HTMLDivElement>(null)
  const transitioningRef = useRef(false)

  const handleCardClick = useCallback(() => {
    if (transitioningRef.current) return
    transitioningRef.current = true

    const tl = gsap.timeline({
      onComplete: () => {
        onEnter()
      },
    })

    if (cameraRef.current) {
      tl.to(cameraRef.current.position, {
        z: 15,
        duration: 1.8,
        ease: 'power3.inOut',
      })
    }

    tl.to(
      morphRef.current,
      {
        morph: 1,
        duration: 1.2,
        ease: 'power2.out',
      },
      0
    )

    if (cardRef.current) {
      tl.to(
        cardRef.current,
        {
          opacity: 0,
          scale: 0.92,
          duration: 0.5,
          ease: 'power2.in',
        },
        0.8
      )
    }
  }, [onEnter])

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: '#ffffff' }}>
      <Canvas
        camera={{ position: [0, 0, 80], fov: 45, near: 0.1, far: 200 }}
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance',
        }}
        style={{ width: '100%', height: '100%' }}
        onCreated={({ camera }) => {
          cameraRef.current = camera as THREE.PerspectiveCamera
        }}
      >
        <color attach="background" args={['#ffffff']} />
        <FractalScene morphRef={morphRef} />
      </Canvas>

      <SignInCard ref={cardRef} onClick={handleCardClick} />
    </div>
  )
}
