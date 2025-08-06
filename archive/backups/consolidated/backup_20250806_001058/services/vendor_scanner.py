"""Vendor Scanner Service for MS11.

This module provides comprehensive vendor scanning and bazaar search functionality:
- Track nearby vendors and bazaar listings via player scan or parser
- Cache vendor name, item type, quantity, and price
- Associate planetary/coordinate location with vendor
- API endpoint for Crafting Mode to search for needed items/resources
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from android_ms11.utils.logging_utils import log_event


@dataclass
class VendorItem:
    """Represents an item available at a vendor."""
    name: str
    quantity: int
    price: int
    item_type: str
    last_updated: str


@dataclass
class VendorLocation:
    """Represents a vendor location."""
    vendor_name: str
    planet: str
    city: str
    coordinates: Tuple[int, int]
    vendor_type: str  # "vendor", "bazaar", "shop"
    last_scan: str
    items: List[VendorItem]


@dataclass
class BazaarListing:
    """Represents a bazaar listing."""
    item_name: str
    quantity: int
    price: int
    seller_name: str
    listing_id: str
    expires_at: str
    location: str


class VendorScanner:
    """Main vendor scanner service for tracking vendors and bazaar listings."""

    def __init__(self, cache_dir: str = "data/vendors"):
        """Initialize the vendor scanner.

        Parameters
        ----------
        cache_dir : str
            Directory to store vendor cache data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.vendors_cache_file = self.cache_dir / "vendors_cache.json"
        self.bazaar_cache_file = self.cache_dir / "bazaar_cache.json"
        
        # Load existing cache
        self.vendors_cache: Dict[str, VendorLocation] = {}
        self.bazaar_cache: Dict[str, BazaarListing] = {}
        self.scan_history: List[Dict[str, Any]] = []
        
        self._load_cache()
        
        # Configuration
        self.cache_expiry_hours = 24  # Cache expires after 24 hours
        self.max_cache_size = 1000    # Maximum number of cached vendors
        self.scan_radius = 100        # Scan radius in game units
        
    def _load_cache(self) -> None:
        """Load vendor and bazaar cache from disk."""
        try:
            if self.vendors_cache_file.exists():
                with self.vendors_cache_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vendors_cache = {}
                    for k, v in data.items():
                        # Convert items back to VendorItem dataclasses
                        if "items" in v:
                            items = []
                            for item_data in v["items"]:
                                items.append(VendorItem(**item_data))
                            v["items"] = items
                        self.vendors_cache[k] = VendorLocation(**v)
                log_event(f"[VENDOR_SCANNER] Loaded {len(self.vendors_cache)} cached vendors")
            
            if self.bazaar_cache_file.exists():
                with self.bazaar_cache_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.bazaar_cache = {
                        k: BazaarListing(**v) for k, v in data.items()
                    }
                log_event(f"[VENDOR_SCANNER] Loaded {len(self.bazaar_cache)} cached bazaar listings")
                
        except Exception as e:
            log_event(f"[VENDOR_SCANNER] Error loading cache: {e}")
    
    def _save_cache(self) -> None:
        """Save vendor and bazaar cache to disk."""
        try:
            # Convert dataclasses to dicts for JSON serialization
            vendors_data = {
                k: asdict(v) for k, v in self.vendors_cache.items()
            }
            bazaar_data = {
                k: asdict(v) for k, v in self.bazaar_cache.items()
            }
            
            with self.vendors_cache_file.open("w", encoding="utf-8") as f:
                json.dump(vendors_data, f, indent=2)
            
            with self.bazaar_cache_file.open("w", encoding="utf-8") as f:
                json.dump(bazaar_data, f, indent=2)
                
            log_event(f"[VENDOR_SCANNER] Saved cache: {len(self.vendors_cache)} vendors, {len(self.bazaar_cache)} bazaar listings")
            
        except Exception as e:
            log_event(f"[VENDOR_SCANNER] Error saving cache: {e}")
    
    def scan_nearby_vendors(self, player_location: Tuple[str, str, Tuple[int, int]]) -> List[VendorLocation]:
        """Scan for nearby vendors at the player's location.

        Parameters
        ----------
        player_location : tuple
            (planet, city, (x, y)) coordinates of the player

        Returns
        -------
        List[VendorLocation]
            List of detected vendors
        """
        planet, city, coords = player_location
        current_time = datetime.now().isoformat()
        
        log_event(f"[VENDOR_SCANNER] Scanning for vendors at {city}, {planet} ({coords})")
        
        # Simulate vendor detection (in real implementation, this would use OCR/vision)
        detected_vendors = self._simulate_vendor_detection(planet, city, coords)
        
        # Update cache with detected vendors
        for vendor in detected_vendors:
            vendor_id = f"{vendor.vendor_name}_{planet}_{city}"
            self.vendors_cache[vendor_id] = vendor
        
        # Clean up expired cache entries
        self._cleanup_expired_cache()
        
        # Save updated cache
        self._save_cache()
        
        # Record scan
        scan_record = {
            "timestamp": current_time,
            "location": player_location,
            "vendors_detected": len(detected_vendors),
            "cache_size": len(self.vendors_cache)
        }
        self.scan_history.append(scan_record)
        
        return detected_vendors
    
    def _simulate_vendor_detection(self, planet: str, city: str, coords: Tuple[int, int]) -> List[VendorLocation]:
        """Simulate vendor detection (placeholder for OCR/vision implementation)."""
        # This would be replaced with actual OCR/vision detection
        # For now, return simulated vendors based on location
        
        vendors = []
        current_time = datetime.now().isoformat()
        
        # Simulate different vendor types based on city
        if city.lower() in ["mos_eisley", "coronet", "theed"]:
            # Major cities have multiple vendor types
            vendor_types = [
                ("General Store", "vendor", ["food", "drinks", "basic_supplies"]),
                ("Weapon Shop", "vendor", ["weapons", "ammo", "armor"]),
                ("Medical Supply", "vendor", ["medicine", "stim_packs", "bandages"]),
                ("Bazaar Terminal", "bazaar", ["various"])
            ]
        else:
            # Smaller cities have basic vendors
            vendor_types = [
                ("Local Vendor", "vendor", ["basic_supplies"]),
                ("Bazaar Terminal", "bazaar", ["various"])
            ]
        
        for vendor_name, vendor_type, item_types in vendor_types:
            # Generate vendor location near player
            vendor_x = coords[0] + (hash(vendor_name) % 200 - 100)
            vendor_y = coords[1] + (hash(vendor_name) % 200 - 100)
            
            # Generate sample items
            items = []
            for item_type in item_types:
                if item_type == "various":
                    # Bazaar has various items
                    sample_items = [
                        ("Durindfire", 10, 5000, "drink"),
                        ("Spice Wine", 5, 3000, "drink"),
                        ("Bantha Steak", 20, 1000, "food"),
                        ("Stimpack", 15, 2000, "medicine")
                    ]
                elif item_type == "weapons":
                    sample_items = [
                        ("Rifle", 3, 15000, "weapon"),
                        ("Pistol", 5, 8000, "weapon"),
                        ("Ammo Pack", 50, 500, "ammo")
                    ]
                elif item_type == "medicine":
                    sample_items = [
                        ("Stimpack", 20, 2000, "medicine"),
                        ("Bandages", 30, 500, "medicine"),
                        ("Antidote", 10, 1500, "medicine")
                    ]
                else:
                    sample_items = [
                        ("Basic Supply", 25, 100, "supply"),
                        ("Local Item", 15, 200, "supply")
                    ]
                
                for name, qty, price, item_type in sample_items:
                    items.append(VendorItem(
                        name=name,
                        quantity=qty,
                        price=price,
                        item_type=item_type,
                        last_updated=current_time
                    ))
            
            vendor = VendorLocation(
                vendor_name=vendor_name,
                planet=planet,
                city=city,
                coordinates=(vendor_x, vendor_y),
                vendor_type=vendor_type,
                last_scan=current_time,
                items=items
            )
            vendors.append(vendor)
        
        return vendors
    
    def scan_bazaar_listings(self, search_terms: List[str] = None) -> List[BazaarListing]:
        """Scan bazaar for listings matching search terms.

        Parameters
        ----------
        search_terms : List[str], optional
            Terms to search for. If None, scans all listings.

        Returns
        -------
        List[BazaarListing]
            List of matching bazaar listings
        """
        current_time = datetime.now().isoformat()
        
        log_event(f"[VENDOR_SCANNER] Scanning bazaar listings for: {search_terms or 'all items'}")
        
        # Simulate bazaar scanning (in real implementation, this would parse bazaar interface)
        detected_listings = self._simulate_bazaar_scanning(search_terms)
        
        # Update cache with detected listings
        for listing in detected_listings:
            self.bazaar_cache[listing.listing_id] = listing
        
        # Clean up expired cache entries
        self._cleanup_expired_cache()
        
        # Save updated cache
        self._save_cache()
        
        return detected_listings
    
    def _simulate_bazaar_scanning(self, search_terms: List[str] = None) -> List[BazaarListing]:
        """Simulate bazaar scanning (placeholder for actual bazaar parsing)."""
        # This would be replaced with actual bazaar interface parsing
        # For now, return simulated listings
        
        listings = []
        current_time = datetime.now().isoformat()
        
        # Sample bazaar items
        sample_items = [
            ("Durindfire", 50, 4500, "Corellian_Trader"),
            ("Spice Wine", 25, 2800, "Naboo_Merchant"),
            ("Bantha Steak", 100, 950, "Tatooine_Farmer"),
            ("Stimpack", 30, 1800, "Medical_Supply_Co"),
            ("Rifle", 5, 14000, "Weapon_Master"),
            ("Pistol", 8, 7500, "Arms_Dealer"),
            ("Ammo Pack", 200, 450, "Munitions_Supply"),
            ("Bandages", 75, 450, "Medical_Supply_Co"),
            ("Antidote", 20, 1400, "Medical_Supply_Co"),
            ("Corellian Brandy", 15, 3500, "Corellian_Trader")
        ]
        
        for item_name, qty, price, seller in sample_items:
            # Filter by search terms if provided
            if search_terms:
                if not any(term.lower() in item_name.lower() for term in search_terms):
                    continue
            
            # Generate listing ID
            listing_id = f"bazaar_{hash(item_name + seller) % 10000:04d}"
            
            # Set expiration (24 hours from now)
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
            
            listing = BazaarListing(
                item_name=item_name,
                quantity=qty,
                price=price,
                seller_name=seller,
                listing_id=listing_id,
                expires_at=expires_at,
                location="Various"
            )
            listings.append(listing)
        
        return listings
    
    def search_for_items(self, item_names: List[str], max_price: int = None, 
                        vendor_types: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search for items across vendors and bazaar listings.

        Parameters
        ----------
        item_names : List[str]
            Names of items to search for
        max_price : int, optional
            Maximum price to consider
        vendor_types : List[str], optional
            Types of vendors to search ("vendor", "bazaar", "shop")

        Returns
        -------
        Dict[str, List[Dict[str, Any]]]
            Search results organized by item name
        """
        log_event(f"[VENDOR_SCANNER] Searching for items: {item_names}")
        
        results = {item_name: [] for item_name in item_names}
        
        # Search in vendor cache
        for vendor_id, vendor in self.vendors_cache.items():
            if vendor_types and vendor.vendor_type not in vendor_types:
                continue
                
            for item in vendor.items:
                if item.name.lower() in [name.lower() for name in item_names]:
                    if max_price and item.price > max_price:
                        continue
                        
                    result = {
                        "source": "vendor",
                        "vendor_name": vendor.vendor_name,
                        "location": f"{vendor.city}, {vendor.planet}",
                        "coordinates": vendor.coordinates,
                        "quantity": item.quantity,
                        "price": item.price,
                        "item_type": item.item_type,
                        "last_updated": item.last_updated
                    }
                    results[item.name].append(result)
        
        # Search in bazaar cache
        for listing_id, listing in self.bazaar_cache.items():
            if listing.item_name.lower() in [name.lower() for name in item_names]:
                if max_price and listing.price > max_price:
                    continue
                    
                result = {
                    "source": "bazaar",
                    "seller_name": listing.seller_name,
                    "location": listing.location,
                    "quantity": listing.quantity,
                    "price": listing.price,
                    "listing_id": listing.listing_id,
                    "expires_at": listing.expires_at
                }
                results[listing.item_name].append(result)
        
        # Remove empty results
        results = {k: v for k, v in results.items() if v}
        
        log_event(f"[VENDOR_SCANNER] Found {sum(len(v) for v in results.values())} results")
        return results
    
    def get_vendor_by_location(self, planet: str, city: str) -> List[VendorLocation]:
        """Get all vendors at a specific location.

        Parameters
        ----------
        planet : str
            Planet name
        city : str
            City name

        Returns
        -------
        List[VendorLocation]
            List of vendors at the location
        """
        vendors = []
        for vendor_id, vendor in self.vendors_cache.items():
            if vendor.planet.lower() == planet.lower() and vendor.city.lower() == city.lower():
                vendors.append(vendor)
        
        return vendors
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the vendor cache.

        Returns
        -------
        Dict[str, Any]
            Cache statistics
        """
        total_items = sum(len(vendor.items) for vendor in self.vendors_cache.values())
        
        # Count items by type
        item_types = {}
        for vendor in self.vendors_cache.values():
            for item in vendor.items:
                item_types[item.item_type] = item_types.get(item.item_type, 0) + 1
        
        # Count vendors by type
        vendor_types = {}
        for vendor in self.vendors_cache.values():
            vendor_types[vendor.vendor_type] = vendor_types.get(vendor.vendor_type, 0) + 1
        
        return {
            "total_vendors": len(self.vendors_cache),
            "total_bazaar_listings": len(self.bazaar_cache),
            "total_items": total_items,
            "item_types": item_types,
            "vendor_types": vendor_types,
            "scan_history_count": len(self.scan_history),
            "cache_size_mb": self._get_cache_size_mb()
        }
    
    def _cleanup_expired_cache(self) -> None:
        """Remove expired cache entries."""
        current_time = datetime.now()
        expired_vendors = []
        expired_listings = []
        
        # Check vendor cache expiry
        for vendor_id, vendor in self.vendors_cache.items():
            last_scan = datetime.fromisoformat(vendor.last_scan)
            if current_time - last_scan > timedelta(hours=self.cache_expiry_hours):
                expired_vendors.append(vendor_id)
        
        # Check bazaar cache expiry
        for listing_id, listing in self.bazaar_cache.items():
            expires_at = datetime.fromisoformat(listing.expires_at)
            if current_time > expires_at:
                expired_listings.append(listing_id)
        
        # Remove expired entries
        for vendor_id in expired_vendors:
            del self.vendors_cache[vendor_id]
        
        for listing_id in expired_listings:
            del self.bazaar_cache[listing_id]
        
        if expired_vendors or expired_listings:
            log_event(f"[VENDOR_SCANNER] Cleaned up {len(expired_vendors)} expired vendors, {len(expired_listings)} expired listings")
        
        # Limit cache size
        if len(self.vendors_cache) > self.max_cache_size:
            # Remove oldest entries
            sorted_vendors = sorted(
                self.vendors_cache.items(),
                key=lambda x: x[1].last_scan
            )
            vendors_to_remove = len(self.vendors_cache) - self.max_cache_size
            for vendor_id, _ in sorted_vendors[:vendors_to_remove]:
                del self.vendors_cache[vendor_id]
            
            log_event(f"[VENDOR_SCANNER] Removed {vendors_to_remove} oldest vendors to maintain cache size")
    
    def _get_cache_size_mb(self) -> float:
        """Get cache size in megabytes."""
        try:
            vendors_size = self.vendors_cache_file.stat().st_size if self.vendors_cache_file.exists() else 0
            bazaar_size = self.bazaar_cache_file.stat().st_size if self.bazaar_cache_file.exists() else 0
            total_bytes = vendors_size + bazaar_size
            return round(total_bytes / (1024 * 1024), 2)
        except Exception:
            return 0.0
    
    def export_cache_report(self, filepath: str = None) -> str:
        """Export a comprehensive cache report.

        Parameters
        ----------
        filepath : str, optional
            Path to save the report. If None, generates a default path.

        Returns
        -------
        str
            Path to the exported report
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/vendors/vendor_cache_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "cache_stats": self.get_cache_stats(),
            "vendors": {k: asdict(v) for k, v in self.vendors_cache.items()},
            "bazaar_listings": {k: asdict(v) for k, v in self.bazaar_cache.items()},
            "scan_history": self.scan_history[-100:]  # Last 100 scans
        }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        log_event(f"[VENDOR_SCANNER] Exported cache report to: {filepath}")
        return filepath


def create_vendor_scanner(cache_dir: str = "data/vendors") -> VendorScanner:
    """Create a new vendor scanner instance.

    Parameters
    ----------
    cache_dir : str
        Directory to store vendor cache data

    Returns
    -------
    VendorScanner
        Configured vendor scanner instance
    """
    return VendorScanner(cache_dir) 