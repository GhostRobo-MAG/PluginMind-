"use client";

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getValidToken, logout, getUserFromToken } from '@/lib/auth';

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: { email?: string; sub?: string; name?: string; picture?: string } | null;
  token: string | null;
}

export interface UseAuthReturn extends AuthState {
  login: (token: string) => void;
  logout: () => void;
  checkAuth: () => boolean;
}

/**
 * Custom hook for managing authentication state
 * Handles token validation, expiry detection, and user state
 */
export function useAuth(): UseAuthReturn {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    token: null
  });
  
  const router = useRouter();

  // Check authentication status
  const checkAuth = useCallback((): boolean => {
    const token = getValidToken();
    
    if (!token) {
      setAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null
      });
      return false;
    }

    const user = getUserFromToken(token);
    setAuthState({
      isAuthenticated: true,
      isLoading: false,
      user,
      token
    });
    return true;
  }, []);

  // Login function
  const login = useCallback((token: string) => {
    localStorage.setItem('token', token);
    const user = getUserFromToken(token);
    
    setAuthState({
      isAuthenticated: true,
      isLoading: false,
      user,
      token
    });
  }, []);

  // Logout function
  const handleLogout = useCallback(() => {
    setAuthState({
      isAuthenticated: false,
      isLoading: false,
      user: null,
      token: null
    });
    logout();
  }, []);

  // Check auth on mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Set up periodic token validation
  useEffect(() => {
    const interval = setInterval(() => {
      if (authState.isAuthenticated) {
        const isStillValid = checkAuth();
        if (!isStillValid) {
          // Token expired, redirect to login
          router.push('/login');
        }
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [authState.isAuthenticated, checkAuth, router]);

  return {
    ...authState,
    login,
    logout: handleLogout,
    checkAuth
  };
}

/**
 * Hook for components that require authentication
 * Automatically redirects to login if not authenticated
 */
export function useRequireAuth(): UseAuthReturn {
  const auth = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      router.push('/login');
    }
  }, [auth.isLoading, auth.isAuthenticated, router]);

  return auth;
}