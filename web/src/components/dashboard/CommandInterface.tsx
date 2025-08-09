'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CommandLineIcon,
  PaperAirplaneIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

interface CommandInterfaceProps {
  onCommand: (command: any) => void
  disabled?: boolean
}

interface CommandHistory {
  id: string
  command: string
  timestamp: number
  status: 'pending' | 'success' | 'error'
  response?: string
}

export function CommandInterface({ onCommand, disabled = false }: CommandInterfaceProps) {
  const [command, setCommand] = useState('')
  const [history, setHistory] = useState<CommandHistory[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const historyRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when new history item is added
  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight
    }
  }, [history])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!command.trim() || disabled) return

    const newCommand: CommandHistory = {
      id: Date.now().toString(),
      command: command.trim(),
      timestamp: Date.now(),
      status: 'pending'
    }

    setHistory(prev => [...prev, newCommand])
    
    // Send command
    onCommand({
      type: 'manual_command',
      command: command.trim(),
      timestamp: Date.now()
    })

    // Simulate response (in real app, this would come from WebSocket)
    setTimeout(() => {
      setHistory(prev => 
        prev.map(cmd => 
          cmd.id === newCommand.id 
            ? { 
                ...cmd, 
                status: Math.random() > 0.2 ? 'success' : 'error',
                response: Math.random() > 0.2 
                  ? `Command "${command.trim()}" executed successfully`
                  : `Error: Command "${command.trim()}" failed`
              }
            : cmd
        )
      )
    }, 1000 + Math.random() * 2000)

    setCommand('')
    setHistoryIndex(-1)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      const commands = history.map(h => h.command)
      if (commands.length > 0) {
        const newIndex = Math.min(historyIndex + 1, commands.length - 1)
        setHistoryIndex(newIndex)
        setCommand(commands[commands.length - 1 - newIndex] || '')
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex > 0) {
        const commands = history.map(h => h.command)
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setCommand(commands[commands.length - 1 - newIndex] || '')
      } else {
        setHistoryIndex(-1)
        setCommand('')
      }
    }
  }

  const getStatusIcon = (status: CommandHistory['status']) => {
    switch (status) {
      case 'pending':
        return <div className="loading-spinner w-3 h-3" />
      case 'success':
        return <CheckCircleIcon className="h-3 w-3 text-success-400" />
      case 'error':
        return <XCircleIcon className="h-3 w-3 text-danger-400" />
    }
  }

  const getStatusColor = (status: CommandHistory['status']) => {
    switch (status) {
      case 'pending': return 'text-warning-400'
      case 'success': return 'text-success-400'
      case 'error': return 'text-danger-400'
    }
  }

  return (
    <motion.div 
      className="card-gaming p-6 h-96 flex flex-col"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.4 }}
    >
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <CommandLineIcon className="h-5 w-5 text-primary-400" />
        Command Interface
      </h3>

      {/* Command History */}
      <div 
        ref={historyRef}
        className="flex-1 bg-black/50 rounded-lg p-3 mb-4 overflow-y-auto font-mono text-sm space-y-2"
      >
        <AnimatePresence>
          {history.length === 0 ? (
            <div className="text-slate-500 text-center py-4">
              <CommandLineIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No commands executed yet</p>
              <p className="text-xs mt-1">Type a command below to get started</p>
            </div>
          ) : (
            history.map((item) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-1"
              >
                {/* Command */}
                <div className="flex items-center gap-2">
                  <span className="text-primary-400">$</span>
                  <span className="text-slate-200">{item.command}</span>
                  <div className="ml-auto flex items-center gap-2">
                    {getStatusIcon(item.status)}
                    <span className="text-xs text-slate-400">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                {/* Response */}
                {item.response && (
                  <div className={`pl-4 text-xs ${getStatusColor(item.status)}`}>
                    {item.response}
                  </div>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Command Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-primary-400 font-mono">
            $
          </span>
          <input
            ref={inputRef}
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter MS11 command..."
            disabled={disabled}
            className={`
              w-full pl-8 pr-4 py-2 bg-slate-800/50 border border-slate-600/50 rounded-lg
              text-slate-200 font-mono text-sm placeholder-slate-400
              focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/30
              focus:outline-none transition-colors duration-200
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          />
        </div>
        
        <button
          type="submit"
          disabled={!command.trim() || disabled}
          className="button-primary px-3 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <PaperAirplaneIcon className="h-4 w-4" />
        </button>
      </form>

      {/* Help Text */}
      <div className="mt-2 text-xs text-slate-500">
        <p>Use ↑/↓ arrows for command history</p>
        <p>Examples: "start_mode combat", "check_health", "pause_session"</p>
      </div>
    </motion.div>
  )
}