"use client";

import { ReactNode } from "react";
import { useAuth } from "@/hooks/useAuth";

interface Session {
  user: {
    id: string;
    email: string;
    name?: string;
  };
  token: string;
}

interface SessionContextType {
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  refreshSession: () => Promise<void>;
  logout: () => Promise<void>;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // This provider is now deprecated/redundant as the app is wrapped 
  // with the main AuthProvider from hooks/useAuth in layout.tsx.
  // We keep this as a passthrough to avoid breaking existing imports.
  return <>{children}</>;
}

export function useSession(): SessionContextType {
  const { user, isLoading, isAuthenticated, refreshSession, logout } = useAuth();

  // Map useAuth state to the expected Session shape
  const session: Session | null = user ? {
    user: user,
    token: "", // Token is managed internally by apiClient/cookies, not exposed in useAuth
  } : null;

  return {
    session,
    isLoading,
    isAuthenticated,
    refreshSession,
    logout,
  };
}
