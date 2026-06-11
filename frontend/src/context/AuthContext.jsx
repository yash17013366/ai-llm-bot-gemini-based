import { createContext, useCallback, useContext, useMemo, useState } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isAuthenticated = Boolean(token);

  const persistToken = useCallback((accessToken) => {
    localStorage.setItem("token", accessToken);
    setToken(accessToken);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post("/auth/login", { email, password });
      persistToken(response.data.access_token);
      return true;
    } catch (err) {
      const message =
        err.response?.data?.detail || "Login failed. Please try again.";
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [persistToken]);

  const register = useCallback(async (username, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post("/auth/register", {
        username,
        email,
        password,
      });
      persistToken(response.data.access_token);
      return true;
    } catch (err) {
      const message =
        err.response?.data?.detail || "Registration failed. Please try again.";
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [persistToken]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setError(null);
  }, []);

  const value = useMemo(
    () => ({
      token,
      isAuthenticated,
      loading,
      error,
      login,
      register,
      logout,
      clearError,
    }),
    [token, isAuthenticated, loading, error, login, register, logout, clearError]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
