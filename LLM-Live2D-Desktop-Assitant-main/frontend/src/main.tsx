import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

console.log('🚀 React app starting...')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

console.log('✅ React app rendered')