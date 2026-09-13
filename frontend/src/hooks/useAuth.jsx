import { useState, useEffect, createContext, useContext } from 'react';
import * as api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const res = await api.checkAuth();
      setUser(res.data?.user || { username: 'admin' });
      setIsAuthenticated(true);
    } catch (error) {
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      setLoading(true);
      const res = await api.loginUser(username, password);
      const userData = res.data?.user || { username };
      setUser(userData);
      setIsAuthenticated(true);
      return { success: true, user: userData };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Credenciales incorrectas. Verifique usuario y contraseña.'
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.logoutUser();
    } catch (error) {
      console.error('Logout error', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, login, logout, checkAuth, rol: user?.rol }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
