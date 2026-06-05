"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type {
  AuthUser,
  LoginCredentials,
  RegisterCredentials,
} from "@/types/auth";

type AuthContextValue = {
  user: AuthUser | null;
  isLoading: boolean;
  role: string | null;
  login: (credentials: LoginCredentials) => Promise<AuthUser>;
  register: (credentials: RegisterCredentials) => Promise<AuthUser>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<AuthUser | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

async function readJson<T>(response: Response): Promise<T> {
  const data = (await response.json()) as T & { message?: string };

  if (!response.ok) {
    throw new Error(data.message ?? "Authentication request failed");
  }

  return data;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const data = await readJson<{ user: AuthUser | null }>(
      await fetch("/api/auth/me", { cache: "no-store" }),
    );
    setUser(data.user);
    return data.user;
  }, []);

  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    refreshUser()
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false));
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [refreshUser]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const data = await readJson<{ user: AuthUser }>(
      await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
      }),
    );
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (credentials: RegisterCredentials) => {
    const data = await readJson<{ user: AuthUser }>(
      await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
      }),
    );
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      role: user?.role ?? null,
      login,
      register,
      logout,
      refreshUser,
    }),
    [isLoading, login, logout, refreshUser, register, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
