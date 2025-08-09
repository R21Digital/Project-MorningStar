// Core MS11 types
export interface MS11Session {
  id: string
  character_name: string
  server: string
  status: 'idle' | 'running' | 'paused' | 'stopped' | 'error'
  created_at: string
  updated_at: string
  mode_start_time?: string
  current_mode?: string
}

export interface MS11Command {
  type: string
  action?: string
  parameters?: Record<string, any>
  timestamp: number
  client_id?: string
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy'
  uptime: number
  components: {
    database: ComponentHealth
    cache: ComponentHealth
    ocr: ComponentHealth
    websocket: ComponentHealth
  }
  metrics: {
    cpu_usage: number
    memory_usage: number
    active_sessions: number
    total_commands: number
  }
}

export interface ComponentHealth {
  status: 'healthy' | 'degraded' | 'unhealthy'
  latency?: number
  error_rate?: number
  last_check: string
}

export interface PerformanceMetric {
  timestamp: number
  cpu_usage?: number
  memory_usage?: number
  response_time?: number
  commands_per_second?: number
  error_rate?: number
  active_connections?: number
}

export interface WebSocketEvent {
  type: string
  data: any
  timestamp: number
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
  timestamp: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

// User and Auth types
export interface User {
  id: string
  username: string
  email?: string
  role: 'admin' | 'user' | 'viewer'
  permissions: string[]
  created_at: string
  last_login_at: string
  preferences: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  notifications: boolean
  auto_refresh: boolean
  refresh_interval: number
  dashboard_layout?: Record<string, any>
}

// Dashboard types
export interface DashboardWidget {
  id: string
  type: 'chart' | 'metric' | 'status' | 'log' | 'command'
  title: string
  position: { x: number; y: number; w: number; h: number }
  config: Record<string, any>
}

export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string
  borderColor?: string
  borderWidth?: number
}