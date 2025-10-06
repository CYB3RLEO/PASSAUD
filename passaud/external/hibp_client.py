"""
Have I Been Pwned API client for PassAud.
"""

import logging
import requests
import hashlib
import time
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class HIBPClient:
    """Client for the Have I Been Pwned API."""
    
    def __init__(self, api_key: Optional[str] = None, rate_limit_delay: float = 1.5):
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.base_url = "https://api.pwnedpasswords.com"
        self.logger = logging.getLogger(__name__)
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Respect rate limits by adding delays between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def check_password(self, password: str) -> int:
        """
        Check if a password has been pwned.
        Returns the number of times the password was found in breaches.
        """
        try:
            self._rate_limit()
            
            # Hash the password with SHA-1
            hash_full = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix = hash_full[:5]
            suffix = hash_full[5:]
            
            # Make the request
            headers = {
                "User-Agent": "PassAud-Password-Auditing-Tool",
                "Add-Padding": "true"
            }
            
            if self.api_key:
                headers["hibp-api-key"] = self.api_key
            
            url = f"{self.base_url}/range/{prefix}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the response
            for line in response.text.splitlines():
                parts = line.split(':')
                if len(parts) == 2 and parts[0] == suffix:
                    return int(parts[1])
            
            return 0
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HIBP API request failed: {e}")
            return -1  # -1 indicates API error
        except Exception as e:
            self.logger.error(f"Error checking password with HIBP: {e}")
            return -1
    
    def check_hash(self, hash_prefix: str) -> Optional[str]:
        """
        Check a hash prefix against HIBP.
        Returns the response text containing matching hashes.
        """
        try:
            self._rate_limit()
            
            headers = {
                "User-Agent": "PassAud-Password-Auditing-Tool",
                "Add-Padding": "true"
            }
            
            if self.api_key:
                headers["hibp-api-key"] = self.api_key
            
            url = f"{self.base_url}/range/{hash_prefix}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error checking hash with HIBP: {e}")
            return None
    
    def is_password_compromised(self, password: str, threshold: int = 1) -> Tuple[bool, int]:
        """
        Check if password is compromised based on threshold.
        Returns (is_compromised, breach_count)
        """
        count = self.check_password(password)
        if count == -1:  # API error
            return False, 0
        return count >= threshold, count