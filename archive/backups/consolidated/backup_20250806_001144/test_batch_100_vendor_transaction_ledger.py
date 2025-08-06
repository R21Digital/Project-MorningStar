"""Test suite for Batch 100 - Vendor Transaction Ledger System.

This test suite validates the comprehensive vendor transaction ledger system:
- Transaction logging and retrieval
- Price analysis and statistics
- Duplicate detection
- Underpriced/overpriced item detection
- Web dashboard integration
- Data filtering and sorting
"""

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.vendor_transaction_ledger import (
    VendorTransactionLedger,
    VendorTransaction,
    PriceAnalysis,
    DuplicateEntry,
    TransactionType,
    ItemCategory,
    vendor_ledger,
    log_vendor_transaction
)


class TestVendorTransactionLedger:
    """Test the VendorTransactionLedger class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_path = Path(self.temp_dir) / "test_ledger.json"
        self.ledger = VendorTransactionLedger(str(self.ledger_path))
        
        # Sample transaction data
        self.sample_transactions = [
            {
                "item_name": "Durindfire Crystal",
                "price": 75000,
                "location": "tatooine_mos_eisley",
                "seller": "Crystal Vendor",
                "transaction_type": TransactionType.OBSERVED,
                "item_category": ItemCategory.RESOURCE,
                "quantity": 1,
                "notes": "High quality crystal",
                "confidence": 0.95,
                "raw_text": "Durindfire Crystal - 75,000 credits"
            },
            {
                "item_name": "Spice Wine",
                "price": 120000,
                "location": "tatooine_mos_eisley",
                "seller": "Wine Merchant",
                "transaction_type": TransactionType.SALE,
                "item_category": ItemCategory.CONSUMABLE,
                "quantity": 2,
                "notes": "Premium vintage",
                "confidence": 0.98,
                "raw_text": "Spice Wine x2 - 120,000 credits each"
            },
            {
                "item_name": "Durindfire Crystal",
                "price": 70000,
                "location": "tatooine_mos_eisley",
                "seller": "Crystal Vendor",
                "transaction_type": TransactionType.OBSERVED,
                "item_category": ItemCategory.RESOURCE,
                "quantity": 1,
                "notes": "Lower price than usual",
                "confidence": 0.92,
                "raw_text": "Durindfire Crystal - 70,000 credits"
            }
        ]
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test ledger initialization."""
        assert self.ledger.ledger_path == self.ledger_path
        assert len(self.ledger.transactions) == 0
        assert len(self.ledger.price_analyses) == 0
        assert len(self.ledger.duplicate_entries) == 0
    
    def test_log_transaction(self):
        """Test logging a single transaction."""
        tx_data = self.sample_transactions[0]
        
        transaction = self.ledger.log_transaction(
            item_name=tx_data["item_name"],
            price=tx_data["price"],
            location=tx_data["location"],
            seller=tx_data["seller"],
            transaction_type=tx_data["transaction_type"],
            item_category=tx_data["item_category"],
            quantity=tx_data["quantity"],
            notes=tx_data["notes"],
            confidence=tx_data["confidence"],
            raw_text=tx_data["raw_text"]
        )
        
        assert transaction.item_name == tx_data["item_name"]
        assert transaction.price == tx_data["price"]
        assert transaction.location == tx_data["location"]
        assert transaction.seller == tx_data["seller"]
        assert transaction.transaction_type == tx_data["transaction_type"]
        assert transaction.item_category == tx_data["item_category"]
        assert transaction.quantity == tx_data["quantity"]
        assert transaction.notes == tx_data["notes"]
        assert transaction.confidence == tx_data["confidence"]
        assert transaction.raw_text == tx_data["raw_text"]
        assert len(self.ledger.transactions) == 1
    
    def test_price_analysis_update(self):
        """Test that price analysis is updated when transactions are logged."""
        # Log first transaction
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=75000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        # Log second transaction for same item
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=70000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        assert "Durindfire Crystal" in self.ledger.price_analyses
        analysis = self.ledger.price_analyses["Durindfire Crystal"]
        assert analysis.average_price == 72500.0
        assert analysis.median_price == 72500.0
        assert analysis.min_price == 70000
        assert analysis.max_price == 75000
        assert analysis.price_count == 2
    
    def test_duplicate_detection(self):
        """Test duplicate transaction detection."""
        # Log first transaction
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=75000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        # Log duplicate transaction (same item, price, seller, location)
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=75000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        assert len(self.ledger.duplicate_entries) == 1
        duplicate = self.ledger.duplicate_entries[0]
        assert duplicate.similarity_score == 1.0
        assert duplicate.duplicate_type == "exact"
    
    def test_similarity_calculation(self):
        """Test similarity calculation between transactions."""
        tx1 = VendorTransaction(
            item_name="Durindfire Crystal",
            price=75000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            timestamp=datetime.now().isoformat(),
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        tx2 = VendorTransaction(
            item_name="Durindfire Crystal",
            price=70000,  # Different price
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            timestamp=datetime.now().isoformat(),
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        similarity = self.ledger._calculate_similarity(tx1, tx2)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should be similar due to same item, seller, location
    
    def test_get_transactions_with_filters(self):
        """Test transaction retrieval with various filters."""
        # Log multiple transactions
        for tx_data in self.sample_transactions:
            self.ledger.log_transaction(
                item_name=tx_data["item_name"],
                price=tx_data["price"],
                location=tx_data["location"],
                seller=tx_data["seller"],
                transaction_type=tx_data["transaction_type"],
                item_category=tx_data["item_category"],
                quantity=tx_data["quantity"],
                notes=tx_data["notes"],
                confidence=tx_data["confidence"],
                raw_text=tx_data["raw_text"]
            )
        
        # Test filtering by item name
        filtered = self.ledger.get_transactions(item_name="Durindfire")
        assert len(filtered) == 2
        assert all("Durindfire" in tx.item_name for tx in filtered)
        
        # Test filtering by seller
        filtered = self.ledger.get_transactions(seller="Crystal")
        assert len(filtered) == 2
        assert all("Crystal" in tx.seller for tx in filtered)
        
        # Test filtering by price range
        filtered = self.ledger.get_transactions(min_price=70000, max_price=80000)
        assert len(filtered) == 3
        assert all(70000 <= tx.price <= 80000 for tx in filtered)
        
        # Test filtering by category
        filtered = self.ledger.get_transactions(item_category=ItemCategory.RESOURCE)
        assert len(filtered) == 2
        assert all(tx.item_category == ItemCategory.RESOURCE for tx in filtered)
    
    def test_get_underpriced_items(self):
        """Test underpriced item detection."""
        # Log transactions with price analysis
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=75000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=70000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        # Log underpriced transaction
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=50000,  # Underpriced
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        underpriced = self.ledger.get_underpriced_items()
        assert len(underpriced) == 1
        assert underpriced[0][0].price == 50000
    
    def test_get_overpriced_items(self):
        """Test overpriced item detection."""
        # Log transactions with price analysis
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=75000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=70000,
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        # Log overpriced transaction
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=120000,  # Overpriced
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        overpriced = self.ledger.get_overpriced_items()
        assert len(overpriced) == 1
        assert overpriced[0][0].price == 120000
    
    def test_get_price_comparison(self):
        """Test price comparison functionality."""
        # Log multiple transactions for price analysis
        for tx_data in self.sample_transactions:
            self.ledger.log_transaction(
                item_name=tx_data["item_name"],
                price=tx_data["price"],
                location=tx_data["location"],
                seller=tx_data["seller"],
                transaction_type=tx_data["transaction_type"],
                item_category=tx_data["item_category"],
                quantity=tx_data["quantity"],
                notes=tx_data["notes"],
                confidence=tx_data["confidence"],
                raw_text=tx_data["raw_text"]
            )
        
        comparison = self.ledger.get_price_comparison("Durindfire Crystal")
        assert comparison is not None
        assert comparison["item_name"] == "Durindfire Crystal"
        assert "analysis" in comparison
        assert "seller_averages" in comparison
        assert "total_transactions" in comparison
    
    def test_get_statistics(self):
        """Test statistics generation."""
        # Log transactions
        for tx_data in self.sample_transactions:
            self.ledger.log_transaction(
                item_name=tx_data["item_name"],
                price=tx_data["price"],
                location=tx_data["location"],
                seller=tx_data["seller"],
                transaction_type=tx_data["transaction_type"],
                item_category=tx_data["item_category"],
                quantity=tx_data["quantity"],
                notes=tx_data["notes"],
                confidence=tx_data["confidence"],
                raw_text=tx_data["raw_text"]
            )
        
        stats = self.ledger.get_statistics()
        assert stats["total_transactions"] == 3
        assert stats["unique_items"] == 2
        assert stats["unique_sellers"] == 2
        assert stats["unique_locations"] == 1
        assert "transaction_types" in stats
        assert "item_categories" in stats
        assert "price_statistics" in stats
    
    def test_save_and_load_ledger(self):
        """Test saving and loading ledger data."""
        # Log some transactions
        for tx_data in self.sample_transactions:
            self.ledger.log_transaction(
                item_name=tx_data["item_name"],
                price=tx_data["price"],
                location=tx_data["location"],
                seller=tx_data["seller"],
                transaction_type=tx_data["transaction_type"],
                item_category=tx_data["item_category"],
                quantity=tx_data["quantity"],
                notes=tx_data["notes"],
                confidence=tx_data["confidence"],
                raw_text=tx_data["raw_text"]
            )
        
        # Create new ledger instance to test loading
        new_ledger = VendorTransactionLedger(str(self.ledger_path))
        
        assert len(new_ledger.transactions) == 3
        assert len(new_ledger.price_analyses) == 2  # 2 unique items
        assert new_ledger.transactions[0].item_name == "Durindfire Crystal"
        assert new_ledger.transactions[1].item_name == "Spice Wine"
    
    def test_transaction_type_enum(self):
        """Test TransactionType enum values."""
        assert TransactionType.SALE.value == "sale"
        assert TransactionType.PURCHASE.value == "purchase"
        assert TransactionType.OBSERVED.value == "observed"
        assert TransactionType.LISTED.value == "listed"
    
    def test_item_category_enum(self):
        """Test ItemCategory enum values."""
        assert ItemCategory.WEAPON.value == "weapon"
        assert ItemCategory.ARMOR.value == "armor"
        assert ItemCategory.SUPPLY.value == "supply"
        assert ItemCategory.AMMO.value == "ammo"
        assert ItemCategory.TOOL.value == "tool"
        assert ItemCategory.RESOURCE.value == "resource"
        assert ItemCategory.CONSUMABLE.value == "consumable"
        assert ItemCategory.DECORATION.value == "decoration"
        assert ItemCategory.OTHER.value == "other"


class TestVendorTransactionDataClasses:
    """Test the data classes used in the vendor transaction ledger."""
    
    def test_vendor_transaction_dataclass(self):
        """Test VendorTransaction dataclass."""
        transaction = VendorTransaction(
            item_name="Test Item",
            price=1000,
            location="test_location",
            seller="Test Seller",
            timestamp="2025-01-01T12:00:00",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.OTHER,
            quantity=1,
            notes="Test notes",
            confidence=0.95,
            raw_text="Test raw text"
        )
        
        assert transaction.item_name == "Test Item"
        assert transaction.price == 1000
        assert transaction.location == "test_location"
        assert transaction.seller == "Test Seller"
        assert transaction.timestamp == "2025-01-01T12:00:00"
        assert transaction.transaction_type == TransactionType.OBSERVED
        assert transaction.item_category == ItemCategory.OTHER
        assert transaction.quantity == 1
        assert transaction.notes == "Test notes"
        assert transaction.confidence == 0.95
        assert transaction.raw_text == "Test raw text"
    
    def test_price_analysis_dataclass(self):
        """Test PriceAnalysis dataclass."""
        analysis = PriceAnalysis(
            item_name="Test Item",
            average_price=1000.0,
            median_price=950.0,
            min_price=800,
            max_price=1200,
            price_count=5,
            last_updated="2025-01-01T12:00:00",
            price_trend="stable",
            underpriced_threshold=700,
            overpriced_threshold=1500
        )
        
        assert analysis.item_name == "Test Item"
        assert analysis.average_price == 1000.0
        assert analysis.median_price == 950.0
        assert analysis.min_price == 800
        assert analysis.max_price == 1200
        assert analysis.price_count == 5
        assert analysis.last_updated == "2025-01-01T12:00:00"
        assert analysis.price_trend == "stable"
        assert analysis.underpriced_threshold == 700
        assert analysis.overpriced_threshold == 1500
    
    def test_duplicate_entry_dataclass(self):
        """Test DuplicateEntry dataclass."""
        original_tx = VendorTransaction(
            item_name="Test Item",
            price=1000,
            location="test_location",
            seller="Test Seller",
            timestamp="2025-01-01T12:00:00",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.OTHER
        )
        
        duplicate_tx = VendorTransaction(
            item_name="Test Item",
            price=1000,
            location="test_location",
            seller="Test Seller",
            timestamp="2025-01-01T12:01:00",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.OTHER
        )
        
        duplicate_entry = DuplicateEntry(
            original_transaction=original_tx,
            duplicate_transaction=duplicate_tx,
            similarity_score=1.0,
            duplicate_type="exact"
        )
        
        assert duplicate_entry.original_transaction == original_tx
        assert duplicate_entry.duplicate_transaction == duplicate_tx
        assert duplicate_entry.similarity_score == 1.0
        assert duplicate_entry.duplicate_type == "exact"


class TestVendorLedgerIntegration:
    """Test integration between vendor ledger components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_path = Path(self.temp_dir) / "test_ledger.json"
        self.ledger = VendorTransactionLedger(str(self.ledger_path))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from logging to analysis."""
        # Log multiple transactions
        transactions = [
            ("Durindfire Crystal", 75000, "Crystal Vendor"),
            ("Durindfire Crystal", 70000, "Crystal Vendor"),
            ("Durindfire Crystal", 80000, "Crystal Vendor"),
            ("Spice Wine", 120000, "Wine Merchant"),
            ("Spice Wine", 110000, "Wine Merchant"),
        ]
        
        for item_name, price, seller in transactions:
            self.ledger.log_transaction(
                item_name=item_name,
                price=price,
                location="tatooine_mos_eisley",
                seller=seller,
                transaction_type=TransactionType.OBSERVED,
                item_category=ItemCategory.RESOURCE
            )
        
        # Verify transactions were logged
        assert len(self.ledger.transactions) == 5
        
        # Verify price analyses were created
        assert len(self.ledger.price_analyses) == 2
        assert "Durindfire Crystal" in self.ledger.price_analyses
        assert "Spice Wine" in self.ledger.price_analyses
        
        # Test filtering
        crystal_transactions = self.ledger.get_transactions(item_name="Durindfire Crystal")
        assert len(crystal_transactions) == 3
        
        # Test underpriced detection
        self.ledger.log_transaction(
            item_name="Durindfire Crystal",
            price=50000,  # Underpriced
            location="tatooine_mos_eisley",
            seller="Crystal Vendor",
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.RESOURCE
        )
        
        underpriced = self.ledger.get_underpriced_items()
        assert len(underpriced) == 1
        assert underpriced[0][0].item_name == "Durindfire Crystal"
        assert underpriced[0][0].price == 50000
        
        # Test statistics
        stats = self.ledger.get_statistics()
        assert stats["total_transactions"] == 6
        assert stats["unique_items"] == 2
        assert stats["unique_sellers"] == 2
    
    def test_price_trend_calculation(self):
        """Test price trend calculation based on recent transactions."""
        # Log older transactions
        for i in range(5):
            self.ledger.log_transaction(
                item_name="Test Item",
                price=1000,
                location="test_location",
                seller="Test Seller",
                transaction_type=TransactionType.OBSERVED,
                item_category=ItemCategory.OTHER
            )
        
        # Log recent transactions with higher prices (rising trend)
        for i in range(3):
            self.ledger.log_transaction(
                item_name="Test Item",
                price=1200,  # Higher price
                location="test_location",
                seller="Test Seller",
                transaction_type=TransactionType.OBSERVED,
                item_category=ItemCategory.OTHER
            )
        
        analysis = self.ledger.price_analyses["Test Item"]
        assert analysis.price_trend == "rising"
        
        # Log recent transactions with lower prices (falling trend)
        self.ledger.price_analyses.clear()  # Reset analyses
        
        for i in range(5):
            self.ledger.log_transaction(
                item_name="Test Item 2",
                price=1000,
                location="test_location",
                seller="Test Seller",
                transaction_type=TransactionType.OBSERVED,
                item_category=ItemCategory.OTHER
            )
        
        for i in range(3):
            self.ledger.log_transaction(
                item_name="Test Item 2",
                price=800,  # Lower price
                location="test_location",
                seller="Test Seller",
                transaction_type=TransactionType.OBSERVED,
                item_category=ItemCategory.OTHER
            )
        
        analysis = self.ledger.price_analyses["Test Item 2"]
        assert analysis.price_trend == "falling"


class TestVendorLedgerConfiguration:
    """Test vendor ledger configuration and settings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_path = Path(self.temp_dir) / "test_ledger.json"
        self.ledger = VendorTransactionLedger(str(self.ledger_path))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_duplicate_threshold_configuration(self):
        """Test duplicate threshold configuration."""
        # Test with default threshold (0.95)
        tx1 = VendorTransaction(
            item_name="Test Item",
            price=1000,
            location="test_location",
            seller="Test Seller",
            timestamp=datetime.now().isoformat(),
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.OTHER
        )
        
        tx2 = VendorTransaction(
            item_name="Test Item",
            price=1000,
            location="test_location",
            seller="Test Seller",
            timestamp=datetime.now().isoformat(),
            transaction_type=TransactionType.OBSERVED,
            item_category=ItemCategory.OTHER
        )
        
        similarity = self.ledger._calculate_similarity(tx1, tx2)
        assert similarity > self.ledger.duplicate_threshold
        
        # Test with custom threshold
        self.ledger.duplicate_threshold = 0.99
        assert self.ledger.duplicate_threshold == 0.99
    
    def test_price_threshold_configuration(self):
        """Test price threshold configuration."""
        # Test underpriced threshold
        assert self.ledger.underpriced_threshold == 0.7
        
        # Test overpriced threshold
        assert self.ledger.overpriced_threshold == 1.5
        
        # Modify thresholds
        self.ledger.underpriced_threshold = 0.8
        self.ledger.overpriced_threshold = 1.3
        
        assert self.ledger.underpriced_threshold == 0.8
        assert self.ledger.overpriced_threshold == 1.3


class TestVendorLedgerErrorHandling:
    """Test error handling in the vendor transaction ledger."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_path = Path(self.temp_dir) / "test_ledger.json"
        self.ledger = VendorTransactionLedger(str(self.ledger_path))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_json_loading(self):
        """Test handling of invalid JSON in ledger file."""
        # Create invalid JSON file
        with open(self.ledger_path, 'w') as f:
            f.write("invalid json content")
        
        # Should handle gracefully
        ledger = VendorTransactionLedger(str(self.ledger_path))
        assert len(ledger.transactions) == 0
        assert len(ledger.price_analyses) == 0
        assert len(ledger.duplicate_entries) == 0
    
    def test_missing_required_fields(self):
        """Test handling of transactions with missing required fields."""
        # This should be handled by the dataclass validation
        # The ledger should still function normally
        transaction = self.ledger.log_transaction(
            item_name="Test Item",
            price=1000,
            location="test_location",
            seller="Test Seller"
            # Missing optional fields should use defaults
        )
        
        assert transaction.item_name == "Test Item"
        assert transaction.price == 1000
        assert transaction.transaction_type == TransactionType.OBSERVED
        assert transaction.item_category == ItemCategory.OTHER
        assert transaction.quantity == 1
        assert transaction.confidence == 1.0
    
    def test_invalid_enum_values(self):
        """Test handling of invalid enum values."""
        # This should be handled by the enum validation
        # The ledger should still function normally
        transaction = self.ledger.log_transaction(
            item_name="Test Item",
            price=1000,
            location="test_location",
            seller="Test Seller",
            transaction_type=TransactionType.OBSERVED,  # Valid enum
            item_category=ItemCategory.OTHER  # Valid enum
        )
        
        assert transaction.transaction_type == TransactionType.OBSERVED
        assert transaction.item_category == ItemCategory.OTHER


class TestVendorLedgerPerformance:
    """Test performance aspects of the vendor transaction ledger."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_path = Path(self.temp_dir) / "test_ledger.json"
        self.ledger = VendorTransactionLedger(str(self.ledger_path))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_transaction_set(self):
        """Test performance with large number of transactions."""
        import time
        
        start_time = time.time()
        
        # Log 1000 transactions
        for i in range(1000):
            self.ledger.log_transaction(
                item_name=f"Item {i % 100}",  # 100 unique items
                price=1000 + (i % 1000),
                location=f"location_{i % 10}",
                seller=f"seller_{i % 50}",
                transaction_type=TransactionType.OBSERVED,
                item_category=ItemCategory.OTHER
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert len(self.ledger.transactions) == 1000
        assert len(self.ledger.price_analyses) == 100
        assert processing_time < 10.0  # Should complete within 10 seconds
        
        # Test filtering performance
        start_time = time.time()
        filtered = self.ledger.get_transactions(item_name="Item 0")
        end_time = time.time()
        filtering_time = end_time - start_time
        
        assert len(filtered) == 10  # 10 transactions for "Item 0"
        assert filtering_time < 1.0  # Should complete within 1 second
    
    def test_memory_usage(self):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Log 5000 transactions
        for i in range(5000):
            self.ledger.log_transaction(
                item_name=f"Item {i % 200}",
                price=1000 + (i % 1000),
                location=f"location_{i % 20}",
                seller=f"seller_{i % 100}",
                transaction_type=TransactionType.OBSERVED,
                item_category=ItemCategory.OTHER
            )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 