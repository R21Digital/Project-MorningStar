#!/usr/bin/env python3
"""
SWGDB API Client for Pushing Character Stat Data

This module handles communication with the SWGDB API to upload character stat data
with proper authentication, retry logic, and error handling.
"""

import json
import time
import hashlib
import hmac
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ocr.stat_extractor import CharacterProfile, StatType
from core.attribute_profile import OptimizationProfile, OptimizationType
from utils.logging_utils import log_event


class SWGDBStatAPIClient:
    """Client for communicating with SWGDB API for stat data."""
    
    def __init__(self, api_url: str, api_key: str, user_hash: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.user_hash = user_hash
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _generate_signature(self, data: str, timestamp: str) -> str:
        """Generate HMAC signature for authentication."""
        message = f"{timestamp}.{data}"
        signature = hmac.new(
            self.api_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _prepare_headers(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare headers for API request."""
        timestamp = str(int(time.time()))
        data_str = json.dumps(data, sort_keys=True)
        signature = self._generate_signature(data_str, timestamp)
        
        return {
            "Content-Type": "application/json",
            "X-SWGDB-API-Key": self.api_key,
            "X-SWGDB-User-Hash": self.user_hash,
            "X-SWGDB-Timestamp": timestamp,
            "X-SWGDB-Signature": signature,
            "User-Agent": "MS11-StatTracker/1.0.0"
        }
    
    def push_character_stats(self, character_profile: CharacterProfile) -> Dict[str, Any]:
        """
        Push character stats to SWGDB API.
        
        Parameters
        ----------
        character_profile : CharacterProfile
            Character profile with stats to upload
            
        Returns
        -------
        Dict[str, Any]
            Upload result
        """
        try:
            # Prepare stat data
            stat_data = self._prepare_stat_data(character_profile)
            
            # Prepare request
            url = f"{self.api_url}/player/stats/upload"
            headers = self._prepare_headers(stat_data)
            
            # Make request
            response = self.session.post(
                url,
                json=stat_data,
                headers=headers,
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "swgdb_stat_id": result.get("stat_id"),
                    "character_name": character_profile.character_name,
                    "stats_uploaded": len(character_profile.stats),
                    "message": "Character stats uploaded successfully"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed - check API key and user hash"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "Access denied - insufficient permissions"
                }
            elif response.status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limit exceeded - try again later"
                }
            elif response.status_code >= 500:
                return {
                    "success": False,
                    "error": f"Server error ({response.status_code}) - try again later"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error ({response.status_code}): {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout - server not responding"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection error - check network and API URL"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _prepare_stat_data(self, character_profile: CharacterProfile) -> Dict[str, Any]:
        """Prepare character stat data for API upload."""
        # Convert stats to API format
        stats_data = {}
        for stat_type, stat in character_profile.stats.items():
            stats_data[stat_type.value] = {
                "current_value": stat.current_value,
                "max_value": stat.max_value,
                "percentage": stat.percentage,
                "confidence": stat.confidence,
                "source": stat.source,
                "timestamp": stat.timestamp
            }
        
        # Prepare API payload
        stat_data = {
            "character_name": character_profile.character_name,
            "profession": character_profile.profession,
            "level": character_profile.level,
            "scan_timestamp": character_profile.scan_timestamp,
            "scan_method": character_profile.scan_method,
            "confidence_score": character_profile.confidence_score,
            "stats": stats_data,
            "resistances": character_profile.resistances,
            "tapes": character_profile.tapes,
            "upload_timestamp": datetime.now().isoformat(),
            "data_version": "1.0"
        }
        
        return stat_data
    
    def push_optimization_profile(self, optimization_profile: OptimizationProfile) -> Dict[str, Any]:
        """
        Push optimization profile to SWGDB API.
        
        Parameters
        ----------
        optimization_profile : OptimizationProfile
            Optimization profile to upload
            
        Returns
        -------
        Dict[str, Any]
            Upload result
        """
        try:
            # Prepare optimization data
            opt_data = self._prepare_optimization_data(optimization_profile)
            
            # Prepare request
            url = f"{self.api_url}/player/optimization/upload"
            headers = self._prepare_headers(opt_data)
            
            # Make request
            response = self.session.post(
                url,
                json=opt_data,
                headers=headers,
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "swgdb_opt_id": result.get("optimization_id"),
                    "character_name": optimization_profile.character_name,
                    "optimization_type": optimization_profile.optimization_type.value,
                    "optimization_score": optimization_profile.optimization_score,
                    "message": "Optimization profile uploaded successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error ({response.status_code}): {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Upload error: {str(e)}"
            }
    
    def _prepare_optimization_data(self, optimization_profile: OptimizationProfile) -> Dict[str, Any]:
        """Prepare optimization data for API upload."""
        # Convert targets to API format
        targets_data = []
        for target in optimization_profile.targets:
            target_data = {
                "stat_type": target.stat_type.value,
                "target_value": target.target_value,
                "priority": target.priority,
                "current_value": target.current_value,
                "difference": target.difference,
                "percentage_complete": target.percentage_complete
            }
            targets_data.append(target_data)
        
        # Prepare API payload
        opt_data = {
            "character_name": optimization_profile.character_name,
            "profession": optimization_profile.profession,
            "optimization_type": optimization_profile.optimization_type.value,
            "optimization_score": optimization_profile.optimization_score,
            "targets": targets_data,
            "created_timestamp": optimization_profile.created_timestamp,
            "last_updated": optimization_profile.last_updated,
            "upload_timestamp": datetime.now().isoformat(),
            "data_version": "1.0"
        }
        
        return opt_data
    
    def batch_upload_stats(self, character_profiles: List[CharacterProfile]) -> Dict[str, Any]:
        """
        Upload multiple character profiles in a batch.
        
        Parameters
        ----------
        character_profiles : List[CharacterProfile]
            List of character profiles to upload
            
        Returns
        -------
        Dict[str, Any]
            Batch upload result
        """
        try:
            # Prepare batch data
            batch_data = {
                "profiles": [],
                "upload_timestamp": datetime.now().isoformat(),
                "total_profiles": len(character_profiles)
            }
            
            for profile in character_profiles:
                profile_data = self._prepare_stat_data(profile)
                batch_data["profiles"].append(profile_data)
            
            # Prepare request
            url = f"{self.api_url}/player/stats/batch-upload"
            headers = self._prepare_headers(batch_data)
            
            # Make request
            response = self.session.post(
                url,
                json=batch_data,
                headers=headers,
                timeout=60
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "uploaded_count": result.get("uploaded_count", 0),
                    "failed_count": result.get("failed_count", 0),
                    "stat_ids": result.get("stat_ids", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"Batch upload failed ({response.status_code}): {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Batch upload error: {str(e)}"
            }
    
    def get_stat_history(self, character_name: str, days: int = 30) -> Dict[str, Any]:
        """
        Get character stat history from SWGDB.
        
        Parameters
        ----------
        character_name : str
            Name of the character
        days : int
            Number of days of history to retrieve
            
        Returns
        -------
        Dict[str, Any]
            Stat history data
        """
        try:
            url = f"{self.api_url}/player/stats/history/{character_name}"
            params = {"days": days}
            headers = {
                "X-SWGDB-API-Key": self.api_key,
                "X-SWGDB-User-Hash": self.user_hash
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "history": response.json(),
                    "character_name": character_name
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get history ({response.status_code})"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"History retrieval error: {str(e)}"
            }
    
    def get_optimization_history(self, character_name: str) -> Dict[str, Any]:
        """
        Get character optimization history from SWGDB.
        
        Parameters
        ----------
        character_name : str
            Name of the character
            
        Returns
        -------
        Dict[str, Any]
            Optimization history data
        """
        try:
            url = f"{self.api_url}/player/optimization/history/{character_name}"
            headers = {
                "X-SWGDB-API-Key": self.api_key,
                "X-SWGDB-User-Hash": self.user_hash
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "history": response.json(),
                    "character_name": character_name
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get optimization history ({response.status_code})"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Optimization history error: {str(e)}"
            }
    
    def validate_credentials(self) -> Dict[str, Any]:
        """Validate API credentials."""
        try:
            url = f"{self.api_url}/auth/validate"
            headers = {
                "X-SWGDB-API-Key": self.api_key,
                "X-SWGDB-User-Hash": self.user_hash
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "valid": True,
                    "user_info": response.json()
                }
            elif response.status_code == 401:
                return {
                    "success": True,
                    "valid": False,
                    "error": "Invalid credentials"
                }
            else:
                return {
                    "success": False,
                    "error": f"Validation failed ({response.status_code})"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation error: {str(e)}"
            }


class SWGDBStatUploadManager:
    """Manages SWGDB stat uploads with rate limiting and error handling."""
    
    def __init__(self, api_client: SWGDBStatAPIClient):
        self.api_client = api_client
        self.upload_queue: List[CharacterProfile] = []
        self.rate_limit_delay = 2.0  # seconds between uploads
        self.max_batch_size = 5
    
    def add_to_queue(self, character_profile: CharacterProfile) -> None:
        """Add character profile to upload queue."""
        self.upload_queue.append(character_profile)
        log_event(f"[SWGDB_STAT] Added {character_profile.character_name} to upload queue")
    
    def process_queue(self) -> Dict[str, Any]:
        """Process the upload queue."""
        if not self.upload_queue:
            return {
                "success": True,
                "processed": 0,
                "message": "Queue is empty"
            }
        
        results = {
            "success": True,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process in batches
        while self.upload_queue:
            batch = self.upload_queue[:self.max_batch_size]
            self.upload_queue = self.upload_queue[self.max_batch_size:]
            
            # Upload batch
            response = self.api_client.batch_upload_stats(batch)
            
            if response["success"]:
                results["successful"] += response.get("uploaded_count", 0)
                results["failed"] += response.get("failed_count", 0)
            else:
                results["failed"] += len(batch)
                results["errors"].append(response["error"])
            
            results["processed"] += len(batch)
            
            # Rate limiting
            if self.upload_queue:
                time.sleep(self.rate_limit_delay)
        
        log_event(f"[SWGDB_STAT] Processed {results['processed']} profiles from queue")
        return results
    
    def upload_single_profile(self, character_profile: CharacterProfile) -> Dict[str, Any]:
        """Upload a single character profile."""
        return self.api_client.push_character_stats(character_profile)
    
    def upload_optimization_profile(self, optimization_profile: OptimizationProfile) -> Dict[str, Any]:
        """Upload a single optimization profile."""
        return self.api_client.push_optimization_profile(optimization_profile)


def test_api_connection(api_url: str, api_key: str, user_hash: str) -> Dict[str, Any]:
    """Test connection to SWGDB API."""
    client = SWGDBStatAPIClient(api_url, api_key, user_hash)
    
    # Test credentials
    auth_result = client.validate_credentials()
    if not auth_result["success"] or not auth_result.get("valid"):
        return {
            "success": False,
            "error": "Authentication failed",
            "details": auth_result.get("error", "Unknown error")
        }
    
    return {
        "success": True,
        "user_info": auth_result.get("user_info", {})
    }


def main():
    """Main function for testing the SWGDB Stat API client."""
    # Test configuration
    api_url = "https://api.swgdb.com/v1"
    api_key = "test_api_key"
    user_hash = "test_user_hash"
    
    # Test connection
    print("Testing SWGDB Stat API connection...")
    result = test_api_connection(api_url, api_key, user_hash)
    
    if result["success"]:
        print("✅ API connection successful")
        print(f"User Info: {result.get('user_info', {})}")
    else:
        print("❌ API connection failed")
        print(f"Error: {result.get('error')}")
        print(f"Details: {result.get('details')}")


if __name__ == '__main__':
    main() 