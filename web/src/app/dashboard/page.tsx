'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon, 
  CpuChipIcon,
  ClockIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  CommandLineIcon,
  UserCircleIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'

import { useWebSocket, useSessionUpdates, useModeExecution, usePerformanceMetrics } from '@/lib/providers/websocket-provider'
import { useAuth } from '@/lib/providers/auth-provider'
import { DashboardCard } from '@/components/ui/DashboardCard'
import { StatusIndicator } from '@/components/ui/StatusIndicator'
import { PerformanceChart } from '@/components/charts/PerformanceChart'
import { SessionMonitor } from '@/components/dashboard/SessionMonitor'
import { CommandInterface } from '@/components/dashboard/CommandInterface'
import { QuickActions } from '@/components/dashboard/QuickActions'

interface SystemStatus {
  ms11_core: 'online' | 'offline' | 'error'
  database: 'online' | 'offline' | 'error'
  cache: 'online' | 'offline' | 'error'
  ocr_engine: 'online' | 'offline' | 'error'
  last_updated: string
}

export default function DashboardPage() {
  const { isConnected, sendCommand } = useWebSocket()
  const { user } = useAuth()
  const sessionData = useSessionUpdates()
  const modeData = useModeExecution()
  const performanceMetrics = usePerformanceMetrics()

  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    ms11_core: 'offline',
    database: 'offline', 
    cache: 'offline',
    ocr_engine: 'offline',
    last_updated: new Date().toISOString()
  })

  const [currentSession, setCurrentSession] = useState<any>(null)
  const [activeMode, setActiveMode] = useState<string | null>(null)
  const [sessionStats, setSessionStats] = useState({
    total_runtime: 0,
    commands_executed: 0,
    success_rate: 0,
    last_activity: null as string | null
  })

  // Fetch system status
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        const response = await fetch('/api/health')
        if (response.ok) {
          const healthData = await response.json()
          setSystemStatus({
            ms11_core: healthData.status === 'healthy' ? 'online' : 'error',
            database: healthData.components?.database?.status === 'healthy' ? 'online' : 'error',
            cache: healthData.components?.cache?.status === 'healthy' ? 'online' : 'error',
            ocr_engine: healthData.components?.ocr?.status === 'healthy' ? 'online' : 'error',
            last_updated: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error)
      }
    }

    fetchSystemStatus()
    const interval = setInterval(fetchSystemStatus, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  // Update session data from WebSocket
  useEffect(() => {
    if (sessionData) {
      setCurrentSession(sessionData)
      if (sessionData.stats) {
        setSessionStats(sessionData.stats)
      }
    }
  }, [sessionData])

  // Update mode execution data
  useEffect(() => {
    if (modeData) {
      setActiveMode(modeData.mode_name || null)
    }
  }, [modeData])

  const handleQuickCommand = (command: string) => {
    sendCommand({
      type: 'quick_action',
      command,
      timestamp: Date.now()
    })
  }

  const getOverallSystemStatus = (): 'online' | 'warning' | 'error' => {
    const statuses = Object.values(systemStatus).slice(0, -1) // Exclude last_updated
    
    if (statuses.every(status => status === 'online')) return 'online'
    if (statuses.some(status => status === 'error')) return 'error'
    return 'warning'
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100
      }
    }
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <motion.div 
          className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div>
            <h1 className="text-3xl font-bold font-game text-white mb-2">
              MS11 Dashboard
            </h1>
            <p className="text-slate-400">
              Welcome back, <span className="text-primary-400">{user?.username || 'User'}</span>
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              <StatusIndicator 
                status={isConnected ? 'online' : 'offline'} 
                size="sm" 
                animated 
              />
              <span className="text-sm text-slate-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* System Status */}
            <div className="flex items-center gap-2">
              <StatusIndicator 
                status={getOverallSystemStatus()} 
                size="sm" 
                animated 
              />
              <span className="text-sm text-slate-400">
                System {getOverallSystemStatus()}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Main Grid */}
        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* System Status Cards */}
          <motion.div variants={itemVariants} className="lg:col-span-3">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <DashboardCard
                title="MS11 Core"
                value={systemStatus.ms11_core}
                icon={<CpuChipIcon className="h-6 w-6" />}
                status={systemStatus.ms11_core}
              />
              <DashboardCard
                title="Database"
                value={systemStatus.database}
                icon={<ChartBarIcon className="h-6 w-6" />}
                status={systemStatus.database}
              />
              <DashboardCard
                title="Cache"
                value={systemStatus.cache}
                icon={<ClockIcon className="h-6 w-6" />}
                status={systemStatus.cache}
              />
              <DashboardCard
                title="OCR Engine"
                value={systemStatus.ocr_engine}
                icon={<CommandLineIcon className="h-6 w-6" />}
                status={systemStatus.ocr_engine}
              />
            </div>
          </motion.div>

          {/* Session Monitor */}
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <SessionMonitor 
              session={currentSession}
              activeMode={activeMode}
              stats={sessionStats}
            />
          </motion.div>

          {/* Quick Actions */}
          <motion.div variants={itemVariants}>
            <QuickActions 
              onCommand={handleQuickCommand}
              disabled={!isConnected}
            />
          </motion.div>

          {/* Performance Chart */}
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <div className="card-gaming p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <ChartBarIcon className="h-5 w-5 text-primary-400" />
                Performance Metrics
              </h3>
              <PerformanceChart data={performanceMetrics} />
            </div>
          </motion.div>

          {/* Command Interface */}
          <motion.div variants={itemVariants}>
            <CommandInterface 
              onCommand={sendCommand}
              disabled={!isConnected}
            />
          </motion.div>
        </motion.div>

        {/* Footer Status */}
        <motion.div 
          className="text-center text-sm text-slate-500"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          Last updated: {new Date(systemStatus.last_updated).toLocaleTimeString()}
        </motion.div>
      </div>
    </div>
  )
}