"use client";

import { TrendingUp } from "lucide-react";
import { Area, AreaChart, CartesianGrid, XAxis, ResponsiveContainer } from "recharts";
import { ChartCard, ChartCardContent, ChartCardDescription, ChartCardFooter, ChartCardHeader, ChartCardTitle } from "@/componets/ui/chart-components";
import { ChartConfig, ChartContainer ,ChartTooltip, ChartTooltipContent, } from "@/componets/ui/chart-components";

const chartData = [
  { month: "January", desktop: 186, mobile: 80 },
  { month: "February", desktop: 305, mobile: 200 },
  { month: "March", desktop: 237, mobile: 120 },
  { month: "April", desktop: 73, mobile: 190 },
  { month: "May", desktop: 209, mobile: 130 },
  { month: "June", desktop: 214, mobile: 140 },
];

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#9E88F9",
  },
  mobile: {
    label: "Mobile",
    color: "#5D39F5",
  },
} satisfies ChartConfig;

export function ChartAreaStacked() {
  return (
    <ChartCard className="w-full">
      <ChartCardContent className="p-0">
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              accessibilityLayer
              data={chartData}
              margin={{
                left: 12,
                right: 12,
                top: 20,
                bottom: 20,
              }}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="month"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={(value) => value.slice(0, 3)}
              />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent indicator="dot" />}
              />
              <Area
                dataKey="mobile"
                type="natural"
                fill={chartConfig.mobile.color}
                fillOpacity={0.4}
                stroke={chartConfig.mobile.color}
                stackId="a"
              />
              <Area
                dataKey="desktop"
                type="natural"
                fill={chartConfig.desktop.color}
                fillOpacity={0.4}
                stroke={chartConfig.desktop.color}
                stackId="a"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartContainer>
      </ChartCardContent>
      <ChartCardFooter>
        <div className="flex w-full items-start gap-2 text-sm">
          <div className="grid gap-2">
            <div className="flex items-center gap-2 leading-none font-medium">
              Выросло на 5.2% в этот месяц <TrendingUp className="h-4 w-4" />
            </div>
            <div className="text-gray-500 flex items-center gap-2 leading-none">
              Январь - Ноябрь 2025
            </div>
          </div>
        </div>
      </ChartCardFooter>
    </ChartCard>
  );
}