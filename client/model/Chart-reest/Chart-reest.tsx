"use client";

import { TrendingUp } from "lucide-react";
import { Area, AreaChart, CartesianGrid, XAxis, ResponsiveContainer } from "recharts";
import { ChartCard, ChartCardContent, ChartCardDescription, ChartCardFooter, ChartCardHeader, ChartCardTitle } from "@/componets/ui/chart-components";
import { ChartConfig, ChartContainer ,ChartTooltip, ChartTooltipContent, } from "@/componets/ui/chart-components";

const chartData = [
  { month: "Январь", Всего: 186, Аккредитовано: 80 },
  { month: "Февраль", Всего: 305, Аккредитовано: 200 },
  { month: "Март", Всего: 237, Аккредитовано: 120 },
  { month: "Апрель", Всего: 190, Аккредитовано: 190 },
  { month: "Май", Всего: 209, Аккредитовано: 130 },
  { month: "Июнь", Всего: 214, Аккредитовано: 140 },
  { month: "Июль", Всего: 414, Аккредитовано: 140 },
  { month: "Август", Всего: 384, Аккредитовано: 345 },
  { month: "Сентябрь", Всего: 314, Аккредитовано: 290 },
  { month: "Октябрь", Всего: 214, Аккредитовано: 214 },
  { month: "Ноябрь", Всего: 314, Аккредитовано: 261 },
];

const chartConfig = {
  Всего: {
    label: "Всего",
    color: "#9E88F9",
  },
  Аккредитовано: {
    label: "Аккредитовано",
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
                dataKey="Всего"
                type="natural"
                fill={chartConfig.Всего.color}
                fillOpacity={0.4}
                stroke={chartConfig.Всего.color}
                stackId="a"
              />
              <Area
                dataKey="Аккредитовано"
                type="natural"
                fill={chartConfig.Аккредитовано.color}
                fillOpacity={0.4}
                stroke={chartConfig.Аккредитовано.color}
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