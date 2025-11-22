"use client"
import * as React from "react"
import {   ChartCard,
  ChartCardHeader,
  ChartCardFooter,
  ChartCardTitle,
  ChartCardDescription,
  ChartCardContent, } from "@/componets/ui/chart-card"
import { ChartContainer,  ChartTooltip,
  PieChart,
  Pie,
  Label } from "@/componets/ui/charts-parts"

export interface PieDonutChartData {
  name: string
  value: number
  color?: string
}

interface PieDonutTextProps {
  data?: PieDonutChartData[] // делаем опциональным
  title?: string
  description?: string
  centerText?: string
  centerLabel?: string
  height?: number
}

export const PieDonutText: React.FC<PieDonutTextProps> = ({
  data = [], 
  title = "Диаграмма",
  description,
  centerText,
  centerLabel = "Всего",
  height = 300,
}) => {
  const total = React.useMemo(() => {
    return data?.reduce((sum, item) => sum + item.value, 0) || 0
  }, [data])

  const chartConfig = React.useMemo(() => {
    return data?.reduce((config, item) => {
      config[item.name] = {
        label: item.name,
        color: item.color || `hsl(${Math.random() * 360}, 70%, 50%)`
      }
      return config
    }, {} as any) || {}
  }, [data])

  // Если данных нет, показываем заглушку
  if (!data || data.length === 0) {
    return (
      <ChartCard className="w-[400px]">
        <ChartCardHeader>
          <ChartCardTitle>{title}</ChartCardTitle>
          {description && <ChartCardDescription>{description}</ChartCardDescription>}
        </ChartCardHeader>
        <ChartCardContent>
          <div className="flex items-center justify-center" style={{ height }}>
            <p className="text-gray-500">Нет данных для отображения</p>
          </div>
        </ChartCardContent>
      </ChartCard>
    )
  }

  return (
    <ChartCard className="w-[400px]">
      <ChartCardHeader>
        <ChartCardTitle>{title}</ChartCardTitle>
        {description && <ChartCardDescription>{description}</ChartCardDescription>}
      </ChartCardHeader>
      
      <ChartCardContent>
        <ChartContainer 
          config={chartConfig}
          className="mx-auto aspect-square"
          style={{ height }}
        >
          <PieChart>
            <ChartTooltip />
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius="60%"
              outerRadius="80%"
              stroke="none"
            >
              {data.map((entry, index) => (
                <cell 
                  key={`cell-${index}`} 
                  fill={entry.color || `hsl(${index * 60}, 70%, 50%)`} 
                />
              ))}
              
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="text-2xl font-bold fill-foreground"
                        >
                          {centerText || total.toLocaleString()}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy + 24}
                          className="text-sm fill-muted-foreground"
                        >
                          {centerLabel}
                        </tspan>
                      </text>
                    )
                  }
                  return null
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </ChartCardContent>
      
      <ChartCardFooter>
        <div className="text-sm text-muted-foreground">
          Общее количество: {total.toLocaleString()}
        </div>
      </ChartCardFooter>
    </ChartCard>
  )
}



export default PieDonutText