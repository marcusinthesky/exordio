"use client";

import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@exordio/ui/components/chart";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";

export function ActivityChart({
  data,
  label = "Activity",
}: {
  data: { label: string; value: number }[];
  label?: string;
}) {
  return (
    <figure className="space-y-3">
      <figcaption className="sr-only">{label}</figcaption>
      <ChartContainer
        config={{ value: { label, color: "var(--chart-1)" } }}
        className="h-52 w-full"
      >
        <AreaChart
          data={data}
          accessibilityLayer
          margin={{ left: 8, right: 8 }}
        >
          <CartesianGrid vertical={false} />
          <XAxis
            dataKey="label"
            tickLine={false}
            axisLine={false}
            tickMargin={8}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Area
            type="monotone"
            dataKey="value"
            stroke="var(--color-value)"
            fill="var(--color-value)"
            fillOpacity={0.12}
            strokeWidth={2}
            isAnimationActive={false}
          />
        </AreaChart>
      </ChartContainer>
      <table className="sr-only">
        <caption>{label} data</caption>
        <thead>
          <tr>
            <th scope="col">Period</th>
            <th scope="col">Value</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.label}>
              <th scope="row">{item.label}</th>
              <td>{item.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
