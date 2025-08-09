'use client'

import { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react'
import { toast } from 'react-hot-toast'

// Import Socket.IO client dynamically to avoid SSR issues
let io: any = null
let Socket: any = null

if (typeof window !== 'undefined') {
  const socketClient = require('socket.io-client')
  io = socketClient.io
  Socket = socketClient.Socket
}

interface WebSocketContextType {
  socket: any | null
  isConnected: boolean
  lastPong: Date | null
  reconnectCount: number
  sendCommand: (command: any) => void
  subscribeToEvents: (events: string[], callback: (data: any) => void) => () => void
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

interface WebSocketProviderProps {
  children: ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [socket, setSocket] = useState<any | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastPong, setLastPong] = useState<Date | null>(null)
  const [reconnectCount, setReconnectCount] = useState(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const pingIntervalRef = useRef<NodeJS.Timeout>()

  // Initialize socket connection
  useEffect(() => {
    // Only initialize on client side
    if (typeof window === 'undefined' || !io) return
    
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:5000'
    
    const newSocket = io(wsUrl, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 10000,
      reconnectionAttempts: 5,
      forceNew: true,
    })

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('✅ WebSocket connected:', newSocket.id)
      setIsConnected(true)
      setReconnectCount(0)
      
      // Start ping/pong monitoring
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current)
      }
      pingIntervalRef.current = setInterval(() => {
        newSocket.emit('ping', Date.now())
      }, 30000) // Ping every 30 seconds

      toast.success('Connected to MS11 server', {
        id: 'websocket-connection',
        duration: 3000,
      })
    })

    newSocket.on('disconnect', (reason: any) => {
      console.log('❌ WebSocket disconnected:', reason)
      setIsConnected(false)
      
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current)
      }

      if (reason === 'io server disconnect') {
        // Server initiated disconnect - try to reconnect
        toast.error('Server disconnected - attempting reconnect...', {
          id: 'websocket-connection',
        })
      }
    })

    newSocket.on('connect_error', (error: any) => {
      console.error('❌ WebSocket connection error:', error)
      setReconnectCount(prev => prev + 1)
      
      if (reconnectCount < 5) {
        toast.error(`Connection failed (${reconnectCount + 1}/5) - retrying...`, {
          id: 'websocket-connection',
        })
      } else {
        toast.error('Unable to connect to MS11 server', {
          id: 'websocket-connection',
          duration: 10000,
        })
      }
    })

    newSocket.on('reconnect', (attemptNumber: any) => {
      console.log('🔄 WebSocket reconnected after', attemptNumber, 'attempts')
      toast.success('Reconnected to MS11 server', {
        id: 'websocket-connection',
        duration: 2000,
      })
    })

    newSocket.on('pong', (timestamp: any) => {
      setLastPong(new Date(timestamp))
    })

    // MS11 specific event handlers
    newSocket.on('session_update', (data: any) => {
      console.log('📊 Session update:', data)
      // Handle session updates
    })

    newSocket.on('mode_execution', (data: any) => {
      console.log('⚡ Mode execution:', data)
      // Handle mode execution updates
    })

    newSocket.on('quest_update', (data: any) => {
      console.log('📜 Quest update:', data)
      // Handle quest progress updates
    })

    newSocket.on('system_alert', (data: any) => {
      console.log('🚨 System alert:', data)
      toast.error(`System Alert: ${data.message}`, {
        duration: 8000,
      })
    })

    newSocket.on('performance_metric', (data: any) => {
      console.log('📈 Performance metric:', data)
      // Handle performance metrics for real-time charts
    })

    setSocket(newSocket)

    // Cleanup on unmount
    return () => {
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current)
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      newSocket.close()
    }
  }, [])

  // Send command to MS11 backend
  const sendCommand = (command: any) => {
    if (socket && isConnected) {
      socket.emit('ms11_command', {
        ...command,
        timestamp: Date.now(),
        client_id: socket.id,
      })
    } else {
      toast.error('Not connected to MS11 server')
    }
  }

  // Subscribe to multiple events with cleanup
  const subscribeToEvents = (events: string[], callback: (data: any) => void) => {
    if (!socket) return () => {}

    events.forEach(event => {
      socket.on(event, callback)
    })

    // Return cleanup function
    return () => {
      events.forEach(event => {
        socket.off(event, callback)
      })
    }
  }

  const value: WebSocketContextType = {
    socket,
    isConnected,
    lastPong,
    reconnectCount,
    sendCommand,
    subscribeToEvents,
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

// Custom hooks for specific MS11 events
export function useSessionUpdates() {
  const { subscribeToEvents } = useWebSocket()
  const [sessionData, setSessionData] = useState<any>(null)

  useEffect(() => {
    const cleanup = subscribeToEvents(['session_update'], (data) => {
      setSessionData(data)
    })
    return cleanup
  }, [subscribeToEvents])

  return sessionData
}

export function useModeExecution() {
  const { subscribeToEvents } = useWebSocket()
  const [modeData, setModeData] = useState<any>(null)

  useEffect(() => {
    const cleanup = subscribeToEvents(['mode_execution'], (data) => {
      setModeData(data)
    })
    return cleanup
  }, [subscribeToEvents])

  return modeData
}

export function usePerformanceMetrics() {
  const { subscribeToEvents } = useWebSocket()
  const [metrics, setMetrics] = useState<any[]>([])

  useEffect(() => {
    const cleanup = subscribeToEvents(['performance_metric'], (data) => {
      setMetrics(prev => [...prev.slice(-49), data]) // Keep last 50 metrics
    })
    return cleanup
  }, [subscribeToEvents])

  return metrics
}