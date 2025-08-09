'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { format } from 'date-fns'

interface PerformanceMetric {
  timestamp: number
  cpu_usage?: number
  memory_usage?: number
  response_time?: number
  commands_per_second?: number
  error_rate?: number
}

interface PerformanceChartProps {
  data: PerformanceMetric[]
  metric?: 'cpu_usage' | 'memory_usage' | 'response_time' | 'commands_per_second' | 'error_rate'
  height?: number
}

export function PerformanceChart({ 
  data = [], 
  metric = 'cpu_usage', 
  height = 200 
}: PerformanceChartProps) {
  // Process data for chart
  const chartData = data
    .slice(-50) // Show last 50 data points
    .map((item) => ({
      time: format(new Date(item.timestamp), 'HH:mm:ss'),
      value: item[metric] || 0,
      timestamp: item.timestamp
    }))

  const getMetricInfo = () => {
    switch (metric) {
      case 'cpu_usage':
        return { 
          name: 'CPU Usage', 
          color: '#3b82f6', 
          suffix: '%',
          max: 100 
        }
      case 'memory_usage':
        return { 
          name: 'Memory Usage', 
          color: '#10b981', 
          suffix: 'MB',
          max: undefined 
        }
      case 'response_time':
        return { 
          name: 'Response Time', 
          color: '#f59e0b', 
          suffix: 'ms',
          max: undefined 
        }
      case 'commands_per_second':
        return { 
          name: 'Commands/sec', 
          color: '#8b5cf6', 
          suffix: '',
          max: undefined 
        }
      case 'error_rate':
        return { 
          name: 'Error Rate', 
          color: '#ef4444', 
          suffix: '%',
          max: 100 
        }
      default:
        return { 
          name: 'Value', 
          color: '#6b7280', 
          suffix: '',
          max: undefined 
        }
    }
  }

  const metricInfo = getMetricInfo()

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]
      return (
        <div className="glass-effect rounded-lg p-3 border border-slate-600/50">
          <p className="text-slate-300 text-sm mb-1">
            Time: <span className="text-white">{label}</span>
          </p>
          <p className="text-slate-300 text-sm">
            {metricInfo.name}: <span className="font-semibold" style={{ color: metricInfo.color }}>
              {data.value?.toFixed(2)}{metricInfo.suffix}
            </span>
          </p>
        </div>
      )
    }
    return null
  }

  if (!data.length) {
    return (
      <div 
        className="flex items-center justify-center bg-slate-800/30 rounded-lg"
        style={{ height }}
      >
        <p className="text-slate-500 text-sm">No performance data available</p>
      </div>
    )
  }

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={metricInfo.color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={metricInfo.color} stopOpacity={0.05}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#475569" 
            opacity={0.3}
          />
          
          <XAxis 
            dataKey="time"
            stroke="#94a3b8"
            fontSize={12}
            tick={{ fill: '#94a3b8' }}
            tickLine={{ stroke: '#475569' }}
          />
          
          <YAxis 
            stroke="#94a3b8"
            fontSize={12}
            tick={{ fill: '#94a3b8' }}
            tickLine={{ stroke: '#475569' }}
            domain={metricInfo.max ? [0, metricInfo.max] : ['auto', 'auto']}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Area
            type="monotone"
            dataKey="value"
            stroke={metricInfo.color}
            strokeWidth={2}
            fill="url(#colorValue)"
            dot={{ fill: metricInfo.color, strokeWidth: 2, r: 3 }}
            activeDot={{ r: 5, fill: metricInfo.color, stroke: '#fff', strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}