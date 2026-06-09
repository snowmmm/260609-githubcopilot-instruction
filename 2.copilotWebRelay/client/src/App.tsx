import { useState, useEffect, useRef, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Message {
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [status, setStatus] = useState<ConnectionStatus>('connecting')
  const [isProcessing, setIsProcessing] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  useEffect(() => {
    const wsUrl = `ws://localhost:3001`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'connected':
          setStatus('connected')
          break

        case 'delta':
          setMessages(prev => {
            const last = prev[prev.length - 1]
            if (last && last.role === 'assistant' && last.isStreaming) {
              return [
                ...prev.slice(0, -1),
                { ...last, content: last.content + data.content },
              ]
            } else {
              return [
                ...prev,
                { role: 'assistant', content: data.content, isStreaming: true },
              ]
            }
          })
          break

        case 'message':
          setMessages(prev => {
            const last = prev[prev.length - 1]
            if (last && last.role === 'assistant' && last.isStreaming) {
              return [
                ...prev.slice(0, -1),
                { role: 'assistant', content: data.content, isStreaming: false },
              ]
            }
            return [...prev, { role: 'assistant', content: data.content, isStreaming: false }]
          })
          break

        case 'idle':
          setIsProcessing(false)
          setMessages(prev => prev.map(m => ({ ...m, isStreaming: false })))
          inputRef.current?.focus()
          break

        case 'error':
          console.error('Server error:', data.message)
          setStatus('error')
          setIsProcessing(false)
          break
      }
    }

    ws.onclose = () => {
      setStatus('disconnected')
      console.log('WebSocket disconnected')
    }

    ws.onerror = () => {
      setStatus('error')
    }

    return () => {
      ws.close()
    }
  }, [])

  const sendMessage = useCallback(() => {
    const trimmed = input.trim()
    if (!trimmed || !wsRef.current || isProcessing) return

    setMessages(prev => [...prev, { role: 'user', content: trimmed }])
    wsRef.current.send(JSON.stringify({ type: 'chat', content: trimmed }))
    setInput('')
    setIsProcessing(true)
  }, [input, isProcessing])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }, [sendMessage])

  const statusLabel: Record<ConnectionStatus, { text: string; color: string }> = {
    connecting: { text: '接続中...', color: '#f59e0b' },
    connected: { text: '接続済み', color: '#10b981' },
    disconnected: { text: '切断', color: '#ef4444' },
    error: { text: 'エラー', color: '#ef4444' },
  }

  const { text: statusText, color: statusColor } = statusLabel[status]

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 Copilot Chat</h1>
        <div className="status">
          <span className="status-dot" style={{ backgroundColor: statusColor }} />
          {statusText}
        </div>
      </header>

      <main className="chat-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>👋 メッセージを入力して、Copilot とチャットを始めましょう！</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              {msg.role === 'assistant' ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              ) : (
                <p>{msg.content}</p>
              )}
              {msg.isStreaming && <span className="cursor">▌</span>}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      <footer className="input-area">
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isProcessing ? '応答を待っています...' : 'メッセージを入力...'}
            disabled={isProcessing || status !== 'connected'}
            autoFocus
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isProcessing || status !== 'connected'}
          >
            送信
          </button>
        </div>
      </footer>
    </div>
  )
}

export default App
