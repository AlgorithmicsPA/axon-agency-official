"use client";

import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import type { Catalog } from "@/lib/types";

export function useCatalog() {
  const api = useApiClient();
  
  return useQuery({
    queryKey: ["catalog"],
    queryFn: async () => {
      const { data } = await api.get<Catalog>("/api/catalog");
      return data;
    },
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
