"use client";

import dynamic from "next/dynamic";
import { categoryColor } from "@/lib/utils";
import type { CategorySpend } from "@/types";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface SpendingChartProps {
  data: CategorySpend[];
  height?: number;
}

export function SpendingChart({ data, height = 260 }: SpendingChartProps) {
  const sorted = [...data].sort((a, b) => b.total - a.total).slice(0, 8);
  const labels = sorted.map((d) => d.category);
  const values = sorted.map((d) => d.total);
  const colors = sorted.map((d) => categoryColor(d.category));

  const plotData: Plotly.Data[] = [
    {
      type: "bar",
      orientation: "h",
      x: values,
      y: labels,
      marker: {
        color: colors,
        opacity: 0.85,
        line: { width: 0 },
      },
      text: values.map((v) => `₹${(v / 1000).toFixed(1)}K`),
      textposition: "outside",
      textfont: { color: "#8892a4", size: 11, family: "Inter" },
      hovertemplate: "<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    } as Plotly.Data,
  ];

  const layout: Partial<Plotly.Layout> = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { t: 10, b: 30, l: 110, r: 60 },
    height,
    xaxis: {
      gridcolor: "#1e2433",
      gridwidth: 1,
      tickfont: { color: "#8892a4", size: 10, family: "Inter" },
      showline: false,
      zeroline: false,
    },
    yaxis: {
      tickfont: { color: "#c4cbd8", size: 11, family: "Inter" },
      showgrid: false,
      zeroline: false,
      autorange: "reversed",
    },
    bargap: 0.35,
  };

  return (
    <Plot
      data={plotData}
      layout={layout}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%", height: `${height}px` }}
    />
  );
}
