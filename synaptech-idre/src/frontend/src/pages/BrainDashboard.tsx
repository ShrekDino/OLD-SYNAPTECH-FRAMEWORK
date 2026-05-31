import { useState, useCallback } from 'react'
import BrainViewer from '../components/BrainViewer'
import ControlPanel from '../components/ControlPanel'
import { useSSE } from '../hooks/useSSE'

export default function BrainDashboard() {
  const [selectedNeuron, setSelectedNeuron] = useState<number | null>(null)
  const { connect, disconnect } = useSSE()

  const handleActivate = useCallback(async (vector: number[]) => {
    try {
      const res = await fetch('/api/v1/connectome/activate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_vector: vector,
          threshold: 0.5,
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      console.log(`Activation: ${data.spike_count} spikes in ${data.latency_ms.toFixed(1)}ms`)
    } catch (err) {
      console.error('Activation failed:', err)
    }
  }, [])

  const handleActivateSelected = useCallback(async (neuronId: number) => {
    const vec = new Array(130_000).fill(0)
    vec[neuronId] = 1.0
    for (let i = 0; i < 20; i++) {
      const neighbor = Math.floor(Math.random() * 130_000)
      vec[neighbor] = Math.random() * 0.8 + 0.2
    }
    await handleActivate(vec)
  }, [handleActivate])

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <BrainViewer selectedNeuron={selectedNeuron} onSelect={setSelectedNeuron} />
      <ControlPanel
        selectedNeuron={selectedNeuron}
        onActivate={handleActivate}
        onActivateSelected={handleActivateSelected}
        onConnect={connect}
        onDisconnect={disconnect}
      />
    </div>
  )
}
