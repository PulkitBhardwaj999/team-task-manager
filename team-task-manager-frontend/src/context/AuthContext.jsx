import { createContext, useState, useCallback, useMemo, useRef, useEffect } from 'react';
import { authService } from '../services';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // always start true
  const [error, setError] = useState(null);
  const initializedRef = useRef(false);

  // ─────────────────────────────────────────────────────────────
  // INIT AUTH (runs once)
  // ─────────────────────────────────────────────────────────────
  const initializeAuth = useCallback(async () => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    const token = localStorage.getItem('access_token');

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await authService.getCurrentUser();
      setUser(response.data);
    } catch (err) {
      console.error("INIT AUTH FAILED:", err);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // run on app mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // ─────────────────────────────────────────────────────────────
  // LOGIN
  // ─────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    try {
      setError(null);
      setLoading(true);

      // clear old tokens (IMPORTANT)
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');

      const response = await authService.login(email, password);

      const { access_token, refresh_token } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // fetch fresh user
      const userResponse = await authService.getCurrentUser();

      console.log("LOGIN USER:", userResponse.data);

      setUser(userResponse.data);

      return true;
    } catch (err) {
      console.error("LOGIN ERROR:", err);
      setError(err.response?.data?.detail || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // ─────────────────────────────────────────────────────────────
  // SIGNUP (FIXED)
  // ─────────────────────────────────────────────────────────────
  const signup = useCallback(async (email, fullName, password, role = 'member') => {
    try {
      setError(null);
      setLoading(true);

      // clear old tokens BEFORE signup (CRITICAL FIX)
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');

      await authService.signup(email, fullName, password, role);

      // immediately login after signup
      const success = await login(email, password);

      return success;
    } catch (err) {
      console.error("SIGNUP ERROR:", err);
      setError(err.response?.data?.detail || 'Signup failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [login]);

  // ─────────────────────────────────────────────────────────────
  // LOGOUT
  // ─────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }, []);

  // ─────────────────────────────────────────────────────────────
  // CONTEXT VALUE
  // ─────────────────────────────────────────────────────────────
  const value = useMemo(() => ({
    user,
    loading,
    error,
    login,
    signup,
    logout,
    initializeAuth,
    isAuthenticated: !!user
  }), [user, loading, error, login, signup, logout, initializeAuth]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}