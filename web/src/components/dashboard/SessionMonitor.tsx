'use client'

import { motion } from 'framer-motion'
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon, 
  UserCircleIcon,
  ClockIcon,
  CommandLineIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { StatusIndicator } from '@/components/ui/StatusIndicator'
import { formatDistanceToNow } from 'date-fns'

interface SessionStats {
  total_runtime: number
  commands_executed: number
  success_rate: number
  last_activity: string | null
}

interface SessionMonitorProps {
  session: any
  activeMode: string | null
  stats: SessionStats
}

export function SessionMonitor({ session, activeMode, stats }: SessionMonitorProps) {
  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    }
    return `${minutes}m ${secs}s`
  }

  const getSessionStatus = () => {
    if (!session) return 'offline'
    if (session.status === 'running') return 'online'
    if (session.status === 'error') return 'error'
    return 'warning'
  }

  return (
    <motion.div 
      className="card-gaming p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <UserCircleIcon className="h-5 w-5 text-primary-400" />
          Session Monitor
        </h3>
        <StatusIndicator 
          status={getSessionStatus()}
          animated
          label={session?.status || 'No Session'}
        />
      </div>

      {session ? (
        <div className="space-y-4">
          {/* Character Info */}
          <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
            <div>
              <p className="text-sm text-slate-400">Character</p>
              <p className="font-semibold text-white">{session.character_name || 'Unknown'}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-400">Server</p>
              <p className="font-semibold text-primary-400">{session.server || 'Default'}</p>
            </div>
          </div>

          {/* Active Mode */}
          {activeMode && (
            <div className="p-3 bg-primary-500/10 border border-primary-500/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <CommandLineIcon className="h-4 w-4 text-primary-400" />
                <p className="text-sm font-medium text-primary-400">Active Mode</p>
              </div>
              <p className="text-white font-semibold">{activeMode}</p>
              <p className="text-xs text-slate-400 mt-1">
                Started {session.mode_start_time ? formatDistanceToNow(new Date(session.mode_start_time)) + ' ago' : 'recently'}
              </p>
            </div>
          )}

          {/* Session Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-slate-800/30 rounded-lg">
              <ClockIcon className="h-5 w-5 text-slate-400 mx-auto mb-1" />
              <p className="text-xs text-slate-400">Runtime</p>
              <p className="font-semibold text-white">{formatDuration(stats.total_runtime)}</p>
            </div>
            
            <div className="text-center p-3 bg-slate-800/30 rounded-lg">
              <CommandLineIcon className="h-5 w-5 text-slate-400 mx-auto mb-1" />
              <p className="text-xs text-slate-400">Commands</p>
              <p className="font-semibold text-white">{stats.commands_executed}</p>
            </div>
            
            <div className="text-center p-3 bg-slate-800/30 rounded-lg">
              <ChartBarIcon className="h-5 w-5 text-slate-400 mx-auto mb-1" />
              <p className="text-xs text-slate-400">Success Rate</p>
              <p className={`font-semibold ${stats.success_rate >= 90 ? 'text-success-400' : stats.success_rate >= 70 ? 'text-warning-400' : 'text-danger-400'}`}>
                {stats.success_rate.toFixed(1)}%
              </p>
            </div>
            
            <div className="text-center p-3 bg-slate-800/30 rounded-lg">
              <ClockIcon className="h-5 w-5 text-slate-400 mx-auto mb-1" />
              <p className="text-xs text-slate-400">Last Activity</p>
              <p className="font-semibold text-white">
                {stats.last_activity ? formatDistanceToNow(new Date(stats.last_activity)) + ' ago' : 'Never'}
              </p>
            </div>
          </div>

          {/* Quick Session Controls */}
          <div className="flex gap-2 pt-2">
            <button 
              className="button-primary flex-1 flex items-center justify-center gap-2"
              onClick={() => {}}
            >
              <PlayIcon className="h-4 w-4" />
              Start
            </button>
            <button 
              className="button-secondary flex-1 flex items-center justify-center gap-2"
              onClick={() => {}}
            >
              <PauseIcon className="h-4 w-4" />
              Pause
            </button>
            <button 
              className="button-danger flex-1 flex items-center justify-center gap-2"
              onClick={() => {}}
            >
              <StopIcon className="h-4 w-4" />
              Stop
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <UserCircleIcon className="h-12 w-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400 mb-2">No active session</p>
          <p className="text-sm text-slate-500">Start a new session to begin monitoring</p>
          <button className="button-primary mt-4">
            Create Session
          </button>
        </div>
      )}
    </motion.div>
  )
}