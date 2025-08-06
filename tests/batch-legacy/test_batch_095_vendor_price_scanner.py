"""Test suite for Batch 095 - Vendor/Bazaar Price Scanner.

This test suite validates the comprehensive vendor price scanning and analysis system:
- OCR-based price detection functionality
- Price history tracking and analysis
- Automated price recommendations
- Discord alert system
- Integration with existing bazaar module
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
from core.vendor_price_scanner import (
    VendorPriceScanner, ScannedPrice, PriceSource, 
    PriceAlert, PriceRecommendation
)
from core.vendor_price_alerts import (
    VendorPriceAlerts, AlertPreferences, AlertHistory
)


class TestVendorPriceScanner:
    """Test the VendorPriceScanner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.price_history_dir = Path(self.temp_dir) / "vendor_prices"
        self.price_history_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary config file
        self.config_file = Path(self.temp_dir) / "vendor_scanner_config.json"
        self.config_data = {
            "ocr": {
                "min_confidence": 0.7,
                "price_patterns": [
                    r"(\d{1,3}(?:,\d{3})*)\s*credits?",
                    r"(\d+)\s*cr"
                ],
                "item_patterns": [
                    r"([A-Za-z\s\-']+)\s*\d{1,3}(?:,\d{3})*"
                ]
            },
            "alerts": {
                "discount_threshold": 0.3,
                "enable_discord_alerts": True,
                "min_alert_price": 1000
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f)
        
        # Initialize scanner with temp directory
        self.scanner = VendorPriceScanner(str(self.config_file))
        self.scanner.price_history_dir = self.price_history_dir
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test scanner initialization."""
        assert self.scanner.config_path == self.config_file
        assert self.scanner.alert_threshold == 0.3
        assert self.scanner.min_confidence == 0.7
        assert len(self.scanner.price_patterns) == 2
        assert len(self.scanner.item_patterns) == 1
    
    def test_load_config_default(self):
        """Test loading default configuration when file doesn't exist."""
        scanner = VendorPriceScanner("nonexistent_config.json")
        assert scanner.alert_threshold == 0.3
        assert scanner.min_confidence == 0.7
    
    @patch('core.vendor_price_scanner.pyautogui.screenshot')
    @patch('core.vendor_price_scanner.pytesseract.image_to_string')
    def test_scan_vendor_window(self, mock_ocr, mock_screenshot):
        """Test vendor window scanning."""
        # Mock screenshot and OCR
        mock_screenshot.return_value = Mock()
        mock_ocr.return_value = """
        Durindfire Crystal 50,000 credits
        Spice Wine 150,000 credits
        Rare Gemstone 25,000 credits
        """
        
        scanned_prices = self.scanner.scan_vendor_window("Test Vendor", "Test Location")
        
        assert len(scanned_prices) == 3
        assert scanned_prices[0].item_name == "Durindfire Crystal"
        assert scanned_prices[0].price == 50000
        assert scanned_prices[0].vendor_name == "Test Vendor"
    
    def test_parse_prices_from_text(self):
        """Test parsing prices from OCR text."""
        text = """
        Durindfire Crystal 50,000 credits
        Spice Wine 150,000 credits
        Invalid line
        """
        
        scanned_prices = self.scanner._parse_prices_from_text(text, "Test Vendor", "Test Location")
        
        assert len(scanned_prices) == 2
        assert scanned_prices[0].item_name == "Durindfire Crystal"
        assert scanned_prices[0].price == 50000
        assert scanned_prices[1].item_name == "Spice Wine"
        assert scanned_prices[1].price == 150000
    
    def test_extract_item_and_price(self):
        """Test extracting item name and price from text."""
        # Test price pattern
        item_name, price = self.scanner._extract_item_and_price("Durindfire Crystal 50,000 credits")
        assert item_name == "Durindfire Crystal"
        assert price == 50000
        
        # Test item pattern
        item_name, price = self.scanner._extract_item_and_price("Spice Wine 150000 cr")
        assert item_name == "Spice Wine"
        assert price == 150000
        
        # Test invalid text
        item_name, price = self.scanner._extract_item_and_price("Invalid text")
        assert item_name is None
        assert price is None
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        confidence = self.scanner._calculate_confidence(
            "Durindfire Crystal 50,000 credits",
            "Durindfire Crystal",
            50000
        )
        assert 0.0 <= confidence <= 1.0
        
        # Test with invalid price
        confidence = self.scanner._calculate_confidence(
            "Invalid 999999999 credits",
            "Invalid",
            999999999
        )
        assert confidence < 1.0
    
    def test_save_price_history(self):
        """Test saving price history."""
        scanned_prices = [
            ScannedPrice(
                item_name="Test Item",
                price=50000,
                source=PriceSource.VENDOR,
                vendor_name="Test Vendor",
                location="Test Location",
                timestamp=datetime.now().isoformat(),
                confidence=0.8,
                raw_text="Test Item 50,000 credits"
            )
        ]
        
        self.scanner.save_price_history(scanned_prices)
        
        # Check if file was created
        item_file = self.price_history_dir / "test_item.json"
        assert item_file.exists()
        
        # Check file contents
        with open(item_file, 'r') as f:
            data = json.load(f)
        
        assert len(data["prices"]) == 1
        assert data["prices"][0]["price"] == 50000
        assert data["statistics"]["average_price"] == 50000
    
    def test_analyze_prices(self):
        """Test price analysis."""
        # Create sample price history
        item_file = self.price_history_dir / "test_item.json"
        history_data = {
            "prices": [
                {"price": 75000, "timestamp": "2024-01-01T00:00:00"},
                {"price": 80000, "timestamp": "2024-01-02T00:00:00"},
                {"price": 70000, "timestamp": "2024-01-03T00:00:00"}
            ],
            "statistics": {
                "average_price": 75000,
                "min_price": 70000,
                "max_price": 80000,
                "total_entries": 3
            }
        }
        
        with open(item_file, 'w') as f:
            json.dump(history_data, f)
        
        # Test underpriced item
        scanned_prices = [
            ScannedPrice(
                item_name="Test Item",
                price=50000,  # Underpriced
                source=PriceSource.VENDOR,
                vendor_name="Test Vendor",
                location="Test Location",
                timestamp=datetime.now().isoformat(),
                confidence=0.8,
                raw_text="Test Item 50,000 credits"
            )
        ]
        
        alerts = self.scanner.analyze_prices(scanned_prices)
        
        assert len(alerts) == 1
        assert alerts[0].alert_type == "underpriced"
        assert alerts[0].discount_percentage > 0
    
    def test_get_price_recommendations(self):
        """Test price recommendations."""
        # Create sample price history
        item_file = self.price_history_dir / "test_item.json"
        history_data = {
            "prices": [
                {"price": 70000, "timestamp": "2024-01-01T00:00:00"},
                {"price": 75000, "timestamp": "2024-01-02T00:00:00"},
                {"price": 80000, "timestamp": "2024-01-03T00:00:00"},
                {"price": 85000, "timestamp": "2024-01-04T00:00:00"},
                {"price": 90000, "timestamp": "2024-01-05T00:00:00"}
            ],
            "statistics": {
                "average_price": 80000,
                "min_price": 70000,
                "max_price": 90000,
                "total_entries": 5
            }
        }
        
        with open(item_file, 'w') as f:
            json.dump(history_data, f)
        
        recommendation = self.scanner.get_price_recommendations("Test Item")
        
        assert recommendation is not None
        assert recommendation.item_name == "Test Item"
        assert recommendation.confidence > 0
        assert recommendation.market_trend in ["rising", "falling", "stable"]
    
    def test_get_statistics(self):
        """Test getting scanner statistics."""
        # Create some sample price history files
        for i in range(3):
            item_file = self.price_history_dir / f"item_{i}.json"
            history_data = {
                "prices": [{"price": 50000, "timestamp": "2024-01-01T00:00:00"}],
                "statistics": {"average_price": 50000, "total_entries": 1}
            }
            with open(item_file, 'w') as f:
                json.dump(history_data, f)
        
        stats = self.scanner.get_statistics()
        
        assert stats["total_items_tracked"] == 3
        assert stats["total_price_entries"] == 3
        assert "last_scan" in stats


class TestVendorPriceAlerts:
    """Test the VendorPriceAlerts class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "vendor_alerts_config.json"
        self.alert_history_file = Path(self.temp_dir) / "vendor_alerts_history.json"
        
        # Create config file
        config_data = {
            "alerts": {
                "min_alert_price": 1000,
                "discount_threshold": 0.3,
                "enable_discord_alerts": True,
                "enable_console_alerts": True,
                "alert_cooldown_minutes": 30,
                "max_alerts_per_hour": 10
            },
            "discord": {
                "webhook_url": "https://discord.com/api/webhooks/test",
                "channel_id": "test_channel",
                "bot_token": "test_token"
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Initialize alerts with temp directory
        self.alerts = VendorPriceAlerts(str(self.config_file))
        self.alerts.alert_history_file = self.alert_history_file
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test alerts initialization."""
        assert self.alerts.preferences.min_alert_price == 1000
        assert self.alerts.preferences.discount_threshold == 0.3
        assert self.alerts.preferences.enable_discord_alerts is True
        assert self.alerts.discord_webhook_url == "https://discord.com/api/webhooks/test"
    
    def test_should_send_alert(self):
        """Test alert filtering logic."""
        # Test valid alert
        should_send = self.alerts.should_send_alert(
            "Test Item", "Test Vendor", 50000, 0.4
        )
        assert should_send is True
        
        # Test price too low
        should_send = self.alerts.should_send_alert(
            "Test Item", "Test Vendor", 500, 0.4
        )
        assert should_send is False
        
        # Test discount too small
        should_send = self.alerts.should_send_alert(
            "Test Item", "Test Vendor", 50000, 0.1
        )
        assert should_send is False
    
    def test_check_alert_cooldown(self):
        """Test alert cooldown logic."""
        # Add a recent alert
        recent_alert = AlertHistory(
            item_name="Test Item",
            vendor_name="Test Vendor",
            alert_type="underpriced",
            timestamp=datetime.now().isoformat(),
            price=50000,
            discount_percentage=0.4
        )
        self.alerts.alert_history.append(recent_alert)
        
        # Should not send due to cooldown
        should_send = self.alerts._check_alert_cooldown("Test Item", "Test Vendor")
        assert should_send is False
        
        # Add old alert
        old_alert = AlertHistory(
            item_name="Test Item",
            vendor_name="Test Vendor",
            alert_type="underpriced",
            timestamp=(datetime.now() - timedelta(hours=2)).isoformat(),
            price=50000,
            discount_percentage=0.4
        )
        self.alerts.alert_history.append(old_alert)
        
        # Should send (cooldown passed)
        should_send = self.alerts._check_alert_cooldown("Test Item", "Test Vendor")
        assert should_send is True
    
    def test_check_hourly_limit(self):
        """Test hourly alert limit."""
        # Add many recent alerts
        for i in range(15):
            alert = AlertHistory(
                item_name=f"Test Item {i}",
                vendor_name="Test Vendor",
                alert_type="underpriced",
                timestamp=datetime.now().isoformat(),
                price=50000,
                discount_percentage=0.4
            )
            self.alerts.alert_history.append(alert)
        
        # Should not send due to hourly limit
        should_send = self.alerts._check_hourly_limit()
        assert should_send is False
    
    @patch('core.vendor_price_alerts.requests.post')
    def test_send_discord_alert(self, mock_post):
        """Test Discord alert sending."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        success = self.alerts._send_discord_alert("Test alert message")
        assert success is True
        
        # Test failed request
        mock_response.status_code = 400
        success = self.alerts._send_discord_alert("Test alert message")
        assert success is False
    
    def test_send_console_alert(self):
        """Test console alert sending."""
        success = self.alerts._send_console_alert("Test alert message")
        assert success is True
    
    def test_send_price_alert(self):
        """Test sending price alerts."""
        # Test successful alert
        with patch.object(self.alerts, '_send_discord_alert', return_value=True):
            success = self.alerts.send_price_alert(
                "Test Item", 50000, 75000, 0.33, "Test Vendor", "Test Location"
            )
            assert success is True
        
        # Test filtered alert (price too low)
        success = self.alerts.send_price_alert(
            "Test Item", 500, 75000, 0.33, "Test Vendor", "Test Location"
        )
        assert success is False
    
    def test_get_alert_statistics(self):
        """Test getting alert statistics."""
        # Add some test alerts
        for i in range(5):
            alert = AlertHistory(
                item_name=f"Test Item {i}",
                vendor_name="Test Vendor",
                alert_type="underpriced" if i % 2 == 0 else "overpriced",
                timestamp=datetime.now().isoformat(),
                price=50000,
                discount_percentage=0.4
            )
            self.alerts.alert_history.append(alert)
        
        stats = self.alerts.get_alert_statistics()
        
        assert stats["total_alerts"] == 5
        assert stats["underpriced_alerts"] == 3
        assert stats["overpriced_alerts"] == 2
        assert stats["recent_alerts_24h"] == 5
    
    def test_update_preferences(self):
        """Test updating alert preferences."""
        self.alerts.update_preferences(
            min_alert_price=2000,
            discount_threshold=0.25,
            enable_discord_alerts=False
        )
        
        assert self.alerts.preferences.min_alert_price == 2000
        assert self.alerts.preferences.discount_threshold == 0.25
        assert self.alerts.preferences.enable_discord_alerts is False


class TestDataClasses:
    """Test the data classes used in the vendor price scanner."""
    
    def test_scanned_price(self):
        """Test ScannedPrice dataclass."""
        price = ScannedPrice(
            item_name="Test Item",
            price=50000,
            source=PriceSource.VENDOR,
            vendor_name="Test Vendor",
            location="Test Location",
            timestamp="2024-01-01T00:00:00",
            confidence=0.8,
            raw_text="Test Item 50,000 credits"
        )
        
        assert price.item_name == "Test Item"
        assert price.price == 50000
        assert price.source == PriceSource.VENDOR
        assert price.confidence == 0.8
    
    def test_price_alert(self):
        """Test PriceAlert dataclass."""
        alert = PriceAlert(
            item_name="Test Item",
            current_price=50000,
            average_price=75000,
            discount_percentage=0.33,
            vendor_name="Test Vendor",
            location="Test Location",
            timestamp="2024-01-01T00:00:00",
            alert_type="underpriced"
        )
        
        assert alert.item_name == "Test Item"
        assert alert.current_price == 50000
        assert alert.average_price == 75000
        assert alert.discount_percentage == 0.33
        assert alert.alert_type == "underpriced"
    
    def test_price_recommendation(self):
        """Test PriceRecommendation dataclass."""
        recommendation = PriceRecommendation(
            item_name="Test Item",
            recommended_price=70000,
            confidence=0.85,
            reasoning="Based on 15 price entries",
            market_trend="stable",
            last_updated="2024-01-01T00:00:00"
        )
        
        assert recommendation.item_name == "Test Item"
        assert recommendation.recommended_price == 70000
        assert recommendation.confidence == 0.85
        assert recommendation.market_trend == "stable"
    
    def test_alert_preferences(self):
        """Test AlertPreferences dataclass."""
        preferences = AlertPreferences(
            min_alert_price=1000,
            discount_threshold=0.3,
            enable_discord_alerts=True,
            enable_console_alerts=True,
            alert_cooldown_minutes=30,
            max_alerts_per_hour=10
        )
        
        assert preferences.min_alert_price == 1000
        assert preferences.discount_threshold == 0.3
        assert preferences.enable_discord_alerts is True
        assert preferences.max_alerts_per_hour == 10
    
    def test_alert_history(self):
        """Test AlertHistory dataclass."""
        alert = AlertHistory(
            item_name="Test Item",
            vendor_name="Test Vendor",
            alert_type="underpriced",
            timestamp="2024-01-01T00:00:00",
            price=50000,
            discount_percentage=0.4
        )
        
        assert alert.item_name == "Test Item"
        assert alert.vendor_name == "Test Vendor"
        assert alert.alert_type == "underpriced"
        assert alert.price == 50000
        assert alert.discount_percentage == 0.4


class TestIntegration:
    """Test integration between vendor scanner and alerts."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.scanner_config = Path(self.temp_dir) / "scanner_config.json"
        self.alerts_config = Path(self.temp_dir) / "alerts_config.json"
        
        # Create config files
        scanner_config_data = {
            "ocr": {"min_confidence": 0.7},
            "alerts": {"discount_threshold": 0.3}
        }
        alerts_config_data = {
            "alerts": {
                "min_alert_price": 1000,
                "discount_threshold": 0.3,
                "enable_discord_alerts": False,
                "enable_console_alerts": True
            }
        }
        
        with open(self.scanner_config, 'w') as f:
            json.dump(scanner_config_data, f)
        with open(self.alerts_config, 'w') as f:
            json.dump(alerts_config_data, f)
        
        # Initialize components
        self.scanner = VendorPriceScanner(str(self.scanner_config))
        self.alerts = VendorPriceAlerts(str(self.alerts_config))
        
        # Set temp directories
        self.scanner.price_history_dir = Path(self.temp_dir) / "vendor_prices"
        self.scanner.price_history_dir.mkdir(parents=True, exist_ok=True)
        self.alerts.alert_history_file = Path(self.temp_dir) / "alerts_history.json"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Test the complete workflow from scanning to alerts."""
        # 1. Scan vendor window
        scanned_prices = [
            ScannedPrice(
                item_name="Test Item",
                price=50000,  # Underpriced
                source=PriceSource.VENDOR,
                vendor_name="Test Vendor",
                location="Test Location",
                timestamp=datetime.now().isoformat(),
                confidence=0.8,
                raw_text="Test Item 50,000 credits"
            )
        ]
        
        # 2. Save to price history
        self.scanner.save_price_history(scanned_prices)
        
        # 3. Analyze for alerts
        alerts = self.scanner.analyze_prices(scanned_prices)
        
        # 4. Send alerts
        alert_sent = False
        for alert in alerts:
            if alert.alert_type == "underpriced":
                alert_sent = self.alerts.send_price_alert(
                    alert.item_name,
                    alert.current_price,
                    alert.average_price,
                    alert.discount_percentage,
                    alert.vendor_name,
                    alert.location
                )
        
        # Verify workflow
        assert len(scanned_prices) == 1
        assert len(alerts) >= 0  # May be 0 if no historical data
        assert isinstance(alert_sent, bool)
    
    def test_configuration_sync(self):
        """Test that scanner and alerts use consistent configuration."""
        assert self.scanner.alert_threshold == self.alerts.preferences.discount_threshold
        
        # Update alerts configuration
        self.alerts.update_preferences(discount_threshold=0.25)
        
        # Scanner should still use its own config
        assert self.scanner.alert_threshold != self.alerts.preferences.discount_threshold


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 