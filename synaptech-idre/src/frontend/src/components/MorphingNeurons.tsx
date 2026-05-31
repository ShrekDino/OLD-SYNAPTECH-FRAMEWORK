import { useRef, useEffect, useMemo, forwardRef, useImperativeHandle } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const N_NEURONS = 130_000
const SPHERE_RADIUS = 0.3

export interface MorphHandle {
  setMorph: (v: number) => void
}

export const MorphingNeurons = forwardRef<MorphHandle, { morphRef: { current: { morph: number } } }>(
  ({ morphRef }, ref) => {
    const meshRef = useRef<THREE.InstancedMesh>(null)
    const materialRef = useRef<THREE.ShaderMaterial>(null)
    const timeRef = useRef(0)

    useImperativeHandle(ref, () => ({
      setMorph: (v) => { morphRef.current.morph = v },
    }))

    const { fractalPos, neuronPos } = useMemo(() => {
      const fPos = new Float32Array(N_NEURONS * 3)
      const nPos = new Float32Array(N_NEURONS * 3)
      const seeds = new Float32Array(N_NEURONS)

      for (let i = 0; i < N_NEURONS; i++) {
        const seed = i / N_NEURONS
        seeds[i] = seed

        const theta = seed * Math.PI * 2 * 7
        const phi = Math.acos(2 * ((seed * 13.37) % 1) - 1)
        const r = 20 + 10 * Math.sin(seed * 47.11)
        fPos[i * 3] = r * Math.sin(phi) * Math.cos(theta)
        fPos[i * 3 + 1] = r * Math.cos(phi)
        fPos[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta)

        const t = i / N_NEURONS
        const tx = 40 * (t - 0.5) * 0.8
        const ty = 40 * (0.5 - Math.abs(t - 0.5) * 2) * 0.4
        const tz = 10 * Math.sin(t * Math.PI * 4) * 0.6
        nPos[i * 3] = tx
        nPos[i * 3 + 1] = ty
        nPos[i * 3 + 2] = tz
      }
      return { fractalPos: fPos, neuronPos: nPos, seeds }
    }, [])

    useEffect(() => {
      if (!meshRef.current) return
      const mesh = meshRef.current
      mesh.count = N_NEURONS

      const dummy = new THREE.Object3D()
      for (let i = 0; i < N_NEURONS; i++) {
        dummy.position.set(fractalPos[i * 3], fractalPos[i * 3 + 1], fractalPos[i * 3 + 2])
        dummy.updateMatrix()
        mesh.setMatrixAt(i, dummy.matrix)
      }
      mesh.instanceMatrix.needsUpdate = true

      const geometry = mesh.geometry
      geometry.setAttribute('aFractalPos', new THREE.InstancedBufferAttribute(fractalPos, 3))
      geometry.setAttribute('aNeuronPos', new THREE.InstancedBufferAttribute(neuronPos, 3))
      geometry.setAttribute(
        'aSeed',
        new THREE.InstancedBufferAttribute(
          new Float32Array(N_NEURONS).map((_, i) => (i / N_NEURONS)),
          1
        )
      )

      return () => {
        geometry.deleteAttribute('aFractalPos')
        geometry.deleteAttribute('aNeuronPos')
        geometry.deleteAttribute('aSeed')
      }
    }, [fractalPos, neuronPos])

    useFrame(() => {
      timeRef.current += 0.01
      if (materialRef.current) {
        materialRef.current.uniforms.uTime.value = timeRef.current
        materialRef.current.uniforms.uMorph.value = morphRef.current.morph
      }

      if (!meshRef.current) return
      const mesh = meshRef.current
      const m = morphRef.current.morph
      const dummy = new THREE.Object3D()
      for (let i = 0; i < N_NEURONS; i++) {
        const jitter = (1 - m) * 2
        const ax = timeRef.current * 1.7 + (i / N_NEURONS) * 13.37
        const ay = timeRef.current * 2.1 + (i / N_NEURONS) * 7.11
        const jx = Math.sin(ax) * jitter
        const jy = Math.cos(ay) * jitter
        const jz = Math.sin(ax + ay) * jitter * 0.7

        const fx = fractalPos[i * 3]
        const fy = fractalPos[i * 3 + 1]
        const fz = fractalPos[i * 3 + 2]
        const nx = neuronPos[i * 3]
        const ny = neuronPos[i * 3 + 1]
        const nz = neuronPos[i * 3 + 2]

        dummy.position.set(
          fx + (nx - fx) * m + jx,
          fy + (ny - fy) * m + jy,
          fz + (nz - fz) * m + jz
        )
        dummy.updateMatrix()
        mesh.setMatrixAt(i, dummy.matrix)
      }
      mesh.instanceMatrix.needsUpdate = true
    })

    return (
      <instancedMesh ref={meshRef} args={[undefined, undefined, N_NEURONS]}>
        <sphereGeometry args={[SPHERE_RADIUS, 6, 6]} />
        <shaderMaterial
          ref={materialRef}
          vertexShader={document.getElementById('morph-vert')?.textContent || morphVert}
          fragmentShader={document.getElementById('morph-frag')?.textContent || morphFrag}
          uniforms={{
            uMorph: { value: 0 },
            uTime: { value: 0 },
            uJitterIntensity: { value: 3.0 },
          }}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </instancedMesh>
    )
  }
)

MorphingNeurons.displayName = 'MorphingNeurons'

const morphVert = `
attribute vec3 aFractalPos;
attribute vec3 aNeuronPos;
attribute float aSeed;

uniform float uMorph;
uniform float uTime;
uniform float uJitterIntensity;

varying vec3 vColor;
varying float vMorphAmount;
varying float vSeed;

void main() {
  float jitter = (1.0 - uMorph) * uJitterIntensity;
  float ax = uTime * 1.7 + aSeed * 13.37;
  float ay = uTime * 2.1 + aSeed * 7.11;
  vec3 jitterOffset = vec3(
    sin(ax) * jitter,
    cos(ay) * jitter,
    sin(ax + ay) * jitter * 0.7
  );

  vec3 pos = mix(aFractalPos, aNeuronPos, uMorph) + jitterOffset;

  vec4 worldPos = instanceMatrix * vec4(pos, 1.0);
  vec4 mvPos = viewMatrix * worldPos;

  vec3 techBlue = vec3(0.161, 0.475, 1.0);
  vec3 circuitGold = vec3(1.0, 0.702, 0.0);
  vColor = mix(techBlue, circuitGold, uMorph * 0.3);
  vMorphAmount = uMorph;
  vSeed = aSeed;

  gl_Position = projectionMatrix * mvPos;
  gl_PointSize = 2.5 + uMorph * 2.0;
}
`

const morphFrag = `
varying vec3 vColor;
varying float vMorphAmount;
varying float vSeed;

uniform float uTime;

void main() {
  vec2 center = gl_PointCoord - vec2(0.5);
  float dist = length(center);
  if (dist > 0.5) discard;

  float softness = 1.0 - smoothstep(0.0, 0.5, dist);
  float glow = softness * (0.6 + 0.4 * vMorphAmount);
  float ripple = 0.5 + 0.5 * sin(uTime * 3.0 + vSeed * 6.28);

  vec3 goldGlow = vec3(1.0, 0.702, 0.0) * glow * 0.5 * ripple;
  vec3 color = vColor + goldGlow;
  float alpha = glow * 0.85;

  gl_FragColor = vec4(color, alpha);
}
`
