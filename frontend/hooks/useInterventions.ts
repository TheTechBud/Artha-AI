import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

// ── Interventions ─────────────────────────────────────────────────────────────

export function useInterventions() {
  return useQuery({
    queryKey: ["interventions"],
    queryFn: api.interventions.list,
  });
}

export function useGenerateIntervention() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (riskType?: string) => api.interventions.generate(riskType),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["interventions"] }),
  });
}

export function useDismissIntervention() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.interventions.dismiss(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["interventions"] }),
  });
}

// ── Narrative ─────────────────────────────────────────────────────────────────

export function useNarrative() {
  return useQuery({
    queryKey: ["narrative", "latest"],
    queryFn: api.narrative.latest,
  });
}

export function useGenerateNarrative() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.narrative.generate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["narrative"] }),
  });
}

// ── AI ────────────────────────────────────────────────────────────────────────

export function useArchetype() {
  return useQuery({
    queryKey: ["ai", "archetype"],
    queryFn: api.ai.archetype,
    staleTime: 10 * 60 * 1000, // 10 min — archetype rarely changes
  });
}

export function useRisks() {
  return useQuery({
    queryKey: ["ai", "risks"],
    queryFn: api.ai.risks,
  });
}

export function usePredictionsCalendar() {
  return useQuery({
    queryKey: ["ai", "calendar"],
    queryFn: api.ai.calendar,
  });
}
