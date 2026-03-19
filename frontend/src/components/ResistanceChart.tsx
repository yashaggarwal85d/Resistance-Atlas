"use client";
import { BarChart, Bar, XAxis, YAxis, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { AntibioticResult } from "@/lib/types";

interface Props {
  antibiotics: AntibioticResult[];
}

const RISK_COLORS = {
  Resistant: "#ef4444",
  Susceptible: "#10b981",
};

export default function ResistanceChart({ antibiotics }: Props) {
  const data = antibiotics.map((a) => ({
    name: a.antibiotic.length > 12 ? a.antibiotic.slice(0, 11) + "\u2026" : a.antibiotic,
    fullName: a.antibiotic,
    confidence: Math.round(a.confidence * 100),
    prediction: a.prediction,
  }));

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 12, right: 24, top: 4, bottom: 4 }}>
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12, fill: "#374151" }}
            axisLine={false}
            tickLine={false}
            width={88}
          />
          <Tooltip
            formatter={(value: number, _: string, entry: any) => [
              `${value}% confidence`,
              entry.payload.prediction,
            ]}
            labelFormatter={(label: string, payload: any[]) =>
              payload?.[0]?.payload?.fullName || label
            }
            contentStyle={{
              borderRadius: "8px",
              border: "0.5px solid #e5e7eb",
              fontSize: "13px",
            }}
          />
          <Bar dataKey="confidence" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={RISK_COLORS[entry.prediction as keyof typeof RISK_COLORS]}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
