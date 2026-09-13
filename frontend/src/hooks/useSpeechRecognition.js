import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Resolves the vendor-prefixed Web Speech API constructor.
 * Chrome/Edge/Safari expose it; Firefox does not.
 *
 * Looked up on each call rather than cached at module scope, so a polyfill
 * loaded after this module (and the stub used in tests) is still picked up.
 */
function getSpeechRecognition() {
  if (typeof window === 'undefined') return undefined
  return window.SpeechRecognition || window.webkitSpeechRecognition
}

export const isSpeechRecognitionSupported = () => Boolean(getSpeechRecognition())

const ERROR_MESSAGES = {
  'not-allowed': 'Microphone access was blocked. Allow it in your browser settings.',
  'service-not-allowed': 'Microphone access was blocked by your browser or OS.',
  'no-speech': "I didn't catch that — try again.",
  'audio-capture': 'No microphone found. Check that one is connected.',
  network: 'Speech recognition needs a network connection.',
  aborted: null, // Triggered by our own stop() call; not worth surfacing.
}

/**
 * Wraps the Web Speech API in a React-friendly interface.
 *
 * Exposes the in-progress (interim) transcript separately from the confirmed
 * (final) one so the command bar can show words appearing as they are spoken
 * while only ever submitting text the engine has committed to.
 *
 * @param {object} options
 * @param {string} [options.lang] BCP-47 language tag for recognition.
 * @param {boolean} [options.continuous] Keep listening through natural pauses.
 * @param {(transcript: string) => void} [options.onFinalResult] Called once per confirmed phrase.
 * @param {() => void} [options.onEnd] Called when the engine stops listening.
 */
export default function useSpeechRecognition({
  lang = 'en-US',
  continuous = false,
  onFinalResult,
  onEnd,
} = {}) {
  const [supported, setSupported] = useState(() => Boolean(getSpeechRecognition()))
  const [listening, setListening] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  const [finalTranscript, setFinalTranscript] = useState('')
  const [error, setError] = useState(null)

  const recognitionRef = useRef(null)
  // Callbacks live in refs so that re-creating them on every render does not
  // tear down and rebuild the recognition instance mid-utterance.
  const onFinalResultRef = useRef(onFinalResult)
  const onEndRef = useRef(onEnd)
  // Set while a stop was requested by us, so the resulting `aborted` error and
  // the auto-restart logic can both tell it apart from an unexpected stop.
  const manualStopRef = useRef(false)

  useEffect(() => {
    onFinalResultRef.current = onFinalResult
    onEndRef.current = onEnd
  }, [onFinalResult, onEnd])

  useEffect(() => {
    const SpeechRecognitionImpl = getSpeechRecognition()
    setSupported(Boolean(SpeechRecognitionImpl))
    if (!SpeechRecognitionImpl) return undefined

    const recognition = new SpeechRecognitionImpl()
    recognition.lang = lang
    recognition.continuous = continuous
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onstart = () => {
      setListening(true)
      setError(null)
    }

    recognition.onresult = (event) => {
      let interim = ''

      // resultIndex marks the first result that changed since the last event,
      // so earlier finalised phrases are not re-emitted.
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i]
        const transcript = result[0].transcript

        if (result.isFinal) {
          const phrase = transcript.trim()
          if (phrase) {
            setFinalTranscript(phrase)
            onFinalResultRef.current?.(phrase)
          }
        } else {
          interim += transcript
        }
      }

      setInterimTranscript(interim)
    }

    recognition.onerror = (event) => {
      const message = ERROR_MESSAGES[event.error]
      if (message !== null) {
        setError(message || `Speech recognition error: ${event.error}`)
      }
      setListening(false)
    }

    recognition.onend = () => {
      setListening(false)
      setInterimTranscript('')
      onEndRef.current?.()
      manualStopRef.current = false
    }

    recognitionRef.current = recognition

    return () => {
      manualStopRef.current = true
      recognition.onstart = null
      recognition.onresult = null
      recognition.onerror = null
      recognition.onend = null
      try {
        recognition.abort()
      } catch {
        // Already stopped; nothing to clean up.
      }
      recognitionRef.current = null
    }
  }, [lang, continuous])

  const start = useCallback(() => {
    const recognition = recognitionRef.current
    if (!recognition) {
      setError('This browser does not support speech recognition. Try Chrome or Edge.')
      return
    }

    setError(null)
    setInterimTranscript('')
    manualStopRef.current = false

    try {
      recognition.start()
    } catch {
      // start() throws InvalidStateError if it is already running, which is a
      // harmless double-click rather than a real failure.
    }
  }, [])

  const stop = useCallback(() => {
    const recognition = recognitionRef.current
    if (!recognition) return

    manualStopRef.current = true
    try {
      recognition.stop()
    } catch {
      // Not running.
    }
  }, [])

  const toggle = useCallback(() => {
    if (listening) {
      stop()
    } else {
      start()
    }
  }, [listening, start, stop])

  const reset = useCallback(() => {
    setInterimTranscript('')
    setFinalTranscript('')
    setError(null)
  }, [])

  return {
    supported,
    listening,
    interimTranscript,
    finalTranscript,
    error,
    start,
    stop,
    toggle,
    reset,
  }
}
