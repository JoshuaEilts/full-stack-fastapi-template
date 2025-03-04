import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface AuthContextData {
  isAuthenticated: boolean;
  token: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    loadStoredToken();
  }, []);

  async function loadStoredToken() {
    const storedToken = await AsyncStorage.getItem('@VoicesBeyond:token');
    if (storedToken) {
      setToken(storedToken);
      api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
  }

  async function signIn(email: string, password: string) {
    try {
      const response = await api.post('/api/v1/login/access-token', {
        username: email,
        password: password,
      });

      const { access_token } = response.data;
      await AsyncStorage.setItem('@VoicesBeyond:token', access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setToken(access_token);
    } catch (error) {
      throw new Error('Authentication failed');
    }
  }

  async function signOut() {
    await AsyncStorage.removeItem('@VoicesBeyond:token');
    api.defaults.headers.common['Authorization'] = '';
    setToken(null);
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
        token,
        signIn,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 