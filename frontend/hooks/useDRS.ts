import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useDRS() {
  return useQuery({
    queryKey: ["drs", "current"],
    queryFn: api.drs.current,
  });
}

export function useDRSHistory(days = 30) {
  return useQuery({
    queryKey: ["drs", "history", days],
    queryFn: () => api.drs.history(days),
  });
}

export function useRecalculateDRS() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.drs.recalculate,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["drs"] });
      qc.invalidateQueries({ queryKey: ["ai"] });
      qc.invalidateQueries({ queryKey: ["interventions"] });
      qc.invalidateQueries({ queryKey: ["narrative"] });
    },
  });
}
