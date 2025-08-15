# User-based Rate Limiting
from fastapi import Request, HTTPException
from typing import Dict, Tuple, Optional
import time
from collections import defaultdict

class UserRateLimiter:
    def __init__(self):
        self.user_requests: Dict[str, List[float]] = defaultdict(list)
        self.user_limits: Dict[str, Tuple[int, int]] = {
            "free": (100, 3600),      # 100 requests per hour
            "basic": (1000, 3600),    # 1000 requests per hour
            "premium": (10000, 3600), # 10000 requests per hour
            "enterprise": (100000, 3600) # 100000 requests per hour
        }
    
    def is_allowed(self, user_id: str, plan: str = "free") -> Tuple[bool, Dict[str, int]]:
        """Check if user request is allowed"""
        now = time.time()
        max_requests, window = self.user_limits.get(plan, self.user_limits["free"])
        
        # Clean old requests
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id] 
            if now - req_time < window
        ]
        
        # Check if limit exceeded
        current_requests = len(self.user_requests[user_id])
        is_allowed = current_requests < max_requests
        
        # Add current request if allowed
        if is_allowed:
            self.user_requests[user_id].append(now)
        
        return is_allowed, {
            "current": current_requests,
            "limit": max_requests,
            "remaining": max(0, max_requests - current_requests),
            "reset_time": int(now + window)
        }
    
    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """Get user rate limiting statistics"""
        now = time.time()
        requests = self.user_requests.get(user_id, [])
        
        # Count requests in last hour
        hour_ago = now - 3600
        requests_last_hour = len([req for req in requests if req > hour_ago])
        
        return {
            "total_requests": len(requests),
            "requests_last_hour": requests_last_hour
        }

user_rate_limiter = UserRateLimiter()

def rate_limit_by_user(plan: str = "free"):
    """Decorator for user-based rate limiting"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get user ID from request (implement based on your auth system)
            user_id = get_user_id_from_request(request)
            
            is_allowed, stats = user_rate_limiter.is_allowed(user_id, plan)
            
            if not is_allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(stats["limit"]),
                        "X-RateLimit-Remaining": str(stats["remaining"]),
                        "X-RateLimit-Reset": str(stats["reset_time"])
                    }
                )
            
            # Add rate limit headers to response
            response = await func(request, *args, **kwargs)
            response.headers.update({
                "X-RateLimit-Limit": str(stats["limit"]),
                "X-RateLimit-Remaining": str(stats["remaining"]),
                "X-RateLimit-Reset": str(stats["reset_time"])
            })
            
            return response
        return wrapper
    return decorator

def get_user_id_from_request(request: Request) -> str:
    """Extract user ID from request (implement based on your auth system)"""
    # This should be implemented based on your authentication system
    # For now, return a default value
    return "default_user" 