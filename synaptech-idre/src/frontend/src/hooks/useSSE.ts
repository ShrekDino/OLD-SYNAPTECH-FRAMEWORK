import { useEffect, useRef, useCallback } from 'react'
import { create } from 'zustand'
import type { PulseBatch, NeuronState } from '../types/connectome'

interface SSEState {
  connected: boolean
  neuronStates: Map<number, NeuronState>
  setConnected: (v: boolean) => void
  applyBatch: (batch: PulseBatch) => void
}

export const useSSEStore = create<SSEState>((set) => ({
  connected: false,
  neuronStates: new Map(),
  setConnected: (connected) => set({ connected }),
  applyBatch: (batch) =>
    set((state) => {
      const next = new Map(state.neuronStates)
      for (let i = 0; i < batch.neuron_ids.length; i++) {
        next.set(batch.neuron_ids[i], {
          voltage: batch.voltages[i],
          spike: batch.spikes[i],
        })
      }
      return { neuronStates: next }
    }),
}))

export function useSSE(url: string = '/api/v1/stream/pulses') {
  const esRef = useRef<EventSource | null>(null)
  const setConnected = useSSEStore((s) => s.setConnected)
  const applyBatch = useSSEStore((s) => s.applyBatch)

  const connect = useCallback(() => {
    if (esRef.current) return

    const es = new EventSource(url)
    esRef.current = es

    es.onopen = () => setConnected(true)
    es.onerror = () => {
      setConnected(false)
      es.close()
      esRef.current = null
      setTimeout(connect, 3000)
    }
    es.onmessage = (event) => {
      try {
        const frame = JSON.parse(event.data)
        if (frame.batch) {
          applyBatch(frame.batch as PulseBatch)
        }
      } catch {
        // heartbeat or parse error
      }
    }
  }, [url, setConnected, applyBatch])

  const disconnect = useCallback(() => {
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
      setConnected(false)
    }
  }, [setConnected])

  useEffect(() => {
    return () => disconnect()
  }, [disconnect])

  return { connect, disconnect, store: useSSEStore }
}
