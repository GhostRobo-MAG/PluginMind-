"""
Security Headers Middleware

Adds production-grade HTTP security headers to all responses.
Headers are configured based on environment (production vs development).
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.
    
    In production (debug=False):
    - Adds all security headers including HSTS
    
    In development (debug=True):
    - Adds all security headers except HSTS (to avoid sticky browser state on http://localhost)
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.is_production = not settings.debug
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Only add headers if they don't already exist (idempotent)
        headers_to_add = self._get_security_headers()
        
        for header_name, header_value in headers_to_add.items():
            if header_name not in response.headers:
                response.headers[header_name] = header_value
        
        return response
    
    def _get_security_headers(self) -> dict[str, str]:
        """Get security headers based on environment."""
        headers = {
            # Always add these headers in all environments
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
        }
        
        # Add HSTS only in production
        if self.is_production:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return headers