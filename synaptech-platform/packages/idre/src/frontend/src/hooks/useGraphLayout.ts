import { useEffect, useState, useRef } from 'react'
import type { GraphLayout } from '../types/connectome'

const LAYOUT_URL = '/api/v1/connectome/layout'

export function useGraphLayout() {
  const [layout, setLayout] = useState<GraphLayout | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const workerRef = useRef<Worker | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchLayout() {
      try {
        const res = await fetch(LAYOUT_URL)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()

        const positions = data.positions as number[][]
        const shape: [number, number] = data.shape as [number, number]

        if (!cancelled) {
          setLayout({ positions, shape })
          setLoading(false)

          // refine in worker
          if (typeof Worker !== 'undefined' && positions.length > 0) {
            const workerCode = `
              self.onmessage = function(e) {
                const pos = e.data;
                const n = pos.length;
                const steps = 20;
                for (let s = 0; s < steps; s++) {
                  for (let i = 0; i < n; i++) {
                    for (let j = i + 1; j < n && j < i + 50; j++) {
                      const dx = pos[i][0] - pos[j][0];
                      const dy = pos[i][1] - pos[j][1];
                      const dz = pos[i][2] - pos[j][2];
                      const d = Math.sqrt(dx*dx + dy*dy + dz*dz) + 0.01;
                      const f = 0.001 / (d * d);
                      pos[i][0] += dx * f;
                      pos[i][1] += dy * f;
                      pos[i][2] += dz * f;
                      pos[j][0] -= dx * f;
                      pos[j][1] -= dy * f;
                      pos[j][2] -= dz * f;
                    }
                  }
                }
                self.postMessage(pos);
              };
            `
            const blob = new Blob([workerCode], { type: 'application/javascript' })
            const worker = new Worker(URL.createObjectURL(blob))
            workerRef.current = worker

            worker.postMessage(positions)
            worker.onmessage = (e) => {
              if (!cancelled) {
                setLayout({ positions: e.data, shape })
              }
              worker.terminate()
              workerRef.current = null
            }
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Layout fetch failed')
          setLoading(false)
        }
      }
    }

    fetchLayout()

    return () => {
      cancelled = true
      if (workerRef.current) {
        workerRef.current.terminate()
        workerRef.current = null
      }
    }
  }, [])

  return { layout, loading, error }
}
