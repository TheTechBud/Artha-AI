"use client";

import dynamic from "next/dynamic";
import { drsColor } from "@/lib/utils";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface DRSGaugeProps {
  score: number;
  label: string;
}

export function DRSGauge({ score, label }: DRSGaugeProps) {
  const color = drsColor(score);

  const data: Plotly.Data[] = [
    {
      type: "indicator",
      mode: "gauge+number",
      value: score,
      number: {
        font: { size: 36, color: "#e2e8f0", family: "Inter" },
        suffix: "",
      },
      gauge: {
        axis: {
          range: [0, 100],
          tickvals: [0, 20, 40, 60, 80, 100],
          ticktext: ["0", "20", "40", "60", "80", "100"],
          tickfont: { color: "#8892a4", size: 10, family: "Inter" },
          tickcolor: "#1e2433",
          linecolor: "#1e2433",
        },
        bar: { color, thickness: 0.6 },
        bgcolor: "transparent",
        borderwidth: 0,
        steps: [
          { range: [0, 20],  color: "rgba(239,68,68,0.08)" },
          { range: [20, 40], color: "rgba(249,115,22,0.08)" },
          { range: [40, 60], color: "rgba(245,158,11,0.08)" },
          { range: [60, 80], color: "rgba(20,184,166,0.08)" },
          { range: [80, 100], color: "rgba(34,197,94,0.08)" },
        ],
        threshold: {
          line: { color, width: 3 },
          thickness: 0.8,
          value: score,
        },
      },
    } as Plotly.Data,
  ];

  const layout: Partial<Plotly.Layout> = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { t: 20, b: 20, l: 30, r: 30 },
    height: 220,
    annotations: [
      {
        text: label,
        x: 0.5,
        y: 0.12,
        xref: "paper",
        yref: "paper",
        showarrow: false,
        font: { size: 13, color, family: "Inter", weight: 500 },
      },
    ],
  };

  return (
    <Plot
      data={data}
      layout={layout}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%", height: "220px" }}
    />
  );
}
