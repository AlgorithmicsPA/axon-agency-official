"use client";

import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import type { Metrics } from "@/lib/types";

export function useMetrics() {
  const api = useApiClient();
  
  return useQuery({
    queryKey: ["metrics"],
    queryFn: async () => {
      const { data } = await api.get<Metrics>("/api/metrics");
      return data;
    },
    refetchInterval: 2000,
    refetchOnWindowFocus: false,
  });
}
