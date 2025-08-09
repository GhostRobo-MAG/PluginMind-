/**
 * API utilities with built-in authentication and token expiry handling
 */

import { getValidToken, logout } from './auth';

// Backend base URL from environment variable
const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Debug: log the loaded backend URL
console.log('🔧 Backend URL loaded:', BASE_URL);

export class AuthError extends Error {
  constructor(message: string, public statusCode: number) {
    super(message);
    this.name = 'AuthError';
  }
}

export interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any;
  headers?: Record<string, string>;
  requireAuth?: boolean;
}

/**
 * Makes an authenticated API request with automatic token validation
 * Automatically handles token expiry and redirects to login if needed
 */
export async function apiRequest<T = any>(
  url: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const {
    method = 'GET',
    body,
    headers = {},
    requireAuth = true
  } = options;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers
  };

  // Add authorization header if authentication is required
  if (requireAuth) {
    const token = getValidToken();
    
    if (!token) {
      // Token is invalid or expired, redirect to login
      logout();
      throw new AuthError('Authentication required', 401);
    }

    requestHeaders.Authorization = `Bearer ${token}`;
  }

  const requestOptions: RequestInit = {
    method,
    headers: requestHeaders,
  };

  if (body && (method === 'POST' || method === 'PUT')) {
    requestOptions.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, requestOptions);

    // Handle authentication errors
    if (response.status === 401) {
      // Token might have expired during the request, clear it and redirect
      logout();
      throw new AuthError('Authentication failed', 401);
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }
    
    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error. Please check your connection.');
    }
    
    throw error;
  }
}

/**
 * Specific API calls for the CoinGrok backend
 */

export interface AnalysisRequest {
  user_input: string;
}

export interface AnalysisResponse {
  analysis: string;
  optimized_prompt?: string;
}

/**
 * Submits a crypto analysis request to the backend
 */
export async function submitAnalysis(userInput: string): Promise<AnalysisResponse> {
  return apiRequest<AnalysisResponse>(`${BASE_URL}/analyze`, {
    method: 'POST',
    body: { user_input: userInput },
    requireAuth: true
  });
}

/**
 * Gets the current user profile
 */
export async function getUserProfile(): Promise<any> {
  return apiRequest(`${BASE_URL}/me`, {
    method: 'GET',
    requireAuth: true
  });
}

/**
 * Gets user usage statistics
 */
export async function getUserUsage(): Promise<any> {
  return apiRequest(`${BASE_URL}/me/usage`, {
    method: 'GET',
    requireAuth: true
  });
}