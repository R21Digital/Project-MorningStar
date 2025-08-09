'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'

interface User {
  id: string
  username: string
  email?: string
  role: 'admin' | 'user' | 'viewer'
  permissions: string[]
  lastLoginAt: Date
  preferences: {
    theme: 'light' | 'dark' | 'system'
    notifications: boolean
    autoRefresh: boolean
    refreshInterval: number
  }
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  updatePreferences: (preferences: Partial<User['preferences']>) => void
  hasPermission: (permission: string) => boolean
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Check for existing session on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('ms11_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await fetch('/api/auth/verify', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser({
          ...userData,
          lastLoginAt: new Date(userData.lastLoginAt),
        })
      } else {
        // Invalid token
        localStorage.removeItem('ms11_token')
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      localStorage.removeItem('ms11_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      if (response.ok) {
        const data = await response.json()
        
        // Store token
        localStorage.setItem('ms11_token', data.token)
        
        // Set user data
        setUser({
          ...data.user,
          lastLoginAt: new Date(),
        })

        toast.success(`Welcome back, ${data.user.username}!`)
        
        // Redirect to dashboard
        router.push('/dashboard')
        
        return true
      } else {
        const error = await response.json()
        toast.error(error.message || 'Login failed')
        return false
      }
    } catch (error) {
      console.error('Login error:', error)
      toast.error('Connection error - please try again')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('ms11_token')
    setUser(null)
    toast.success('Logged out successfully')
    router.push('/login')
  }

  const updatePreferences = async (newPreferences: Partial<User['preferences']>) => {
    if (!user) return

    try {
      const updatedPreferences = { ...user.preferences, ...newPreferences }
      
      const response = await fetch('/api/auth/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('ms11_token')}`,
        },
        body: JSON.stringify(updatedPreferences),
      })

      if (response.ok) {
        setUser(prev => prev ? { ...prev, preferences: updatedPreferences } : null)
        toast.success('Preferences updated')
      } else {
        throw new Error('Failed to update preferences')
      }
    } catch (error) {
      console.error('Preferences update failed:', error)
      toast.error('Failed to update preferences')
    }
  }

  const hasPermission = (permission: string): boolean => {
    if (!user) return false
    
    // Admin has all permissions
    if (user.role === 'admin') return true
    
    // Check specific permissions
    return user.permissions.includes(permission)
  }

  const refreshUser = async () => {
    await checkAuth()
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    updatePreferences,
    hasPermission,
    refreshUser,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// HOC for protected routes
export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  requiredPermission?: string
) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading, hasPermission } = useAuth()
    const router = useRouter()

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/login')
      } else if (!isLoading && requiredPermission && !hasPermission(requiredPermission)) {
        toast.error('Insufficient permissions')
        router.push('/dashboard')
      }
    }, [isAuthenticated, isLoading, hasPermission, router])

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      return null
    }

    if (requiredPermission && !hasPermission(requiredPermission)) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-xl font-semibold text-red-400">Access Denied</h1>
            <p className="text-gray-400">You don't have permission to access this page.</p>
          </div>
        </div>
      )
    }

    return <WrappedComponent {...props} />
  }
}