"""Vendor API Plugin for MS11.

This module provides API endpoints for Crafting Mode to search for needed items/resources:
- RESTful API endpoints for vendor and bazaar searches
- Integration with vendor scanner service
- Support for crafting mode item requirements
- Real-time vendor data access
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict

from android_ms11.utils.logging_utils import log_event

# Import vendor scanner service
try:
    from services.vendor_scanner import VendorScanner, create_vendor_scanner
    VENDOR_SCANNER_AVAILABLE = True
except ImportError:
    VENDOR_SCANNER_AVAILABLE = False
    log_event("[VENDOR_API] Vendor scanner service not available")


class VendorAPI:
    """API endpoints for vendor and bazaar search functionality."""
    
    def __init__(self, vendor_scanner: Optional[VendorScanner] = None):
        """Initialize the vendor API.

        Parameters
        ----------
        vendor_scanner : VendorScanner, optional
            Vendor scanner instance. If None, creates a new one.
        """
        if vendor_scanner is None:
            if VENDOR_SCANNER_AVAILABLE:
                self.vendor_scanner = create_vendor_scanner()
            else:
                self.vendor_scanner = None
                log_event("[VENDOR_API] No vendor scanner available")
        else:
            self.vendor_scanner = vendor_scanner
        
        self.api_version = "1.0"
        self.endpoints = {
            "search_items": "/api/vendor/search",
            "get_vendors": "/api/vendor/list",
            "get_bazaar": "/api/vendor/bazaar",
            "scan_location": "/api/vendor/scan",
            "get_stats": "/api/vendor/stats"
        }
        
        self.request_history: List[Dict[str, Any]] = []
        
    def search_items(self, item_names: List[str], max_price: int = None,
                    vendor_types: List[str] = None, include_bazaar: bool = True) -> Dict[str, Any]:
        """Search for items across vendors and bazaar.

        Parameters
        ----------
        item_names : List[str]
            Names of items to search for
        max_price : int, optional
            Maximum price to consider
        vendor_types : List[str], optional
            Types of vendors to search ("vendor", "bazaar", "shop")
        include_bazaar : bool
            Whether to include bazaar listings in search

        Returns
        -------
        Dict[str, Any]
            API response with search results
        """
        if not self.vendor_scanner:
            return self._error_response("Vendor scanner not available")
        
        try:
            log_event(f"[VENDOR_API] Search request for items: {item_names}")
            
            # Perform search
            results = self.vendor_scanner.search_for_items(
                item_names=item_names,
                max_price=max_price,
                vendor_types=vendor_types
            )
            
            # Filter bazaar results if requested
            if not include_bazaar:
                for item_name in results:
                    results[item_name] = [
                        result for result in results[item_name]
                        if result["source"] != "bazaar"
                    ]
            
            # Record request
            self._record_request("search_items", {
                "item_names": item_names,
                "max_price": max_price,
                "vendor_types": vendor_types,
                "include_bazaar": include_bazaar,
                "results_count": sum(len(v) for v in results.values())
            })
            
            return self._success_response({
                "search_results": results,
                "total_items_found": sum(len(v) for v in results.values()),
                "items_searched": item_names
            })
            
        except Exception as e:
            log_event(f"[VENDOR_API] Error in search_items: {e}")
            return self._error_response(f"Search failed: {str(e)}")
    
    def get_vendors_by_location(self, planet: str, city: str) -> Dict[str, Any]:
        """Get all vendors at a specific location.

        Parameters
        ----------
        planet : str
            Planet name
        city : str
            City name

        Returns
        -------
        Dict[str, Any]
            API response with vendor list
        """
        if not self.vendor_scanner:
            return self._error_response("Vendor scanner not available")
        
        try:
            log_event(f"[VENDOR_API] Get vendors request for {city}, {planet}")
            
            vendors = self.vendor_scanner.get_vendor_by_location(planet, city)
            
            # Convert to serializable format
            vendors_data = []
            for vendor in vendors:
                vendor_dict = asdict(vendor)
                vendors_data.append(vendor_dict)
            
            # Record request
            self._record_request("get_vendors", {
                "planet": planet,
                "city": city,
                "vendors_found": len(vendors)
            })
            
            return self._success_response({
                "vendors": vendors_data,
                "location": f"{city}, {planet}",
                "total_vendors": len(vendors)
            })
            
        except Exception as e:
            log_event(f"[VENDOR_API] Error in get_vendors_by_location: {e}")
            return self._error_response(f"Failed to get vendors: {str(e)}")
    
    def scan_location(self, player_location: tuple) -> Dict[str, Any]:
        """Scan for vendors at the player's current location.

        Parameters
        ----------
        player_location : tuple
            (planet, city, (x, y)) coordinates of the player

        Returns
        -------
        Dict[str, Any]
            API response with scan results
        """
        if not self.vendor_scanner:
            return self._error_response("Vendor scanner not available")
        
        try:
            log_event(f"[VENDOR_API] Scan location request: {player_location}")
            
            vendors = self.vendor_scanner.scan_nearby_vendors(player_location)
            
            # Convert to serializable format
            vendors_data = []
            for vendor in vendors:
                vendor_dict = asdict(vendor)
                vendors_data.append(vendor_dict)
            
            # Record request
            self._record_request("scan_location", {
                "location": player_location,
                "vendors_detected": len(vendors)
            })
            
            return self._success_response({
                "vendors_detected": vendors_data,
                "scan_location": player_location,
                "total_vendors": len(vendors)
            })
            
        except Exception as e:
            log_event(f"[VENDOR_API] Error in scan_location: {e}")
            return self._error_response(f"Scan failed: {str(e)}")
    
    def get_bazaar_listings(self, search_terms: List[str] = None) -> Dict[str, Any]:
        """Get bazaar listings matching search terms.

        Parameters
        ----------
        search_terms : List[str], optional
            Terms to search for. If None, returns all listings.

        Returns
        -------
        Dict[str, Any]
            API response with bazaar listings
        """
        if not self.vendor_scanner:
            return self._error_response("Vendor scanner not available")
        
        try:
            log_event(f"[VENDOR_API] Get bazaar listings request: {search_terms}")
            
            listings = self.vendor_scanner.scan_bazaar_listings(search_terms)
            
            # Convert to serializable format
            listings_data = []
            for listing in listings:
                listing_dict = asdict(listing)
                listings_data.append(listing_dict)
            
            # Record request
            self._record_request("get_bazaar_listings", {
                "search_terms": search_terms,
                "listings_found": len(listings)
            })
            
            return self._success_response({
                "bazaar_listings": listings_data,
                "search_terms": search_terms,
                "total_listings": len(listings)
            })
            
        except Exception as e:
            log_event(f"[VENDOR_API] Error in get_bazaar_listings: {e}")
            return self._error_response(f"Failed to get bazaar listings: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the vendor cache.

        Returns
        -------
        Dict[str, Any]
            API response with cache statistics
        """
        if not self.vendor_scanner:
            return self._error_response("Vendor scanner not available")
        
        try:
            log_event("[VENDOR_API] Get cache stats request")
            
            stats = self.vendor_scanner.get_cache_stats()
            
            # Record request
            self._record_request("get_cache_stats", {
                "total_vendors": stats.get("total_vendors", 0),
                "total_listings": stats.get("total_bazaar_listings", 0)
            })
            
            return self._success_response({
                "cache_stats": stats,
                "api_version": self.api_version,
                "vendor_scanner_available": True
            })
            
        except Exception as e:
            log_event(f"[VENDOR_API] Error in get_cache_stats: {e}")
            return self._error_response(f"Failed to get cache stats: {str(e)}")
    
    def get_crafting_suggestions(self, required_items: List[str], max_budget: int = None) -> Dict[str, Any]:
        """Get suggestions for crafting mode based on required items.

        Parameters
        ----------
        required_items : List[str]
            Items required for crafting
        max_budget : int, optional
            Maximum budget for purchasing items

        Returns
        -------
        Dict[str, Any]
            API response with crafting suggestions
        """
        if not self.vendor_scanner:
            return self._error_response("Vendor scanner not available")
        
        try:
            log_event(f"[VENDOR_API] Crafting suggestions request for: {required_items}")
            
            # Search for required items
            search_results = self.vendor_scanner.search_for_items(
                item_names=required_items,
                max_price=max_budget
            )
            
            # Generate suggestions
            suggestions = []
            total_cost = 0
            
            for item_name, results in search_results.items():
                if results:
                    # Find the best deal (lowest price)
                    best_deal = min(results, key=lambda x: x["price"])
                    
                    suggestion = {
                        "item_name": item_name,
                        "best_deal": best_deal,
                        "alternative_sources": len(results) - 1,
                        "total_sources": len(results)
                    }
                    suggestions.append(suggestion)
                    total_cost += best_deal["price"]
            
            # Record request
            self._record_request("get_crafting_suggestions", {
                "required_items": required_items,
                "max_budget": max_budget,
                "suggestions_count": len(suggestions),
                "total_cost": total_cost
            })
            
            return self._success_response({
                "crafting_suggestions": suggestions,
                "required_items": required_items,
                "total_cost": total_cost,
                "budget_remaining": max_budget - total_cost if max_budget else None,
                "items_found": len(suggestions),
                "items_missing": len(required_items) - len(suggestions)
            })
            
        except Exception as e:
            log_event(f"[VENDOR_API] Error in get_crafting_suggestions: {e}")
            return self._error_response(f"Failed to get crafting suggestions: {str(e)}")
    
    def export_cache_report(self) -> Dict[str, Any]:
        """Export a comprehensive cache report.

        Returns
        -------
        Dict[str, Any]
            API response with report file path
        """
        if not self.vendor_scanner:
            return self._error_response("Vendor scanner not available")
        
        try:
            log_event("[VENDOR_API] Export cache report request")
            
            report_path = self.vendor_scanner.export_cache_report()
            
            # Record request
            self._record_request("export_cache_report", {
                "report_path": report_path
            })
            
            return self._success_response({
                "report_path": report_path,
                "export_successful": True
            })
            
        except Exception as e:
            log_event(f"[VENDOR_API] Error in export_cache_report: {e}")
            return self._error_response(f"Failed to export cache report: {str(e)}")
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and available endpoints.

        Returns
        -------
        Dict[str, Any]
            API information
        """
        return self._success_response({
            "api_name": "Vendor API",
            "version": self.api_version,
            "vendor_scanner_available": self.vendor_scanner is not None,
            "endpoints": self.endpoints,
            "total_requests": len(self.request_history)
        })
    
    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a successful API response.

        Parameters
        ----------
        data : Dict[str, Any]
            Response data

        Returns
        -------
        Dict[str, Any]
            Success response
        """
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error API response.

        Parameters
        ----------
        error_message : str
            Error message

        Returns
        -------
        Dict[str, Any]
            Error response
        """
        return {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": error_message
        }
    
    def _record_request(self, endpoint: str, details: Dict[str, Any]) -> None:
        """Record an API request for monitoring.

        Parameters
        ----------
        endpoint : str
            API endpoint called
        details : Dict[str, Any]
            Request details
        """
        request_record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "details": details
        }
        self.request_history.append(request_record)
        
        # Keep only last 100 requests
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]
    
    def get_request_history(self) -> List[Dict[str, Any]]:
        """Get API request history.

        Returns
        -------
        List[Dict[str, Any]]
            Request history
        """
        return self.request_history


def create_vendor_api(vendor_scanner: Optional[VendorScanner] = None) -> VendorAPI:
    """Create a new vendor API instance.

    Parameters
    ----------
    vendor_scanner : VendorScanner, optional
        Vendor scanner instance. If None, creates a new one.

    Returns
    -------
    VendorAPI
        Configured vendor API instance
    """
    return VendorAPI(vendor_scanner) 