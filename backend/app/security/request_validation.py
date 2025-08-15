# Request Validation
from fastapi import Request, HTTPException
from typing import Dict, Any, List, Optional
import json
import re
from pydantic import BaseModel, validator

class RequestValidator:
    def __init__(self):
        self.allowed_headers = {
            "Content-Type",
            "Authorization",
            "User-Agent",
            "Accept",
            "X-API-Version",
            "X-Request-ID"
        }
        
        self.blocked_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"document\.",
            r"window\."
        ]
    
    def validate_headers(self, headers: Dict[str, str]) -> List[str]:
        """Validate request headers"""
        errors = []
        
        for header_name in headers:
            if header_name.lower() not in {h.lower() for h in self.allowed_headers}:
                errors.append(f"Blocked header: {header_name}")
        
        return errors
    
    def validate_payload(self, payload: Dict[str, Any]) -> List[str]:
        """Validate request payload for malicious content"""
        errors = []
        payload_str = json.dumps(payload, default=str)
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, payload_str, re.IGNORECASE):
                errors.append(f"Malicious content detected: {pattern}")
        
        return errors
    
    def validate_content_length(self, content_length: int, max_size: int = 1048576) -> bool:
        """Validate content length"""
        return content_length <= max_size
    
    def validate_content_type(self, content_type: str) -> bool:
        """Validate content type"""
        allowed_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ]
        return any(allowed_type in content_type for allowed_type in allowed_types)

class ValidationMiddleware:
    def __init__(self):
        self.validator = RequestValidator()
    
    async def validate_request(self, request: Request) -> None:
        """Validate incoming request"""
        errors = []
        
        # Validate headers
        header_errors = self.validator.validate_headers(dict(request.headers))
        errors.extend(header_errors)
        
        # Validate content length
        content_length = request.headers.get("content-length")
        if content_length:
            if not self.validator.validate_content_length(int(content_length)):
                errors.append("Content length too large")
        
        # Validate content type
        content_type = request.headers.get("content-type", "")
        if not self.validator.validate_content_type(content_type):
            errors.append("Invalid content type")
        
        # Validate payload if present
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                payload = await request.json()
                payload_errors = self.validator.validate_payload(payload)
                errors.extend(payload_errors)
            except:
                pass
        
        if errors:
            raise HTTPException(status_code=400, detail={"validation_errors": errors})

# Pydantic models for request validation
class SecureRequestModel(BaseModel):
    @validator('*', pre=True)
    def validate_no_malicious_content(cls, v):
        if isinstance(v, str):
            for pattern in RequestValidator().blocked_patterns:
                if re.search(pattern, v, re.IGNORECASE):
                    raise ValueError(f"Malicious content detected: {pattern}")
        return v

# Example usage
class UserCreateRequest(SecureRequestModel):
    username: str
    email: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError("Invalid email format")
        return v

validation_middleware = ValidationMiddleware() 