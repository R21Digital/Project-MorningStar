# MS11 Server API

Complete backend server for the MS11 automation platform with WebSocket real-time communication, REST API endpoints, JWT authentication, and advanced monitoring.

## Features

### 🚀 **Core Server Features**
- **Flask-SocketIO** WebSocket server for real-time communication
- **REST API** endpoints for all dashboard operations
- **JWT Authentication** with role-based access control
- **Advanced Monitoring** with health checks and alerting
- **Performance Metrics** collection and streaming
- **Session Management** with real-time status updates
- **Command Execution** with WebSocket result broadcasting

### 🔐 **Authentication & Security**
- JWT token-based authentication
- Role-based permissions (admin, user, viewer)
- Refresh token support
- CORS protection and security headers
- Input validation and sanitization
- Rate limiting and abuse prevention

### 📊 **Monitoring & Alerting**
- Real-time health checks for all components
- Metric threshold monitoring with customizable alerts
- Performance regression detection
- System resource monitoring (CPU, memory, disk)
- Alert management with resolution tracking
- Prometheus metrics export

### 🔄 **Real-time Communication**
- WebSocket broadcasting for session updates
- Live performance metrics streaming
- Command execution result broadcasting
- Client connection management
- Auto-reconnection handling

## Quick Start

### Prerequisites
- Python 3.11+
- All MS11 core dependencies
- Server dependencies (see requirements/server.txt)

### Installation
```bash
# Install server dependencies
pip install -r requirements/server.txt

# Start the server
python api/ms11_server.py

# Or with custom settings
python api/ms11_server.py --host 0.0.0.0 --port 5000 --debug
```

### Development Mode
```bash
# Run in development mode with auto-reload
python api/ms11_server.py --dev
```

## API Documentation

### Authentication Endpoints

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_id",
      "username": "admin",
      "role": "admin",
      "permissions": ["dashboard:read", "sessions:write", ...]
    },
    "tokens": {
      "access_token": "jwt_token",
      "refresh_token": "refresh_token",
      "expires_in": 86400
    }
  }
}
```

#### Token Refresh
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

#### Verify Token
```http
GET /api/auth/verify
Authorization: Bearer your_jwt_token
```

### Health & Monitoring

#### System Health
```http
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "components": {
      "database": {"status": "healthy", "latency": 12.5},
      "cache": {"status": "healthy", "latency": 2.1},
      "ocr": {"status": "healthy", "latency": 156.3},
      "websocket": {"status": "healthy", "connected_clients": 3}
    },
    "metrics": {
      "cpu_usage": 23.4,
      "memory_usage": 67.8,
      "active_sessions": 3
    }
  }
}
```

#### Performance Metrics
```http
GET /api/metrics?limit=50&type=cpu_usage
```

#### Prometheus Metrics
```http
GET /api/metrics/prometheus
```

### Session Management

#### Get Sessions
```http
GET /api/sessions
Authorization: Bearer your_jwt_token
```

#### Create Session
```http
POST /api/sessions
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
  "character_name": "TestCharacter",
  "server": "Basilisk"
}
```

#### Update Session
```http
PUT /api/sessions/{session_id}
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
  "status": "running",
  "current_mode": "combat_training"
}
```

### Command Execution

#### Execute Command
```http
POST /api/commands
Authorization: Bearer your_jwt_token
Content-Type: application/json

{
  "command": "start_mode combat",
  "type": "manual_command"
}
```

#### Command History
```http
GET /api/commands/history?limit=100
Authorization: Bearer your_jwt_token
```

## WebSocket Events

### Client → Server Events

#### Connect
```javascript
socket.emit('connect');
// Response: 'connection_established' with session info
```

#### Send Command
```javascript
socket.emit('ms11_command', {
  type: 'quick_action',
  command: 'start_session',
  timestamp: Date.now()
});
```

#### Subscribe to Room
```javascript
socket.emit('subscribe_room', {
  room: 'session_updates'
});
```

### Server → Client Events

#### Session Updates
```javascript
socket.on('session_update', (data) => {
  console.log('Session updated:', data);
});
```

#### Performance Metrics
```javascript
socket.on('performance_metric', (data) => {
  console.log('New metric:', data);
});
```

#### Command Results
```javascript
socket.on('command_result', (data) => {
  console.log('Command completed:', data);
});
```

#### System Alerts
```javascript
socket.on('system_alert', (data) => {
  console.log('Alert:', data.message);
});
```

## Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=true

# Database (if using external DB)
DATABASE_URL=sqlite:///ms11.db

# Redis (if using Redis cache)
REDIS_URL=redis://localhost:6379
```

### Default Users
The server creates default users for development:

- **admin/any_password** - Full administrative access
- **user/any_password** - Standard user permissions
- **viewer/any_password** - Read-only access

**⚠️ Change these in production!**

## Monitoring & Alerting

### Health Checks
The system includes built-in health checks for:
- CPU usage monitoring
- Memory usage tracking
- Disk space monitoring
- Component availability checks

### Alert Levels
- **INFO** - Informational messages
- **WARNING** - Potential issues requiring attention
- **ERROR** - Problems affecting functionality
- **CRITICAL** - Severe issues requiring immediate action

### Metric Thresholds
Default thresholds are configured for:
- CPU usage > 85% for 5+ minutes
- Memory usage > 90% for 3+ minutes
- Error rate > 5% for 2+ minutes
- Response time > 5s for 1+ minute

## Testing

### Integration Tests
```bash
# Run comprehensive integration tests
python test_server_integration.py
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test authentication
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "test"}'

# Test WebSocket connection
wscat -c ws://localhost:5000/socket.io/?transport=websocket
```

## Architecture

### Component Overview
```
MS11 Server
├── WebSocket Server (Flask-SocketIO)
│   ├── Real-time event broadcasting
│   ├── Client connection management
│   └── Command execution handling
├── REST API (Flask)
│   ├── Authentication endpoints
│   ├── Session management
│   ├── Health & metrics
│   └── Configuration management
├── Authentication (JWT)
│   ├── Token generation/validation
│   ├── Role-based permissions
│   └── User management
├── Monitoring System
│   ├── Health checks
│   ├── Metric thresholds
│   ├── Alert management
│   └── Performance tracking
└── Core Integration
    ├── Session tracker
    ├── Metrics collector
    └── Enhanced error handling
```

### Data Flow
1. **Dashboard connects** via WebSocket to receive real-time updates
2. **Authentication** validates user permissions for API access
3. **Commands** are executed and results broadcast to all clients
4. **Monitoring** continuously checks system health and sends alerts
5. **Metrics** are collected and streamed to dashboard for visualization

## Production Deployment

### Security Considerations
- Change default JWT secret key
- Remove default demo users
- Enable HTTPS/WSS in production
- Configure proper CORS origins
- Implement rate limiting
- Set up proper logging and monitoring

### Performance Tuning
- Use production WSGI server (gunicorn, uWSGI)
- Configure Redis for caching and session storage
- Set up database connection pooling
- Enable gzip compression
- Implement CDN for static assets

### Example Production Setup
```bash
# Install production server
pip install gunicorn gevent

# Run with gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 api.ms11_server:app

# Or with uWSGI
uwsgi --http :5000 --gevent 1000 --http-websockets --module api.ms11_server:app
```

## Troubleshooting

### Common Issues

#### WebSocket Connection Fails
- Check CORS settings
- Verify firewall rules
- Ensure port 5000 is accessible
- Check browser WebSocket support

#### Authentication Errors
- Verify JWT secret key configuration
- Check token expiration
- Validate user permissions
- Review authentication logs

#### High Resource Usage
- Monitor system health checks
- Review active session count
- Check for memory leaks
- Analyze performance metrics

### Debug Mode
```bash
# Enable detailed logging
python api/ms11_server.py --debug

# Check specific component logs
grep "websocket_server" logs/ms11.log
grep "auth_middleware" logs/ms11.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## License

MIT License - see LICENSE file for details.