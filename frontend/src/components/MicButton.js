import React from 'react'

function MicIcon({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" y1="19" x2="12" y2="22" />
    </svg>
  )
}

function MicOffIcon({ className }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <line x1="2" y1="2" x2="22" y2="22" />
      <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V5a3 3 0 0 0-5.94-.6" />
      <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23" />
      <line x1="12" y1="19" x2="12" y2="22" />
    </svg>
  )
}

/**
 * Push-to-talk control for the command bar.
 *
 * Renders as a toggle: click to start dictating, click again to stop. While
 * listening it pulses so there is an unmistakable visual cue that the mic is
 * live, which matters because the page is otherwise silent.
 */
export default function MicButton({ listening, supported, disabled, onToggle }) {
  const unavailable = !supported || disabled

  const label = !supported
    ? 'Voice input is not supported in this browser. Try Chrome, Edge, or Safari.'
    : listening
    ? 'Stop listening'
    : 'Speak a command'

  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={unavailable}
      aria-label={label}
      aria-pressed={listening}
      title={label}
      className={`relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full border transition
        ${
          unavailable
            ? 'cursor-not-allowed border-gray-200 bg-gray-100 text-gray-400'
            : listening
            ? 'border-red-500 bg-red-500 text-white shadow-lg shadow-red-200'
            : 'border-gray-300 bg-white text-gray-700 hover:border-black hover:text-black'
        }`}
    >
      {listening && (
        <span className="absolute inset-0 animate-ping rounded-full bg-red-400 opacity-60" />
      )}
      {supported ? (
        <MicIcon className="relative h-5 w-5" />
      ) : (
        <MicOffIcon className="relative h-5 w-5" />
      )}
    </button>
  )
}
