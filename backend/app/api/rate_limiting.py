# Advanced Rate Limiting
from fastapi import Request, HTTPException
from typing import Dict, Tuple
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.limits = {
            "default": (100, 3600),  # 100 requests per hour
            "api": (1000, 3600),     # 1000 requests per hour
            "admin": (10000, 3600)   # 10000 requests per hour
        }
    
    def is_allowed(self, client_id: str, limit_type: str = "default") -> bool:
        """Check if request is allowed"""
        now = time.time()
        window, max_requests = self.limits.get(limit_type, self.limits["default"])
        
        # Clean old requests
        self.requests[client_id] = [req_time for req_time in self.requests[client_id] 
                                  if now - req_time < window]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit_middleware(request: Request, limit_type: str = "default"):
    """Rate limiting middleware"""
    client_id = request.client.host
    if not rate_limiter.is_allowed(client_id, limit_type):
        raise HTTPException(status_code=429, detail="Rate limit exceeded") 