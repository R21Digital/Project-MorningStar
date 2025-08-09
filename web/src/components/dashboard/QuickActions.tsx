'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  PlayIcon,
  PauseIcon,
  StopIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  BookOpenIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface QuickActionsProps {
  onCommand: (command: string) => void
  disabled?: boolean
}

export function QuickActions({ onCommand, disabled = false }: QuickActionsProps) {
  const [isLoading, setIsLoading] = useState<string | null>(null)

  const handleAction = async (action: string, label: string) => {
    if (disabled) return
    
    setIsLoading(action)
    try {
      onCommand(action)
      // Simulate loading time
      await new Promise(resolve => setTimeout(resolve, 1000))
    } finally {
      setIsLoading(null)
    }
  }

  const actions = [
    {
      id: 'start_session',
      label: 'Start Session',
      icon: PlayIcon,
      color: 'text-success-400',
      bgColor: 'bg-success-500/10 hover:bg-success-500/20',
      borderColor: 'border-success-500/20 hover:border-success-500/40'
    },
    {
      id: 'pause_session',
      label: 'Pause Session',
      icon: PauseIcon,
      color: 'text-warning-400',
      bgColor: 'bg-warning-500/10 hover:bg-warning-500/20',
      borderColor: 'border-warning-500/20 hover:border-warning-500/40'
    },
    {
      id: 'stop_session',
      label: 'Stop Session',
      icon: StopIcon,
      color: 'text-danger-400',
      bgColor: 'bg-danger-500/10 hover:bg-danger-500/20',
      borderColor: 'border-danger-500/20 hover:border-danger-500/40'
    },
    {
      id: 'reload_config',
      label: 'Reload Config',
      icon: ArrowPathIcon,
      color: 'text-primary-400',
      bgColor: 'bg-primary-500/10 hover:bg-primary-500/20',
      borderColor: 'border-primary-500/20 hover:border-primary-500/40'
    },
    {
      id: 'run_diagnostics',
      label: 'Run Diagnostics',
      icon: Cog6ToothIcon,
      color: 'text-slate-400',
      bgColor: 'bg-slate-500/10 hover:bg-slate-500/20',
      borderColor: 'border-slate-500/20 hover:border-slate-500/40'
    },
    {
      id: 'emergency_stop',
      label: 'Emergency Stop',
      icon: ExclamationTriangleIcon,
      color: 'text-red-400',
      bgColor: 'bg-red-500/10 hover:bg-red-500/20',
      borderColor: 'border-red-500/20 hover:border-red-500/40'
    }
  ]

  return (
    <motion.div 
      className="card-gaming p-6"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
    >
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <ChartBarIcon className="h-5 w-5 text-primary-400" />
        Quick Actions
      </h3>

      <div className="space-y-3">
        {actions.map((action, index) => {
          const Icon = action.icon
          const isActionLoading = isLoading === action.id
          
          return (
            <motion.button
              key={action.id}
              className={`
                w-full p-3 rounded-lg border transition-all duration-200
                ${action.bgColor} ${action.borderColor}
                flex items-center justify-center gap-3
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-102 active:scale-98'}
              `}
              onClick={() => handleAction(action.id, action.label)}
              disabled={disabled || isActionLoading}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              whileHover={disabled ? {} : { scale: 1.02 }}
              whileTap={disabled ? {} : { scale: 0.98 }}
            >
              {isActionLoading ? (
                <div className="loading-spinner w-4 h-4" />
              ) : (
                <Icon className={`h-4 w-4 ${action.color}`} />
              )}
              
              <span className={`text-sm font-medium ${action.color}`}>
                {action.label}
              </span>
            </motion.button>
          )
        })}
      </div>

      {/* Status Message */}
      <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
        <p className="text-xs text-slate-400 text-center">
          {disabled 
            ? 'Connect to MS11 server to enable actions'
            : 'All systems ready'
          }
        </p>
      </div>
    </motion.div>
  )
}