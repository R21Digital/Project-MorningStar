"""Track average sale prices to adjust pricing behavior."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.logging_utils import log_event


@dataclass
class PriceEntry:
    """Represents a price entry for an item."""
    item_name: str
    price: int
    timestamp: str
    source: str  # "sale", "purchase", "observed"


@dataclass
class ItemPriceStats:
    """Price statistics for an item."""
    item_name: str
    average_price: float
    min_price: int
    max_price: int
    total_sales: int
    last_updated: str


class PriceTracker:
    """Track and analyze item prices for intelligent pricing."""
    
    def __init__(self, price_history_file: str = "data/bazaar/price_history.json"):
        """Initialize the price tracker.
        
        Parameters
        ----------
        price_history_file : str
            Path to price history JSON file
        """
        self.price_history_file = Path(price_history_file)
        self.price_data = self._load_price_data()
        self.min_sales_for_average = 3
        
        # Ensure directory exists
        self.price_history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_price_data(self) -> Dict[str, Any]:
        """Load price data from file."""
        if self.price_history_file.exists():
            try:
                with self.price_history_file.open("r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, IOError) as e:
                log_event(f"[PRICE] Error loading price data: {e}")
        
        # Return default structure
        return {
            "last_updated": datetime.now().isoformat(),
            "items": {},
            "statistics": {
                "total_sales": 0,
                "total_revenue": 0,
                "average_sale_price": 0
            }
        }
    
    def _save_price_data(self) -> None:
        """Save price data to file."""
        try:
            self.price_data["last_updated"] = datetime.now().isoformat()
            with self.price_history_file.open("w", encoding="utf-8") as fh:
                json.dump(self.price_data, fh, indent=2)
        except IOError as e:
            log_event(f"[PRICE] Error saving price data: {e}")
    
    def add_sale(self, item_name: str, price: int, source: str = "sale") -> None:
        """Record a sale transaction.
        
        Parameters
        ----------
        item_name : str
            Name of the item sold
        price : int
            Sale price in credits
        source : str
            Source of the price data
        """
        timestamp = datetime.now().isoformat()
        
        # Add to items list
        if item_name not in self.price_data["items"]:
            self.price_data["items"][item_name] = {
                "prices": [],
                "statistics": {
                    "average_price": 0,
                    "min_price": price,
                    "max_price": price,
                    "total_sales": 0,
                    "last_updated": timestamp
                }
            }
        
        # Add price entry
        price_entry = {
            "price": price,
            "timestamp": timestamp,
            "source": source
        }
        self.price_data["items"][item_name]["prices"].append(price_entry)
        
        # Update statistics
        self._update_item_statistics(item_name)
        self._update_global_statistics()
        
        # Save data
        self._save_price_data()
        
        log_event(f"[PRICE] Recorded sale: {item_name} for {price:,} credits")
    
    def _update_item_statistics(self, item_name: str) -> None:
        """Update statistics for a specific item."""
        item_data = self.price_data["items"][item_name]
        prices = [entry["price"] for entry in item_data["prices"]]
        
        if prices:
            item_data["statistics"]["average_price"] = sum(prices) / len(prices)
            item_data["statistics"]["min_price"] = min(prices)
            item_data["statistics"]["max_price"] = max(prices)
            item_data["statistics"]["total_sales"] = len(prices)
            item_data["statistics"]["last_updated"] = datetime.now().isoformat()
    
    def _update_global_statistics(self) -> None:
        """Update global price statistics."""
        total_sales = 0
        total_revenue = 0
        
        for item_name, item_data in self.price_data["items"].items():
            for price_entry in item_data["prices"]:
                if price_entry["source"] == "sale":
                    total_sales += 1
                    total_revenue += price_entry["price"]
        
        self.price_data["statistics"]["total_sales"] = total_sales
        self.price_data["statistics"]["total_revenue"] = total_revenue
        
        if total_sales > 0:
            self.price_data["statistics"]["average_sale_price"] = total_revenue / total_sales
    
    def get_item_price_stats(self, item_name: str) -> Optional[ItemPriceStats]:
        """Get price statistics for an item.
        
        Parameters
        ----------
        item_name : str
            Name of the item
            
        Returns
        -------
        ItemPriceStats or None
            Price statistics for the item
        """
        if item_name not in self.price_data["items"]:
            return None
        
        item_data = self.price_data["items"][item_name]
        stats = item_data["statistics"]
        
        return ItemPriceStats(
            item_name=item_name,
            average_price=stats["average_price"],
            min_price=stats["min_price"],
            max_price=stats["max_price"],
            total_sales=stats["total_sales"],
            last_updated=stats["last_updated"]
        )
    
    def get_recommended_price(self, item_name: str, base_price: int = None) -> int:
        """Get recommended selling price for an item.
        
        Parameters
        ----------
        item_name : str
            Name of the item
        base_price : int, optional
            Base price to use if no history exists
            
        Returns
        -------
        int
            Recommended selling price
        """
        stats = self.get_item_price_stats(item_name)
        
        if stats and stats.total_sales >= self.min_sales_for_average:
            # Use historical average with slight markup
            recommended = int(stats.average_price * 1.1)  # 10% markup
            log_event(f"[PRICE] Recommended price for {item_name}: {recommended:,} (based on {stats.total_sales} sales)")
            return recommended
        elif base_price:
            # Use provided base price
            log_event(f"[PRICE] Using base price for {item_name}: {base_price:,}")
            return base_price
        else:
            # Default price
            default_price = 1000
            log_event(f"[PRICE] Using default price for {item_name}: {default_price:,}")
            return default_price
    
    def should_sell_item(self, item_name: str, current_price: int, 
                        min_value_threshold: int = 5000) -> bool:
        """Determine if an item should be sold based on price and threshold.
        
        Parameters
        ----------
        item_name : str
            Name of the item
        current_price : int
            Current vendor price for the item
        min_value_threshold : int
            Minimum value threshold for selling
            
        Returns
        -------
        bool
            True if item should be sold
        """
        # Check minimum threshold
        if current_price < min_value_threshold:
            log_event(f"[PRICE] {item_name} below threshold ({current_price:,} < {min_value_threshold:,})")
            return False
        
        # Check against historical prices
        stats = self.get_item_price_stats(item_name)
        if stats and stats.total_sales >= self.min_sales_for_average:
            if current_price < stats.average_price * 0.8:  # 20% below average
                log_event(f"[PRICE] {item_name} price too low compared to average")
                return False
        
        log_event(f"[PRICE] {item_name} approved for sale at {current_price:,}")
        return True
    
    def get_price_trend(self, item_name: str, days: int = 7) -> Optional[float]:
        """Get price trend for an item over the specified period.
        
        Parameters
        ----------
        item_name : str
            Name of the item
        days : int
            Number of days to analyze
            
        Returns
        -------
        float or None
            Price trend (positive = increasing, negative = decreasing)
        """
        if item_name not in self.price_data["items"]:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_prices = []
        
        for price_entry in self.price_data["items"][item_name]["prices"]:
            entry_date = datetime.fromisoformat(price_entry["timestamp"])
            if entry_date >= cutoff_date:
                recent_prices.append(price_entry["price"])
        
        if len(recent_prices) < 2:
            return None
        
        # Calculate trend (simple linear regression)
        prices = sorted(recent_prices)
        if len(prices) >= 2:
            trend = (prices[-1] - prices[0]) / len(prices)
            return trend
        
        return None
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global price statistics.
        
        Returns
        -------
        Dict[str, Any]
            Global statistics
        """
        return self.price_data["statistics"].copy()
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Remove price data older than specified days.
        
        Parameters
        ----------
        days : int
            Number of days to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        items_to_remove = []
        
        for item_name, item_data in self.price_data["items"].items():
            # Filter out old price entries
            item_data["prices"] = [
                entry for entry in item_data["prices"]
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
            ]
            
            # Remove item if no prices remain
            if not item_data["prices"]:
                items_to_remove.append(item_name)
            else:
                # Update statistics
                self._update_item_statistics(item_name)
        
        # Remove empty items
        for item_name in items_to_remove:
            del self.price_data["items"][item_name]
        
        # Update global statistics
        self._update_global_statistics()
        self._save_price_data()
        
        log_event(f"[PRICE] Cleaned up data older than {days} days") 