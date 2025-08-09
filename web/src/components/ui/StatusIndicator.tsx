'use client'

import { motion } from 'framer-motion'

interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'error' | 'warning'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  animated?: boolean
  label?: string
  className?: string
}

export function StatusIndicator({ 
  status, 
  size = 'md', 
  animated = false, 
  label,
  className = ''
}: StatusIndicatorProps) {
  const sizeClasses = {
    xs: 'w-2 h-2',
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }

  const statusClasses = {
    online: 'status-online',
    offline: 'status-offline',
    error: 'status-error',
    warning: 'status-warning'
  }

  const getStatusText = () => {
    switch (status) {
      case 'online': return 'Online'
      case 'offline': return 'Offline'
      case 'error': return 'Error'
      case 'warning': return 'Warning'
    }
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <motion.div
        className={`
          rounded-full border-2 border-white/20
          ${sizeClasses[size]}
          ${statusClasses[status]}
          ${animated ? 'animate-status-pulse' : ''}
        `}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ 
          type: 'spring', 
          stiffness: 500, 
          damping: 30,
          delay: 0.1
        }}
      />
      
      {label && (
        <span className="text-sm text-slate-300">
          {label || getStatusText()}
        </span>
      )}
    </div>
  )
}