"""
Hardened IP address extraction utilities.

Provides secure IP address extraction from FastAPI requests with
IPv4/IPv6 validation and header sanitization.
"""

import ipaddress
from typing import Optional
from fastapi import Request

from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_client_ip(request: Request) -> str:
    """
    Extract client IP address with hardened validation.
    
    Attempts to extract IP from various sources with proper validation:
    1. Direct client IP (if available)
    2. X-Forwarded-For header (first valid IP)
    3. X-Real-IP header
    4. Fallback to "unknown"
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Validated IP address or "unknown" if no valid IP found
    """
    # Try direct client IP first
    if request.client and request.client.host:
        ip = _validate_ip(request.client.host)
        if ip:
            return ip
    
    # Try X-Forwarded-For header (proxy/load balancer)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take first IP from comma-separated list
        first_ip = forwarded_for.split(",")[0].strip()
        ip = _validate_ip(first_ip)
        if ip:
            return ip
    
    # Try X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        ip = _validate_ip(real_ip.strip())
        if ip:
            return ip
    
    logger.warning("Unable to extract valid client IP address")
    return "unknown"


def _validate_ip(ip_str: str) -> Optional[str]:
    """
    Validate IP address string for IPv4/IPv6 compliance.
    
    Args:
        ip_str: IP address string to validate
        
    Returns:
        str: Validated IP address or None if invalid
    """
    if not ip_str or not isinstance(ip_str, str):
        return None
    
    # Remove any surrounding whitespace
    ip_str = ip_str.strip()
    
    # Basic length check to prevent abuse
    if len(ip_str) > 45:  # Max IPv6 length is 39, add some buffer
        return None
    
    try:
        # Handle IPv6 zone IDs - for rate limiting, we don't support them
        # as they're interface-specific and not useful for rate limiting
        if '%' in ip_str:
            return None
            
        # This validates both IPv4 and IPv6
        ip_obj = ipaddress.ip_address(ip_str)
        return str(ip_obj)
    except (ipaddress.AddressValueError, ValueError):
        logger.debug(f"Invalid IP address format: {ip_str}")
        return None