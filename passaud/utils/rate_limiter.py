"""
Rate limiting utilities for PassAud.
"""

import time
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting for API calls to prevent abuse."""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
    def wait(self):
        """Wait if necessary to respect rate limits."""
        with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.request_times = [t for t in self.request_times if now - t < 60]
            
            if len(self.request_times) >= self.requests_per_minute:
                oldest = self.request_times[0]
                wait_time = 60 - (now - oldest)
                if wait_time > 0:
                    self.logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
                    # Update times after waiting
                    now = time.time()
                    self.request_times = [t for t in self.request_times if now - t < 60]
            
            self.request_times.append(time.time())