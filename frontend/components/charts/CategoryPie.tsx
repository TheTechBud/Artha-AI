"use client";

import dynamic from "next/dynamic";
import { categoryColor } from "@/lib/utils";
import type { CategorySpend } from "@/types";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface CategoryPieProps {
  data: CategorySpend[];
  height?: number;
}

export function CategoryPie({ data, height = 260 }: CategoryPieProps) {
  const top = [...data].sort((a, b) => b.total - a.total).slice(0, 6);

  const plotData: Plotly.Data[] = [
    {
      type: "pie",
      labels: top.map((d) => d.category),
      values: top.map((d) => d.total),
      hole: 0.62,
      marker: {
        colors: top.map((d) => categoryColor(d.category)),
        line: { color: "#161b27", width: 2 },
      },
      textinfo: "none",
      hovertemplate: "<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
      rotation: -90,
    } as Plotly.Data,
  ];

  const layout: Partial<Plotly.Layout> = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { t: 0, b: 0, l: 0, r: 0 },
    height,
    showlegend: true,
    legend: {
      orientation: "v",
      x: 0.72,
      y: 0.5,
      font: { color: "#8892a4", size: 10, family: "Inter" },
      bgcolor: "transparent",
      itemclick: false,
      itemdoubleclick: false,
    },
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
