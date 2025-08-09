# MS11 Dashboard

Modern web dashboard for the MS11 gaming automation platform with real-time monitoring, command interface, and performance analytics.

## Features

- **Real-time monitoring** - Live session tracking, system health, and performance metrics
- **WebSocket integration** - Real-time communication with MS11 backend
- **Interactive command interface** - Execute MS11 commands directly from the web interface
- **Performance visualization** - Charts and graphs for system performance analysis
- **Responsive design** - Works on desktop, tablet, and mobile devices
- **Modern UI/UX** - Gaming-themed interface with smooth animations
- **Authentication system** - User management with role-based permissions
- **Dark mode** - Optimized for gaming environments

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, Framer Motion
- **Charts**: Recharts
- **Real-time**: Socket.IO Client
- **State Management**: Zustand, React Query
- **Forms**: React Hook Form
- **Icons**: Heroicons

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm 8+
- MS11 backend server running

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:
```
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_WS_URL=ws://localhost:5000
NEXT_PUBLIC_APP_NAME=MS11 Dashboard
```

### Development

Start the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building

Build for production:
```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                   # Next.js app router pages
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── dashboard/        # Dashboard-specific components
│   └── charts/          # Chart components
├── lib/                  # Utility libraries
│   ├── providers/        # React context providers
│   └── api/             # API client functions
├── styles/              # Global styles and CSS
├── types/               # TypeScript type definitions
└── hooks/               # Custom React hooks
```

## Key Components

### WebSocket Provider
Real-time communication with MS11 backend:
- Connection management with auto-reconnect
- Event subscription system
- Custom hooks for session updates, mode execution, performance metrics

### Dashboard Page
Main interface featuring:
- System status cards
- Live session monitoring
- Performance charts
- Quick action buttons
- Command interface

### Authentication
- JWT-based authentication
- Role-based permissions (admin, user, viewer)
- Protected routes with HOC wrapper

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm run test` - Run tests
- `npm run storybook` - Start Storybook for component development

## Configuration

The dashboard can be configured through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:5000` | MS11 backend API URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:5000` | WebSocket server URL |
| `NEXT_PUBLIC_APP_NAME` | `MS11 Dashboard` | Application name |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the linter and type checker
6. Submit a pull request

## License

MIT License - see LICENSE file for details.