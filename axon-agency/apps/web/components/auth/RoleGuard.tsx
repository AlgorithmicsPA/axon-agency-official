"use client";

import { ReactNode } from "react";
import { useAuth } from "@/contexts/AuthContext";

interface RoleGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function AdminOnly({ children, fallback = null }: RoleGuardProps) {
  const { isAdmin, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (!isAdmin) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

export function ClientOnly({ children, fallback = null }: RoleGuardProps) {
  const { isClient, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (!isClient) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

export function AuthenticatedOnly({ children, fallback = null }: RoleGuardProps) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (!user) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

export function TenantOnly({ children, fallback = null }: RoleGuardProps) {
  const { isTenantUser, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (!isTenantUser) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
