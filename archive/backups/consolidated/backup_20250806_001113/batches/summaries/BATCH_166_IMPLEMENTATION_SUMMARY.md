# Batch 166 – SWGDB Private API v1 (Bot ↔ Site Bridge)

## Overview

**Goal**: Establish clean separation between public SWGDB and private MS11 data with secure authentication and data ingestion endpoints.

**Status**: ✅ **COMPLETED** - All tests passing (100% success rate)

**Implementation Date**: August 5, 2025

## Key Features Implemented

### 🔐 Authentication System
- **Discord ID + Signed Token Authentication**
  - HMAC-SHA256 signed tokens with expiry
  - Rate limiting and failed attempt tracking
  - Token generation, verification, and info retrieval
  - Automatic token expiry and cleanup

### 📊 Session Data Ingestion
- **POST /api/private/v1/sessions** endpoint
  - Comprehensive session data validation
  - Per-user data isolation and namespacing
  - Session statistics and analytics
  - Duplicate session handling and updates

### 🎒 Loot Data Ingestion
- **POST /api/private/v1/loot** endpoint
  - Loot item tracking with rarity and value
  - Item history and statistics
  - Total value calculation and aggregation
  - Per-user loot session management

### 🛡️ Security & Validation
- **Payload Validation** using Pydantic/JSON schema
- **Input sanitization** and type checking
- **Rate limiting** to prevent abuse
- **Error handling** with detailed logging
- **Data isolation** between users

## Files Created/Modified

### Core API Implementation
- **`/swgdb_api/private/routes/session_ingest.py`** - Session ingestion endpoint
- **`/swgdb_api/private/routes/loot_ingest.py`** - Loot ingestion endpoint
- **`/swgdb_api/auth/discord_token_guard.py`** - Discord authentication system
- **`/swgdb_api/schemas/session_v1.json`** - Session data JSON schema
- **`/swgdb_api/schemas/session_v1.py`** - Pydantic models for session validation

### Testing & Documentation
- **`demo_batch_166_swgdb_private_api.py`** - Comprehensive demonstration script
- **`test_batch_166_swgdb_private_api.py`** - Complete test suite (100% pass rate)
- **`BATCH_166_IMPLEMENTATION_SUMMARY.md`** - This implementation summary

## Technical Architecture

### Authentication Flow
```
1. Bot generates Discord token for user
2. Token includes Discord ID + expiry + HMAC signature
3. API receives POST with Authorization: Bearer <token>
4. Token verified against Discord ID in X-Discord-ID header
5. Rate limiting and security checks applied
6. Request processed if authentication successful
```

### Data Storage Architecture
```
User Namespace: user_{discord_id}
├── Sessions: /data/character_sessions/sessions.json
│   ├── Session entries with metadata
│   ├── User statistics and analytics
│   └── Timestamp tracking and updates
└── Loot: /data/character_loot/loot.json
    ├── Loot session entries
    ├── Item history and tracking
    └── Value aggregation and statistics
```

### API Endpoints

#### Session Ingestion
```http
POST /api/private/v1/sessions
Headers:
  Authorization: Bearer <discord_token>
  X-Discord-ID: <discord_id>
  Content-Type: application/json

Body:
{
  "session_data": {
    "session_id": "unique_session_id",
    "duration_minutes": 120,
    "xp_gained": 5000,
    "credits_earned": 25000,
    "location": "Naboo - Theed",
    "activity_type": "combat",
    "character_name": "PlayerName",
    "profession": "Rifleman",
    "level": 45,
    "faction": "rebel"
  }
}
```

#### Loot Ingestion
```http
POST /api/private/v1/loot
Headers:
  Authorization: Bearer <discord_token>
  X-Discord-ID: <discord_id>
  Content-Type: application/json

Body:
{
  "loot_data": {
    "session_id": "loot_session_id",
    "loot_items": [
      {
        "item_name": "Composite Armor",
        "quantity": 1,
        "rarity": "rare",
        "value_credits": 50000,
        "item_type": "armor"
      }
    ],
    "total_value": 50000
  }
}
```

#### Session Retrieval
```http
GET /api/private/v1/sessions/{discord_id}?limit=50
Headers:
  Authorization: Bearer <discord_token>
```

#### Loot Retrieval
```http
GET /api/private/v1/loot/{discord_id}?limit=50
Headers:
  Authorization: Bearer <discord_token>
```

#### Item History
```http
GET /api/private/v1/loot/{discord_id}/items?item_name=Composite Armor&limit=100
Headers:
  Authorization: Bearer <discord_token>
```

## Security Features

### Token Security
- **HMAC-SHA256 signatures** for token integrity
- **Automatic expiry** (configurable, default 24 hours)
- **Rate limiting** (5 attempts per 5 minutes)
- **Failed attempt tracking** with cleanup
- **Token revocation** capabilities

### Data Security
- **Per-user namespacing** prevents data cross-contamination
- **Input validation** prevents injection attacks
- **Type checking** ensures data integrity
- **Error handling** prevents information leakage

### API Security
- **HTTPS enforcement** (configurable)
- **Header validation** for required fields
- **Content-Type enforcement**
- **Request size limits** and validation

## Data Validation

### Session Data Schema
```json
{
  "session_id": "string (required, alphanumeric + _-)",
  "duration_minutes": "integer (0-1440)",
  "xp_gained": "integer (0-1000000)",
  "credits_earned": "integer (0-1000000000)",
  "activity_type": "enum (combat, crafting, questing, etc.)",
  "faction": "enum (rebel, imperial, neutral, unknown)",
  "performance_metrics": "object (optional)",
  "combat_stats": "object (optional)",
  "crafting_stats": "object (optional)",
  "quest_stats": "object (optional)"
}
```

### Loot Data Schema
```json
{
  "session_id": "string (required)",
  "loot_items": "array (required, non-empty)",
  "total_value": "integer (optional, auto-calculated)",
  "location": "string (optional)",
  "notes": "string (optional)"
}
```

## Error Handling

### HTTP Status Codes
- **200 OK** - Successful operation
- **400 Bad Request** - Invalid payload or validation error
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Rate limited or access denied
- **500 Internal Server Error** - Server-side processing error

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "timestamp": "2025-08-05T02:10:28.248139+00:00"
}
```

## Performance & Scalability

### Data Storage
- **JSON-based storage** for simplicity and portability
- **Per-user namespacing** enables horizontal scaling
- **Efficient lookups** with indexed user namespaces
- **Automatic cleanup** of expired rate limit data

### API Performance
- **Fast token verification** with HMAC comparison
- **Efficient session processing** with minimal overhead
- **Optimized data retrieval** with user-specific queries
- **Background cleanup** of expired data

## Testing Results

### Test Coverage
- ✅ **Discord Token Authentication** - Token generation, verification, expiry
- ✅ **Session Data Validation** - Schema validation, type checking
- ✅ **Session Ingestion** - Data processing, retrieval, isolation
- ✅ **Loot Ingestion** - Item tracking, statistics, history
- ✅ **API Endpoints Simulation** - Request structure, headers, authentication
- ✅ **Error Handling** - Invalid data rejection, security validation
- ✅ **Data Isolation** - Per-user separation, cross-contamination prevention

### Test Statistics
- **Total Tests**: 7
- **Passed**: 7
- **Failed**: 0
- **Success Rate**: 100.0%

## Usage Examples

### Generating a Discord Token
```python
from swgdb_api.auth.discord_token_guard import generate_discord_token

# Generate token for user
discord_id = "123456789012345678"
token = generate_discord_token(discord_id, expiry_hours=24)
print(f"Bearer {token}")
```

### Ingesting Session Data
```python
import requests

url = "https://api.swgdb.com/api/private/v1/sessions"
headers = {
    "Authorization": f"Bearer {token}",
    "X-Discord-ID": discord_id,
    "Content-Type": "application/json"
}

session_data = {
    "session_data": {
        "session_id": "combat_session_001",
        "duration_minutes": 120,
        "xp_gained": 5000,
        "credits_earned": 25000,
        "activity_type": "combat",
        "location": "Naboo - Theed"
    }
}

response = requests.post(url, json=session_data, headers=headers)
print(f"Status: {response.status_code}")
```

### Ingesting Loot Data
```python
loot_data = {
    "loot_data": {
        "session_id": "loot_session_001",
        "loot_items": [
            {
                "item_name": "Composite Armor",
                "quantity": 1,
                "rarity": "rare",
                "value_credits": 50000,
                "item_type": "armor"
            }
        ],
        "total_value": 50000
    }
}

response = requests.post(
    "https://api.swgdb.com/api/private/v1/loot",
    json=loot_data,
    headers=headers
)
```

## Configuration

### Discord Authentication Config
```json
{
  "secret_key": "your-secret-key-here",
  "token_expiry_hours": 24,
  "max_attempts": 5,
  "rate_limit_window": 300,
  "created_at": "2025-08-05T02:10:28.248139+00:00",
  "description": "Discord authentication configuration for SWGDB Private API"
}
```

## Benefits

### For Bot Developers
- **Secure authentication** with Discord integration
- **Simple API endpoints** for data ingestion
- **Comprehensive validation** prevents data corruption
- **Detailed error messages** for debugging

### For Site Administrators
- **Clean data separation** from public APIs
- **Per-user data isolation** ensures privacy
- **Scalable architecture** supports growth
- **Comprehensive logging** for monitoring

### For End Users
- **Privacy protection** with user-specific namespaces
- **Data integrity** through validation and verification
- **Reliable service** with error handling and recovery
- **Performance optimization** for fast response times

## Future Enhancements

### Planned Features
- **Database integration** for improved scalability
- **Real-time notifications** for data ingestion events
- **Advanced analytics** and reporting capabilities
- **Bulk data import** for historical data migration
- **Webhook support** for external integrations

### Potential Improvements
- **Caching layer** for improved performance
- **Compression** for large payloads
- **Batch processing** for multiple records
- **Data export** capabilities
- **Admin dashboard** for monitoring and management

## Conclusion

Batch 166 successfully implements a robust, secure, and scalable private API system that provides clean separation between public SWGDB and private MS11 data. The implementation includes comprehensive authentication, data validation, error handling, and testing, ensuring a production-ready solution for bot-to-site communication.

**Key Achievements:**
- ✅ 100% test pass rate
- ✅ Secure Discord authentication
- ✅ Comprehensive data validation
- ✅ Per-user data isolation
- ✅ Production-ready error handling
- ✅ Scalable architecture design

The SWGDB Private API v1 is now ready for deployment and integration with MS11 bot systems. 