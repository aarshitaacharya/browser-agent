import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

/**
 * Minimal stand-in for the Web Speech API. jsdom ships no implementation, so
 * tests drive recognition by hand through the instance the app constructs.
 */
class MockSpeechRecognition {
  static instances = []

  constructor() {
    this.lang = ''
    this.continuous = false
    this.interimResults = false
    this.started = false
    MockSpeechRecognition.instances.push(this)
  }

  start() {
    this.started = true
    this.onstart?.()
  }

  stop() {
    this.started = false
    this.onend?.()
  }

  abort() {
    this.started = false
  }

  // Test helper: emit a recognition result the way the real engine would.
  emit(transcript, isFinal) {
    this.onresult?.({
      resultIndex: 0,
      results: [Object.assign([{ transcript }], { isFinal })],
    })
  }
}

// Emits a result on the most recently constructed recogniser. Wrapped in act()
// because the engine's callbacks drive React state from outside React.
const emitSpeech = (transcript, isFinal) =>
  act(() => {
    const recognition =
      MockSpeechRecognition.instances[MockSpeechRecognition.instances.length - 1]
    recognition.emit(transcript, isFinal)
  })

beforeEach(() => {
  MockSpeechRecognition.instances = []
  window.SpeechRecognition = MockSpeechRecognition
  window.speechSynthesis = { speak: jest.fn(), cancel: jest.fn() }
  window.SpeechSynthesisUtterance = function SpeechSynthesisUtterance(text) {
    this.text = text
  }
  global.fetch = jest.fn()
})

afterEach(() => {
  jest.resetAllMocks()
  delete window.SpeechRecognition
})

test('renders the command bar with a mic control', () => {
  render(<App />)
  expect(screen.getByLabelText('Command')).toBeInTheDocument()
  expect(screen.getByLabelText('Speak a command')).toBeInTheDocument()
})

test('shows the interim transcript while dictating', async () => {
  render(<App />)

  await userEvent.click(screen.getByLabelText('Speak a command'))
  await emitSpeech('go to wikipedia', false)

  await waitFor(() =>
    expect(screen.getByLabelText('Command')).toHaveValue('go to wikipedia')
  )
})

test('submits a finished utterance in hands-free mode', async () => {
  global.fetch.mockResolvedValue({
    ok: true,
    json: async () => ({
      status: 'success',
      result: ['Executed action: goto'],
      spoken_summary: 'Done. I completed 1 step.',
    }),
  })

  render(<App />)

  await userEvent.click(screen.getByLabelText('Speak a command'))
  await emitSpeech('go to wikipedia', true)

  await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(1))

  const [url, options] = global.fetch.mock.calls[0]
  expect(url).toContain('/interact')
  expect(JSON.parse(options.body)).toEqual({
    command: 'go to wikipedia',
    source: 'voice',
  })

  await screen.findByText(/Executed action: goto/)
})

test('holds the transcript for review when hands-free is off', async () => {
  render(<App />)

  await userEvent.click(screen.getByLabelText(/Hands-free/i))
  await userEvent.click(screen.getByLabelText('Speak a command'))
  await emitSpeech('take a screenshot', true)

  await waitFor(() =>
    expect(screen.getByLabelText('Command')).toHaveValue('take a screenshot')
  )
  expect(global.fetch).not.toHaveBeenCalled()
})

test('degrades to typing when the browser has no speech recognition', async () => {
  delete window.SpeechRecognition
  render(<App />)

  expect(
    screen.getByLabelText(/Voice input is not supported/i)
  ).toBeDisabled()
  expect(screen.getByText(/Voice input needs the Web Speech API/i)).toBeInTheDocument()
})
