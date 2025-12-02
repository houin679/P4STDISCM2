import React from 'react';
import api from '@/lib/api';

type UserRole = 'unauthenticated' | 'student' | 'faculty' | 'course_audit_admin';

interface AuthContextType {
  userRole: UserRole;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userRole, setUserRole] = React.useState<UserRole>('unauthenticated');

  React.useEffect(() => {
    // On mount, check for token. We don't parse token here; assume frontend refresh flow.
    const token = localStorage.getItem('access_token');
    if (!token) return;
    // Optionally decode token to extract user id / exp. For now, attempt refresh to validate.
    (async () => {
      try {
        const res = await fetch((import.meta.env.VITE_API_URL as string || 'http://127.0.0.1:8000') + '/api/auth/refresh', { method: 'POST', credentials: 'include' });
        if (!res.ok) {
          localStorage.removeItem('access_token');
          setUserRole('unauthenticated');
          return;
        }
        const data = await res.json();
        if (data.role) setUserRole(data.role as UserRole);
        if (data.access_token) localStorage.setItem('access_token', data.access_token);
      } catch {
        localStorage.removeItem('access_token');
        setUserRole('unauthenticated');
      }
    })();
  }, []);

  const login = async (username: string, password: string) => {
    const res = await api.loginRequest(username, password);
    if (!res.ok) return false;
    const data = await res.json();
    if (data.access_token) localStorage.setItem('access_token', data.access_token);
    if (data.role) setUserRole(data.role);
    else setUserRole('student');
    return true;
  };

  const logout = async () => {
    await api.logoutRequest();
    localStorage.removeItem('access_token');
    setUserRole('unauthenticated');
  };

  return (
    <AuthContext.Provider value={{ userRole, login, logout }}>{children}</AuthContext.Provider>
  );
};

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
