import React, { useState } from 'react'

function App() {
  const [command, setCommand] = useState('')
  const [log, setLog] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!command.trim()) return
    setLoading(true)
    setLog((prev) => [...prev, `➡️ Command: ${command}`])

    try {
      const res = await fetch('http://localhost:8000/interact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      })

      const data = await res.json()

      if (data.status === 'success') {
        for (const line of data.result) {
          setLog((prev) => [...prev, `✅ ${line}`])
        }
      } else {
        setLog((prev) => [...prev, `❌ Error: ${data.detail}`])
      }
    } catch (err) {
      setLog((prev) => [...prev, `❌ Network Error: ${err.message}`])
    } finally {
      setLoading(false)
      setCommand('')
    }
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🧠 Browser AI Agent</h1>
      <input
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        placeholder="e.g. Search for puppies on YouTube"
        style={{ width: '100%', padding: '8px', fontSize: '1rem' }}
      />
      <button onClick={handleSubmit} disabled={loading} style={{ marginTop: '1rem' }}>
        {loading ? 'Thinking...' : 'Send'}
      </button>

      <div style={{ marginTop: '2rem', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
        {log.map((line, idx) => (
          <div key={idx}>{line}</div>
        ))}
      </div>
    </div>
  )
}

export default App
