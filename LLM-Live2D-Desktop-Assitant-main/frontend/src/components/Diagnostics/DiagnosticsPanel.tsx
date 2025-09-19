import React, { useState } from 'react'
import { API_CONFIG, ENDPOINTS } from '../../config/api'
import { useHealthCheck, useMockTTS, useMockSTT } from '../../hooks/useAPI'
import { useWebSocket } from '../../hooks/useWebSocket'

interface TestResult {
  message: string
  type: 'success' | 'error' | 'info'
  timestamp: number
}

export const DiagnosticsPanel: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([])
  const [isRunningTest, setIsRunningTest] = useState(false)

  // API hooks for testing
  const healthAPI = useHealthCheck()
  const ttsAPI = useMockTTS()
  const sttAPI = useMockSTT()
  
  // WebSocket hook for echo testing
  const echoWS = useWebSocket('/ws/echo', { autoConnect: false })

  const addTestResult = (message: string, type: TestResult['type'] = 'info') => {
    const result: TestResult = {
      message,
      type,
      timestamp: Date.now()
    }
    setTestResults(prev => [...prev, result])
  }

  const clearResults = () => {
    setTestResults([])
  }

  const testHealthEndpoint = async () => {
    setIsRunningTest(true)
    addTestResult('Testing health endpoint using useAPI hook...', 'info')
    
    const data = await healthAPI.get('/health')
    
    if (data) {
      addTestResult(`Health check passed: ${data.message}`, 'success')
      addTestResult(`Server port: ${data.port}`, 'info')
      addTestResult(`Timestamp: ${new Date(data.timestamp * 1000).toLocaleTimeString()}`, 'info')
    } else if (healthAPI.error) {
      addTestResult(`Health check failed: ${healthAPI.error}`, 'error')
    }
    
    setIsRunningTest(false)
  }

  const testMockTTS = async () => {
    setIsRunningTest(true)
    addTestResult('Testing mock TTS endpoint using useAPI hook...', 'info')
    
    const data = await ttsAPI.post('/api/tts/mock', {
      text: 'This is a test of the mock TTS system using React hooks',
      voice: 'en-US-JennyNeural'
    })
    
    if (data && data.status === 'success') {
      addTestResult(`Mock TTS passed: ${data.message}`, 'success')
      addTestResult(`Audio length: ${data.audio_length}s`, 'info')
      addTestResult(`Voice: ${data.voice}`, 'info')
    } else if (ttsAPI.error) {
      addTestResult(`Mock TTS failed: ${ttsAPI.error}`, 'error')
    }
    
    setIsRunningTest(false)
  }

  const testMockSTT = async () => {
    setIsRunningTest(true)
    addTestResult('Testing mock STT endpoint using useAPI hook...', 'info')
    
    const data = await sttAPI.post('/api/stt/mock', {
      audio: 'mock_base64_audio_data_from_react_hooks',
      language: 'en'
    })
    
    if (data && data.status === 'success') {
      addTestResult(`Mock STT passed: ${data.message}`, 'success')
      addTestResult(`Transcription: "${data.transcription}"`, 'info')
      addTestResult(`Confidence: ${data.confidence}`, 'info')
      addTestResult(`Language: ${data.language}`, 'info')
    } else if (sttAPI.error) {
      addTestResult(`Mock STT failed: ${sttAPI.error}`, 'error')
    }
    
    setIsRunningTest(false)
  }

  const testWebSocketEcho = () => {
    setIsRunningTest(true)
    addTestResult('Testing WebSocket echo using useWebSocket hook...', 'info')
    
    // Connect to echo endpoint
    echoWS.connect()
    
    // Set up message handler
    const handleEchoMessage = (message: any) => {
      if (message.type === 'echo') {
        addTestResult(`Echo received: ${message.message}`, 'success')
        addTestResult(`Original: ${JSON.stringify(message.original)}`, 'info')
        addTestResult(`Server timestamp: ${new Date(message.timestamp * 1000).toLocaleTimeString()}`, 'info')
        echoWS.disconnect()
        setIsRunningTest(false)
      }
    }

    // Wait for connection then send test message
    const checkConnection = () => {
      if (echoWS.isConnected) {
        addTestResult('WebSocket echo connected via hook', 'success')
        
        const testMessage = {
          type: 'test',
          message: 'Hello WebSocket Echo from React Hook',
          timestamp: Date.now()
        }
        
        echoWS.sendMessage(testMessage)
        
        // Set up temporary message handler
        const originalOnMessage = echoWS.lastMessage
        setTimeout(() => {
          if (echoWS.lastMessage && echoWS.lastMessage !== originalOnMessage) {
            handleEchoMessage(echoWS.lastMessage)
          }
        }, 100)
        
      } else if (echoWS.connectionAttempts > 0) {
        addTestResult(`WebSocket echo connection failed after ${echoWS.connectionAttempts} attempts`, 'error')
        setIsRunningTest(false)
      } else {
        // Still connecting, check again
        setTimeout(checkConnection, 100)
      }
    }

    checkConnection()
    
    // Timeout after 5 seconds
    setTimeout(() => {
      if (isRunningTest) {
        addTestResult('WebSocket echo test timed out', 'error')
        echoWS.disconnect()
        setIsRunningTest(false)
      }
    }, 5000)
  }

  return (
    <div className="diagnostics-panel">
      <h3>🔧 Development Diagnostics</h3>
      
      <div style={{ marginBottom: '15px' }}>
        <div className="connection-status">
          <span className="status-indicator connected"></span>
          <span>API Base: {API_CONFIG.baseURL}</span>
        </div>
        <div className="connection-status">
          <span className="status-indicator connected"></span>
          <span>WS Base: {API_CONFIG.wsURL}</span>
        </div>
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <button 
          onClick={testHealthEndpoint} 
          disabled={isRunningTest}
        >
          Test Health
        </button>
        <button 
          onClick={testMockTTS} 
          disabled={isRunningTest}
        >
          Test Mock TTS
        </button>
        <button 
          onClick={testMockSTT} 
          disabled={isRunningTest}
        >
          Test Mock STT
        </button>
        <button 
          onClick={testWebSocketEcho} 
          disabled={isRunningTest}
        >
          Test WS Echo
        </button>
        <button 
          onClick={clearResults}
          disabled={isRunningTest}
        >
          Clear Results
        </button>
      </div>
      
      <div className="test-result">
        {testResults.map((result, index) => (
          <p key={index} className={result.type}>
            [{new Date(result.timestamp).toLocaleTimeString()}] {result.message}
          </p>
        ))}
        {testResults.length === 0 && (
          <p className="info">Click buttons above to run tests...</p>
        )}
      </div>
    </div>
  )
}