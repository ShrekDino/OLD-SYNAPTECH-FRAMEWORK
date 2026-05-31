import { useRef, useEffect, useMemo, useCallback } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { GraphLayout, NeuronState } from '../types/connectome'

interface Props {
  layout: GraphLayout
  neuronStates: Map<number, NeuronState>
  neuronCount: number
  selectedNeuron: number | null
  onSelect: (id: number | null) => void
}

const SPHERE_RADIUS = 0.3
const COLOR_IDLE = new THREE.Color('#1a3366')
const COLOR_ACTIVE = new THREE.Color('#ff4444')
const COLOR_SPIKE = new THREE.Color('#ffaa00')
const COLOR_SELECTED = new THREE.Color('#00ff88')

const tempMatrix = new THREE.Matrix4()
const tempPos = new THREE.Vector3()
const tempColor = new THREE.Color()

export function NeuronInstances({ layout, neuronStates, neuronCount, selectedNeuron, onSelect }: Props) {
  const meshRef = useRef<THREE.InstancedMesh>(null)

  const positions = useMemo(() => {
    const p = layout.positions
    const arr = new Float32Array(neuronCount * 3)
    for (let i = 0; i < Math.min(neuronCount, p.length); i++) {
      arr[i * 3] = p[i][0] * 35
      arr[i * 3 + 1] = p[i][1] * 35
      arr[i * 3 + 2] = p[i][2] * 35
    }
    return arr
  }, [layout, neuronCount])

  useEffect(() => {
    if (!meshRef.current) return
    const mesh = meshRef.current
    mesh.count = Math.min(neuronCount, layout.positions.length)

    const colorArray = new Float32Array(mesh.count * 3)
    for (let i = 0; i < mesh.count; i++) {
      tempPos.set(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2])
      tempMatrix.identity()
      tempMatrix.setPosition(tempPos)
      mesh.setMatrixAt(i, tempMatrix)
      COLOR_IDLE.toArray(colorArray, i * 3)
    }
    mesh.instanceMatrix.needsUpdate = true
    mesh.instanceColor = new THREE.InstancedBufferAttribute(colorArray, 3)
    mesh.instanceColor.needsUpdate = true
  }, [positions, layout, neuronCount])

  useFrame(() => {
    if (!meshRef.current || !meshRef.current.instanceColor) return
    const colors = meshRef.current.instanceColor.array as Float32Array
    const count = meshRef.current.count
    let needsUpdate = false

    for (let i = 0; i < count; i++) {
      if (i === selectedNeuron) {
        COLOR_SELECTED.toArray(colors, i * 3)
        needsUpdate = true
        continue
      }

      const state = neuronStates.get(i)
      if (state) {
        const intensity = Math.min(Math.abs(state.voltage) / 1.0, 1.0)
        if (state.spike) {
          COLOR_SPIKE.toArray(colors, i * 3)
        } else if (intensity > 0.3) {
          tempColor.copy(COLOR_ACTIVE).lerp(COLOR_SPIKE, intensity)
          tempColor.toArray(colors, i * 3)
        } else {
          tempColor.copy(COLOR_IDLE).lerp(COLOR_ACTIVE, intensity * 3)
          tempColor.toArray(colors, i * 3)
        }
        needsUpdate = true
      }
    }

    if (needsUpdate) {
      meshRef.current.instanceColor!.needsUpdate = true
    }
  })

  const handlePointerDown = useCallback((e: any) => {
    e.stopPropagation()
    const id = e.instanceId
    if (id !== undefined) {
      onSelect(id === selectedNeuron ? null : id)
    }
  }, [selectedNeuron, onSelect])

  const count = Math.min(neuronCount, layout.positions.length)

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, count]}
      onPointerDown={handlePointerDown}
    >
      <sphereGeometry args={[SPHERE_RADIUS, 6, 6]} />
      <meshStandardMaterial
        vertexColors
      />
    </instancedMesh>
  )
}
