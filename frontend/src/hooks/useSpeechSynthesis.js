import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Looked up per call rather than cached at module scope, matching
 * useSpeechRecognition so tests and late polyfills both work.
 */
function getSynth() {
  return typeof window !== 'undefined' ? window.speechSynthesis : undefined
}

/**
 * Minimal wrapper around the Web Speech API's synthesis half, so the agent can
 * report back out loud and the interaction stays hands-free end to end.
 *
 * @param {object} options
 * @param {string} [options.lang] BCP-47 language tag for the chosen voice.
 */
export default function useSpeechSynthesis({ lang = 'en-US' } = {}) {
  const [supported, setSupported] = useState(() => Boolean(getSynth()))
  const [speaking, setSpeaking] = useState(false)
  const utteranceRef = useRef(null)

  // Cancel any queued speech when the component goes away, otherwise the
  // browser keeps talking after the UI is gone.
  useEffect(() => {
    setSupported(Boolean(getSynth()))
    return () => {
      getSynth()?.cancel()
    }
  }, [])

  const cancel = useCallback(() => {
    const synth = getSynth()
    if (!synth) return
    synth.cancel()
    setSpeaking(false)
  }, [])

  const speak = useCallback(
    (text) => {
      const synth = getSynth()
      if (!synth || !text) return

      // Never let two summaries overlap.
      synth.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = lang
      utterance.rate = 1.05
      utterance.onstart = () => setSpeaking(true)
      utterance.onend = () => setSpeaking(false)
      utterance.onerror = () => setSpeaking(false)

      utteranceRef.current = utterance
      synth.speak(utterance)
    },
    [lang]
  )

  return {
    supported,
    speaking,
    speak,
    cancel,
  }
}
