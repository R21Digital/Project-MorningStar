# Batch 095 – Vendor/Bazaar Price Scanner Implementation Summary

## Overview

**Batch 095** implements a comprehensive vendor price scanning and analysis system for SWGDB, providing OCR-based price detection from vendor windows, automated price analysis, and Discord alerts for underpriced items. This system integrates with existing bazaar modules and provides real-time monitoring capabilities.

## Core Components

### 1. VendorPriceScanner (`core/vendor_price_scanner.py`)

**Purpose**: Main OCR-based price detection and analysis engine.

**Key Features**:
- **OCR Price Detection**: Uses `pytesseract` and `cv2` for screen capture and text extraction
- **Pattern Matching**: Regex-based price and item name extraction from vendor windows
- **Confidence Scoring**: Intelligent confidence calculation for parsed prices
- **Price History**: Persistent storage of scanned prices in JSON format
- **Price Analysis**: Automated detection of underpriced/overpriced items
- **Recommendations**: AI-driven price recommendations based on historical data

**Data Structures**:
```python
@dataclass
class ScannedPrice:
    item_name: str
    price: int
    source: PriceSource
    vendor_name: str
    location: str
    timestamp: str
    confidence: float
    raw_text: str

@dataclass
class PriceAlert:
    item_name: str
    current_price: int
    average_price: float
    discount_percentage: float
    vendor_name: str
    location: str
    timestamp: str
    alert_type: str

@dataclass
class PriceRecommendation:
    item_name: str
    recommended_price: int
    confidence: float
    reasoning: str
    market_trend: str
    last_updated: str
```

**Key Methods**:
- `scan_vendor_window()`: OCR-based price scanning
- `analyze_prices()`: Price analysis and alert generation
- `get_price_recommendations()`: AI-driven price recommendations
- `save_price_history()`: Persistent price data storage

### 2. VendorPriceAlerts (`core/vendor_price_alerts.py`)

**Purpose**: Discord alert system for underpriced items.

**Key Features**:
- **Alert Filtering**: Configurable thresholds and preferences
- **Cooldown Management**: Prevents alert spam with time-based cooldowns
- **Discord Integration**: Webhook-based Discord notifications
- **Console Alerts**: Fallback console output for alerts
- **Alert History**: Persistent tracking of sent alerts

**Data Structures**:
```python
@dataclass
class AlertPreferences:
    min_alert_price: int = 1000
    discount_threshold: float = 0.3
    enable_discord_alerts: bool = True
    enable_console_alerts: bool = True
    alert_cooldown_minutes: int = 30
    max_alerts_per_hour: int = 10

@dataclass
class AlertHistory:
    item_name: str
    vendor_name: str
    alert_type: str
    timestamp: str
    price: int
    discount_percentage: float
```

**Key Methods**:
- `send_price_alert()`: Send alerts via Discord/console
- `should_send_alert()`: Alert filtering logic
- `update_preferences()`: Dynamic preference management
- `get_alert_statistics()`: Alert performance metrics

### 3. Dashboard Interface (`dashboard/templates/vendor_price_scanner.html`)

**Purpose**: Web-based control interface for the vendor price scanner.

**Features**:
- **Real-time Statistics**: Items tracked, price entries, recent alerts
- **Scanner Controls**: Start/stop scanning, configure parameters
- **Alert Settings**: Configure thresholds and notification preferences
- **Price Analysis**: View current price analysis and recommendations
- **Recent Alerts**: Historical alert tracking and management

**Key Sections**:
- Scanner Status Dashboard
- OCR Configuration Controls
- Alert Management Interface
- Price Analysis Results
- Historical Data Visualization

### 4. API Endpoints (`dashboard/app.py`)

**Purpose**: RESTful API for vendor scanner functionality.

**Endpoints**:
- `GET /api/vendor-scanner/statistics`: Scanner performance metrics
- `GET /api/vendor-scanner/alert-settings`: Current alert configuration
- `GET /api/vendor-scanner/recent-alerts`: Recent alert history
- `POST /api/vendor-scanner/start-scan`: Start scanning process
- `POST /api/vendor-scanner/stop-scan`: Stop scanning process
- `POST /api/vendor-scanner/perform-scan`: Single scan execution
- `POST /api/vendor-scanner/update-alert-settings`: Update preferences
- `POST /api/vendor-scanner/analyze-prices`: Price analysis
- `GET /api/vendor-scanner/recommendations`: Price recommendations

## Data Storage

### Price History Structure
```
data/vendor_prices/
├── durindfire_crystal.json
├── spice_wine.json
├── rare_gemstone.json
└── ...
```

**File Format**:
```json
{
  "prices": [
    {
      "price": 50000,
      "source": "vendor",
      "vendor_name": "Coronet Vendor",
      "location": "Coronet, Corellia",
      "timestamp": "2024-01-01T12:00:00",
      "confidence": 0.85
    }
  ],
  "statistics": {
    "average_price": 75000,
    "min_price": 50000,
    "max_price": 100000,
    "total_entries": 15,
    "last_updated": "2024-01-01T12:00:00"
  }
}
```

### Alert History Structure
```
data/vendor_alerts_history.json
```

**File Format**:
```json
[
  {
    "item_name": "Durindfire Crystal",
    "vendor_name": "Test Vendor",
    "alert_type": "underpriced",
    "timestamp": "2024-01-01T12:00:00",
    "price": 50000,
    "discount_percentage": 0.33
  }
]
```

## Configuration System

### Scanner Configuration (`config/vendor_scanner_config.json`)
```json
{
  "ocr": {
    "min_confidence": 0.7,
    "price_patterns": [
      "(\d{1,3}(?:,\d{3})*)\s*credits?",
      "(\d+)\s*cr"
    ],
    "item_patterns": [
      "([A-Za-z\s\-']+)\s*\d{1,3}(?:,\d{3})*"
    ]
  },
  "alerts": {
    "discount_threshold": 0.3,
    "enable_discord_alerts": true,
    "min_alert_price": 1000
  },
  "scanning": {
    "auto_scan_interval": 30,
    "max_scan_duration": 300
  }
}
```

### Alert Configuration (`config/vendor_alerts_config.json`)
```json
{
  "alerts": {
    "min_alert_price": 1000,
    "discount_threshold": 0.3,
    "enable_discord_alerts": true,
    "enable_console_alerts": true,
    "alert_cooldown_minutes": 30,
    "max_alerts_per_hour": 10
  },
  "discord": {
    "webhook_url": "https://discord.com/api/webhooks/...",
    "channel_id": "channel_id",
    "bot_token": "bot_token"
  },
  "filtering": {
    "excluded_items": [],
    "excluded_vendors": [],
    "min_confidence": 0.7
  }
}
```

## OCR Implementation

### Image Preprocessing Pipeline
1. **Screen Capture**: `pyautogui.screenshot()` for full screen capture
2. **Color Conversion**: RGB to BGR for OpenCV compatibility
3. **Grayscale Conversion**: Better text recognition
4. **Thresholding**: Otsu's method for binary image
5. **Morphological Operations**: Clean up text artifacts
6. **OCR Processing**: `pytesseract.image_to_string()`

### Pattern Matching
**Price Patterns**:
- `(\d{1,3}(?:,\d{3})*)\s*credits?` - "50,000 credits"
- `(\d+)\s*cr` - "50000 cr"
- `Price:\s*(\d{1,3}(?:,\d{3})*)` - "Price: 50,000"

**Item Patterns**:
- `([A-Za-z\s\-']+)\s*\d{1,3}(?:,\d{3})*` - "Item Name 50,000"

### Confidence Scoring
**Factors**:
- Base confidence (0.3) for successful extraction
- Price range validation (0.2)
- Item name length validation (0.2)
- Text cleanliness (0.1)
- Price format consistency (0.1)
- Text length penalties (-0.2 for extremes)

## Alert System

### Alert Filtering Logic
1. **Minimum Price Check**: Item price >= min_alert_price
2. **Discount Threshold**: |discount_percentage| >= threshold
3. **Excluded Items/Vendors**: Filter out unwanted sources
4. **Cooldown Check**: Prevent spam with time-based cooldowns
5. **Hourly Limit**: Maximum alerts per hour

### Discord Integration
**Webhook Payload**:
```json
{
  "embeds": [{
    "title": "💰 Vendor Price Alert",
    "description": "Alert message content",
    "color": 0x00ff00,
    "timestamp": "2024-01-01T12:00:00"
  }]
}
```

## Integration Points

### Existing Bazaar Module
- **PriceTracker**: Historical price analysis and trends
- **VendorManager**: Intelligent vendor interactions
- **BazaarDetector**: Vendor terminal detection
- **Data Sharing**: Price history synchronization

### Future Enhancements
- **Crafting Integration**: Profitability calculations
- **Multi-server Support**: Cross-server price tracking
- **AI Predictions**: Machine learning price forecasting
- **Mobile App**: Real-time mobile notifications

## Performance Considerations

### Scalability
- **Modular Design**: Independent scanner and alert components
- **Efficient Storage**: JSON-based price history with statistics
- **Background Processing**: Non-blocking OCR operations
- **Memory Management**: Cleanup of temporary data

### Optimization
- **Confidence Filtering**: Only process high-confidence results
- **Cooldown Management**: Prevent excessive alert generation
- **Caching**: Price history caching for faster analysis
- **Batch Processing**: Multiple vendor scanning in sequence

## Security & Privacy

### Data Protection
- **Local Storage**: All data stored locally
- **No Sensitive Data**: No personal information collected
- **Configurable Filtering**: Exclude specific items/vendors
- **Audit Trail**: Complete alert history tracking

### Discord Security
- **Webhook Authentication**: Secure Discord webhook URLs
- **Rate Limiting**: Built-in alert frequency limits
- **Error Handling**: Graceful failure handling
- **Fallback Options**: Console alerts when Discord unavailable

## Testing & Quality Assurance

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Testing**: OCR and Discord integration testing
- **Performance Tests**: Scalability and performance validation

### Demo Scripts
- **Comprehensive Demo**: `demo_batch_095_vendor_price_scanner.py`
- **Feature Showcase**: All major functionality demonstrated
- **Integration Examples**: Bazaar module integration
- **Future Roadmap**: Enhancement possibilities

## Deployment & Usage

### Installation Requirements
```bash
pip install opencv-python pytesseract pyautogui requests
```

### Configuration Steps
1. Create configuration files in `config/`
2. Set up Discord webhook (optional)
3. Configure alert preferences
4. Test OCR functionality
5. Start scanning process

### Dashboard Access
- **URL**: `http://localhost:8000/vendor-price-scanner`
- **Features**: Real-time monitoring and control
- **Statistics**: Performance metrics and analytics
- **Configuration**: Dynamic preference management

## Benefits & Impact

### For Users
- **Automated Price Discovery**: No manual vendor checking
- **Real-time Alerts**: Immediate notification of good deals
- **Price Intelligence**: Historical data and trends
- **Time Savings**: Automated scanning and analysis

### For System
- **Data Collection**: Comprehensive price database
- **Market Intelligence**: Price trend analysis
- **Integration Ready**: Compatible with existing modules
- **Extensible**: Foundation for future enhancements

## Future Enhancements

### Phase 2: Advanced Analysis
- **Machine Learning**: Price prediction models
- **Market Trends**: Advanced trend analysis
- **Multi-server**: Cross-server price comparison
- **Crafting Integration**: Profitability calculations

### Phase 3: Mobile & Web
- **Mobile App**: Real-time mobile notifications
- **Web Dashboard**: Advanced analytics interface
- **API Expansion**: External integrations
- **Social Features**: Community price sharing

### Phase 4: AI Integration
- **Predictive Analytics**: Price forecasting
- **Smart Recommendations**: AI-driven suggestions
- **Automated Trading**: Buy/sell recommendations
- **Market Analysis**: Comprehensive market insights

## Conclusion

Batch 095 successfully implements a comprehensive vendor price scanning and analysis system that provides:

1. **OCR-based price detection** from vendor windows
2. **Automated price analysis** with historical data
3. **Discord alert system** for underpriced items
4. **Integration** with existing bazaar modules
5. **Web dashboard** for monitoring and control
6. **Extensible architecture** for future enhancements

The system is production-ready with comprehensive testing, documentation, and integration capabilities, providing a solid foundation for automated price monitoring and market intelligence in SWGDB. 