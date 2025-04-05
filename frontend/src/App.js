import React, { useState, useRef, useEffect } from 'react'

function App() {
  const [command, setCommand] = useState('')
  const [log, setLog] = useState([])
  const [loading, setLoading] = useState(false)
  const logRef = useRef(null)

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

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [log])

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-center">🧠 Browser AI Agent</h1>

        <div className="flex gap-2">
          <input
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="Type a command like 'Search puppies on YouTube'"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`px-4 py-2 rounded-md text-white font-medium transition ${
              loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-black hover:bg-gray-800'
            }`}
          >
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </div>

        <div
          ref={logRef}
          className="bg-white border border-gray-200 rounded-md p-4 h-96 overflow-auto text-sm font-mono space-y-1 shadow"
        >
          {log.map((line, idx) => (
            <div key={idx} className={
              line.startsWith('✅') ? 'text-green-600' :
              line.startsWith('❌') ? 'text-red-600' :
              line.startsWith('➡️') ? 'text-blue-600' : ''
            }>
              {line}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App
