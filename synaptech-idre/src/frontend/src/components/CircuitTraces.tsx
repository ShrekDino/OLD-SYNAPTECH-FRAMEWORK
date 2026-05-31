import { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const N_NEURONS = 130_000
const N_HUBS = 2000
const CONNECTIONS_PER_HUB = 2

export function CircuitTraces({
  morphRef,
}: {
  morphRef: { current: { morph: number } }
}) {
  const lineRef = useRef<THREE.LineSegments>(null)
  const materialRef = useRef<THREE.ShaderMaterial>(null)
  const timeRef = useRef(0)

  const { positions, distances, seeds } = useMemo(() => {
    const hubIndices = new Set<number>()
    while (hubIndices.size < N_HUBS) {
      hubIndices.add(Math.floor(Math.random() * N_NEURONS))
    }
    const hubs = Array.from(hubIndices)
    const segments: number[] = []
    const dists: number[] = []
    const seedArr: number[] = []

    for (let hi = 0; hi < hubs.length; hi++) {
      const h = hubs[hi]
      const hx = (h / N_NEURONS) * 40 - 20
      const hy = Math.sin((h / N_NEURONS) * Math.PI * 2) * 10
      const hz = Math.cos((h / N_NEURONS) * Math.PI * 2) * 5

      const candidates: { idx: number; dist: number }[] = []
      for (let c = 0; c < 20; c++) {
        const n = hubs[(hi + c * 7 + 3) % hubs.length]
        if (n === h) continue
        const nx = (n / N_NEURONS) * 40 - 20
        const ny = Math.sin((n / N_NEURONS) * Math.PI * 2) * 10
        const nz = Math.cos((n / N_NEURONS) * Math.PI * 2) * 5
        const d = Math.sqrt((hx - nx) ** 2 + (hy - ny) ** 2 + (hz - nz) ** 2)
        candidates.push({ idx: n, dist: d })
      }
      candidates.sort((a, b) => a.dist - b.dist)

      for (let k = 0; k < Math.min(CONNECTIONS_PER_HUB, candidates.length); k++) {
        const n = candidates[k].idx
        const nhx = (n / N_NEURONS) * 40 - 20
        const nhy = Math.sin((n / N_NEURONS) * Math.PI * 2) * 10
        const nhz = Math.cos((n / N_NEURONS) * Math.PI * 2) * 5

        segments.push(hx, hy, hz, nhx, nhy, nhz)
        dists.push(candidates[k].dist, candidates[k].dist)
        seedArr.push(hi / N_HUBS, (hi + 1) / N_HUBS)
      }
    }

    return {
      positions: new Float32Array(segments),
      distances: new Float32Array(dists),
      seeds: new Float32Array(seedArr),
    }
  }, [])

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    const nVerts = positions.length / 3
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('aDistance', new THREE.BufferAttribute(distances, 1))
    geo.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1))
    geo.setAttribute('aSourcePos', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('aTargetPos', new THREE.BufferAttribute(positions, 3))

    const indices: number[] = []
    for (let i = 0; i < nVerts; i++) indices.push(i)
    geo.setIndex(indices)

    return geo
  }, [positions, distances, seeds])

  const linePositions = useMemo(() => {
    const nVerts = positions.length / 3
    const src = new Float32Array(positions)
    const tgt = new Float32Array(positions)
    for (let i = 0; i < nVerts; i += 2) {
      const s1 = i * 3
      const s2 = (i + 1) * 3
      tgt[s1] = positions[s1 + 3] || positions[s1]
      tgt[s1 + 1] = positions[s1 + 4] || positions[s1 + 1]
      tgt[s1 + 2] = positions[s1 + 5] || positions[s1 + 2]
      tgt[s2] = positions[s1]
      tgt[s2 + 1] = positions[s1 + 1]
      tgt[s2 + 2] = positions[s1 + 2]
    }
    return { src, tgt }
  }, [positions])

  useEffect(() => {
    if (!geometry) return
    geometry.attributes.aSourcePos = new THREE.BufferAttribute(linePositions.src, 3)
    geometry.attributes.aTargetPos = new THREE.BufferAttribute(linePositions.tgt, 3)
  }, [geometry, linePositions])

  useFrame(() => {
    timeRef.current += 0.008
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = timeRef.current
      materialRef.current.uniforms.uMorph.value = morphRef.current.morph
    }
  })

  return (
    <lineSegments ref={lineRef} geometry={geometry}>
      <shaderMaterial
        ref={materialRef}
        vertexShader={circuitVert}
        fragmentShader={circuitFrag}
        uniforms={{
          uMorph: { value: 0 },
          uTime: { value: 0 },
          uOpacity: { value: 0.6 },
        }}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </lineSegments>
  )
}

const circuitVert = `
attribute vec3 aSourcePos;
attribute vec3 aTargetPos;
attribute float aDistance;
attribute float aSeed;

uniform float uMorph;
uniform float uTime;

varying float vPulse;
varying float vDist;

void main() {
  vec3 pos = mix(aSourcePos, aTargetPos, uMorph);

  vec4 mvPos = modelViewMatrix * vec4(pos, 1.0);
  vDist = aDistance;
  vPulse = aSeed;

  gl_Position = projectionMatrix * mvPos;
}
`

const circuitFrag = `
uniform float uTime;
uniform float uOpacity;

varying float vPulse;
varying float vDist;

void main() {
  float pulse = 0.5 + 0.5 * sin(uTime * 2.0 + vPulse * 6.28);

  vec3 techBlue = vec3(0.161, 0.475, 1.0);
  vec3 circuitGold = vec3(1.0, 0.702, 0.0);
  vec3 color = mix(techBlue, circuitGold, pulse * 0.6);

  float alpha = uOpacity * (0.15 + 0.45 * pulse);

  gl_FragColor = vec4(color, alpha);
}
`
