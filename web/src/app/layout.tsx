import type { Metadata } from 'next'
import { Inter, JetBrains_Mono, Orbitron } from 'next/font/google'
import { ThemeProvider } from 'next-themes'
import { Toaster } from 'react-hot-toast'

import { QueryProvider } from '@/lib/providers/query-provider'
import { WebSocketProvider } from '@/lib/providers/websocket-provider'
import { AuthProvider } from '@/lib/providers/auth-provider'

import '@/styles/globals.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
})

const orbitron = Orbitron({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-game',
})

export const metadata: Metadata = {
  title: {
    template: '%s | MS11 Dashboard',
    default: 'MS11 Dashboard - Gaming Automation Platform',
  },
  description: 'Modern web dashboard for MS11 gaming automation platform with real-time monitoring, command interface, and performance analytics.',
  keywords: [
    'ms11',
    'gaming',
    'automation',
    'dashboard',
    'monitoring',
    'star wars galaxies',
    'real-time',
    'performance'
  ],
  authors: [{ name: 'MS11 Development Team' }],
  creator: 'MS11 Development Team',
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'MS11 Dashboard',
    description: 'Gaming automation platform with enterprise-grade monitoring and control.',
    siteName: 'MS11 Dashboard',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'MS11 Dashboard',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MS11 Dashboard',
    description: 'Gaming automation platform with enterprise-grade monitoring.',
    images: ['/og-image.png'],
  },
  robots: {
    index: false, // Private dashboard
    follow: false,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
}

interface RootLayoutProps {
  children: React.ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0ea5e9" />
      </head>
      <body 
        className={`${inter.variable} ${jetbrainsMono.variable} ${orbitron.variable} font-sans antialiased`}
        suppressHydrationWarning
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>
            <AuthProvider>
              <WebSocketProvider>
                <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
                  {/* Background effects */}
                  <div className="fixed inset-0 bg-gaming-grid bg-grid opacity-20" />
                  <div className="fixed inset-0 bg-gradient-to-t from-transparent via-blue-500/5 to-transparent" />
                  
                  {/* Main content */}
                  <div className="relative z-10">
                    {children}
                  </div>
                  
                  {/* Toast notifications */}
                  <Toaster
                    position="top-right"
                    toastOptions={{
                      duration: 4000,
                      className: 'glass-effect border-primary-500/20',
                      style: {
                        background: 'rgba(15, 23, 42, 0.8)',
                        color: '#f8fafc',
                        border: '1px solid rgba(59, 130, 246, 0.2)',
                        backdropFilter: 'blur(12px)',
                      },
                    }}
                  />
                </div>
              </WebSocketProvider>
            </AuthProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}