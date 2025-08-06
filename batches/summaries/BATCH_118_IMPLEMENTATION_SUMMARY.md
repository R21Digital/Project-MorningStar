# Batch 118 – Session Upload Bridge to SWGDB

## Goal
Upload sanitized bot session data to the user's SWGDB dashboard view with comprehensive data serialization, secure authentication, and internal debugging tools.

## Overview
Batch 118 implements a complete session upload bridge system that serializes bot session logs, sanitizes sensitive data, and pushes the information to SWGDB via a secure API. The system includes data serialization, authentication, upload management, and an internal log viewer for debugging.

## Key Features

### 🔐 **Secure Authentication**
- HMAC signature-based authentication with SWGDB API
- User hash and API key validation
- Rate limiting and retry logic
- Credential validation and error handling

### 📊 **Data Serialization**
- Comprehensive session data serialization
- XP gained, credits, quests, planets visited tracking
- Sensitive data sanitization (communications, player encounters)
- Performance metrics calculation
- Metadata preservation

### 🔄 **Upload Management**
- Batch upload capabilities with rate limiting
- Retry logic for failed uploads
- Upload queue management
- Progress tracking and statistics

### 🛠️ **Internal Log Viewer**
- Session data debugging and analysis
- Search and filtering capabilities
- Session comparison tools
- Export functionality

## Files Created

### `/bridge/session_uploader.py`
**Purpose**: Main session upload orchestrator that handles finding, loading, sanitizing, and uploading session data to SWGDB.

**Key Features**:
- `SessionUploader` class for managing uploads
- `UploadConfig` dataclass for configuration
- Session file discovery and loading
- Data sanitization with configurable options
- Upload history tracking and statistics
- Retry logic for failed uploads

**Technical Details**:
- Integrates with `SessionLogSerializer` for data preparation
- Uses `SWGDBAPIClient` for API communication
- Supports multiple session directories
- Configurable sanitization options
- Upload history persistence

### `/swgdb_api/push_session_data.py`
**Purpose**: SWGDB API client for secure communication with the SWGDB API.

**Key Features**:
- `SWGDBAPIClient` class for API communication
- `SWGDBUploadManager` for batch upload management
- HMAC signature authentication
- Comprehensive error handling
- Rate limiting and retry logic

**Technical Details**:
- Uses `requests` library with retry strategy
- HMAC-SHA256 signature generation
- Support for single and batch uploads
- Credential validation
- API info and status checking

### `/core/log_serializer.py`
**Purpose**: Serializes session logs for upload with sanitization and structured data organization.

**Key Features**:
- `SessionLogSerializer` class for data serialization
- Comprehensive data structure definitions
- Sensitive data sanitization
- Performance metrics calculation
- Error handling and fallback

**Technical Details**:
- Serializes XP, credits, quests, locations, events
- Sanitizes communication events and player encounters
- Calculates efficiency scores and performance metrics
- Preserves metadata and original data structure
- Handles various data formats and edge cases

### `/data/sessions/log_viewer.py`
**Purpose**: Internal log viewer for debugging and analyzing session data before upload.

**Key Features**:
- `SessionLogViewer` class for session analysis
- Session listing and detailed viewing
- Search and filtering capabilities
- Session comparison tools
- Export functionality

**Technical Details**:
- Interactive command-line interface
- Session statistics and analysis
- Search across multiple fields
- Session comparison with metrics
- File export capabilities

## Technical Implementation

### Authentication System
```python
# HMAC signature generation
def _generate_signature(self, data: str, timestamp: str) -> str:
    message = f"{timestamp}.{data}"
    signature = hmac.new(
        self.api_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature
```

### Data Sanitization
```python
# Sensitive data removal
def _sanitize_communication_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if self._contains_sensitive_info(event.get("message", "")):
        event["message"] = "[SENSITIVE_MESSAGE_REMOVED]"
        event["_sanitized"] = True
    return event
```

### Session Serialization
```python
# Structured data organization
serialized = SerializedSession(
    session_id=session_id,
    character_name=character_name,
    start_time=start_time,
    end_time=end_time,
    duration_minutes=duration_minutes,
    xp_data=xp_data,
    credit_data=credit_data,
    quest_data=quest_data,
    location_data=location_data,
    event_data=event_data,
    performance_metrics=performance_metrics,
    metadata=metadata
)
```

## Configuration

### Environment Variables
```bash
SWGDB_API_URL=https://api.swgdb.com/v1
SWGDB_API_KEY=your_api_key_here
SWGDB_USER_HASH=your_user_hash_here
UPLOAD_INTERVAL_MINUTES=5
MAX_RETRIES=3
RETRY_DELAY_SECONDS=30
SANITIZE_DATA=true
INCLUDE_EVENTS=true
INCLUDE_LOCATIONS=true
INCLUDE_COMMUNICATIONS=false
INCLUDE_PLAYER_ENCOUNTERS=false
```

### Upload Configuration
```python
config = UploadConfig(
    swgdb_api_url="https://api.swgdb.com/v1",
    api_key="your_api_key",
    user_hash="your_user_hash",
    sanitize_data=True,
    include_events=True,
    include_locations=True,
    include_communications=False,
    include_player_encounters=False
)
```

## Usage Instructions

### Basic Upload
```python
from bridge.session_uploader import SessionUploader, UploadConfig

# Create configuration
config = UploadConfig(
    swgdb_api_url="https://api.swgdb.com/v1",
    api_key="your_api_key",
    user_hash="your_user_hash"
)

# Create uploader
uploader = SessionUploader(config)

# Upload all sessions
results = uploader.upload_all_sessions()
print(f"Uploaded: {results['uploaded']}, Failed: {results['failed']}")
```

### API Client Usage
```python
from swgdb_api.push_session_data import SWGDBAPIClient

# Create client
client = SWGDBAPIClient(
    api_url="https://api.swgdb.com/v1",
    api_key="your_api_key",
    user_hash="your_user_hash"
)

# Validate credentials
auth_result = client.validate_credentials()
if auth_result["valid"]:
    # Upload session
    result = client.push_session_data(session_data)
    print(f"Upload success: {result['success']}")
```

### Log Viewer Usage
```python
from data.sessions.log_viewer import SessionLogViewer

# Create viewer
viewer = SessionLogViewer("data/sessions")

# List sessions
viewer.list_sessions(limit=10)

# View specific session
viewer.view_session("session_id_123")

# Search sessions
results = viewer.search_sessions("quest")

# Analyze all sessions
analysis = viewer.analyze_sessions()
print(f"Total XP gained: {analysis['total_xp_gained']:,}")
```

### Command Line Usage
```bash
# List recent sessions
python data/sessions/log_viewer.py --list

# View specific session
python data/sessions/log_viewer.py --view session_id_123

# Search sessions
python data/sessions/log_viewer.py --search "quest"

# Analyze sessions
python data/sessions/log_viewer.py --analyze

# Interactive mode
python data/sessions/log_viewer.py --interactive
```

## Security Features

### Data Sanitization
- **Communication Events**: Removes or sanitizes whisper/tell messages
- **Player Encounters**: Removes player names for privacy
- **Guild Alerts**: Sanitizes sensitive guild communications
- **Action Logs**: Filters sensitive actions and commands

### Authentication
- **HMAC Signatures**: Secure API authentication
- **Timestamp Validation**: Prevents replay attacks
- **Rate Limiting**: Prevents abuse
- **Credential Validation**: Verifies API access

### Privacy Protection
- **Configurable Sanitization**: User controls what data is included
- **Sensitive Pattern Detection**: Automatic detection of private information
- **Player Name Removal**: Protects player privacy
- **Message Sanitization**: Removes sensitive communication content

## Error Handling

### Upload Errors
- **Network Timeouts**: Automatic retry with exponential backoff
- **Authentication Failures**: Clear error messages and credential validation
- **Rate Limiting**: Automatic delay and retry
- **API Errors**: Detailed error reporting and logging

### Data Errors
- **Invalid Session Data**: Graceful handling with error sessions
- **Missing Fields**: Default values and fallback handling
- **Serialization Errors**: Error session creation with metadata
- **File System Errors**: Comprehensive error logging

## Performance Considerations

### Upload Optimization
- **Batch Uploads**: Multiple sessions per API call
- **Rate Limiting**: Configurable delays between uploads
- **Queue Management**: Efficient upload queue processing
- **Retry Logic**: Intelligent retry with backoff

### Data Processing
- **Incremental Uploads**: Only upload new sessions
- **Efficient Serialization**: Optimized data structure
- **Memory Management**: Streaming for large datasets
- **Caching**: Upload history and statistics caching

## Testing

### Demo Script
```bash
python demo_batch_118_session_upload.py
```

**Features Demonstrated**:
- Session serialization with sanitization
- SWGDB API integration
- Upload manager functionality
- Log viewer capabilities
- Complete workflow demonstration

### Test Suite
```bash
python test_batch_118_session_upload.py
```

**Test Coverage**:
- **SessionLogSerializer**: 10+ test methods
- **SWGDBAPIClient**: 8+ test methods
- **SWGDBUploadManager**: 6+ test methods
- **SessionUploader**: 7+ test methods
- **SessionLogViewer**: 10+ test methods

**Total**: 40+ comprehensive test methods covering all functionality

## Future Enhancements

### Planned Features
- **WebSocket Integration**: Real-time upload status
- **Advanced Analytics**: Session pattern analysis
- **Custom Dashboards**: User-defined metrics
- **API Rate Optimization**: Dynamic rate limiting
- **Compression**: Data compression for large uploads

### Potential Improvements
- **Database Integration**: Persistent session storage
- **Advanced Filtering**: Complex search queries
- **Export Formats**: Multiple export formats (CSV, XML)
- **Scheduled Uploads**: Automated upload scheduling
- **Multi-User Support**: User-specific upload queues

## Dependencies

### Core Dependencies
```python
requests>=2.25.0          # HTTP client for API calls
urllib3>=1.26.0           # HTTP library with retry support
pathlib                    # File system operations
json                       # JSON serialization
datetime                   # Time handling
typing                     # Type hints
unittest.mock              # Testing and mocking
```

### Optional Dependencies
```python
argparse                   # Command line argument parsing
collections                # Data structures for analysis
tempfile                   # Temporary file handling
shutil                     # File system utilities
```

## Integration Points

### With Existing Systems
- **Session Manager**: Integrates with existing session tracking
- **Discord Authentication**: Uses existing auth system from Batch 116
- **Dashboard**: Provides data for web dashboard
- **Logging**: Integrates with existing logging system

### API Endpoints
- **SWGDB Upload**: `/sessions/upload`
- **Batch Upload**: `/sessions/batch-upload`
- **Status Check**: `/sessions/{id}/status`
- **Auth Validation**: `/auth/validate`
- **API Info**: `/info`

## Monitoring and Debugging

### Upload Monitoring
- **Upload Statistics**: Success rates and error tracking
- **Performance Metrics**: Upload speed and efficiency
- **Error Logging**: Detailed error reporting
- **Retry Tracking**: Failed upload retry monitoring

### Debugging Tools
- **Log Viewer**: Interactive session analysis
- **Export Functionality**: Session data export
- **Search Capabilities**: Multi-field search
- **Comparison Tools**: Session-to-session comparison

## Conclusion

Batch 118 provides a comprehensive session upload bridge system that securely and efficiently uploads sanitized bot session data to SWGDB. The system includes robust authentication, data sanitization, upload management, and debugging tools, making it production-ready for real-world use.

The implementation follows best practices for security, performance, and maintainability, with comprehensive testing and documentation. The modular design allows for easy extension and customization to meet specific requirements. 