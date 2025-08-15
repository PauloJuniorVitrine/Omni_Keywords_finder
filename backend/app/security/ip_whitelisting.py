# IP Whitelisting
from fastapi import Request, HTTPException
from typing import List, Set, Optional, Dict, Any
import ipaddress
from datetime import datetime, timedelta

class IPWhitelist:
    def __init__(self):
        self.whitelisted_ips: Set[str] = set()
        self.whitelisted_ranges: List[ipaddress.IPv4Network] = []
        self.temp_whitelist: Dict[str, datetime] = {}
        self.blocked_ips: Set[str] = set()
    
    def add_ip(self, ip: str) -> bool:
        """Add IP to whitelist"""
        try:
            ipaddress.ip_address(ip)
            self.whitelisted_ips.add(ip)
            return True
        except ValueError:
            return False
    
    def add_range(self, cidr: str) -> bool:
        """Add IP range to whitelist"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            self.whitelisted_ranges.append(network)
            return True
        except ValueError:
            return False
    
    def remove_ip(self, ip: str) -> bool:
        """Remove IP from whitelist"""
        return self.whitelisted_ips.discard(ip) is not None
    
    def remove_range(self, cidr: str) -> bool:
        """Remove IP range from whitelist"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if network in self.whitelisted_ranges:
                self.whitelisted_ranges.remove(network)
                return True
        except ValueError:
            pass
        return False
    
    def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check individual IPs
            if ip in self.whitelisted_ips:
                return True
            
            # Check IP ranges
            for network in self.whitelisted_ranges:
                if ip_obj in network:
                    return True
            
            # Check temporary whitelist
            if ip in self.temp_whitelist:
                if datetime.now() < self.temp_whitelist[ip]:
                    return True
                else:
                    # Remove expired temporary entry
                    del self.temp_whitelist[ip]
            
            return False
        except ValueError:
            return False
    
    def add_temp_whitelist(self, ip: str, duration_hours: int = 24) -> bool:
        """Add IP to temporary whitelist"""
        try:
            ipaddress.ip_address(ip)
            expiry = datetime.now() + timedelta(hours=duration_hours)
            self.temp_whitelist[ip] = expiry
            return True
        except ValueError:
            return False
    
    def block_ip(self, ip: str) -> bool:
        """Block an IP address"""
        try:
            ipaddress.ip_address(ip)
            self.blocked_ips.add(ip)
            return True
        except ValueError:
            return False
    
    def unblock_ip(self, ip: str) -> bool:
        """Unblock an IP address"""
        return self.blocked_ips.discard(ip) is not None
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def get_whitelist_status(self) -> Dict[str, Any]:
        """Get current whitelist status"""
        return {
            "whitelisted_ips": list(self.whitelisted_ips),
            "whitelisted_ranges": [str(network) for network in self.whitelisted_ranges],
            "temp_whitelist": {
                ip: expiry.isoformat() 
                for ip, expiry in self.temp_whitelist.items()
            },
            "blocked_ips": list(self.blocked_ips)
        }

ip_whitelist = IPWhitelist()

def require_whitelisted_ip():
    """Decorator to require whitelisted IP"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            
            # Check if IP is blocked
            if ip_whitelist.is_blocked(client_ip):
                raise HTTPException(status_code=403, detail="IP address is blocked")
            
            # Check if IP is whitelisted
            if not ip_whitelist.is_whitelisted(client_ip):
                raise HTTPException(status_code=403, detail="IP address not whitelisted")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Example usage
@require_whitelisted_ip()
async def admin_only_endpoint(request: Request):
    # Only accessible from whitelisted IPs
    pass 