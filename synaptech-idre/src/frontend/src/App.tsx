import { useState } from 'react'
import SignInScreen from './pages/SignInScreen'
import BrainDashboard from './pages/BrainDashboard'

type AppStage = 'SIGN_IN' | 'DASHBOARD'

export default function App() {
  const [stage, setStage] = useState<AppStage>('SIGN_IN')

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {stage === 'SIGN_IN' ? (
        <SignInScreen onEnter={() => setStage('DASHBOARD')} />
      ) : (
        <BrainDashboard />
      )}
    </div>
  )
}
