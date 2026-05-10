import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { TransactionUploadEnvelope } from "@/types";

export function useTransactions(page = 1, pageSize = 50, category?: string) {
  return useQuery({
    queryKey: ["transactions", page, pageSize, category],
    queryFn: () => api.transactions.list(page, pageSize, category),
  });
}

export function useUploadTransactions() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File): Promise<TransactionUploadEnvelope> => api.transactions.upload(file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["analytics"] });
      qc.invalidateQueries({ queryKey: ["drs"] });
      qc.invalidateQueries({ queryKey: ["interventions"] });
      qc.invalidateQueries({ queryKey: ["narrative"] });
      qc.invalidateQueries({ queryKey: ["ai"] });
    },
  });
}

export function useAnalyticsSummary() {
  return useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: api.analytics.summary,
  });
}

export function useVelocity() {
  return useQuery({
    queryKey: ["analytics", "velocity"],
    queryFn: api.analytics.velocity,
  });
}

export function useRecurring() {
  return useQuery({
    queryKey: ["analytics", "recurring"],
    queryFn: api.analytics.recurring,
  });
}
