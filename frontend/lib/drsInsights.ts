import type { DRSComponents } from "@/types";

/** Mirrors backend utils/constants.py DRS_WEIGHTS */
const DRS_WEIGHTS: Record<keyof DRSComponents, number> = {
  budget_adherence: 0.25,
  velocity_stability: 0.2,
  savings_rate: 0.2,
  recurring_coverage: 0.15,
  emotional_spend: 0.1,
  salary_gap: 0.1,
};

export interface DriverInsight {
  key: keyof DRSComponents;
  /** Contribution to DRS in points (0–100 scale), approximate */
  points: number;
  strength01: number;
}

/** Sorted strongest contributors to the headline score (highest weighted contribution first). */
export function rankDrivers(components: DRSComponents): DriverInsight[] {
  const rows = (Object.keys(DRS_WEIGHTS) as (keyof DRSComponents)[]).map((key) => {
    const strength01 = components[key];
    const points = strength01 * DRS_WEIGHTS[key] * 100;
    return { key, points, strength01 };
  });
  return rows.sort((a, b) => b.points - a.points);
}

/** Components dragging the score down most (lowest strength first). */
export function weakestLinks(components: DRSComponents, take = 2): DriverInsight[] {
  return rankDrivers(components)
    .slice()
    .sort((a, b) => a.strength01 - b.strength01)
    .slice(0, take);
}
