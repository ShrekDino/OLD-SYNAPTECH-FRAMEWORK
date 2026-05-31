import { useCallback, useRef } from 'react'
import * as THREE from 'three'
import gsap from 'gsap'

export function useCameraTransition() {
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)
  const morphRef = useRef<{ morph: number }>({ morph: 0 })
  const cardRef = useRef<HTMLDivElement | null>(null)

  const flyToDashboard = useCallback((): Promise<void> => {
    return new Promise((resolve) => {
      const tl = gsap.timeline({
        onComplete: () => {
          resolve()
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
    })
  }, [])

  return { cameraRef, morphRef, cardRef, flyToDashboard }
}
