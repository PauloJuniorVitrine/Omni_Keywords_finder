# API Versioning
from fastapi import APIRouter, Request
from typing import Dict, Any
import re

class APIVersionManager:
    def __init__(self):
        self.versions: Dict[str, APIRouter] = {}
        self.default_version = "v1"
    
    def register_version(self, version: str, router: APIRouter) -> None:
        """Register a new API version"""
        self.versions[version] = router
    
    def get_version_router(self, version: str) -> APIRouter:
        """Get router for specific version"""
        return self.versions.get(version, self.versions[self.default_version])
    
    def get_version_from_request(self, request: Request) -> str:
        """Extract version from request"""
        # Check URL path
        path = request.url.path
        version_match = re.search(r'/api/v(\d+)', path)
        if version_match:
            return f"v{version_match.group(1)}"
        
        # Check header
        version_header = request.headers.get("X-API-Version")
        if version_header:
            return f"v{version_header}"
        
        # Check query parameter
        version_param = request.query_params.get("version")
        if version_param:
            return f"v{version_param}"
        
        return self.default_version

api_version_manager = APIVersionManager()

def versioned_router(version: str):
    """Decorator to create versioned router"""
    def decorator(func):
        router = APIRouter(prefix=f"/api/{version}")
        func(router)
        api_version_manager.register_version(version, router)
        return router
    return decorator

# Example usage:
@versioned_router("v1")
def create_v1_routes(router: APIRouter):
    @router.get("/users")
    async def get_users_v1():
        return {"version": "v1", "users": []}

@versioned_router("v2")
def create_v2_routes(router: APIRouter):
    @router.get("/users")
    async def get_users_v2():
        return {"version": "v2", "users": [], "metadata": {}} 