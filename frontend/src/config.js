/**
 * Backend base URL. Override with REACT_APP_API_BASE in a .env file when the
 * agent runs somewhere other than the default local port.
 */
export const API_BASE =
  process.env.REACT_APP_API_BASE || 'http://localhost:8000'
