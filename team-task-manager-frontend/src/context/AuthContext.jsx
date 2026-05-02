import { createContext, useState, useCallback, useMemo, useRef } from 'react';
import { authService } from '../services';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => !!localStorage.getItem('access_token'));
  const [error, setError] = useState(null);
  const initializedRef = useRef(false);

  // Initialize user from localStorage
  const initializeAuth = useCallback(async () => {
    if (initializedRef.current) {
      return;
    }

    initializedRef.current = true;
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        setLoading(true);
        const response = await authService.getCurrentUser();
        setUser(response.data);
      } catch (err) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      } finally {
        setLoading(false);
      }
    }
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      setError(null);
      setLoading(true);
      const response = await authService.login(email, password);
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      const userResponse = await authService.getCurrentUser();
      setUser(userResponse.data);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const signup = useCallback(async (email, fullName, password) => {
    try {
      setError(null);
      setLoading(true);
      await authService.signup(email, fullName, password);
      await login(email, password);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }, []);

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
