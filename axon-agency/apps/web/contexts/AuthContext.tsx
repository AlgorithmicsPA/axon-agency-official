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

  // Maneja el caso de respuestas sin cuerpo para evitar el error "Unexpected end of JSON input"
  // cuando el servidor devuelve una respuesta vacía o no-JSON (ej: 401/403 sin body)
  const fetchUser = async () => {
    setIsLoading(true);
    try {
      // Usar API_BASE_URL directamente para evitar problemas con rewrites
      const apiBaseUrl = typeof window !== "undefined" 
        ? (process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8090")
        : "http://localhost:8090";
      const url = `${apiBaseUrl.replace(/\/$/, "")}/api/auth/me`;
      
      const res = await fetch(url, {
        credentials: "include",
      });

      if (!res.ok) {
        setUser(null);
        return;
      }

      // Leer el cuerpo como texto primero para manejar respuestas vacías
      const text = await res.text();
      if (!text) {
        setUser(null);
        return;
      }

      // Intentar parsear JSON solo si hay contenido
      const data = JSON.parse(text);
      setUser(data);
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
