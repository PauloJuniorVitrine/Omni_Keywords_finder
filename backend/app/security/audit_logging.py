# Audit Logging
from fastapi import Request
from typing import Dict, Any, Optional, List
import json
import time
from datetime import datetime
from enum import Enum

class AuditEventType(Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    API_ACCESS = "api_access"
    DATA_ACCESS = "data_access"
    DATA_MODIFY = "data_modify"
    SYSTEM_CONFIG = "system_config"
    SECURITY_EVENT = "security_event"

class AuditLogger:
    def __init__(self):
        self.log_file = "audit.log"
    
    def log_event(self, 
                  event_type: AuditEventType,
                  user_id: Optional[str],
                  action: str,
                  resource: str,
                  details: Dict[str, Any] = None,
                  ip_address: str = None,
                  user_agent: str = None,
                  success: bool = True) -> None:
        """Log an audit event"""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success
        }
        
        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
    
    def get_user_activity(self, user_id: str, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get audit logs for a specific user"""
        activities = []
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry["user_id"] == user_id:
                        if start_time and datetime.fromisoformat(entry["timestamp"]) < start_time:
                            continue
                        if end_time and datetime.fromisoformat(entry["timestamp"]) > end_time:
                            continue
                        activities.append(entry)
                except:
                    continue
        
        return activities
    
    def get_security_events(self, event_type: AuditEventType = None) -> List[Dict[str, Any]]:
        """Get security-related audit events"""
        events = []
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if event_type is None or entry["event_type"] == event_type.value:
                        if entry["event_type"] in ["security_event", "user_login", "user_logout"]:
                            events.append(entry)
                except:
                    continue
        
        return events

audit_logger = AuditLogger()

def audit_log(event_type: AuditEventType, action: str, resource: str):
    """Decorator for automatic audit logging"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Extract user info from request
            user_id = get_user_id_from_request(request)
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent")
            
            try:
                # Execute the function
                result = await func(request, *args, **kwargs)
                
                # Log successful event
                audit_logger.log_event(
                    event_type=event_type,
                    user_id=user_id,
                    action=action,
                    resource=resource,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Log failed event
                audit_logger.log_event(
                    event_type=event_type,
                    user_id=user_id,
                    action=action,
                    resource=resource,
                    details={"error": str(e)},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False
                )
                raise
        
        return wrapper
    return decorator

def get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from request (implement based on your auth system)"""
    # This should be implemented based on your authentication system
    # For now, return None
    return None

# Example usage
@audit_log(AuditEventType.API_ACCESS, "GET", "/api/users")
async def get_users(request: Request):
    # Function implementation
    pass 