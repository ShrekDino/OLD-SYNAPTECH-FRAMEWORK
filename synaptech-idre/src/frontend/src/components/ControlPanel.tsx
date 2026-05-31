import { useState, useEffect } from 'react'
import { useSSEStore, useSSE } from '../hooks/useSSE'

interface Props {
  selectedNeuron: number | null
  onActivate: (vector: number[]) => void
  onActivateSelected: (neuronId: number) => void
  onConnect: () => void
  onDisconnect: () => void
}

export default function ControlPanel({ selectedNeuron, onActivate, onActivateSelected, onConnect, onDisconnect }: Props) {
  const [threshold, setThreshold] = useState(0.5)
  const [neuronInfo, setNeuronInfo] = useState<string>('')
  const connected = useSSEStore((s) => s.connected)
  const activeNeurons = useSSEStore((s) => s.neuronStates.size)

  useEffect(() => {
    if (selectedNeuron !== null) {
      setNeuronInfo(`Neuron #${selectedNeuron.toLocaleString()}`)
      const state = useSSEStore.getState().neuronStates.get(selectedNeuron)
      if (state) {
        setNeuronInfo(`Neuron #${selectedNeuron.toLocaleString()} | V=${state.voltage.toFixed(3)}${state.spike ? ' ⚡' : ''}`)
      }
    } else {
      setNeuronInfo('')
    }
  }, [selectedNeuron])

  const handleRandomStimulus = () => {
    const vec = new Array(130_000).fill(0)
    for (let i = 0; i < 130_000; i += 50) {
      vec[i] = Math.random() * 0.8 + 0.2
    }
    onActivate(vec)
  }

  const handleActivateSelected = () => {
    if (selectedNeuron !== null) {
      onActivateSelected(selectedNeuron)
    }
  }

  return (
    <div style={{
      position: 'absolute',
      top: 16,
      left: 16,
      zIndex: 10,
      background: 'rgba(8, 8, 15, 0.88)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 10,
      padding: '14px 18px',
      minWidth: 220,
      fontFamily: 'monospace',
      fontSize: 12,
      userSelect: 'none',
    }}>
      <div style={{ fontWeight: 700, marginBottom: 10, color: '#4488ff', fontSize: 13 }}>
        SynapTech IDRE
      </div>

      {/* Connection status */}
      <div style={{ marginBottom: 10 }}>
        <div style={{ color: '#888', marginBottom: 4, fontSize: 11 }}>SSE</div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <div style={{
            width: 7, height: 7, borderRadius: '50%',
            background: connected ? '#00ff44' : '#ff4444',
            boxShadow: connected ? '0 0 6px #00ff44' : 'none',
          }} />
          <span style={{ color: connected ? '#00ff44' : '#ff4444', fontSize: 11 }}>
            {connected ? 'Live' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Connect / Disconnect */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 10 }}>
        <button onClick={onConnect} disabled={connected}
          style={{
            padding: '5px 10px', borderRadius: 5, border: '1px solid #4488ff',
            background: connected ? '#141a2e' : '#4488ff', color: '#fff',
            cursor: connected ? 'not-allowed' : 'pointer', flex: 1, fontSize: 11,
          }}
        >Connect</button>
        <button onClick={onDisconnect} disabled={!connected}
          style={{
            padding: '5px 10px', borderRadius: 5, border: '1px solid #ff4444',
            background: !connected ? '#2e1414' : '#ff4444', color: '#fff',
            cursor: !connected ? 'not-allowed' : 'pointer', flex: 1, fontSize: 11,
          }}
        >Disconnect</button>
      </div>

      {/* Selected neuron */}
      <div style={{
        marginBottom: 10, padding: '6px 8px',
        background: 'rgba(0,255,136,0.06)',
        borderRadius: 5, border: '1px solid rgba(0,255,136,0.15)',
        minHeight: 32,
      }}>
        {neuronInfo ? (
          <span style={{ color: '#00ff88', fontSize: 11 }}>{neuronInfo}</span>
        ) : (
          <span style={{ color: '#555', fontSize: 11 }}>Click a neuron to select</span>
        )}
      </div>

      {/* Threshold */}
      <div style={{ marginBottom: 10 }}>
        <div style={{ color: '#888', marginBottom: 3, fontSize: 11 }}>
          Threshold: {threshold.toFixed(2)}
        </div>
        <input type="range" min="0" max="1" step="0.01"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          style={{ width: '100%', accentColor: '#4488ff' }}
        />
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <button onClick={handleActivateSelected} disabled={selectedNeuron === null}
          style={{
            padding: '6px 12px', borderRadius: 5, border: '1px solid #00ff88',
            background: selectedNeuron === null ? '#0a1a14' : '#004422',
            color: selectedNeuron === null ? '#335544' : '#00ff88',
            cursor: selectedNeuron === null ? 'not-allowed' : 'pointer',
            fontSize: 11, fontWeight: 600,
          }}
        >
          Activate Selected Neuron
        </button>
        <button onClick={handleRandomStimulus}
          style={{
            padding: '6px 12px', borderRadius: 5, border: '1px solid #4488ff',
            background: '#0a1224', color: '#4488ff',
            cursor: 'pointer', fontSize: 11,
          }}
        >
          Random Stimulus (100k neurons)
        </button>
      </div>

      <div style={{ marginTop: 10, color: '#444', fontSize: 10 }}>
        {activeNeurons} neurons active · {connected ? 'streaming' : 'paused'}
      </div>
    </div>
  )
}
