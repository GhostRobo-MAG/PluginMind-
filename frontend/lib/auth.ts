/**
 * Authentication utilities for token management and validation
 */

export interface DecodedToken {
  exp: number;
  iat: number;
  email?: string;
  sub?: string;
  [key: string]: any;
}

/**
 * Decodes a JWT token payload without verification
 * @param token - JWT token string
 * @returns Decoded payload or null if invalid
 */
export function decodeJWT(token: string): DecodedToken | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const payload = parts[1];
    // Add padding if needed for base64 decoding
    const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
    const decodedPayload = atob(paddedPayload);
    
    return JSON.parse(decodedPayload);
  } catch (error) {
    console.warn('Failed to decode JWT token:', error);
    return null;
  }
}

/**
 * Checks if a JWT token is expired
 * @param token - JWT token string
 * @returns true if token is expired, false if still valid, null if invalid token
 */
export function isTokenExpired(token: string): boolean | null {
  const decoded = decodeJWT(token);
  if (!decoded || !decoded.exp) {
    return null;
  }

  // exp is in seconds, Date.now() is in milliseconds
  const currentTime = Math.floor(Date.now() / 1000);
  return decoded.exp < currentTime;
}

/**
 * Gets a valid token from localStorage, removing it if expired
 * @returns Valid token string or null if no valid token
 */
export function getValidToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const token = localStorage.getItem('token');
  if (!token) {
    return null;
  }

  const expired = isTokenExpired(token);
  if (expired === true) {
    // Token is expired, remove it
    localStorage.removeItem('token');
    return null;
  }
  
  if (expired === null) {
    // Token is invalid, remove it
    localStorage.removeItem('token');
    return null;
  }

  return token;
}

/**
 * Clears the authentication token and redirects to login
 */
export function logout(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
}

/**
 * Gets user information from the token
 * @param token - JWT token string
 * @returns User info or null if invalid
 */
export function getUserFromToken(token: string): { email?: string; sub?: string } | null {
  const decoded = decodeJWT(token);
  if (!decoded) {
    return null;
  }

  return {
    email: decoded.email,
    sub: decoded.sub
  };
}