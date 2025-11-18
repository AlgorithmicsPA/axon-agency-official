"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface User {
  id?: number;
  username: string;
  email?: string;
  role: string;
  is_admin?: boolean;
  tenant_id?: string | null;
  tenant_slug?: string | null;
  tenant_name?: string | null;
}

interface AuthContextType {
  user: User | null;
  role: string | null;
  isAdmin: boolean;
  isClient: boolean;
  tenantId: string | null;
  tenantSlug: string | null;
  tenantName: string | null;
  isTenantUser: boolean;
  isLoading: boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  role: null,
  isAdmin: false,
  isClient: false,
  tenantId: null,
  tenantSlug: null,
  tenantName: null,
  isTenantUser: false,
  isLoading: true,
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const response = await fetch("/api/auth/me", {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("Error fetching user:", error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const role = user?.role || null;
  const isAdmin = user?.is_admin === true || role === "admin";
  const isClient = role === "viewer" || role === "member";
  
  // Tenant context from user
  const tenantId = user?.tenant_id || null;
  const tenantSlug = user?.tenant_slug || null;
  const tenantName = user?.tenant_name || null;
  const isTenantUser = !!tenantId && !isAdmin;

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAdmin,
        isClient,
        tenantId,
        tenantSlug,
        tenantName,
        isTenantUser,
        isLoading,
        refreshUser: fetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
