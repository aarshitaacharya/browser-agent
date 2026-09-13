import React, { useCallback, useEffect, useRef, useState } from 'react'
import MicButton from './components/MicButton'
import Toggle from './components/Toggle'
import useSpeechRecognition from './hooks/useSpeechRecognition'
import useSpeechSynthesis from './hooks/useSpeechSynthesis'
import { API_BASE } from './config'

const LOG_KINDS = {
  command: 'text-blue-600',
  success: 'text-green-600',
  error: 'text-red-600',
  info: 'text-gray-500',
}

const ICONS = {
  command: '➡️',
  success: '✅',
  error: '❌',
  info: 'ℹ️',
}

// Result strings the backend uses to signal a step that did not work.
const FAILURE_PREFIXES = ['failed', 'click failed', 'unknown action', 'no ', 'skipped']

// Multi-step plans with LLM planning + real browser actions can legitimately
// take a while; this is a "something is actually stuck" ceiling, not a
// typical-case budget.
const REQUEST_TIMEOUT_MS = 120_000

function isFailure(line) {
  const lower = line.toLowerCase()
  return (
    FAILURE_PREFIXES.some((prefix) => lower.startsWith(prefix)) ||
    lower.includes('no valid selector')
  )
}

function App() {
  const [command, setCommand] = useState('')
  const [log, setLog] = useState([])
  const [loading, setLoading] = useState(false)
  const [handsFree, setHandsFree] = useState(true)
  const [speakResults, setSpeakResults] = useState(true)

  const logRef = useRef(null)
  const inputRef = useRef(null)
  // Mirrors `loading` for callbacks owned by the speech engine, which capture
  // their closure once and would otherwise read a stale value.
  const loadingRef = useRef(false)

  const { speak, cancel: cancelSpeech, supported: canSpeak } = useSpeechSynthesis()

  const appendLog = useCallback((kind, message) => {
    setLog((prev) => [...prev, { kind, message, id: `${Date.now()}-${prev.length}` }])
  }, [])

  const runCommand = useCallback(
    async (rawCommand, source = 'text') => {
      const text = rawCommand.trim()
      if (!text || loadingRef.current) return

      loadingRef.current = true
      setLoading(true)
      setCommand('')
      appendLog('command', `${source === 'voice' ? '🎙️ ' : ''}${text}`)

      // A hung backend (LLM cold-starting, browser dead) would otherwise leave
      // the UI on "Thinking..." forever with no feedback at all.
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

      try {
        const res = await fetch(`${API_BASE}/interact`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: text, source }),
          signal: controller.signal,
        })

        const data = await res.json()

        if (!res.ok) {
          const detail = data.detail || `Request failed with status ${res.status}`
          appendLog('error', `Error: ${detail}`)
          if (speakResults) speak("Sorry, I couldn't do that.")
          return
        }

        for (const line of data.result) {
          appendLog(isFailure(line) ? 'error' : 'success', line)
        }

        if (speakResults && data.spoken_summary) {
          speak(data.spoken_summary)
        }
      } catch (err) {
        const message =
          err.name === 'AbortError'
            ? `Timed out after ${REQUEST_TIMEOUT_MS / 1000}s. The agent may still be working — check the browser window.`
            : `Could not reach the agent at ${API_BASE}. Is the backend running? (${err.message})`
        appendLog('error', message)
        if (speakResults) speak('I could not reach the agent.')
      } finally {
        clearTimeout(timeoutId)
        loadingRef.current = false
        setLoading(false)
      }
    },
    [appendLog, speak, speakResults]
  )

  // A finished utterance either fills the box for review, or runs straight
  // away when hands-free mode is on.
  const handleFinalResult = useCallback(
    (transcript) => {
      if (handsFree) {
        runCommand(transcript, 'voice')
      } else {
        setCommand(transcript)
        inputRef.current?.focus()
      }
    },
    [handsFree, runCommand]
  )

  const {
    supported: micSupported,
    listening,
    interimTranscript,
    error: speechError,
    toggle: toggleMic,
    stop: stopMic,
  } = useSpeechRecognition({ onFinalResult: handleFinalResult })

  useEffect(() => {
    if (speechError) appendLog('error', speechError)
  }, [speechError, appendLog])

  // Speaking over the agent's own voice would feed the summary back into the
  // recogniser, so listening always wins.
  useEffect(() => {
    if (listening) cancelSpeech()
  }, [listening, cancelSpeech])

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [log])

  const handleSubmit = () => runCommand(command, 'text')

  const handleClearLog = () => setLog([])

  // What the input shows: live dictation while speaking, typed text otherwise.
  const displayValue = listening && interimTranscript ? interimTranscript : command

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 px-4 py-6">
      <div className="w-full max-w-3xl mx-auto flex flex-col gap-5 p-2">
        <header className="text-center">
          <h1 className="text-2xl sm:text-3xl font-bold">Browser AI Agent</h1>
          <p className="mt-1 text-sm text-gray-500">
            Type a command, or press the mic and just say it.
          </p>
        </header>

        <div className="flex flex-col gap-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex flex-1 items-center gap-2 rounded-md border border-gray-300 bg-white px-2 shadow-sm focus-within:ring-2 focus-within:ring-black">
              <MicButton
                listening={listening}
                supported={micSupported}
                disabled={loading}
                onToggle={toggleMic}
              />
              <input
                ref={inputRef}
                value={displayValue}
                onChange={(e) => setCommand(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                placeholder={
                  listening ? 'Listening…' : 'Type a command, or press the mic to speak…'
                }
                aria-label="Command"
                className={`flex-1 bg-transparent py-2 pr-2 focus:outline-none ${
                  listening && interimTranscript ? 'italic text-gray-500' : ''
                }`}
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading || !command.trim()}
              className={`w-full sm:w-auto px-5 py-2 rounded-md text-white font-medium transition ${
                loading || !command.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-black hover:bg-gray-800'
              }`}
            >
              {loading ? 'Thinking...' : 'Send'}
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 px-1">
            <Toggle
              checked={handsFree}
              onChange={setHandsFree}
              disabled={!micSupported}
              label="Hands-free"
              hint="Run a spoken command as soon as you stop talking, instead of waiting for Send."
            />
            <Toggle
              checked={speakResults}
              onChange={(value) => {
                setSpeakResults(value)
                if (!value) cancelSpeech()
              }}
              disabled={!canSpeak}
              label="Speak results"
              hint="Read the outcome of each run back out loud."
            />
            {listening && (
              <button
                onClick={stopMic}
                className="ml-auto text-sm text-red-600 hover:underline"
              >
                Stop listening
              </button>
            )}
          </div>

          {!micSupported && (
            <p className="px-1 text-xs text-amber-600">
              Voice input needs the Web Speech API — available in Chrome, Edge, and
              Safari. You can still type commands here.
            </p>
          )}
        </div>

        <div className="flex-1 overflow-hidden">
          <div
            ref={logRef}
            aria-live="polite"
            className="bg-white border border-gray-200 rounded-md p-4 h-[24rem] overflow-auto text-sm font-mono space-y-1 shadow"
          >
            {log.length === 0 ? (
              <p className="text-gray-400">
                Nothing yet. Try “search for machine learning on Wikipedia and take a
                screenshot”.
              </p>
            ) : (
              log.map((entry) => (
                <div key={entry.id} className={LOG_KINDS[entry.kind]}>
                  {ICONS[entry.kind]} {entry.message}
                </div>
              ))
            )}
          </div>
          <div className="text-right">
            <button
              onClick={handleClearLog}
              className="mt-2 text-sm text-gray-500 hover:text-red-600 underline transition"
            >
              Clear log
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
