#!/usr/bin/env python3
"""
SWGDB API Client for Pushing Session Data

This module handles communication with the SWGDB API to upload session data
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


class SWGDBAPIClient:
    """Client for communicating with SWGDB API."""
    
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
            "User-Agent": "MS11-Bot/1.0.0"
        }
    
    def push_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Push session data to SWGDB API."""
        try:
            # Prepare request
            url = f"{self.api_url}/sessions/upload"
            headers = self._prepare_headers(session_data)
            
            # Make request
            response = self.session.post(
                url,
                json=session_data,
                headers=headers,
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                return {
                    "success": True,
                    "swgdb_session_id": response.json().get("session_id"),
                    "message": "Session uploaded successfully"
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
    
    def batch_upload_sessions(self, sessions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload multiple sessions in a batch."""
        try:
            # Prepare request
            url = f"{self.api_url}/sessions/batch-upload"
            batch_data = {
                "sessions": sessions_data,
                "upload_timestamp": datetime.now().isoformat(),
                "total_sessions": len(sessions_data)
            }
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
                    "session_ids": result.get("session_ids", [])
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
    
    def get_upload_status(self, session_id: str) -> Dict[str, Any]:
        """Get upload status for a specific session."""
        try:
            url = f"{self.api_url}/sessions/{session_id}/status"
            headers = {
                "X-SWGDB-API-Key": self.api_key,
                "X-SWGDB-User-Hash": self.user_hash
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get status ({response.status_code})"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Status check error: {str(e)}"
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
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and limits."""
        try:
            url = f"{self.api_url}/info"
            headers = {
                "X-SWGDB-API-Key": self.api_key,
                "X-SWGDB-User-Hash": self.user_hash
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "info": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get API info ({response.status_code})"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API info error: {str(e)}"
            }


class SWGDBUploadManager:
    """Manages SWGDB uploads with rate limiting and error handling."""
    
    def __init__(self, api_client: SWGDBAPIClient):
        self.api_client = api_client
        self.upload_queue: List[Dict[str, Any]] = []
        self.rate_limit_delay = 1.0  # seconds between uploads
        self.max_batch_size = 10
    
    def add_to_queue(self, session_data: Dict[str, Any]) -> None:
        """Add session data to upload queue."""
        self.upload_queue.append({
            "data": session_data,
            "added_timestamp": datetime.now().isoformat(),
            "retry_count": 0
        })
    
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
            
            # Prepare batch data
            batch_data = [item["data"] for item in batch]
            
            # Upload batch
            response = self.api_client.batch_upload_sessions(batch_data)
            
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
        
        return results
    
    def retry_failed_uploads(self, max_retries: int = 3) -> Dict[str, Any]:
        """Retry failed uploads from the queue."""
        retry_queue = [item for item in self.upload_queue if item["retry_count"] < max_retries]
        
        if not retry_queue:
            return {
                "success": True,
                "retried": 0,
                "message": "No failed uploads to retry"
            }
        
        results = {
            "success": True,
            "retried": 0,
            "successful": 0,
            "failed": 0
        }
        
        for item in retry_queue:
            item["retry_count"] += 1
            
            response = self.api_client.push_session_data(item["data"])
            
            if response["success"]:
                results["successful"] += 1
                self.upload_queue.remove(item)
            else:
                results["failed"] += 1
            
            results["retried"] += 1
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        return results


def test_api_connection(api_url: str, api_key: str, user_hash: str) -> Dict[str, Any]:
    """Test connection to SWGDB API."""
    client = SWGDBAPIClient(api_url, api_key, user_hash)
    
    # Test credentials
    auth_result = client.validate_credentials()
    if not auth_result["success"] or not auth_result.get("valid"):
        return {
            "success": False,
            "error": "Authentication failed",
            "details": auth_result.get("error", "Unknown error")
        }
    
    # Get API info
    info_result = client.get_api_info()
    if not info_result["success"]:
        return {
            "success": False,
            "error": "Failed to get API info",
            "details": info_result.get("error", "Unknown error")
        }
    
    return {
        "success": True,
        "api_info": info_result.get("info", {}),
        "user_info": auth_result.get("user_info", {})
    }


def main():
    """Main function for testing the SWGDB API client."""
    # Test configuration
    api_url = "https://api.swgdb.com/v1"
    api_key = "test_api_key"
    user_hash = "test_user_hash"
    
    # Test connection
    print("Testing SWGDB API connection...")
    result = test_api_connection(api_url, api_key, user_hash)
    
    if result["success"]:
        print("✅ API connection successful")
        print(f"API Info: {result.get('api_info', {})}")
        print(f"User Info: {result.get('user_info', {})}")
    else:
        print("❌ API connection failed")
        print(f"Error: {result.get('error')}")
        print(f"Details: {result.get('details')}")


if __name__ == '__main__':
    main() 