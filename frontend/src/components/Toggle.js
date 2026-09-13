import React from 'react'

/**
 * Small labelled switch used for the voice preferences in the command bar.
 */
export default function Toggle({ checked, onChange, label, hint, disabled }) {
  return (
    <label
      title={hint}
      className={`flex items-center gap-2 text-sm select-none ${
        disabled ? 'cursor-not-allowed text-gray-400' : 'cursor-pointer text-gray-600'
      }`}
    >
      <span className="relative inline-flex">
        <input
          type="checkbox"
          checked={checked}
          disabled={disabled}
          onChange={(e) => onChange(e.target.checked)}
          className="peer sr-only"
        />
        <span
          className={`h-5 w-9 rounded-full transition-colors ${
            disabled ? 'bg-gray-200' : checked ? 'bg-black' : 'bg-gray-300'
          }`}
        />
        <span
          className={`absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${
            checked ? 'translate-x-4' : ''
          }`}
        />
      </span>
      {label}
    </label>
  )
}
