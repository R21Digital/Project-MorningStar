"""Main vendor manager for intelligent bazaar/vendor operations."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import pyautogui
import cv2
import numpy as np

from .bazaar_detector import BazaarDetector, VendorInterface
from .price_tracker import PriceTracker
from src.vision.ocr import screen_text, capture_screen
from utils.logging_utils import log_event


@dataclass
class InventoryItem:
    """Represents an item in inventory."""
    name: str
    quantity: int
    estimated_value: int
    should_sell: bool


@dataclass
class VendorTransaction:
    """Represents a vendor transaction."""
    item_name: str
    quantity: int
    price: int
    transaction_type: str  # "sale", "purchase"
    timestamp: str


class VendorManager:
    """Main vendor manager for intelligent bazaar operations."""
    
    def __init__(self, config_path: str = "config/bazaar_config.json"):
        """Initialize the vendor manager.
        
        Parameters
        ----------
        config_path : str
            Path to bazaar configuration file
        """
        self.config = self._load_config(config_path)
        self.detector = BazaarDetector(config_path)
        self.price_tracker = PriceTracker()
        
        # Configuration
        self.auto_sell_junk = self.config.get("auto_sell_junk", True)
        self.loot_min_value_threshold = self.config.get("loot_min_value_threshold", 5000)
        self.excluded_items = set(self.config.get("excluded_items", []))
        
        # Transaction tracking
        self.transactions: List[VendorTransaction] = []
        self.session_revenue = 0
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load bazaar configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}
    
    def detect_and_interact_with_vendor(self) -> bool:
        """Detect vendor terminal and interact with it.
        
        Returns
        -------
        bool
            True if vendor interaction was successful
        """
        log_event("[VENDOR] Scanning for vendor terminals...")
        
        # Detect vendor terminals
        terminals = self.detector.detect_vendor_terminals()
        if not terminals:
            log_event("[VENDOR] No vendor terminals detected")
            return False
        
        # Click on the first detected terminal
        terminal = terminals[0]
        center_x = terminal.x + terminal.width // 2
        center_y = terminal.y + terminal.height // 2
        
        log_event(f"[VENDOR] Interacting with {terminal.terminal_type} terminal")
        pyautogui.click(center_x, center_y)
        time.sleep(1)  # Wait for interface to load
        
        # Check if vendor interface is now visible
        if self.detector.is_vendor_screen():
            log_event("[VENDOR] Successfully opened vendor interface")
            return True
        else:
            log_event("[VENDOR] Failed to open vendor interface")
            return False
    
    def scan_inventory_for_sale(self) -> List[InventoryItem]:
        """Scan inventory for items that should be sold.
        
        Returns
        -------
        List[InventoryItem]
            List of items to sell
        """
        log_event("[VENDOR] Scanning inventory for saleable items...")
        
        # This is a simplified implementation
        # In practice, you'd use OCR to read the inventory list
        items_to_sell = []
        
        # Simulate inventory scan
        # In real implementation, you'd extract this from OCR
        inventory_text = screen_text()
        
        # Parse inventory items (simplified)
        items = self._parse_inventory_text(inventory_text)
        
        for item in items:
            if self._should_sell_item(item):
                items_to_sell.append(item)
        
        log_event(f"[VENDOR] Found {len(items_to_sell)} items to sell")
        return items_to_sell
    
    def _parse_inventory_text(self, text: str) -> List[InventoryItem]:
        """Parse inventory text to extract items.
        
        Parameters
        ----------
        text : str
            OCR text from inventory
            
        Returns
        -------
        List[InventoryItem]
            Parsed inventory items
        """
        items = []
        
        # Simplified parsing - in practice you'd use more sophisticated OCR
        lines = text.split('\n')
        for line in lines:
            # Look for item patterns (item name + quantity + value)
            # This is a simplified regex - adjust based on actual game UI
            match = re.search(r'(\w+(?:\s+\w+)*)\s+(\d+)\s+(\d+)', line)
            if match:
                name = match.group(1).strip()
                quantity = int(match.group(2))
                value = int(match.group(3))
                
                item = InventoryItem(
                    name=name,
                    quantity=quantity,
                    estimated_value=value,
                    should_sell=False  # Will be determined later
                )
                items.append(item)
        
        return items
    
    def _should_sell_item(self, item: InventoryItem) -> bool:
        """Determine if an item should be sold.
        
        Parameters
        ----------
        item : InventoryItem
            Item to evaluate
            
        Returns
        -------
        bool
            True if item should be sold
        """
        # Check if item is excluded
        if item.name in self.excluded_items:
            log_event(f"[VENDOR] {item.name} is in excluded list")
            return False
        
        # Check minimum value threshold
        if item.estimated_value < self.loot_min_value_threshold:
            log_event(f"[VENDOR] {item.name} below threshold ({item.estimated_value:,} < {self.loot_min_value_threshold:,})")
            return False
        
        # Check with price tracker
        if self.price_tracker.should_sell_item(item.name, item.estimated_value, self.loot_min_value_threshold):
            item.should_sell = True
            return True
        
        return False
    
    def sell_items(self, items: List[InventoryItem]) -> List[VendorTransaction]:
        """Sell items to vendor.
        
        Parameters
        ----------
        items : List[InventoryItem]
            Items to sell
            
        Returns
        -------
        List[VendorTransaction]
            List of completed transactions
        """
        if not items:
            log_event("[VENDOR] No items to sell")
            return []
        
        transactions = []
        interface = self.detector.detect_vendor_interface()
        
        if not interface or not interface.sell_button:
            log_event("[VENDOR] Could not detect sell button")
            return []
        
        # Click sell button
        sell_x, sell_y = interface.sell_button
        pyautogui.click(sell_x, sell_y)
        time.sleep(0.5)
        
        for item in items:
            if self._sell_single_item(item, interface):
                transaction = VendorTransaction(
                    item_name=item.name,
                    quantity=item.quantity,
                    price=item.estimated_value,
                    transaction_type="sale",
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                transactions.append(transaction)
                
                # Record in price tracker
                self.price_tracker.add_sale(item.name, item.estimated_value)
                
                # Update session revenue
                self.session_revenue += item.estimated_value * item.quantity
        
        log_event(f"[VENDOR] Sold {len(transactions)} items for {self.session_revenue:,} credits")
        return transactions
    
    def _sell_single_item(self, item: InventoryItem, interface: VendorInterface) -> bool:
        """Sell a single item.
        
        Parameters
        ----------
        item : InventoryItem
            Item to sell
        interface : VendorInterface
            Vendor interface elements
            
        Returns
        -------
        bool
            True if sale was successful
        """
        try:
            # This is a simplified implementation
            # In practice, you'd need to:
            # 1. Find the item in the inventory list
            # 2. Click on it to select
            # 3. Click sell button
            # 4. Confirm sale
            
            log_event(f"[VENDOR] Selling {item.name} x{item.quantity} for {item.estimated_value:,} credits")
            
            # Simulate item selection and sale
            # In real implementation, you'd use OCR to find item position
            if interface.inventory_list:
                # Click in inventory area (simplified)
                inv_x, inv_y, inv_w, inv_h = interface.inventory_list
                pyautogui.click(inv_x + inv_w // 2, inv_y + inv_h // 2)
                time.sleep(0.2)
            
            # Click sell button again
            if interface.sell_button:
                sell_x, sell_y = interface.sell_button
                pyautogui.click(sell_x, sell_y)
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            log_event(f"[VENDOR] Error selling {item.name}: {e}")
            return False
    
    def buy_items(self, target_items: List[str], max_spend: int = 50000) -> List[VendorTransaction]:
        """Buy items from vendor.
        
        Parameters
        ----------
        target_items : List[str]
            List of item names to buy
        max_spend : int
            Maximum credits to spend
            
        Returns
        -------
        List[VendorTransaction]
            List of completed transactions
        """
        if not target_items:
            log_event("[VENDOR] No target items specified for purchase")
            return []
        
        transactions = []
        interface = self.detector.detect_vendor_interface()
        
        if not interface or not interface.buy_button:
            log_event("[VENDOR] Could not detect buy button")
            return []
        
        # Click buy button
        buy_x, buy_y = interface.buy_button
        pyautogui.click(buy_x, buy_y)
        time.sleep(0.5)
        
        total_spent = 0
        
        for item_name in target_items:
            if total_spent >= max_spend:
                log_event(f"[VENDOR] Reached spending limit ({max_spend:,} credits)")
                break
            
            # Get item price from vendor
            item_price = self._get_vendor_price(item_name)
            if item_price is None:
                continue
            
            if total_spent + item_price <= max_spend:
                if self._buy_single_item(item_name, item_price, interface):
                    transaction = VendorTransaction(
                        item_name=item_name,
                        quantity=1,
                        price=item_price,
                        transaction_type="purchase",
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    )
                    transactions.append(transaction)
                    total_spent += item_price
                    
                    # Record purchase in price tracker
                    self.price_tracker.add_sale(item_name, item_price, "purchase")
        
        log_event(f"[VENDOR] Bought {len(transactions)} items for {total_spent:,} credits")
        return transactions
    
    def _get_vendor_price(self, item_name: str) -> Optional[int]:
        """Get vendor price for an item.
        
        Parameters
        ----------
        item_name : str
            Name of the item
            
        Returns
        -------
        int or None
            Vendor price, or None if not found
        """
        # This is a simplified implementation
        # In practice, you'd use OCR to read the vendor's price list
        
        # For now, return a default price
        default_prices = {
            "health pack": 100,
            "stimpack": 50,
            "energy cell": 25,
            "repair kit": 200
        }
        
        return default_prices.get(item_name.lower(), 100)
    
    def _buy_single_item(self, item_name: str, price: int, interface: VendorInterface) -> bool:
        """Buy a single item.
        
        Parameters
        ----------
        item_name : str
            Name of item to buy
        price : int
            Price of the item
        interface : VendorInterface
            Vendor interface elements
            
        Returns
        -------
        bool
            True if purchase was successful
        """
        try:
            log_event(f"[VENDOR] Buying {item_name} for {price:,} credits")
            
            # This is a simplified implementation
            # In practice, you'd need to:
            # 1. Find the item in the vendor's inventory
            # 2. Click on it to select
            # 3. Click buy button
            # 4. Confirm purchase
            
            # Simulate purchase
            time.sleep(0.2)
            
            return True
            
        except Exception as e:
            log_event(f"[VENDOR] Error buying {item_name}: {e}")
            return False
    
    def auto_sell_junk(self) -> List[VendorTransaction]:
        """Automatically sell junk items.
        
        Returns
        -------
        List[VendorTransaction]
            List of completed transactions
        """
        if not self.auto_sell_junk:
            log_event("[VENDOR] Auto-sell junk is disabled")
            return []
        
        log_event("[VENDOR] Starting auto-sell junk process...")
        
        # Detect vendor
        if not self.detect_and_interact_with_vendor():
            return []
        
        # Scan inventory
        items_to_sell = self.scan_inventory_for_sale()
        
        # Sell items
        transactions = self.sell_items(items_to_sell)
        
        return transactions
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary.
        
        Returns
        -------
        Dict[str, Any]
            Session summary
        """
        return {
            "total_transactions": len(self.transactions),
            "session_revenue": self.session_revenue,
            "price_stats": self.price_tracker.get_global_statistics()
        } 