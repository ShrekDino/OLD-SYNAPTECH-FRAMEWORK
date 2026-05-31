import { forwardRef } from 'react'

interface Props {
  onClick: () => void
}

const SignInCard = forwardRef<HTMLDivElement, Props>(({ onClick }, ref) => {
  return (
    <div
      ref={ref}
      onClick={onClick}
      style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 10,
        background: 'rgba(255, 255, 255, 0.12)',
        backdropFilter: 'blur(25px)',
        WebkitBackdropFilter: 'blur(25px)',
        border: '1px solid rgba(255, 255, 255, 0.75)',
        borderRadius: 20,
        boxShadow:
          '0 8px 32px rgba(41, 121, 255, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04)',
        padding: '48px 40px',
        minWidth: 380,
        maxWidth: 420,
        cursor: 'pointer',
        transition: 'box-shadow 0.3s ease',
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.boxShadow =
          '0 12px 48px rgba(41, 121, 255, 0.14), 0 4px 12px rgba(0, 0, 0, 0.06)'
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.boxShadow =
          '0 8px 32px rgba(41, 121, 255, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04)'
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 36 }}>
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none" style={{ marginBottom: 16 }}>
          <circle cx="28" cy="28" r="27" stroke="#2979FF" strokeWidth="1.5" fill="none" />
          <circle cx="28" cy="28" r="12" fill="#2979FF" fillOpacity="0.1" stroke="#FFB300" strokeWidth="1.5" />
          <path d="M28 16 L28 40 M16 28 L40 28" stroke="#2979FF" strokeWidth="1.5" strokeLinecap="round" />
          <path d="M20 20 Q28 24 36 20" stroke="#FFB300" strokeWidth="1.2" fill="none" strokeLinecap="round" />
          <path d="M20 36 Q28 32 36 36" stroke="#FFB300" strokeWidth="1.2" fill="none" strokeLinecap="round" />
        </svg>
        <h1 style={{
          margin: 0,
          fontFamily: "'Inter', system-ui, sans-serif",
          fontWeight: 700,
          fontSize: 22,
          color: '#1a1a2e',
          letterSpacing: '-0.3px',
        }}>
          SynapTechBio
        </h1>
        <p style={{
          margin: '4px 0 0',
          fontFamily: "'Inter', system-ui, sans-serif",
          fontSize: 12,
          color: '#888',
          fontWeight: 400,
          letterSpacing: '0.2px',
        }}>
          Integrated Data Representation Engine
        </p>
      </div>

      <div style={{ marginBottom: 14 }}>
        <input
          placeholder="Username"
          onClick={(e) => e.stopPropagation()}
          onMouseDown={(e) => e.stopPropagation()}
          style={{
            width: '100%',
            padding: '14px 16px',
            borderRadius: 10,
            border: '1px solid rgba(0,0,0,0.06)',
            fontSize: 14,
            fontFamily: "'Inter', system-ui, sans-serif",
            background: 'rgba(255,255,255,0.7)',
            color: '#1a1a2e',
            outline: 'none',
            transition: 'border-color 0.2s',
            boxSizing: 'border-box',
          }}
          onFocus={(e) => { e.target.style.borderColor = '#2979FF' }}
          onBlur={(e) => { e.target.style.borderColor = 'rgba(0,0,0,0.06)' }}
        />
      </div>
      <div style={{ marginBottom: 24 }}>
        <input
          type="password"
          placeholder="Password"
          onClick={(e) => e.stopPropagation()}
          onMouseDown={(e) => e.stopPropagation()}
          style={{
            width: '100%',
            padding: '14px 16px',
            borderRadius: 10,
            border: '1px solid rgba(0,0,0,0.06)',
            fontSize: 13,
            fontFamily: "'Inter', system-ui, sans-serif",
            background: 'rgba(255,255,255,0.7)',
            color: '#1a1a2e',
            outline: 'none',
            transition: 'border-color 0.2s',
            boxSizing: 'border-box',
          }}
          onFocus={(e) => { e.target.style.borderColor = '#2979FF' }}
          onBlur={(e) => { e.target.style.borderColor = 'rgba(0,0,0,0.06)' }}
        />
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation()
          onClick()
        }}
        style={{
          width: '100%',
          padding: '14px',
          borderRadius: 10,
          border: 'none',
          background: 'linear-gradient(135deg, #2979FF 0%, #FFB300 100%)',
          color: '#fff',
          fontFamily: "'Inter', system-ui, sans-serif",
          fontWeight: 600,
          fontSize: 15,
          cursor: 'pointer',
          letterSpacing: '0.3px',
          transition: 'opacity 0.2s, transform 0.15s',
        }}
        onMouseOver={(e) => { e.currentTarget.style.opacity = '0.92' }}
        onMouseOut={(e) => { e.currentTarget.style.opacity = '1' }}
        onMouseDown={(e) => { e.currentTarget.style.transform = 'scale(0.98)' }}
        onMouseUp={(e) => { e.currentTarget.style.transform = 'scale(1)' }}
      >
        Enter SynapTech IDRE
      </button>
      <p style={{
        margin: '16px 0 0',
        textAlign: 'center',
        fontFamily: "'Inter', system-ui, sans-serif",
        fontSize: 10,
        color: '#bbb',
        letterSpacing: '0.5px',
      }}>
        Click anywhere on the card to begin the experience
      </p>
    </div>
  )
})

SignInCard.displayName = 'SignInCard'
export default SignInCard
