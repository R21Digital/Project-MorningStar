# MS11 Dashboard Setup Guide

## Overview

The MS11 Dashboard is a web-based interface for managing and controlling the MS11 automation system. It provides:

- Discord-based authentication
- License management (limited to 4 users)
- Real-time system status monitoring
- Session management and control
- Admin panel for license management

## Prerequisites

1. **Discord Application**: You need to create a Discord application for OAuth authentication
2. **Python Dependencies**: Ensure all required packages are installed
3. **MS11 System**: The MS11 system should be properly configured and running

## Setup Instructions

### 1. Discord Application Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "MS11 Dashboard")
3. Go to the "OAuth2" section in the left sidebar
4. Copy the "Client ID" and "Client Secret"
5. Add the redirect URI: `http://localhost:8000/ms11/auth/discord/callback` (for development)
6. Save the changes

### 2. Configuration

1. Update `config/discord_oauth.json` with your Discord application credentials:
```json
{
  "client_id": "YOUR_ACTUAL_CLIENT_ID",
  "client_secret": "YOUR_ACTUAL_CLIENT_SECRET",
  "redirect_uri": "http://localhost:8000/ms11/auth/discord/callback",
  "scope": "identify",
  "auth_url": "https://discord.com/api/oauth2/authorize",
  "token_url": "https://discord.com/api/oauth2/token",
  "user_url": "https://discord.com/api/users/@me"
}
```

2. Update the Discord client ID in `dashboard/app.py`:
```python
discord_client_id = "YOUR_ACTUAL_CLIENT_ID"  # Replace with actual client ID
```

### 3. License Management

1. **Initial Setup**: The system will automatically create a license file at `config/ms11_licenses.json`
2. **Add Licenses**: Use the admin panel at `/ms11/admin/licenses` to add authorized users
3. **License Types**:
   - `standard`: Basic access to MS11 dashboard
   - `premium`: Enhanced features (future)
   - `admin`: Full access including license management

### 4. Running the Dashboard

1. Start the Flask application:
```bash
cd dashboard
python app.py
```

2. Access the dashboard:
   - Main dashboard: `http://localhost:8000/ms11`
   - Login page: `http://localhost:8000/ms11/login`
   - Admin panel: `http://localhost:8000/ms11/admin/licenses`

## Usage

### For Users

1. **Login**: Visit `/ms11/login` and click "Continue with Discord"
2. **Authentication**: Complete Discord OAuth flow
3. **Access**: If you have a valid license, you'll be redirected to the dashboard
4. **Dashboard**: Use the dashboard to monitor and control MS11 sessions

### For Administrators

1. **License Management**: Access `/ms11/admin/licenses` to manage user licenses
2. **Add Users**: Use the form to add new Discord users with appropriate license types
3. **Monitor Usage**: View license statistics and usage patterns
4. **Remove Access**: Remove licenses for users who no longer need access

## Security Considerations

1. **Discord OAuth**: Only requests `identify` scope - minimal permissions
2. **License Validation**: All dashboard access requires valid license
3. **Session Management**: Sessions are managed securely with Flask
4. **Rate Limiting**: Consider implementing rate limiting for API endpoints
5. **HTTPS**: Use HTTPS in production for secure communication

## API Endpoints

### Authentication
- `GET /ms11/login` - Login page
- `GET /ms11/auth/discord` - Initiate Discord OAuth
- `GET /ms11/auth/discord/callback` - Discord OAuth callback

### Dashboard
- `GET /ms11` - Main dashboard (requires authentication and license)
- `GET /ms11/license-required` - License required page

### API
- `GET /ms11/api/status` - System status
- `GET /ms11/api/sessions` - List sessions
- `POST /ms11/api/start-session` - Start new session
- `POST /ms11/api/stop-session/<session_id>` - Stop session

### Admin
- `GET /ms11/admin/licenses` - License management
- `POST /ms11/admin/licenses/add` - Add new license
- `POST /ms11/admin/licenses/remove/<discord_id>` - Remove license

## Troubleshooting

### Common Issues

1. **Discord Authentication Fails**:
   - Check Discord application credentials
   - Verify redirect URI matches exactly
   - Ensure application is properly configured

2. **License Not Found**:
   - Verify user has been added to license system
   - Check Discord ID is correct
   - Ensure license is active and not expired

3. **Dashboard Not Loading**:
   - Check Flask application is running
   - Verify all dependencies are installed
   - Check console for error messages

### Debug Mode

Enable debug mode in Flask for detailed error messages:
```python
app.run(host="127.0.0.1", port=8000, debug=True)
```

## Production Deployment

1. **Environment Variables**: Use environment variables for sensitive data
2. **HTTPS**: Configure SSL/TLS certificates
3. **Database**: Consider using a proper database for license storage
4. **Logging**: Implement proper logging for monitoring
5. **Backup**: Regular backups of license data
6. **Monitoring**: Set up monitoring for dashboard availability

## Support

For issues or questions:
- Check the troubleshooting section above
- Review Flask and Discord API documentation
- Contact the MS11 development team

## License

This dashboard is part of the MS11 project and follows the same licensing terms.
