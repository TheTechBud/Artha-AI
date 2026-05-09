"use client";

import dynamic from "next/dynamic";
import type { VelocityPoint, DRSHistoryPoint } from "@/types";
import { drsColor } from "@/lib/utils";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface VelocitySparklineProps {
  data: VelocityPoint[];
  height?: number;
}

export function VelocitySparkline({ data, height = 120 }: VelocitySparklineProps) {
  const x = data.map((d) => d.date);
  const y = data.map((d) => d.rolling_spend);
  const avg = y.reduce((a, b) => a + b, 0) / (y.length || 1);
  const last = y[y.length - 1] ?? 0;
  const isSpike = last > avg * 1.5;
  const lineColor = isSpike ? "#ef4444" : "#14b8a6";

  const plotData: Plotly.Data[] = [
    {
      type: "scatter",
      mode: "lines",
      x,
      y,
      line: { color: lineColor, width: 2, shape: "spline" },
      fill: "tozeroy",
      fillcolor: isSpike ? "rgba(239,68,68,0.08)" : "rgba(20,184,166,0.08)",
      hovertemplate: "%{x|%b %d}<br>₹%{y:,.0f}<extra></extra>",
    } as Plotly.Data,
    {
      type: "scatter",
      mode: "lines",
      x,
      y: Array(x.length).fill(avg),
      line: { color: "#8892a4", width: 1, dash: "dot" },
      hoverinfo: "none",
      showlegend: false,
    } as Plotly.Data,
  ];

  const layout: Partial<Plotly.Layout> = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { t: 8, b: 24, l: 48, r: 8 },
    height,
    xaxis: {
      showgrid: false,
      tickfont: { color: "#8892a4", size: 9, family: "Inter" },
      nticks: 5,
    },
    yaxis: {
      showgrid: true,
      gridcolor: "#1e2433",
      tickfont: { color: "#8892a4", size: 9, family: "Inter" },
      tickformat: ",.0f",
    },
    showlegend: false,
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

// ── DRS History Line ──────────────────────────────────────────────────────────

interface DRSLineProps {
  data: DRSHistoryPoint[];
  height?: number;
}

export function DRSLine({ data, height = 160 }: DRSLineProps) {
  const sorted = [...data].sort(
    (a, b) => new Date(a.calculated_at).getTime() - new Date(b.calculated_at).getTime()
  );
  const x = sorted.map((d) => d.calculated_at.split("T")[0]);
  const y = sorted.map((d) => d.score);
  const latest = y[y.length - 1] ?? 50;
  const lineColor = drsColor(latest);

  const plotData: Plotly.Data[] = [
    {
      type: "scatter",
      mode: "lines+markers",
      x,
      y,
      line: { color: lineColor, width: 2, shape: "spline" },
      marker: { color: lineColor, size: 5 },
      fill: "tozeroy",
      fillcolor: `${lineColor}14`,
      hovertemplate: "%{x}<br>DRS: <b>%{y:.0f}</b><extra></extra>",
    } as Plotly.Data,
  ];

  const layout: Partial<Plotly.Layout> = {
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    margin: { t: 8, b: 28, l: 36, r: 8 },
    height,
    xaxis: {
      showgrid: false,
      tickfont: { color: "#8892a4", size: 9, family: "Inter" },
      nticks: 6,
    },
    yaxis: {
      range: [0, 100],
      showgrid: true,
      gridcolor: "#1e2433",
      tickfont: { color: "#8892a4", size: 9, family: "Inter" },
    },
    showlegend: false,
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
