'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { StatusIndicator } from './StatusIndicator'

interface DashboardCardProps {
  title: string
  value: string | number
  icon: ReactNode
  status?: 'online' | 'offline' | 'error' | 'warning'
  subtitle?: string
  trend?: 'up' | 'down' | 'stable'
  trendValue?: string
  onClick?: () => void
  className?: string
}

export function DashboardCard({
  title,
  value,
  icon,
  status,
  subtitle,
  trend,
  trendValue,
  onClick,
  className = ''
}: DashboardCardProps) {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-success-400'
      case 'down': return 'text-danger-400'
      default: return 'text-slate-400'
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗'
      case 'down': return '↘'
      default: return '→'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-success-400'
      case 'error': return 'text-danger-400'
      case 'warning': return 'text-warning-400'
      default: return 'text-slate-400'
    }
  }

  return (
    <motion.div
      className={`card-gaming p-4 cursor-pointer ${className}`}
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="text-primary-400">
            {icon}
          </div>
          {status && (
            <StatusIndicator 
              status={status} 
              size="xs" 
              animated 
            />
          )}
        </div>
      </div>

      <div className="space-y-1">
        <h3 className="text-sm font-medium text-slate-300">
          {title}
        </h3>
        
        <div className="flex items-end justify-between">
          <span className={`text-2xl font-bold ${getStatusColor(value as string)}`}>
            {typeof value === 'string' && status ? (
              <span className="capitalize">{value}</span>
            ) : (
              value
            )}
          </span>
          
          {trend && trendValue && (
            <div className={`text-xs ${getTrendColor()} flex items-center gap-1`}>
              <span>{getTrendIcon()}</span>
              <span>{trendValue}</span>
            </div>
          )}
        </div>

        {subtitle && (
          <p className="text-xs text-slate-400">
            {subtitle}
          </p>
        )}
      </div>
    </motion.div>
  )
}