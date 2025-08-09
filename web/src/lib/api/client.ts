import axios from 'axios'
import { ApiResponse } from '@/types'

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('ms11_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (typeof window !== 'undefined') {
        localStorage.removeItem('ms11_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// API client functions
export const apiClient = {
  // Health endpoints
  async getHealth() {
    const response = await api.get<ApiResponse>('/api/health')
    return response.data
  },

  async getMetrics() {
    const response = await api.get<ApiResponse>('/api/metrics')
    return response.data
  },

  // Session endpoints
  async getSessions() {
    const response = await api.get<ApiResponse>('/api/sessions')
    return response.data
  },

  async createSession(data: any) {
    const response = await api.post<ApiResponse>('/api/sessions', data)
    return response.data
  },

  async updateSession(id: string, data: any) {
    const response = await api.put<ApiResponse>(`/api/sessions/${id}`, data)
    return response.data
  },

  async deleteSession(id: string) {
    const response = await api.delete<ApiResponse>(`/api/sessions/${id}`)
    return response.data
  },

  // Command endpoints
  async sendCommand(command: any) {
    const response = await api.post<ApiResponse>('/api/commands', command)
    return response.data
  },

  async getCommandHistory() {
    const response = await api.get<ApiResponse>('/api/commands/history')
    return response.data
  },

  // Auth endpoints
  async login(credentials: { username: string; password: string }) {
    const response = await api.post<ApiResponse>('/api/auth/login', credentials)
    return response.data
  },

  async logout() {
    const response = await api.post<ApiResponse>('/api/auth/logout')
    return response.data
  },

  async verifyToken() {
    const response = await api.get<ApiResponse>('/api/auth/verify')
    return response.data
  },

  async updatePreferences(preferences: any) {
    const response = await api.put<ApiResponse>('/api/auth/preferences', preferences)
    return response.data
  },

  // Configuration endpoints
  async getConfig() {
    const response = await api.get<ApiResponse>('/api/config')
    return response.data
  },

  async updateConfig(config: any) {
    const response = await api.put<ApiResponse>('/api/config', config)
    return response.data
  },
}

export default api