export interface Neuron {
  id: number
  pos: [number, number, number]
  color: string
}

export interface PulseBatch {
  neuron_ids: number[]
  voltages: number[]
  spikes: boolean[]
  ts: number
}

export interface SSEFrame {
  batch: PulseBatch
  ts: number
}

export interface NeuronState {
  voltage: number
  spike: boolean
}

export interface GraphLayout {
  positions: number[][]
  shape: [number, number]
}

export interface ConnectomeStatus {
  loaded: boolean
  nonzeros: number
  subscribers: number
  gpu_available: boolean
}
